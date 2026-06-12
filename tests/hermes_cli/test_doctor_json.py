"""Tests for the machine-readable ``hermes doctor --json`` baseline."""

import argparse
import json
from urllib.error import HTTPError

from hermes_cli.subcommands.doctor import build_doctor_parser


def test_doctor_parser_accepts_json_flag():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    build_doctor_parser(subparsers, cmd_doctor=lambda args: args)

    args = parser.parse_args(["doctor", "--json"])

    assert args.command == "doctor"
    assert args.json is True


def test_doctor_json_skips_api_smoke_without_api_server_config(monkeypatch, tmp_path):
    from hermes_cli import doctor_json

    monkeypatch.setattr(doctor_json, "_hermes_home", lambda: tmp_path)
    monkeypatch.setattr(doctor_json, "_gateway_runtime_status", lambda: None)
    monkeypatch.setattr(doctor_json, "_gateway_running_pid", lambda: None)
    monkeypatch.delenv("API_SERVER_ENABLED", raising=False)
    monkeypatch.delenv("API_SERVER_KEY", raising=False)
    monkeypatch.delenv("API_SERVER_HOST", raising=False)
    monkeypatch.delenv("API_SERVER_PORT", raising=False)

    report = doctor_json.build_doctor_json_report(http_request=lambda *_a, **_kw: None)

    assert report["schema_version"] == 1
    assert report["checks"]["api_models"]["status"] == "skipped"
    assert report["checks"]["chat_smoke"]["status"] == "skipped"
    assert report["checks"]["secret_scan"]["details"]["secrets_printed"] is False


def test_doctor_json_runs_authenticated_models_and_chat_smoke_without_leaking_key(
    monkeypatch, tmp_path
):
    from hermes_cli import doctor_json

    calls = []

    class FakeResponse:
        def __init__(self, status, payload):
            self.status = status
            self._payload = payload

        def __enter__(self):
            return self

        def __exit__(self, *_exc):
            return False

        def read(self):
            return json.dumps(self._payload).encode("utf-8")

    def fake_http_request(request, timeout):
        calls.append(
            {
                "url": request.full_url,
                "method": request.get_method(),
                "authorization": request.headers.get("Authorization"),
                "body": request.data.decode("utf-8") if request.data else "",
                "timeout": timeout,
            }
        )
        if request.full_url.endswith("/v1/models"):
            return FakeResponse(200, {"data": [{"id": "hermes-agent"}]})
        if request.full_url.endswith("/v1/chat/completions"):
            return FakeResponse(200, {"choices": [{"message": {"content": "ok"}}]})
        raise HTTPError(request.full_url, 404, "not found", hdrs=None, fp=None)

    monkeypatch.setattr(doctor_json, "_hermes_home", lambda: tmp_path)
    monkeypatch.setattr(doctor_json, "_gateway_runtime_status", lambda: {"gateway_state": "running"})
    monkeypatch.setattr(doctor_json, "_gateway_running_pid", lambda: 123)
    monkeypatch.setenv("API_SERVER_ENABLED", "true")
    monkeypatch.setenv("API_SERVER_KEY", "sk-test-secret")
    monkeypatch.setenv("API_SERVER_HOST", "127.0.0.1")
    monkeypatch.setenv("API_SERVER_PORT", "8642")
    monkeypatch.setenv("API_SERVER_MODEL_NAME", "hermes-agent")

    report = doctor_json.build_doctor_json_report(http_request=fake_http_request)

    assert report["checks"]["api_models"]["status"] == "ok"
    assert report["checks"]["chat_smoke"]["status"] == "ok"
    assert calls[0]["authorization"] == "Bearer sk-test-secret"
    assert calls[1]["authorization"] == "Bearer sk-test-secret"
    assert "sk-test-secret" not in json.dumps(report)
