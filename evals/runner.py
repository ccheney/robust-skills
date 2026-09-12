#!/usr/bin/env python3
"""Run bounded skill selection and artifact evals with Gemini's free-tier API."""

import argparse
import hashlib
import json
import random
import subprocess
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from evals.catalog import Catalog, TOOLS, snapshot
from evals.credentials import from_gcloud
from evals.graders import grade
from evals.providers import DEFAULT_MODEL, Gemini, EvalUnavailable
from evals.validation import validate

HARNESS_VERSION = 2


def run_trial(client, texts, prompt, max_turns=4):
    catalog = Catalog(texts)
    instruction = (
        "Complete the user request. The user's explicit instructions take precedence over skill guidelines. "
        "Use relevant skills when their guidance helps. You can read supplied skill references; "
        "no shell, network, posting, or database tools are available. Return the requested artifact directly."
    )
    if catalog.entries:
        instruction += "\nAvailable skills:\n" + catalog.discovery()
    messages = [
        {"role": "system", "content": instruction},
        {"role": "user", "content": prompt},
    ]
    trace, tokens = [], Counter()
    started = time.monotonic()
    outcome, detail, answer = "inconclusive", "Turn limit reached", ""
    for _ in range(max_turns):
        try:
            response = client.chat(messages, TOOLS if catalog.entries else [])
        except EvalUnavailable as exc:
            outcome, detail = "blocked", str(exc)
            break
        choice = response["choices"][0]
        if not isinstance(choice, dict):
            outcome, detail = "error", "Invalid completion choice"
            break
        message = choice.get("message")
        if not isinstance(message, dict):
            outcome, detail = "error", "Completion has no message object"
            break
        # Preserve the complete message (including provider thought signatures) for replay.
        messages.append(message)
        trace.append(
            {
                "message": message,
                "finish_reason": choice.get("finish_reason"),
                "model": response.get("model"),
                "usage": response.get("usage"),
            }
        )
        usage = response.get("usage")
        for key, value in (usage if isinstance(usage, dict) else {}).items():
            if type(value) is int:
                tokens[key] += value
        if choice.get("finish_reason") not in ("stop", "tool_calls"):
            detail = f"Completion stopped: {choice.get('finish_reason')}"
            break
        calls = message.get("tool_calls") or []
        if not isinstance(calls, list) or len(calls) > 16:
            outcome, detail = "error", "Invalid or excessive tool calls"
            break
        if not calls:
            answer = message.get("content") or ""
            if not isinstance(answer, str) or not answer.strip():
                outcome, detail = "error", "Empty final answer"
            else:
                outcome, detail = "completed", ""
            break
        for call in calls:
            try:
                function = call["function"]
                arguments = function.get("arguments", "{}")
                args = (
                    json.loads(arguments) if isinstance(arguments, str) else arguments
                )
                tool_result = catalog.invoke(function["name"], args)
                call_id = call["id"]
            except (KeyError, TypeError, ValueError, AttributeError):
                outcome, detail = "error", "Malformed tool call"
                break
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call_id,
                    "content": json.dumps(tool_result),
                }
            )
            trace.append(
                {"tool": function["name"], "arguments": args, "result": tool_result}
            )
        if outcome == "error":
            break
    return {
        "status": outcome,
        "detail": detail,
        "answer": answer,
        "selected_skills": sorted(catalog.loaded),
        "references_read": catalog.reads,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "tokens": dict(tokens),
        "trace": trace,
    }


