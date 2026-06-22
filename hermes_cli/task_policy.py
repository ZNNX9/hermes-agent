"""YAML policy gate for managed-agent task intake."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Any, Mapping

import yaml


@dataclass(frozen=True)
class ProjectPolicy:
    project: str
    forbidden_actions: list[str] = field(default_factory=list)
    forbidden_files: list[str] = field(default_factory=list)
    source: str | None = None


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str


def load_policy(path: str | Path) -> ProjectPolicy:
    policy_path = Path(path)
    raw = yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"policy {policy_path} must be a YAML mapping")
    return _policy_from_mapping(raw, source=str(policy_path))


def load_starter_policy(project: str) -> ProjectPolicy:
    slug = _project_slug(project)
    filename = f"{slug}.yaml"
    root = resources.files("hermes_cli.managed_agent_configs")
    policy_file = root.joinpath(filename)
    if not policy_file.is_file():
        raise FileNotFoundError(f"no starter policy for project {project!r}")
    raw = yaml.safe_load(policy_file.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"starter policy {filename} must be a YAML mapping")
    return _policy_from_mapping(raw, source=f"starter:{filename}")


def evaluate_task_policy(policy: ProjectPolicy, task: Mapping[str, Any] | Any) -> PolicyDecision:
    task_data = _task_to_mapping(task)
    title = str(task_data.get("title") or "")
    normalized_title = _normalize_text(title)
    actions = [_normalize_text(item) for item in task_data.get("actions") or []]

    for action in policy.forbidden_actions:
        normalized_action = _normalize_text(action)
        if not normalized_action:
            continue
        if normalized_action in normalized_title or normalized_action in actions:
            return PolicyDecision(
                False,
                (
                    f"blocked by policy {policy.project}: forbidden action "
                    f"{action!r} matched task title"
                ),
            )

    touched_files = _task_files(task_data)
    for path in touched_files:
        for pattern in policy.forbidden_files:
            if _matches_file_pattern(path, pattern):
                return PolicyDecision(
                    False,
                    (
                        f"blocked by policy {policy.project}: forbidden file pattern "
                        f"{pattern!r} matched {path!r}"
                    ),
                )

    return PolicyDecision(True, "allowed: no policy violations")


def _policy_from_mapping(raw: Mapping[str, Any], *, source: str | None = None) -> ProjectPolicy:
    forbidden = raw.get("forbidden") if isinstance(raw.get("forbidden"), dict) else {}
    project = str(raw.get("project") or raw.get("name") or "").strip()
    if not project:
        raise ValueError("policy project is required")
    actions = raw.get("forbidden_actions", forbidden.get("actions", []))
    files = raw.get("forbidden_files", forbidden.get("files", []))
    return ProjectPolicy(
        project=project,
        forbidden_actions=_string_list(actions),
        forbidden_files=_string_list(files),
        source=source,
    )


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    raise ValueError("policy list fields must be strings or lists")


def _task_to_mapping(task: Mapping[str, Any] | Any) -> Mapping[str, Any]:
    if isinstance(task, Mapping):
        return task
    if hasattr(task, "to_dict"):
        data = task.to_dict()
        if isinstance(data, Mapping):
            return data
    return getattr(task, "__dict__", {})


def _task_files(task_data: Mapping[str, Any]) -> list[str]:
    files: list[str] = []
    for key in ("allowed_files", "files", "touched_files", "files_changed"):
        value = task_data.get(key)
        if isinstance(value, str):
            files.append(value)
        elif isinstance(value, list):
            files.extend(str(item) for item in value)
    return [path for path in files if path]


def _matches_file_pattern(path: str, pattern: str) -> bool:
    norm_path = path.strip()
    norm_pattern = pattern.strip()
    if not norm_path or not norm_pattern:
        return False
    if fnmatch.fnmatch(norm_path, norm_pattern):
        return True
    if "/" not in norm_pattern and fnmatch.fnmatch(Path(norm_path).name, norm_pattern):
        return True
    return False


def _normalize_text(value: str) -> str:
    normalized = value.casefold()
    normalized = re.sub(r"[_\-]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def _project_slug(project: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", project.casefold())
