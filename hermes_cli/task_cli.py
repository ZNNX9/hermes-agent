"""``hermes task`` CLI for the managed-agent task queue MVP."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

from hermes_cli.task_policy import (
    PolicyDecision,
    evaluate_task_policy,
    load_policy,
    load_starter_policy,
)
from hermes_cli.task_queue import (
    EvidenceGateError,
    TaskNotFoundError,
    TaskQueue,
)


def build_task_parser(subparsers) -> argparse.ArgumentParser:
    task_parser = subparsers.add_parser(
        "task",
        help="Managed-agent task queue",
        description=(
            "Create and inspect SQLite-backed managed-agent tasks. This MVP "
            "does not spawn workers or perform autonomous merges/deploys."
        ),
    )
    task_sub = task_parser.add_subparsers(dest="task_action")

    add = task_sub.add_parser("add", help="Add a managed-agent task")
    add.add_argument("--task-id", help="Optional deterministic task id")
    add.add_argument("--project", required=True, help="Project name")
    add.add_argument("--title", required=True, help="Task title")
    add.add_argument("--priority", type=int, default=0, help="Higher values list first")
    add.add_argument("--assigned-agent", help="Assigned agent/profile name")
    add.add_argument("--model", help="Preferred model for the assigned agent")
    add.add_argument("--branch", help="Expected work branch")
    add.add_argument(
        "--allowed-file",
        dest="allowed_files",
        action="append",
        default=[],
        help="File/path the task may touch. Repeatable.",
    )
    add.add_argument(
        "--blocked-file",
        dest="blocked_files",
        action="append",
        default=[],
        help="File/path the task must not touch. Repeatable.",
    )
    add.add_argument(
        "--required-evidence",
        dest="required_evidence",
        action="append",
        default=[],
        help="Additional evidence field required before completion. Repeatable.",
    )
    add.add_argument(
        "--human-approval-required",
        action="store_true",
        help="Mark the task as requiring human approval before execution.",
    )
    add.add_argument(
        "--policy",
        help=(
            "Policy YAML to enforce. If omitted, Hermes uses a bundled starter "
            "policy when one exists for --project."
        ),
    )

    list_parser = task_sub.add_parser("list", help="List queued tasks")
    list_parser.add_argument("--project", help="Filter by project")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--json", action="store_true", help="Print JSON")

    show = task_sub.add_parser("show", help="Show task details")
    show.add_argument("task_id")
    show.add_argument("--json", action="store_true", help="Print JSON")

    update = task_sub.add_parser("update-status", help="Update task status")
    update.add_argument("task_id")
    update.add_argument("status")
    update.add_argument(
        "--evidence",
        help="JSON/YAML evidence receipt file, required when status is complete",
    )

    task_parser.set_defaults(func=task_command)
    return task_parser


def task_command(args: argparse.Namespace) -> int:
    action = getattr(args, "task_action", None)
    if action == "add":
        return _cmd_add(args)
    if action == "list":
        return _cmd_list(args)
    if action == "show":
        return _cmd_show(args)
    if action == "update-status":
        return _cmd_update_status(args)
    print("usage: hermes task {add|list|show|update-status}", file=sys.stderr)
    return 2


def _cmd_add(args: argparse.Namespace) -> int:
    draft = {
        "project": args.project,
        "title": args.title,
        "allowed_files": list(args.allowed_files or []),
    }
    decision = _policy_decision_for_add(args, draft)
    if decision is not None and not decision.allowed:
        print(decision.reason, file=sys.stderr)
        return 2

    try:
        task = TaskQueue().add_task(
            task_id=args.task_id,
            project=args.project,
            title=args.title,
            priority=args.priority,
            assigned_agent=args.assigned_agent,
            model=args.model,
            branch=args.branch,
            allowed_files=args.allowed_files,
            blocked_files=args.blocked_files,
            required_evidence=args.required_evidence,
            human_approval_required=args.human_approval_required,
        )
    except Exception as exc:
        print(f"task add: {exc}", file=sys.stderr)
        return 2

    print(f"added {task.task_id} ({task.status}, project={task.project})")
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    tasks = TaskQueue().list_tasks(project=args.project, status=args.status)
    if getattr(args, "json", False):
        print(json.dumps([task.to_dict() for task in tasks], ensure_ascii=False, indent=2))
        return 0
    if not tasks:
        print("No tasks found.")
        return 0
    for task in tasks:
        assignee = task.assigned_agent or "(unassigned)"
        print(
            f"{task.task_id}  {task.status:11s}  p{task.priority:<3d}  "
            f"{task.project:12s}  {assignee:16s}  {task.title}"
        )
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    task = TaskQueue().get_task(args.task_id)
    if task is None:
        print(f"task show: task {args.task_id!r} not found", file=sys.stderr)
        return 1
    if getattr(args, "json", False):
        print(json.dumps(task.to_dict(), ensure_ascii=False, indent=2))
        return 0
    print(f"Task: {task.task_id}")
    print(f"Project: {task.project}")
    print(f"Title: {task.title}")
    print(f"Status: {task.status}")
    print(f"Priority: {task.priority}")
    print(f"Assigned agent: {task.assigned_agent or '(unassigned)'}")
    print(f"Model: {task.model or ''}")
    print(f"Branch: {task.branch or ''}")
    print(f"Allowed files: {', '.join(task.allowed_files) or '(none)'}")
    print(f"Blocked files: {', '.join(task.blocked_files) or '(none)'}")
    print(f"Required evidence: {', '.join(task.required_evidence) or '(default)'}")
    print(f"Human approval required: {task.human_approval_required}")
    return 0


def _cmd_update_status(args: argparse.Namespace) -> int:
    evidence = None
    if args.evidence:
        try:
            evidence = _load_evidence(Path(args.evidence))
        except Exception as exc:
            print(f"task update-status: could not load evidence: {exc}", file=sys.stderr)
            return 2
    try:
        task = TaskQueue().update_status(args.task_id, args.status, evidence=evidence)
    except TaskNotFoundError as exc:
        print(f"task update-status: {exc}", file=sys.stderr)
        return 1
    except (EvidenceGateError, ValueError) as exc:
        print(f"task update-status: {exc}", file=sys.stderr)
        return 2
    print(f"updated {task.task_id} -> {task.status}")
    return 0


def _policy_decision_for_add(
    args: argparse.Namespace,
    draft: dict[str, Any],
) -> PolicyDecision | None:
    if getattr(args, "policy", None):
        policy = load_policy(args.policy)
        return evaluate_task_policy(policy, draft)
    try:
        policy = load_starter_policy(args.project)
    except FileNotFoundError:
        return None
    return evaluate_task_policy(policy, draft)


def _load_evidence(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("evidence receipt must be a JSON/YAML object")
    return data
