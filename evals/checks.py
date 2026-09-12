"""Declarative outcome checks. Configuration is private to graders, never model context."""

import re
from collections import deque, Counter
import json

MISSING = object()
OPS = {
    "equals",
    "set_equals",
    "one_of",
    "contains",
    "contains_all",
    "excludes",
    "length",
    "keys",
    "absent",
    "matches",
    "edges",
    "acyclic",
    "all",
    "any",
}


def at(value, path):
    for part in path:
        try:
            value = value[part]
        except (TypeError, KeyError, IndexError):
            return MISSING
    return value


def evaluate(output, rule):
    op = rule["op"]
    value = at(output, rule.get("path", []))
    expected = rule.get("value")
    if op == "equals":
        return value is not MISSING and value == expected
    if op == "set_equals":
        return isinstance(value, list) and Counter(
            json.dumps(v, sort_keys=True) for v in value
        ) == Counter(json.dumps(v, sort_keys=True) for v in expected)
    if op == "one_of":
        return value is not MISSING and value in expected
    if op == "absent":
        return value is MISSING
    if op == "contains":
        return isinstance(value, (str, list, dict)) and expected in value
    if op == "contains_all":
        return isinstance(value, (str, list, dict)) and all(
            x in value for x in expected
        )
    if op == "excludes":
        return isinstance(value, (str, list, dict)) and all(
            x not in value for x in expected
        )
    if op == "length":
        return isinstance(value, (str, list, dict)) and rule.get("min", 0) <= len(
            value
        ) <= rule.get("max", float("inf"))
    if op == "keys":
        return (
            isinstance(value, dict)
            and set(expected) <= set(value)
            and (not rule.get("exact") or set(value) == set(expected))
        )
    if op == "matches":
        return isinstance(value, str) and re.fullmatch(expected, value) is not None
    if op in ("all", "any"):
        if not isinstance(value, list):
            return False
        results = [all(evaluate(item, c) for c in rule["checks"]) for item in value]
        return all(results) if op == "all" else any(results)
    if op in ("edges", "acyclic"):
        if not isinstance(value, list) or any(
            not isinstance(e, dict)
            or not isinstance(e.get("from"), str)
            or not isinstance(e.get("to"), str)
            for e in value
        ):
            return False
        edges = {(e["from"], e["to"]) for e in value}
        if op == "edges":
            required = {tuple(e) for e in rule.get("required", [])}
            forbidden = {tuple(e) for e in rule.get("forbidden", [])}
            allowed = rule.get("allowed")
            return (
                required <= edges
                and not edges & forbidden
                and (allowed is None or edges <= {tuple(e) for e in allowed})
            )
        nodes = {n for edge in edges for n in edge}
        degree = {n: 0 for n in nodes}
        for a, b in edges:
            degree[b] += 1
        queue = deque(n for n, d in degree.items() if d == 0)
        seen = 0
        while queue:
            node = queue.popleft()
            seen += 1
            for a, b in edges:
                if a == node:
                    degree[b] -= 1
                    if degree[b] == 0:
                        queue.append(b)
        return seen == len(nodes)
    raise ValueError(f"Unknown assertion operator: {op}")


def validate_rule(rule):
    if (
        not isinstance(rule, dict)
        or not isinstance(rule.get("id"), str)
        or not rule["id"]
        or rule.get("op") not in OPS
    ):
        raise ValueError("Assertions need an id and a known operator")
    if not isinstance(rule.get("path", []), list) or any(
        type(p) not in (str, int) or isinstance(p, int) and p < 0
        for p in rule.get("path", [])
    ):
        raise ValueError("Assertion paths must contain string keys/nonnegative indexes")
    op = rule["op"]
    if (
        op
        in {
            "equals",
            "set_equals",
            "one_of",
            "contains",
            "contains_all",
            "excludes",
            "keys",
            "matches",
        }
        and "value" not in rule
    ):
        raise ValueError("Assertion needs a value")
    if op in {
        "set_equals",
        "one_of",
        "contains_all",
        "excludes",
        "keys",
    } and not isinstance(rule["value"], list):
        raise ValueError("This operator needs an array value")
    if op in {"one_of", "contains_all", "excludes", "keys"} and not rule["value"]:
        raise ValueError("This assertion would be empty")
    if op == "matches":
        if not isinstance(rule["value"], str):
            raise ValueError("Regex must be a string")
        re.compile(rule["value"])
    if op == "length":
        if not any(k in rule for k in ("min", "max")):
            raise ValueError("Length needs a bound")
        if any(
            type(rule[k]) is not int or rule[k] < 0 for k in ("min", "max") if k in rule
        ) or rule.get("min", 0) > rule.get("max", float("inf")):
            raise ValueError("Invalid length bounds")
    if op in {"all", "any"}:
        if not isinstance(rule.get("checks"), list) or not rule["checks"]:
            raise ValueError("Nested checks must be nonempty")
        for child in rule["checks"]:
            validate_rule(child)
    if op == "edges":
        if not any(k in rule for k in ("required", "forbidden", "allowed")):
            raise ValueError("Edges need a graph constraint")
        for key in ("required", "forbidden", "allowed"):
            if key in rule and (
                not isinstance(rule[key], list)
                or any(
                    not isinstance(e, list)
                    or len(e) != 2
                    or any(not isinstance(n, str) for n in e)
                    for e in rule[key]
                )
            ):
                raise ValueError("Edges must be pairs of string node IDs")


def check_contract(output, rules):
    results = []
    for rule in rules:
        validate_rule(rule)
        try:
            passed = evaluate(output, rule)
        except (TypeError, ValueError):
            passed = False
        results.append(
            {
                "id": rule["id"],
                "passed": bool(passed),
                "detail": rule.get("description", rule["id"]),
            }
        )
    return results


def finish(assertions, **extra):
    if not assertions:
        return {
            "status": "error",
            "detail": "The grader produced no assertions",
            **extra,
        }
    passed = sum(a["passed"] for a in assertions)
    return {
        "status": "pass" if passed == len(assertions) else "fail",
        "score": passed / len(assertions),
        "detail": f"{passed}/{len(assertions)} assertions passed",
        "assertions": assertions,
        **extra,
    }
