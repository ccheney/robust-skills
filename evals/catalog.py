"""Read only a selected skills snapshot; no access to answers, history, or home skills."""

import json
import re
import subprocess
from pathlib import PurePosixPath

import yaml


def snapshot(root, ref=None):
    if ref:
        # Resolve once so a branch name cannot change halfway through an evaluation.
        commit = subprocess.check_output(
            ["git", "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}"],
            cwd=root,
            text=True,
        ).strip()
        files = subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", commit, "--", "skills"],
            cwd=root,
            text=True,
        ).splitlines()
        texts = {
            p: subprocess.check_output(
                ["git", "show", f"{commit}:{p}"], cwd=root, text=True
            )
            for p in files
            if p.endswith(".md")
        }
    else:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip()
        texts = {
            p.relative_to(root).as_posix(): p.read_text()
            for p in (root / "skills").rglob("*.md")
            if not p.is_symlink()
        }
    return commit, texts


class Catalog:
    def __init__(self, texts):
        self.texts = texts
        self.entries = {}
        self.loaded = set()
        self.reads = []
        for path, text in sorted(texts.items()):
            parts = PurePosixPath(path).parts
            if len(parts) != 3 or parts[0] != "skills" or parts[2] != "SKILL.md":
                continue
            match = re.match(r"\A---\n(.*?)\n---", text, re.S)
            meta = yaml.safe_load(match.group(1)) if match else {}
            if meta.get("name") != parts[1] or not isinstance(
                meta.get("description"), str
            ):
                raise ValueError(f"Invalid skill metadata: {path}")
            self.entries[parts[1]] = meta["description"]

    def discovery(self):
        return json.dumps(
            [{"name": k, "description": v} for k, v in self.entries.items()]
        )

    def invoke(self, name, args):
        if not isinstance(args, dict):
            return {"error": "Arguments must be an object"}
        skill = args.get("skill")
        if not isinstance(skill, str) or skill not in self.entries:
            return {"error": "Unknown skill"}
        if name == "read_skill":
            path = f"skills/{skill}/SKILL.md"
            self.loaded.add(skill)
            self.reads.append(path)
            return {"path": path, "content": self.texts[path]}
        if name == "read_reference":
            relative = args.get("path", "")
            if not isinstance(relative, str):
                return {"error": "Reference path must be a string"}
            parts = PurePosixPath(relative).parts
            if not parts or parts[0] != "references" or ".." in parts:
                return {
                    "error": "Only reference files inside the selected skill are readable"
                }
            if skill not in self.loaded:
                return {"error": "Read this skill's entrypoint before its references"}
            path = f"skills/{skill}/{relative}"
            if path not in self.texts:
                return {"error": "Reference not found"}
            start = args.get("start_line", 1)
            count = args.get("line_count", 80)
            if (
                type(start) is not int
                or type(count) is not int
                or start < 1
                or not 1 <= count <= 100
            ):
                return {
                    "error": "Use a positive start_line and line_count from 1 to 100"
                }
            lines = self.texts[path].splitlines()
            self.reads.append(f"{path}:{start}")
            return {
                "path": path,
                "total_lines": len(lines),
                "start_line": start,
                "content": "\n".join(lines[start - 1 : start - 1 + count]),
            }
        return {"error": "Unknown tool"}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_skill",
            "description": "Read a relevant skill's full instructions.",
            "parameters": {
                "type": "object",
                "properties": {"skill": {"type": "string"}},
                "required": ["skill"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_reference",
            "description": "Read a range of lines from a selected skill's reference file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill": {"type": "string"},
                    "path": {"type": "string"},
                    "start_line": {"type": "integer"},
                    "line_count": {"type": "integer"},
                },
                "required": ["skill", "path"],
            },
        },
    },
]
