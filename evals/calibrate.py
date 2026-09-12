"""Check every reference answer and deliberate counterexample without calling an LLM."""

import argparse
import json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from evals.cases import load_tasks
from evals.graders import grade
from evals.validation import validate


def calibration(root, case, path, intended=None):
    outcome = grade(root, case, (root / "evals" / path).read_text())
    failed = {
        a["id"]
        for a in outcome.get("assertions", [])
        if not a["passed"]
        and a.get("detail") != "Not reached or no measurement returned"
    }
    correct = (
        (outcome["status"] == "pass")
        if intended is None
        else (outcome["status"] == "fail" and set(intended) <= failed)
    )
    return {
        "case": case["id"],
        "skill": case["skill"],
        "path": path,
        "control": "reference" if intended is None else "counterexample",
        "intended_failures": intended,
        "calibrated": correct,
        "outcome": outcome,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", action="append")
    parser.add_argument("--case", dest="case_ids", action="append")
    parser.add_argument("--jobs", type=int, choices=range(1, 5), default=2)
    parser.add_argument(
        "--output", type=Path, default=Path("evals/results/calibration.json")
    )
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    validate(root)
    cases = load_tasks(root)
    for field, wanted in [("skill", args.skill), ("id", args.case_ids)]:
        if wanted:
            missing = set(wanted) - {c[field] for c in cases}
            if missing:
                parser.error(f"Unknown {field}: {sorted(missing)}")
            cases = [c for c in cases if c[field] in wanted]
    if not cases:
        parser.error("No matching controls")
    jobs = [(c, p, None) for c in cases for p in c["references"]] + [
        (c, n["path"], n["fails"]) for c in cases for n in c["counterexamples"]
    ]
    rows = []
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = [pool.submit(calibration, root, *job) for job in jobs]
        for future in as_completed(futures):
            row = future.result()
            rows.append(row)
            if not row["calibrated"]:
                print(
                    f"NOT CALIBRATED: {row['case']} {row['path']}: {row['outcome']}",
                    flush=True,
                )
            elif len(rows) % 25 == 0:
                print(f"Checked {len(rows)}/{len(jobs)} controls", flush=True)
    rows.sort(key=lambda r: (r["case"], r["path"]))
    counts = Counter("pass" if r["calibrated"] else "fail" for r in rows)
    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model_calls": 0,
        "cases": len(cases),
        "controls": len(rows),
        "counts": dict(counts),
        "results": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(
        f"Calibrated {counts['pass']}/{len(rows)} controls across {len(cases)} cases. {args.output}"
    )
    return 0 if not counts["fail"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
