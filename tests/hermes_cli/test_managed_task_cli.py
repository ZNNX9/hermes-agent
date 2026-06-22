from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from hermes_cli.task_cli import build_task_parser, task_command


def _task_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hermes")
    subparsers = parser.add_subparsers(dest="command")
    task_parser = build_task_parser(subparsers)
    task_parser.set_defaults(func=task_command)
    return parser


def test_task_cli_add_list_show_and_complete(tmp_path, monkeypatch, capsys):
    hermes_home = tmp_path / ".hermes"
    hermes_home.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(hermes_home))

    parser = _task_parser()

    args = parser.parse_args(
        [
            "task",
            "add",
            "--task-id",
            "task-cli-1",
            "--project",
            "HandyPro",
            "--title",
            "Add feedback receipt guard",
            "--priority",
            "5",
            "--assigned-agent",
            "codex",
            "--model",
            "openai/gpt-5",
            "--branch",
            "task/task-cli-1",
            "--allowed-file",
            "hermes_cli/task_cli.py",
            "--required-evidence",
            "files_changed",
            "--human-approval-required",
        ]
    )
    assert args.func(args) == 0
    assert "added task-cli-1" in capsys.readouterr().out

    args = parser.parse_args(["task", "list", "--project", "HandyPro"])
    assert args.func(args) == 0
    listed = capsys.readouterr().out
    assert "task-cli-1" in listed
    assert "queued" in listed

    args = parser.parse_args(["task", "show", "task-cli-1", "--json"])
    assert args.func(args) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["project"] == "HandyPro"
    assert payload["human_approval_required"] is True

    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(
        json.dumps(
            {
                "files_changed": ["hermes_cli/task_cli.py"],
                "commands_run": ["scripts/run_tests.sh tests/hermes_cli/test_managed_task_cli.py"],
                "test_results": ["passed"],
                "risk_notes": "CLI-only behavior.",
                "rollback_plan": "Revert the task commit.",
            }
        ),
        encoding="utf-8",
    )
    args = parser.parse_args(
        ["task", "update-status", "task-cli-1", "complete", "--evidence", str(evidence_path)]
    )
    assert args.func(args) == 0
    assert "updated task-cli-1 -> complete" in capsys.readouterr().out


def test_task_cli_blocks_policy_violation(tmp_path, monkeypatch, capsys):
    hermes_home = tmp_path / ".hermes"
    hermes_home.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(hermes_home))
    policy_path = tmp_path / "tradebot.yaml"
    policy_path.write_text(
        """
project: TradeBot
forbidden_actions:
  - live trading
forbidden_files:
  - ".env"
""",
        encoding="utf-8",
    )

    parser = _task_parser()
    args = parser.parse_args(
        [
            "task",
            "add",
            "--task-id",
            "blocked",
            "--project",
            "TradeBot",
            "--title",
            "Enable live trading switch",
            "--policy",
            str(policy_path),
        ]
    )

    assert args.func(args) == 2
    err = capsys.readouterr().err
    assert "blocked by policy" in err
    assert "live trading" in err


def test_main_wires_task_subcommand(tmp_path):
    hermes_home = tmp_path / ".hermes"
    hermes_home.mkdir()
    result = subprocess.run(
        [sys.executable, "-m", "hermes_cli.main", "task", "list"],
        cwd=Path(__file__).parents[2],
        env={
            "PATH": "",
            "HOME": str(tmp_path),
            "HERMES_HOME": str(hermes_home),
            "PYTHONPATH": str(Path(__file__).parents[2]),
        },
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "No tasks found." in result.stdout


def test_main_task_policy_block_exits_nonzero(tmp_path):
    hermes_home = tmp_path / ".hermes"
    hermes_home.mkdir()
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "hermes_cli.main",
            "task",
            "add",
            "--task-id",
            "blocked-main",
            "--project",
            "TradeBot",
            "--title",
            "Enable live trading shortcut",
        ],
        cwd=Path(__file__).parents[2],
        env={
            "PATH": "",
            "HOME": str(tmp_path),
            "HERMES_HOME": str(hermes_home),
            "PYTHONPATH": str(Path(__file__).parents[2]),
        },
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "blocked by policy" in result.stderr
