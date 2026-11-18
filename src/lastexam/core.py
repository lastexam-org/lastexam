"""Dependency-free, data-driven benchmark evaluator. Never executes submissions."""
import copy
import json
import math
from importlib.resources import files
from pathlib import Path


def _numeric_tree(value):
    if isinstance(value, list):
        return bool(value) and all(_numeric_tree(x) for x in value)
    return type(value) in (int, float) and math.isfinite(value)


def load_suite(name="quantum"):
    """Load the bundled quantum suite or a custom JSON file, with validation."""
    raw = (files("lastexam").joinpath("data/quantum.json").read_text(encoding="utf-8")
           if str(name) == "quantum" else Path(name).read_text(encoding="utf-8"))
    suite = json.loads(raw)
    if not isinstance(suite, dict) or suite.get("schema_version") != 1:
        raise ValueError("Suite must be an object with schema_version=1")
    if not isinstance(suite.get("tasks"), list) or not suite["tasks"]:
        raise ValueError("Suite must contain a nonempty tasks list")
    seen = set()
    for task in suite["tasks"]:
        if not isinstance(task, dict):
            raise ValueError("Each task must be an object")
        for key in ("id", "domain", "title", "prompt"):
            if not isinstance(task.get(key), str) or not task[key].strip():
                raise ValueError("Task requires nonempty " + key)
        if task["id"] in seen:
            raise ValueError("Duplicate task id: " + task["id"])
        seen.add(task["id"])
        grader = task.get("grader", {})
        if not isinstance(grader, dict) or grader.get("type") not in ("numeric", "exact"):
            raise ValueError("Unknown grader for " + task["id"])
        if "reference" not in task:
            raise ValueError("Missing reference for " + task["id"])
        if grader["type"] == "numeric":
            if not _numeric_tree(task["reference"]):
                raise ValueError("Numeric references must be finite numbers or nonempty nested lists")
            for key in ("atol", "rtol"):
                value = grader.get(key, 1e-6)
                if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                    raise ValueError("Invalid tolerance: " + key)
    return suite


def public_task(task):
    """Copy a task without its answer key; original is left untouched."""
    return copy.deepcopy({k: v for k, v in task.items() if k not in ("reference", "reference_method")})


def _close(actual, expected, atol, rtol):
    if isinstance(expected, list):
        return (isinstance(actual, list) and len(actual) == len(expected)
                and all(_close(a, b, atol, rtol) for a, b in zip(actual, expected)))
    if type(actual) not in (int, float) or not math.isfinite(actual):
        return False
    return abs(actual - expected) <= atol + rtol * abs(expected)


def _exact(actual, expected):
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(_exact(a, b) for a, b in zip(actual, expected))
    if isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(_exact(actual[k], v) for k, v in expected.items())
    return actual == expected


def grade(task, answer):
    """Return 1.0 for a correct structured answer, otherwise 0.0."""
    grader = task["grader"]
    if grader["type"] == "numeric":
        passed = _close(answer, task["reference"], grader.get("atol", 1e-6), grader.get("rtol", 1e-6))
    elif grader["type"] == "exact":
        passed = _exact(answer, task["reference"])
    else:
        raise ValueError("Unknown grader: " + str(grader["type"]))
    return float(passed)


def evaluate(suite, submissions):
    """Evaluate {task_id: JSON answer}; missing answers score zero, unknown IDs fail."""
    if not isinstance(submissions, dict):
        raise ValueError("Submissions must be a JSON object mapping task IDs to answers")
    ids = {task["id"] for task in suite["tasks"]}
    unknown = set(submissions) - ids
    if unknown:
        raise ValueError("Unknown task IDs: " + ", ".join(sorted(unknown)))
    results, domains = [], {}
    for task in suite["tasks"]:
        present = task["id"] in submissions
        score = grade(task, submissions[task["id"]]) if present else 0.0
        results.append({"id": task["id"], "domain": task["domain"], "score": score, "submitted": present})
        domains.setdefault(task["domain"], []).append(score)
    total = sum(row["score"] for row in results)
    return {"suite": suite.get("id", "custom"), "total": len(results), "correct": int(total),
            "accuracy": total / len(results), "submitted": len(submissions),
            "by_domain": {name: {"total": len(scores), "accuracy": sum(scores) / len(scores)}
                          for name, scores in domains.items()}, "results": results}