def build_plan(root, profile, variants, repeats, seed, baseline_ref=None):
    config = json.loads((root / "evals/profiles.json").read_text())[profile]
    routing = json.loads((root / "evals/routing.json").read_text())
    tasks = json.loads((root / "evals/pilot.json").read_text())
    for key, cases in [("routing", routing), ("tasks", tasks)]:
        if config[key] != "all" and set(config[key]) - {c["id"] for c in cases}:
            raise ValueError(f"Unknown case IDs in profile {profile}: {key}")
    if config["routing"] != "all":
        routing = [c for c in routing if c["id"] in config["routing"]]
    if config["tasks"] != "all":
        tasks = [c for c in tasks if c["id"] in config["tasks"]]
    if "baseline" in variants and not baseline_ref:
        raise ValueError("The baseline variant needs --baseline-ref")
    trials = []
    for kind, cases in [("routing", routing), ("task", tasks)]:
        for case in cases:
            for variant in variants:
                if kind == "routing" and variant == "none":
                    continue
                for repeat in range(repeats):
                    trials.append(
                        {
                            "kind": kind,
                            "case": case,
                            "variant": variant,
                            "repeat": repeat + 1,
                        }
                    )
    random.Random(seed).shuffle(trials)
    if not trials:
        raise ValueError("The selected profile/variants contain no trials")
    return trials


def summarize(rows):
    summary = {}
    for variant in sorted({r["variant"] for r in rows}):
        selected = [r for r in rows if r["variant"] == variant]
        section = {}
        for kind in ("routing", "task"):
            group = [r for r in selected if r["kind"] == kind]
            counts = dict(Counter(r["status"] for r in group))
            completed = counts.get("pass", 0) + counts.get("fail", 0)
            section[kind] = {
                "counts": counts,
                "scored": completed,
                "pass_rate": counts.get("pass", 0) / completed if completed else None,
            }
            if kind == "routing":
                scored = [r for r in group if r["status"] in ("pass", "fail")]
                tp = sum(
                    len(set(r["expected_skills"]) & set(r["selected_skills"]))
                    for r in scored
                )
                fp = sum(
                    len(set(r["selected_skills"]) - set(r["expected_skills"]))
                    for r in scored
                )
                fn = sum(
                    len(set(r["expected_skills"]) - set(r["selected_skills"]))
                    for r in scored
                )
                section[kind].update(
                    true_positives=tp,
                    false_positives=fp,
                    false_negatives=fn,
                    precision=tp / (tp + fp) if tp + fp else None,
                    recall=tp / (tp + fn) if tp + fn else None,
                )
        summary[variant] = section
    return summary


