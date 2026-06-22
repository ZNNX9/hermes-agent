"""SQLite-backed managed-agent task queue.

This is intentionally narrower than the existing kanban dispatcher: it stores
task intent, policy/evidence metadata, and completion receipts. It does not
spawn workers, merge branches, deploy, or talk to external services.
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from hermes_constants import get_hermes_home


VALID_STATUSES = {
    "queued",
    "assigned",
    "in_progress",
    "blocked",
    "review",
    "complete",
    "cancelled",
}

REQUIRED_EVIDENCE_FIELDS = (
    "files_changed",
    "commands_run",
    "test_results",
    "risk_notes",
    "rollback_plan",
)


class TaskQueueError(RuntimeError):
    """Base error for managed task queue operations."""


class TaskNotFoundError(TaskQueueError):
    """Raised when a task id does not exist."""


class EvidenceGateError(TaskQueueError):
    """Raised when a completion attempt lacks a valid evidence receipt."""


@dataclass(frozen=True)
class Task:
    task_id: str
    project: str
    title: str
    status: str = "queued"
    priority: int = 0
    assigned_agent: str | None = None
    model: str | None = None
    branch: str | None = None
    allowed_files: list[str] = field(default_factory=list)
    blocked_files: list[str] = field(default_factory=list)
    required_evidence: list[str] = field(default_factory=list)
    human_approval_required: bool = False
    evidence: dict[str, Any] = field(default_factory=dict)
    created_at: int = 0
    updated_at: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "project": self.project,
            "title": self.title,
            "status": self.status,
            "priority": self.priority,
            "assigned_agent": self.assigned_agent,
            "model": self.model,
            "branch": self.branch,
            "allowed_files": list(self.allowed_files),
            "blocked_files": list(self.blocked_files),
            "required_evidence": list(self.required_evidence),
            "human_approval_required": self.human_approval_required,
            "evidence": dict(self.evidence),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


def default_task_db_path() -> Path:
    return get_hermes_home() / "task_queue" / "tasks.db"


def _json_list(values: Iterable[str] | None) -> str:
    if not values:
        return "[]"
    return json.dumps([str(value) for value in values], ensure_ascii=False)


def _load_json_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return [str(item) for item in data]


def _load_json_object(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def validate_evidence_receipt(
    evidence: dict[str, Any] | None,
    *,
    extra_required: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Validate and normalize a completion evidence receipt."""
    if not evidence:
        raise EvidenceGateError(
            "evidence receipt required before a task can be marked complete"
        )

    required = list(REQUIRED_EVIDENCE_FIELDS)
    for field_name in extra_required or []:
        if field_name not in required:
            required.append(str(field_name))

    missing: list[str] = []
    for field_name in required:
        value = evidence.get(field_name)
        if value is None:
            missing.append(field_name)
            continue
        if isinstance(value, str) and not value.strip():
            missing.append(field_name)
            continue
        if isinstance(value, list) and not value:
            missing.append(field_name)
            continue
    if missing:
        raise EvidenceGateError(
            "evidence receipt missing required field(s): " + ", ".join(missing)
        )

    normalized = dict(evidence)
    for field_name in ("files_changed", "commands_run", "test_results"):
        value = normalized.get(field_name)
        if isinstance(value, str):
            normalized[field_name] = [value]
    return normalized


