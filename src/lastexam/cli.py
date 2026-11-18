"""Command-line interface for task discovery, export and evaluation."""
import argparse
import json
import sys
from pathlib import Path
from . import __version__
from .core import evaluate, load_suite, public_task


def main(argv=None):
    parser = argparse.ArgumentParser(description="LastExam reproducible AI-agent evaluation")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--suite", default="quantum", help="quantum or a custom suite JSON path")
    sub = parser.add_subparsers(dest="command", required=True)
    listing = sub.add_parser("list", help="List tasks")
    listing.add_argument("--domain")
    show = sub.add_parser("show", help="Show a task without the answer key")
    show.add_argument("task_id")
    export = sub.add_parser("export", help="Export prompts as JSONL to stdout")
    export.add_argument("--domain")
    scoring = sub.add_parser("evaluate", help="Score a JSON task_id-to-answer object")
    scoring.add_argument("answers", type=Path)
    args = parser.parse_args(argv)
    try:
        suite = load_suite(args.suite)
        tasks = suite["tasks"]
        domain = getattr(args, "domain", None)
        if domain:
            tasks = [t for t in tasks if t["domain"] == domain]
            if not tasks:
                raise ValueError("Unknown or empty domain: " + domain)
        if args.command == "list":
            for task in tasks:
                print(task["id"] + "\t" + task["domain"] + "\t" + task["title"])
        elif args.command == "show":
            task = next((t for t in tasks if t["id"] == args.task_id), None)
            if task is None:
                raise ValueError("Unknown task ID: " + args.task_id)
            print(json.dumps(public_task(task), indent=2, ensure_ascii=False))
        elif args.command == "export":
            for task in tasks:
                print(json.dumps(public_task(task), ensure_ascii=False))
        else:
            answers = json.loads(args.answers.read_text(encoding="utf-8"))
            print(json.dumps(evaluate(suite, answers), indent=2, ensure_ascii=False))
    except (ValueError, OSError) as exc:
        print("lastexam: " + str(exc), file=sys.stderr)
        return 2
    return 0
