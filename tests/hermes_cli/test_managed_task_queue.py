from __future__ import annotations

import pytest

from hermes_cli.task_queue import EvidenceGateError, TaskQueue


def test_task_queue_persists_supported_fields(tmp_path):
    queue = TaskQueue(tmp_path / "tasks.db")

    task = queue.add_task(
        task_id="task-001",
        project="TradeBot",
        title="Harden Mission Control status view",
        priority=7,
        assigned_agent="codex",
        model="openai/gpt-5",
        branch="task/task-001",
        allowed_files=["ui/mission_control.py", "tests/test_mission_control.py"],
        blocked_files=[".env", "config/secrets.yaml"],
        required_evidence=["files_changed", "commands_run", "test_results"],
        human_approval_required=True,
    )

    assert task.task_id == "task-001"
    assert task.status == "queued"
    assert task.allowed_files == ["ui/mission_control.py", "tests/test_mission_control.py"]
    assert task.blocked_files == [".env", "config/secrets.yaml"]
    assert task.required_evidence == ["files_changed", "commands_run", "test_results"]
    assert task.human_approval_required is True

    reopened = TaskQueue(tmp_path / "tasks.db")
    stored = reopened.get_task("task-001")

    assert stored is not None
    assert stored.project == "TradeBot"
    assert stored.priority == 7
    assert stored.assigned_agent == "codex"
    assert stored.model == "openai/gpt-5"
    assert stored.branch == "task/task-001"


def test_task_queue_lists_by_project_then_priority(tmp_path):
    queue = TaskQueue(tmp_path / "tasks.db")
    queue.add_task(task_id="low", project="HandyPro", title="Low", priority=1)
    queue.add_task(task_id="high", project="HandyPro", title="High", priority=9)
    queue.add_task(task_id="other", project="TradeBot", title="Other", priority=10)

    tasks = queue.list_tasks(project="HandyPro")

    assert [task.task_id for task in tasks] == ["high", "low"]


def test_marking_complete_requires_full_evidence_receipt(tmp_path):
    queue = TaskQueue(tmp_path / "tasks.db")
    queue.add_task(task_id="task-002", project="HandyPro", title="Add QA guard")

    with pytest.raises(EvidenceGateError, match="evidence receipt required"):
        queue.update_status("task-002", "complete")

    incomplete = {
        "files_changed": ["app/qa.py"],
        "commands_run": ["scripts/run_tests.sh tests/hermes_cli/test_qa.py"],
        "test_results": ["passed"],
        "risk_notes": "Low risk; isolated CLI behavior.",
    }
    with pytest.raises(EvidenceGateError, match="rollback_plan"):
        queue.update_status("task-002", "complete", evidence=incomplete)

    receipt = {
        "files_changed": ["app/qa.py", "tests/hermes_cli/test_qa.py"],
        "commands_run": ["scripts/run_tests.sh tests/hermes_cli/test_qa.py"],
        "test_results": ["passed: 3 tests"],
        "risk_notes": "Low risk; isolated CLI behavior.",
        "rollback_plan": "Revert the task commit.",
    }
    updated = queue.update_status("task-002", "complete", evidence=receipt)

    assert updated.status == "complete"
    assert updated.evidence["rollback_plan"] == "Revert the task commit."