class TaskQueue:
    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path is not None else default_task_db_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS managed_agent_tasks (
                    task_id TEXT PRIMARY KEY,
                    project TEXT NOT NULL,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    priority INTEGER NOT NULL DEFAULT 0,
                    assigned_agent TEXT,
                    model TEXT,
                    branch TEXT,
                    allowed_files TEXT NOT NULL DEFAULT '[]',
                    blocked_files TEXT NOT NULL DEFAULT '[]',
                    required_evidence TEXT NOT NULL DEFAULT '[]',
                    human_approval_required INTEGER NOT NULL DEFAULT 0,
                    evidence TEXT,
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_managed_agent_tasks_project_status
                ON managed_agent_tasks(project, status)
                """
            )

    def add_task(
        self,
        *,
        project: str,
        title: str,
        task_id: str | None = None,
        status: str = "queued",
        priority: int = 0,
        assigned_agent: str | None = None,
        model: str | None = None,
        branch: str | None = None,
        allowed_files: Iterable[str] | None = None,
        blocked_files: Iterable[str] | None = None,
        required_evidence: Iterable[str] | None = None,
        human_approval_required: bool = False,
    ) -> Task:
        project = project.strip()
        title = title.strip()
        if not project:
            raise ValueError("project is required")
        if not title:
            raise ValueError("title is required")
        if status not in VALID_STATUSES:
            raise ValueError(f"invalid task status {status!r}")
        task_id = task_id.strip() if task_id else f"task-{uuid.uuid4().hex[:12]}"
        if not task_id:
            raise ValueError("task_id is required")
        now = int(time.time())
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO managed_agent_tasks (
                    task_id, project, title, status, priority, assigned_agent,
                    model, branch, allowed_files, blocked_files,
                    required_evidence, human_approval_required, evidence,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task_id,
                    project,
                    title,
                    status,
                    int(priority),
                    assigned_agent,
                    model,
                    branch,
                    _json_list(allowed_files),
                    _json_list(blocked_files),
                    _json_list(required_evidence),
                    1 if human_approval_required else 0,
                    None,
                    now,
                    now,
                ),
            )
        task = self.get_task(task_id)
        if task is None:
            raise TaskQueueError(f"task {task_id!r} was not persisted")
        return task

    def get_task(self, task_id: str) -> Task | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM managed_agent_tasks WHERE task_id = ?",
                (task_id,),
            ).fetchone()
        return _task_from_row(row) if row is not None else None

    def list_tasks(
        self,
        *,
        project: str | None = None,
        status: str | None = None,
    ) -> list[Task]:
        clauses: list[str] = []
        params: list[Any] = []
        if project:
            clauses.append("project = ?")
            params.append(project)
        if status:
            clauses.append("status = ?")
            params.append(status)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM managed_agent_tasks
                """
                + where
                + " ORDER BY priority DESC, created_at ASC, task_id ASC",
                params,
            ).fetchall()
        return [_task_from_row(row) for row in rows]

    def update_status(
        self,
        task_id: str,
        status: str,
        *,
        evidence: dict[str, Any] | None = None,
    ) -> Task:
        if status not in VALID_STATUSES:
            raise ValueError(f"invalid task status {status!r}")
        task = self.get_task(task_id)
        if task is None:
            raise TaskNotFoundError(f"task {task_id!r} not found")

        evidence_json = None
        if status == "complete":
            normalized = validate_evidence_receipt(
                evidence,
                extra_required=task.required_evidence,
            )
            evidence_json = json.dumps(normalized, ensure_ascii=False)

        now = int(time.time())
        with self._connect() as conn:
            if evidence_json is None:
                conn.execute(
                    """
                    UPDATE managed_agent_tasks
                    SET status = ?, updated_at = ?
                    WHERE task_id = ?
                    """,
                    (status, now, task_id),
                )
            else:
                conn.execute(
                    """
                    UPDATE managed_agent_tasks
                    SET status = ?, evidence = ?, updated_at = ?
                    WHERE task_id = ?
                    """,
                    (status, evidence_json, now, task_id),
                )
        updated = self.get_task(task_id)
        if updated is None:
            raise TaskNotFoundError(f"task {task_id!r} not found")
        return updated


def _task_from_row(row: sqlite3.Row) -> Task:
    return Task(
        task_id=str(row["task_id"]),
        project=str(row["project"]),
        title=str(row["title"]),
        status=str(row["status"]),
        priority=int(row["priority"]),
        assigned_agent=row["assigned_agent"],
        model=row["model"],
        branch=row["branch"],
        allowed_files=_load_json_list(row["allowed_files"]),
        blocked_files=_load_json_list(row["blocked_files"]),
        required_evidence=_load_json_list(row["required_evidence"]),
        human_approval_required=bool(row["human_approval_required"]),
        evidence=_load_json_object(row["evidence"]),
        created_at=int(row["created_at"]),
        updated_at=int(row["updated_at"]),
    )