def save_report(path, report):
    path.mkdir(parents=True, exist_ok=True)
    (path / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    lines = [
        "# Skill evaluation results",
        "",
        f"Model: `{report['model']}`. Harness: `{report['harness_version']}`.",
        "",
        "These results measure the API model with this repository harness, not Codex/Copilot/Claude Code activation.",
        "",
        "| Variant | Suite | Passed | Failed | Unscored |",
        "|---|---|---:|---:|---:|",
    ]
    for variant, suites in report["summary"].items():
        for suite, data in suites.items():
            c = data["counts"]
            unscored = sum(v for k, v in c.items() if k not in ("pass", "fail"))
            lines.append(
                f"| {variant} | {suite} | {c.get('pass', 0)} | {c.get('fail', 0)} | {unscored} |"
            )
    lines += [
        "",
        f"Provider requests: {report.get('requests', 0)}. Missing credentials, quota limits, truncation, and unavailable graders are never counted as passes.",
    ]
    (path / "summary.md").write_text("\n".join(lines) + "\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=["smoke", "full"], default="smoke")
    parser.add_argument("--variants", default="candidate,none")
    parser.add_argument("--baseline-ref")
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-requests", type=int, default=24)
    parser.add_argument("--max-turns", type=int, default=4)
    parser.add_argument("--interval", type=float, default=15)
    parser.add_argument("--timeout", type=float, default=90)
    parser.add_argument("--output", type=Path, default=Path("evals/results/latest"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--local-config", type=Path, default=Path(__file__).parent / "local.json"
    )
    parser.add_argument(
        "--no-local-config",
        action="store_true",
        help="Use environment credentials only",
    )
    args = parser.parse_args(argv)
    variants = args.variants.split(",")
    if (
        not variants
        or len(set(variants)) != len(variants)
        or set(variants) - {"candidate", "none", "baseline"}
    ):
        parser.error("Choose distinct candidate, none, and/or baseline variants")
    if (
        not 1 <= args.repeats <= 10
        or not 1 <= args.max_requests <= 500
        or not 1 <= args.max_turns <= 10
        or not 0 <= args.interval <= 60
        or not 1 <= args.timeout <= 180
    ):
        parser.error(
            "Invalid run limits (repeats 1..10, requests 1..500, turns 1..10, interval 0..60, timeout 1..180)"
        )
    root = Path(__file__).resolve().parents[1]
    try:
        validate(root)
        trials = build_plan(
            root, args.profile, variants, args.repeats, args.seed, args.baseline_ref
        )
        sha, texts = snapshot(root)
        snapshots = {"candidate": texts, "none": {}}
        refs = {"candidate": sha, "none": None}
        if "baseline" in variants:
            refs["baseline"], snapshots["baseline"] = snapshot(root, args.baseline_ref)
    except (ValueError, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))
    dirty = bool(
        subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=root, text=True
        ).strip()
    )
    plan = [
        {
            "id": t["case"]["id"],
            "kind": t["kind"],
            "variant": t["variant"],
            "repeat": t["repeat"],
        }
        for t in trials
    ]
    if args.dry_run:
        print(
            json.dumps(
                {
                    "model": DEFAULT_MODEL,
                    "profile": args.profile,
                    "trials": plan,
                    "max_requests": args.max_requests,
                },
                indent=2,
            )
        )
        return 0
    report = {
        "harness_version": HARNESS_VERSION,
        "model": DEFAULT_MODEL,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "git_refs": refs,
        "dirty": dirty,
        "profile": args.profile,
        "seed": args.seed,
        "snapshots": {
            v: hashlib.sha256(json.dumps(t, sort_keys=True).encode()).hexdigest()
            for v, t in snapshots.items()
        },
        "case_set_sha256": hashlib.sha256(
            json.dumps(trials, sort_keys=True).encode()
        ).hexdigest(),
        "limits": {
            "max_requests": args.max_requests,
            "max_turns": args.max_turns,
            "interval": args.interval,
            "timeout": args.timeout,
        },
        "trials": [],
        "summary": {},
        "requests": 0,
    }
    unavailable = None
    try:
        credentials = None if args.no_local_config else from_gcloud(args.local_config)
        client = Gemini(
            max_requests=args.max_requests,
            interval=args.interval,
            timeout=args.timeout,
            key=credentials["key"] if credentials else None,
            verified_free_tier=bool(credentials),
        )
        report["credential_source"] = (
            credentials["source"] if credentials else {"method": "environment"}
        )
    except EvalUnavailable as exc:
        unavailable = str(exc)
    for trial in trials:
        case = trial["case"]
        prompt = case["prompt"]
        if trial["kind"] == "task":
            prompt += (
                "\n\nInput file "
                + case["input"]
                + ":\n"
                + (root / "evals" / case["input"]).read_text()
            )
        if unavailable:
            outcome = {
                "status": "blocked",
                "detail": unavailable,
                "selected_skills": [],
                "tokens": {},
                "trace": [],
            }
        else:
            outcome = run_trial(
                client, snapshots[trial["variant"]], prompt, args.max_turns
            )
            report["requests"] = client.requests
            report["provider_events"] = client.events
        if outcome["status"] == "completed":
            if trial["kind"] == "routing":
                outcome.update(
                    status="pass"
                    if set(outcome["selected_skills"]) == set(case["expected_skills"])
                    else "fail",
                    detail="Observed read_skill calls compared with expected selection",
                )
            else:
                outcome.update(grade(root, case, outcome["answer"]))
        row = {
            "id": case["id"],
            "kind": trial["kind"],
            "variant": trial["variant"],
            "repeat": trial["repeat"],
            **outcome,
        }
        if trial["kind"] == "routing":
            row["expected_skills"] = case["expected_skills"]
        report["trials"].append(row)
        report["summary"] = summarize(report["trials"])
        save_report(args.output, report)
        print(
            f"{row['variant']} {row['id']} #{row['repeat']}: {row['status']}",
            flush=True,
        )
    statuses = {r["status"] for r in report["trials"]}
    return 2 if statuses - {"pass", "fail"} else (1 if "fail" in statuses else 0)


if __name__ == "__main__":
    raise SystemExit(main())
