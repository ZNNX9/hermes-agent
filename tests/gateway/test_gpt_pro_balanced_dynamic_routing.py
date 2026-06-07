from unittest.mock import patch

import gateway.run as gateway_run
from gateway.config import PlatformConfig
from gateway.platforms.api_server import APIServerAdapter


def _runner():
    runner = object.__new__(gateway_run.GatewayRunner)
    runner._service_tier = ""
    return runner


def _primary_runtime():
    return {
        "api_key": "codex-key",
        "base_url": "https://chatgpt.com/backend-api/codex",
        "provider": "openai-codex",
        "api_mode": "codex_responses",
        "command": None,
        "args": [],
        "credential_pool": None,
        "max_tokens": None,
    }


class _FakeAgent:
    last_kwargs = {}

    def __init__(self, **kwargs):
        type(self).last_kwargs = kwargs


def _api_adapter():
    return APIServerAdapter(PlatformConfig(enabled=True, extra={"model_name": "hermes-agent"}))


def test_local_private_routes_to_local_without_fallback():
    routed = {
        "task_type": "local_private",
        "model": "local/gemma4-12b",
        "route_spec": {
            "model": "local/gemma4-12b",
            "provider": "local",
            "model_id": "gemma4:12b-mlx",
            "local_tier": "private",
        },
        "route_policy_version": "intelligent-dynamic-v4-gpt-pro-balanced",
    }

    with patch("gateway.run._run_gateway_local_router", return_value=routed), patch(
        "hermes_cli.runtime_provider.resolve_runtime_provider",
        return_value={
            "api_key": "no-key-required",
            "base_url": "http://127.0.0.1:8680/v1",
            "provider": "custom",
            "api_mode": "chat_completions",
            "command": None,
            "args": [],
            "credential_pool": None,
        },
    ):
        route = _runner()._resolve_turn_agent_config(
            "本地私密总结一下，不要发到远程",
            "gpt-5.5",
            _primary_runtime(),
        )

    assert route["model"] == "gemma4:12b-mlx"
    assert route["runtime"]["provider"] == "custom"
    assert route["runtime"]["base_url"] == "http://127.0.0.1:8680/v1"
    assert route["fallback_model"] is None
    assert route["dynamic_route"]["task_type"] == "local_private"


def test_coding_edit_keeps_gpt55_and_sets_xhigh_reasoning():
    routed = {
        "task_type": "coding_edit",
        "model": "openai-codex/gpt-5.5",
        "route_spec": {
            "model": "openai-codex/gpt-5.5",
            "reasoning_effort": "xhigh",
        },
        "route_policy_version": "intelligent-dynamic-v4-gpt-pro-balanced",
    }

    with patch("gateway.run._run_gateway_local_router", return_value=routed):
        route = _runner()._resolve_turn_agent_config(
            "edit the code and run tests",
            "gpt-5.5",
            _primary_runtime(),
        )

    assert route["model"] == "gpt-5.5"
    assert route["runtime"]["provider"] == "openai-codex"
    assert route["reasoning_config"] == {"enabled": True, "effort": "xhigh"}


def test_session_model_override_skips_dynamic_routing():
    with patch("gateway.run._run_gateway_local_router") as local_router:
        route = _runner()._resolve_turn_agent_config(
            "本地私密总结一下，不要发到远程",
            "custom-model",
            {**_primary_runtime(), "_session_model_override_active": True},
        )

    local_router.assert_not_called()
    assert route["model"] == "custom-model"


def test_api_server_uses_dynamic_route_when_request_has_no_explicit_model():
    dynamic_route = {
        "task_type": "local_private",
        "model": "gemma4:12b-mlx",
        "runtime_kwargs": {
            "api_key": "no-key-required",
            "base_url": "http://127.0.0.1:8680/v1",
            "provider": "custom",
            "api_mode": "chat_completions",
            "command": None,
            "args": [],
            "credential_pool": None,
            "max_tokens": None,
        },
        "fallback_model": None,
        "route_policy_version": "intelligent-dynamic-v4-gpt-pro-balanced",
    }

    with patch("run_agent.AIAgent", _FakeAgent), patch(
        "gateway.run._resolve_runtime_agent_kwargs", return_value=_primary_runtime()
    ), patch("gateway.run._resolve_gateway_model", return_value="gpt-5.5"), patch(
        "gateway.run._load_gateway_config", return_value={}
    ), patch(
        "gateway.run._resolve_dynamic_turn_route", return_value=dynamic_route
    ), patch(
        "gateway.run.GatewayRunner._load_reasoning_config", return_value={}
    ), patch(
        "gateway.run.GatewayRunner._load_fallback_model", return_value={"provider": "deepseek"}
    ), patch(
        "hermes_cli.tools_config._get_platform_tools", return_value=[]
    ), patch.object(
        APIServerAdapter, "_ensure_session_db", return_value=None
    ):
        _api_adapter()._create_agent(user_message="本地私密总结，不要发到远程")

    assert _FakeAgent.last_kwargs["model"] == "gemma4:12b-mlx"
    assert _FakeAgent.last_kwargs["provider"] == "custom"
    assert _FakeAgent.last_kwargs["base_url"] == "http://127.0.0.1:8680/v1"
    assert _FakeAgent.last_kwargs["fallback_model"] is None


def test_api_server_explicit_provider_model_skips_dynamic_route():
    with patch("run_agent.AIAgent", _FakeAgent), patch(
        "gateway.run._resolve_runtime_agent_kwargs", return_value=_primary_runtime()
    ), patch("gateway.run._resolve_gateway_model", return_value="gpt-5.5"), patch(
        "gateway.run._load_gateway_config", return_value={}
    ), patch(
        "gateway.run._resolve_dynamic_turn_route"
    ) as dynamic_route, patch(
        "gateway.run.GatewayRunner._load_reasoning_config", return_value={}
    ), patch(
        "gateway.run.GatewayRunner._load_fallback_model", return_value={"provider": "deepseek"}
    ), patch(
        "hermes_cli.runtime_provider.resolve_runtime_provider",
        return_value={
            "api_key": "codex-key",
            "base_url": "https://chatgpt.com/backend-api/codex",
            "provider": "openai-codex",
            "api_mode": "codex_responses",
            "command": None,
            "args": [],
            "credential_pool": None,
        },
    ), patch(
        "hermes_cli.tools_config._get_platform_tools", return_value=[]
    ), patch.object(
        APIServerAdapter, "_ensure_session_db", return_value=None
    ):
        _api_adapter()._create_agent(
            user_message="本地私密总结，不要发到远程",
            requested_provider="openai-codex",
            requested_model="gpt-5.5",
        )

    dynamic_route.assert_not_called()
    assert _FakeAgent.last_kwargs["model"] == "gpt-5.5"
    assert _FakeAgent.last_kwargs["provider"] == "openai-codex"
    assert _FakeAgent.last_kwargs["base_url"] == "https://chatgpt.com/backend-api/codex"
