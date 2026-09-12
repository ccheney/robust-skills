"""Load versioned task inventories without exposing grading material to the model."""

import json


def load_tasks(root):
    files = sorted((root / "evals/tasks").glob("*.json"))
    return [case for path in files for case in json.loads(path.read_text())]


def input_prompt(root, case):
    prompt = case["prompt"]
    for relative in case.get("inputs", [case.get("input")]):
        if not relative:
            continue
        path = (root / "evals" / relative).resolve()
        if (
            not path.is_relative_to((root / "evals/fixtures").resolve())
            or not path.is_file()
        ):
            raise ValueError(f"Invalid task input: {relative}")
        prompt += "\n\nInput file " + relative + ":\n" + path.read_text()
    return prompt
