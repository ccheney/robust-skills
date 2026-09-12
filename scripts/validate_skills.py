#!/usr/bin/env python3
"""Check skill metadata, resource links, and evaluation coverage (not behavior).

Requires Python 3.10+ and PyYAML. Run from any directory; defaults to this repo.
"""

import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml


def prose(text):
    """Ignore fenced examples so sample paths are not treated as real links."""
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if marker:
            chars = marker.group(1)
            if fence is None:
                fence = chars
            elif chars[0] == fence[0] and len(chars) >= len(fence):
                fence = None
            continue
        if fence is None:
            yield line


def local_links(path):
    for line in prose(path.read_text()):
        line = re.sub(r"(`+).*?\1", "", line)
        for match in re.finditer(r"\[[^\]\n]*\]\(([^\s)]+)\)", line):
            raw = match.group(1).strip("<>")
            url = urlsplit(raw)
            if not url.scheme and not url.netloc and url.path:
                yield (path.parent / unquote(url.path)).resolve()


def validate(root):
    root = root.resolve()
    errors = []
    entries = sorted((root / "skills").glob("*/SKILL.md"))
    names = set()
    if not entries:
        return ["No skills found"], []
    for entry in entries:
        label = str(entry.relative_to(root))
        match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", entry.read_text(), re.S)
        if not match:
            errors.append(f"{label}: missing YAML frontmatter or body")
            continue
        try:
            meta = yaml.safe_load(match.group(1))
        except yaml.YAMLError as exc:
            errors.append(f"{label}: invalid YAML: {exc}")
            continue
        if not isinstance(meta, dict):
            errors.append(f"{label}: frontmatter must be a mapping")
            continue
        name, description = meta.get("name"), meta.get("description")
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
            errors.append(f"{label}: invalid skill name")
        elif name != entry.parent.name or name in names:
            errors.append(f"{label}: name must match directory and be unique")
        else:
            names.add(name)
        if not isinstance(description, str) or not description.strip() or len(description) > 1024 or "\n" in description:
            errors.append(f"{label}: description must be a nonempty single line, at most 1024 characters")
        if not match.group(2).strip():
            errors.append(f"{label}: empty instructions")
        if "metadata" in meta and not isinstance(meta["metadata"], dict):
            errors.append(f"{label}: metadata must be a mapping")
        interface_file = entry.parent / "agents/openai.yaml"
        if interface_file.exists():
            try:
                ui = yaml.safe_load(interface_file.read_text())
                if not isinstance(ui, dict):
                    raise ValueError("expected a mapping")
                if "policy" in ui:
                    policy = ui["policy"]
                    if not isinstance(policy, dict):
                        raise ValueError("policy must be a mapping")
                    if "allow_implicit_invocation" in policy and not isinstance(policy["allow_implicit_invocation"], bool):
                        raise ValueError("allow_implicit_invocation must be boolean")
            except (yaml.YAMLError, ValueError) as exc:
                errors.append(f"{interface_file.relative_to(root)}: {exc}")
        # Every bundled reference/script must be reachable from its own entrypoint.
        visited, pending = set(), [entry.resolve()]
        while pending:
            path = pending.pop()
            if path in visited:
                continue
            visited.add(path)
            if path.suffix == ".md" and path.is_file():
                for target in local_links(path):
                    if not target.is_file():
                        errors.append(f"{path.relative_to(root)}: missing linked file {target}")
                    elif not target.is_relative_to(entry.parent.resolve()):
                        errors.append(f"{label}: resource link escapes standalone skill: {target}")
                    else:
                        pending.append(target)
        resources = [p for sub in ("references", "scripts") for p in (entry.parent / sub).rglob("*") if p.is_file()]
        for resource in resources:
            if resource.resolve() not in visited:
                errors.append(f"{label}: unreachable resource {resource.relative_to(root)}")
    cases_file = root / "evals/routing.json"
    try:
        cases = json.loads(cases_file.read_text())
        if not isinstance(cases, list):
            raise ValueError("expected an array")
        ids, coverage = set(), {name: set() for name in names}
        for case in cases:
            if not isinstance(case, dict) or not isinstance(case.get("id"), str) or case["id"] in ids:
                raise ValueError("cases need unique string IDs")
            ids.add(case["id"])
            if case.get("owner") not in names or not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
                raise ValueError(f"invalid owner/prompt in {case['id']}")
            expected = case.get("expected_skills")
            if not isinstance(expected, list) or any(not isinstance(n, str) or n not in names for n in expected):
                raise ValueError(f"invalid expected skills in {case['id']}")
            kind = case.get("kind")
            if kind not in {"direct", "indirect", "negative", "incomplete", "boundary", "near-miss", "mixed"}:
                raise ValueError(f"invalid kind in {case['id']}")
            coverage[case["owner"]].add(kind)
        for name, kinds in coverage.items():
            missing = {"direct", "indirect", "negative", "incomplete", "boundary"} - kinds
            if missing:
                errors.append(f"{name}: missing evaluation categories {sorted(missing)}")
    except (OSError, ValueError) as exc:
        errors.append(f"{cases_file}: {exc}")
    workflow_file = root / "evals/workflows.json"
    try:
        workflows = json.loads(workflow_file.read_text())
        if not isinstance(workflows, list) or any(not isinstance(c, dict) for c in workflows):
            raise ValueError("expected an array of workflow cases")
        covered = [c.get("skill") for c in workflows]
        if any(not isinstance(name, str) for name in covered) or set(covered) != names or len(covered) != len(names):
            raise ValueError("provide one workflow case per skill")
        if any(not isinstance(c.get("prompt"), str) or not c["prompt"].strip() for c in workflows):
            raise ValueError("workflow cases need nonempty prompts")
    except (OSError, ValueError) as exc:
        errors.append(f"{workflow_file}: {exc}")
    return errors, entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors, entries = validate(args.root.resolve())
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print(f"Validated {len(entries)} skills: metadata, linked resource reachability, and evaluation coverage.")
    print("This does not test actual model activation, output quality, or external documentation freshness.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
