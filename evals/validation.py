"""Validate the automated case inventory without invoking a model."""

import json
from pathlib import Path

from evals.catalog import Catalog, snapshot


def validate(root):
    _, texts = snapshot(root)
    skills = Catalog(texts).entries
    cases = json.loads((root / "evals/pilot.json").read_text())
    if not isinstance(cases, list) or not cases:
        raise ValueError("pilot.json must be a nonempty array")
    ids = set()
    for case in cases:
        if (
            not isinstance(case, dict)
            or not isinstance(case.get("id"), str)
            or not case["id"]
            or case["id"] in ids
        ):
            raise ValueError("Each pilot case needs a unique string id")
        ids.add(case["id"])
        if case.get("skill") not in skills or case.get("grader") not in (
            "javascript",
            "teams",
            "fsd",
        ):
            raise ValueError(f"Invalid skill/grader for {case['id']}")
        if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
            raise ValueError(f"Missing prompt for {case['id']}")
        if not isinstance(case.get("input"), str):
            raise ValueError(f"Missing input for {case['id']}")
        path = (root / "evals" / case["input"]).resolve()
        if (
            not path.is_relative_to((root / "evals/fixtures").resolve())
            or not path.is_file()
        ):
            raise ValueError(f"Input must exist inside evals/fixtures: {case['id']}")
        oracle = root / "evals/reference_outputs" / f"{case['id']}.txt"
        if not oracle.is_file():
            raise ValueError(f"Missing grader reference output: {case['id']}")
    routing = json.loads((root / "evals/routing.json").read_text())
    profiles = json.loads((root / "evals/profiles.json").read_text())
    for profile, settings in profiles.items():
        for key, known in [("routing", {c["id"] for c in routing}), ("tasks", ids)]:
            chosen = settings.get(key)
            if chosen == "all":
                continue
            if (
                not isinstance(chosen, list)
                or any(not isinstance(c, str) for c in chosen)
                or len(set(chosen)) != len(chosen)
                or set(chosen) - known
            ):
                raise ValueError(f"Invalid {key} cases in {profile}")
    return len(cases)


if __name__ == "__main__":
    count = validate(Path(__file__).resolve().parents[1])
    print(
        f"Validated {count} automated pilot cases and their profiles; no model calls made."
    )
