"""Validate task inputs, private graders, controls, routing splits and profiles offline."""

import json
from pathlib import Path
from evals.catalog import Catalog, snapshot
from evals.cases import load_tasks
from evals.checks import validate_rule

GRADERS = {
    "javascript-runtime",
    "css-runtime",
    "mermaid-runtime",
    "starlark-runtime",
    "drizzle-runtime",
    "postgres-runtime",
    "contract",
    "slack-contract",
    "teams-contract",
    "markup-contract",
    "teams",
    "fsd",
}


def checked_path(root, relative, folder):
    if not isinstance(relative, str):
        raise ValueError("Expected a relative fixture path")
    path = (root / "evals" / relative).resolve()
    if (
        not path.is_relative_to((root / "evals" / folder).resolve())
        or not path.is_file()
    ):
        raise ValueError(f"Expected an existing file inside evals/{folder}: {relative}")
    return path


def expected_assertions(case):
    ids = [r["id"] for r in case.get("assertions", [])]
    mode = case["grader"]
    if mode == "javascript-runtime":
        ids += ["module-loads", "required-exports", *case["assertion_ids"]]
    elif mode == "css-runtime":
        ids += [
            s["id"] + "/" + r["id"]
            for s in case["runtime"]["states"]
            for r in s["checks"]
        ]
    elif mode == "postgres-runtime":
        ids += ["sql-applies", *[r["id"] for r in case["runtime"]["checks"]]]
    elif mode == "mermaid-runtime":
        ids += ["diagram-renders"]
    elif mode == "starlark-runtime":
        ids += ["starlark-syntax"]
    elif mode == "drizzle-runtime":
        ids += ["drizzle-types"]
    elif mode in ("teams", "fsd"):
        ids += ["legacy-outcome"]
    elif mode == "markup-contract":
        ids += [r["id"] for r in case["runtime"]["assertions"]]
    return ids


def validate(root):
    _, texts = snapshot(root)
    skills = Catalog(texts).entries
    tasks = load_tasks(root)
    if not tasks:
        raise ValueError("Task inventory must be nonempty")
    ids = set()
    prompts = set()
    groups = {}
    coverage = set()

    def common(case):
        ident = case.get("id")
        if not isinstance(ident, str) or not ident or ident in ids:
            raise ValueError("Case IDs must be nonempty and unique")
        ids.add(ident)
        prompt = case.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError(f"Missing prompt: {ident}")
        normalized = " ".join(prompt.split()).casefold()
        if normalized in prompts:
            raise ValueError(f"Duplicate prompt: {ident}")
        prompts.add(normalized)
        split = case.get("split")
        group = case.get("group")
        if (
            split not in ("development", "holdout")
            or not isinstance(group, str)
            or not group
        ):
            raise ValueError(f"Missing split/group: {ident}")
        if group in groups and groups[group] != split:
            raise ValueError(f"Group crosses development/holdout boundary: {group}")
        groups[group] = split

    for c in tasks:
        common(c)
        ident = c["id"]
        if c.get("skill") not in skills or c.get("grader") not in GRADERS:
            raise ValueError(f"Invalid skill/grader: {ident}")
        coverage.add(c["skill"])
        if not isinstance(c.get("category"), str) or not c["category"]:
            raise ValueError(f"Missing category: {ident}")
        if not isinstance(c.get("inputs"), list) or not c["inputs"]:
            raise ValueError(f"Missing inputs: {ident}")
        for path in c["inputs"]:
            checked_path(root, path, "fixtures")
        if c["grader"] == "javascript-runtime":
            checked_path(root, c["test"], "assertions")
            if not c.get("assertion_ids") or not c.get("exports"):
                raise ValueError(f"Missing JS behavior checks/exports: {ident}")
        if c["grader"] == "css-runtime":
            checked_path(root, c["runtime"]["html"], "fixtures")
            if not c["runtime"]["states"]:
                raise ValueError(f"Missing browser states: {ident}")
        if c["grader"] == "postgres-runtime":
            checked_path(root, c["runtime"]["setup"], "fixtures")
        for rule in c.get("assertions", []):
            validate_rule(rule)
        if c["grader"] == "markup-contract":
            for rule in c["runtime"]["assertions"]:
                validate_rule(rule)
        expected = expected_assertions(c)
        if not expected or len(expected) != len(set(expected)):
            raise ValueError(f"Missing or duplicate assertion IDs: {ident}")
        if not isinstance(c.get("references"), list) or not c["references"]:
            raise ValueError(f"Missing positive controls: {ident}")
        if (
            not isinstance(c.get("counterexamples"), list)
            or len(c["counterexamples"]) < 2
        ):
            raise ValueError(f"Need two semantic negative controls: {ident}")
        controls = set()
        for path in c["references"]:
            content = checked_path(root, path, "reference_outputs").read_text()
            if not content.strip() or content in controls:
                raise ValueError(f"Empty/duplicate reference: {ident}")
            controls.add(content)
        # Messaging surface validators contribute well-known additional assertions.
        extra = {
            "slack-block-count",
            "slack-surface",
            "slack-text-objects",
            "slack-ids",
            "slack-table-shape",
            "slack-markdown-budget",
            "slack-method-fields",
            "teams-wire-contract",
            "artifact-executes",
            "execution-completes",
        }
        for control in c["counterexamples"]:
            content = checked_path(
                root, control["path"], "reference_outputs"
            ).read_text()
            failures = control.get("fails")
            if not content.strip() or content in controls:
                raise ValueError(f"Empty/duplicate counterexample: {ident}")
            controls.add(content)
            if (
                not isinstance(failures, list)
                or not failures
                or set(failures) - set(expected) - extra
            ):
                raise ValueError(f"Unknown intended failure: {ident}: {failures}")
    if coverage != set(skills):
        raise ValueError(f"Missing task coverage: {set(skills) - coverage}")
    task_ids = {c["id"] for c in tasks}
    routing = json.loads((root / "evals/routing.json").read_text())
    for c in routing:
        common(c)
        expected = c.get("expected_skills")
        if (
            c.get("owner") not in skills
            or not isinstance(expected, list)
            or len(expected) != len(set(expected))
            or set(expected) - set(skills)
        ):
            raise ValueError(f"Invalid routing selection: {c['id']}")
        if not c.get("rationale"):
            raise ValueError(f"Missing routing rationale: {c['id']}")
    profiles = json.loads((root / "evals/profiles.json").read_text())
    for profile, settings in profiles.items():
        for key, known in [
            ("routing", {c["id"] for c in routing}),
            ("tasks", task_ids),
        ]:
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
    return len(tasks)


if __name__ == "__main__":
    count = validate(Path(__file__).resolve().parents[1])
    print(
        f"Validated {count} task cases, controls, routing splits and profiles; no model calls made."
    )
