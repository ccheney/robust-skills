"""Decode the declarative Starlark subset exercised by the BUILD fixtures; never execute it."""

import ast
import json
import sys

source = sys.stdin.read()
values = {}
calls = []
aliases = {}


def decode(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, (ast.List, ast.Tuple)):
        return [decode(x) for x in node.elts]
    if isinstance(node, ast.Dict):
        return {str(decode(k)): decode(v) for k, v in zip(node.keys, node.values)}
    if isinstance(node, ast.Name):
        return values.get(node.id, {"symbol": node.id})
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return decode(node.left) + decode(node.right)
    if isinstance(node, ast.Call):
        return {
            "call": aliases.get(ast.unparse(node.func), ast.unparse(node.func)),
            "args": [decode(a) for a in node.args],
            "kwargs": {k.arg: decode(k.value) for k in node.keywords},
        }
    return {"expression": ast.unparse(node)}


for node in ast.parse(source).body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name):
                values[target.id] = decode(node.value)
    elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        call = decode(node.value)
        calls.append(call)
        if call["call"] == "load":
            aliases.update(call["kwargs"])
print(
    json.dumps(
        {
            "targets": {
                c["kwargs"]["name"]: {"rule": c["call"], **c["kwargs"]}
                for c in calls
                if "name" in c["kwargs"]
            },
            "calls": calls,
            "assignments": values,
            "repositories": [
                name
                for c in calls
                if c["call"] == "use_repo"
                for name in [*c["args"][1:], *c["kwargs"].keys()]
            ],
        }
    )
)
