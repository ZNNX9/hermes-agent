"""Bridge explicit Group of Wisdom requests to the workflow-board panel."""

from __future__ import annotations

import os
import re
from typing import Any

import httpx

DEFAULT_BOARD_URL = "http://127.0.0.1:9120"
DEFAULT_TIMEOUT_SECONDS = 180.0
RESULT_MODEL = "multi-llm-discussion"

_GOW_COMMANDS = {
    "gow",
    "gow+",
    "gowplus",
    "group-wisdom",
    "group_wisdom",
    "group-of-wisdom",
    "group_of_wisdom",
}

_GOW_TEXT_RE = re.compile(
    r"(?i)(?<![a-z0-9])gow\+?(?![a-z0-9])|"
    r"group[\s_-]*(?:of[\s_-]*)?wis(?:e)?dom|"
    r"multi[\s_-]*(?:llm|model)|"
    r"multiple\s+(?:llm|model)s?|"
    r"(?:多模型讨论|多个模型|多个llm|几个llm|群体智慧)",
)


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _board_url() -> str:
    return (
        os.environ.get("HERMES_GOW_BOARD_URL")
        or os.environ.get("HERMES_GROUP_WISDOM_BOARD_URL")
        or DEFAULT_BOARD_URL
    ).rstrip("/")


def _command_from_text(text: str) -> tuple[str | None, str]:
    stripped = (text or "").strip()
    if not stripped.startswith("/"):
        return None, stripped
    head, _, rest = stripped.partition(" ")
    command = head[1:].split("@", 1)[0].lower()
    return command, rest.strip()


def group_wisdom_prompt_from_text(text: str) -> str | None:
    """Return the discussion prompt when *text* explicitly asks for GOW."""
    command, args = _command_from_text(text)
    if command in _GOW_COMMANDS:
        return args
    stripped = (text or "").strip()
    if _GOW_TEXT_RE.search(stripped):
        return stripped
    return None


async def _post_json(
    url: str,
    payload: dict[str, Any],
    timeout_seconds: float,
) -> dict[str, Any]:
    timeout = httpx.Timeout(timeout_seconds, connect=min(10.0, timeout_seconds))
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
    return data if isinstance(data, dict) else {}


def _result(
    *,
    prompt: str,
    content: str,
    history: list[dict[str, Any]],
    api_calls: int,
    failed: bool = False,
    error: str | None = None,
) -> dict[str, Any]:
    messages = list(history or [])
    messages.extend(
        [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": content},
        ]
    )
    result: dict[str, Any] = {
        "final_response": content,
        "messages": messages,
        "api_calls": api_calls,
        "model": RESULT_MODEL,
        "last_prompt_tokens": 0,
        "context_length": None,
        "group_of_wisdom": True,
    }
    if failed:
        result["failed"] = True
    if error:
        result["error"] = error
    return result


async def try_group_wisdom_result(
    *,
    text: str,
    source: Any,
    history: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Return a gateway agent_result for explicit GOW requests, else None."""
    prompt = group_wisdom_prompt_from_text(text)
    if prompt is None:
        return None
    if not prompt.strip():
        content = "请在 `/gow` 后面加上要讨论的问题，例如：`/gow 是否应该上线这个方案？`"
        return _result(prompt=text.strip(), content=content, history=history, api_calls=0)

    url = f"{_board_url()}/api/chat"
    payload = {
        "content": prompt,
        "project_name": "Hermes Group of Wisdom",
        "topic_title": "Hermes Telegram GOW",
        "intent": "discussion",
    }
    timeout_seconds = _env_float("HERMES_GOW_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS)
    try:
        data = await _post_json(url, payload, timeout_seconds)
        assistant = data.get("assistant_message") if isinstance(data, dict) else None
        content = ""
        if isinstance(assistant, dict):
            content = str(assistant.get("content") or "").strip()
        if not content:
            content = "⚠️ Group of Wisdom 返回了空结果。workflow-board 已响应，但没有 assistant_message.content。"
        return _result(prompt=prompt, content=content, history=history, api_calls=1)
    except Exception as exc:
        content = (
            "⚠️ 你明确请求了 Group of Wisdom，但 Hermes 没能连接 workflow-board "
            f"({url})：{exc}\n\n"
            "这次没有 fallback 到 `gpt-5.4-mini`，避免假装完成多模型讨论。"
        )
        return _result(
            prompt=prompt,
            content=content,
            history=history,
            api_calls=0,
            failed=True,
            error=str(exc),
        )
