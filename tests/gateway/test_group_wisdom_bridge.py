import asyncio
import types

from gateway.config import Platform


def _source():
    return types.SimpleNamespace(
        platform=Platform.TELEGRAM,
        chat_type="dm",
        chat_id="12345",
        user_id="user-1",
    )


def test_gow_is_gateway_command():
    from hermes_cli.commands import is_gateway_known_command, resolve_command

    command = resolve_command("gow")

    assert command is not None
    assert command.name == "gow"
    assert is_gateway_known_command("gow") is True


def test_group_wisdom_trigger_detection():
    from gateway.group_wisdom_bridge import group_wisdom_prompt_from_text

    assert group_wisdom_prompt_from_text("/gow compare these options") == "compare these options"
    assert group_wisdom_prompt_from_text("/gow+ 风险评估") == "风险评估"
    assert group_wisdom_prompt_from_text("用 GOW 讨论这个架构") == "用 GOW 讨论这个架构"
    assert group_wisdom_prompt_from_text("请做多模型讨论：是否上线") == "请做多模型讨论：是否上线"
    assert group_wisdom_prompt_from_text("普通聊天不要 panel") is None


def test_group_wisdom_bridge_posts_discussion_payload(monkeypatch):
    from gateway import group_wisdom_bridge

    calls = []

    async def fake_post(url, payload, timeout_seconds):
        calls.append((url, payload, timeout_seconds))
        return {
            "assistant_message": {
                "content": "## Group of Wisdom\n\n结论：走方案 A。",
            },
        }

    monkeypatch.setattr(group_wisdom_bridge, "_post_json", fake_post)
    monkeypatch.setenv("HERMES_GOW_BOARD_URL", "http://board.local:9120")

    result = asyncio.run(
        group_wisdom_bridge.try_group_wisdom_result(
            text="/gow compare these options",
            source=_source(),
            history=[{"role": "user", "content": "earlier"}],
        )
    )

    assert calls == [
        (
            "http://board.local:9120/api/chat",
            {
                "content": "compare these options",
                "project_name": "Hermes Group of Wisdom",
                "topic_title": "Hermes Telegram GOW",
                "intent": "discussion",
            },
            180.0,
        )
    ]
    assert result["final_response"].startswith("## Group of Wisdom")
    assert result["model"] == "multi-llm-discussion"
    assert result["api_calls"] == 1
    assert result["messages"][-2:] == [
        {"role": "user", "content": "compare these options"},
        {"role": "assistant", "content": "## Group of Wisdom\n\n结论：走方案 A。"},
    ]
    assert result["group_of_wisdom"] is True
