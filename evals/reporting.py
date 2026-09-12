"""Transparent per-skill cells, paired outcomes, and empirical repeat consistency."""

import hashlib
from collections import defaultdict


def fingerprint(root):
    digest = hashlib.sha256()
    for folder in ("evals", "skills"):
        for path in sorted((root / folder).rglob("*")):
            relative = path.relative_to(root)
            if (
                not path.is_file()
                or path.is_symlink()
                or any(
                    p in ("results", "evidence", "__pycache__", "node_modules")
                    for p in relative.parts
                )
                or path.name == "local.json"
            ):
                continue
            digest.update(str(relative).encode() + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest()


def breakdown(rows):
    cells = defaultdict(list)
    pairs = defaultdict(dict)
    repeats = defaultdict(list)
    for r in rows:
        cells[(r["variant"], r["kind"], r["skill"], r["split"])].append(r)
        repeats[(r["variant"], r["kind"], r["id"])].append(r)
        if r["kind"] == "task":
            pairs[(r["id"], r["repeat"])][r["variant"]] = r
    result = []
    for key, group in sorted(cells.items()):
        scored = [r for r in group if r["status"] in ("pass", "fail")]
        scores = [r["score"] for r in scored if "score" in r]
        result.append(
            dict(
                zip(("variant", "kind", "skill", "split"), key),
                passed=sum(r["status"] == "pass" for r in scored),
                scored=len(scored),
                unscored=len(group) - len(scored),
                mean_assertion_score=sum(scores) / len(scores) if scores else None,
            )
        )
    comparisons = {}
    for other in ("none", "baseline"):
        counts = {
            "both_pass": 0,
            "candidate_only_pass": 0,
            "other_only_pass": 0,
            "both_fail": 0,
            "unpaired_or_unscored": 0,
        }
        for arms in pairs.values():
            a, b = arms.get("candidate"), arms.get(other)
            if (
                not a
                or not b
                or a["status"] not in ("pass", "fail")
                or b["status"] not in ("pass", "fail")
            ):
                counts["unpaired_or_unscored"] += 1
                continue
            key = (
                "both_pass"
                if a["status"] == b["status"] == "pass"
                else "both_fail"
                if a["status"] == b["status"] == "fail"
                else "candidate_only_pass"
                if a["status"] == "pass"
                else "other_only_pass"
            )
            counts[key] += 1
        comparisons[other] = counts
    consistency = []
    for key, group in sorted(repeats.items()):
        if len(group) < 2:
            continue
        statuses = [r["status"] for r in group]
        complete = all(s in ("pass", "fail") for s in statuses)
        consistency.append(
            dict(
                zip(("variant", "kind", "id"), key),
                trials=len(group),
                scored=sum(s in ("pass", "fail") for s in statuses),
                any_pass="pass" in statuses,
                all_pass=all(s == "pass" for s in statuses) if complete else None,
            )
        )
    return {
        "cells": result,
        "paired_task_outcomes": comparisons,
        "repeat_consistency": consistency,
    }
