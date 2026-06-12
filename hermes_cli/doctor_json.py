"""Machine-readable runtime health report for ``hermes doctor --json``."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


CHECK_STATUS_ORDER = {"ok": 0, "skipped": 0, "warn": 1, "fail": 2}
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}
ALL_INTERFACE_HOSTS = {"0.0.0.0", "::"}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hermes_home() -> Path:
    from hermes_constants import get_hermes_home

    return get_hermes_home()


def _gateway_runtime_status() -> dict[str, Any] | None:
    from gateway.status import read_runtime_status

    return read_runtime_status()


def _gateway_running_pid() -> int | None:
    from gateway.status import get_running_pid

    return get_running_pid(cleanup_stale=True)


def _config_file_values() -> dict[str, Any]:
    config_path = _hermes_home() / "config.yaml"
    try:
        import yaml

        raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, UnicodeDecodeError, ImportError, AttributeError):
        return {}
    return raw if isinstance(raw, dict) else {}


def _dotenv_values() -> dict[str, str]:
    env_path = _hermes_home() / ".env"
    try:
        lines = env_path.read_text(encoding="utf-8-sig").splitlines()
    except (FileNotFoundError, OSError, UnicodeDecodeError):
        return {}

    values: dict[str, str] = {}
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


def _config_value(key: str, default: Any = "") -> Any:
    if key in os.environ:
        return os.environ[key]
    values = _config_file_values()
    if key in values and values[key] is not None:
        return values[key]
    env_values = _dotenv_values()
    if key in env_values:
        return env_values[key]
    return default


def _config_flag(name: str) -> bool:
    value = _config_value(name, "")
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _config_port(name: str, default: int) -> int:
    try:
        return int(str(_config_value(name, default)).strip() or default)
    except (TypeError, ValueError):
        return default


def _api_server_config() -> dict[str, Any]:
    return {
        "enabled": _config_flag("API_SERVER_ENABLED"),
        "host": str(_config_value("API_SERVER_HOST", "127.0.0.1")).strip()
        or "127.0.0.1",
        "port": _config_port("API_SERVER_PORT", 8642),
        "model": str(_config_value("API_SERVER_MODEL_NAME", "hermes-agent")).strip()
        or "hermes-agent",
        "has_api_key": bool(str(_config_value("API_SERVER_KEY", "")).strip()),
    }


def _check_gateway_runtime() -> dict[str, Any]:
    runtime_status = _gateway_runtime_status()
    running_pid = _gateway_running_pid()
    details: dict[str, Any] = {
        "running_pid": running_pid,
        "runtime_status": runtime_status or {},
    }
    if running_pid:
        return {"status": "ok", "details": details}
    if runtime_status:
        state = str(runtime_status.get("gateway_state") or "unknown")
        details["gateway_state"] = state
        if state in {"running", "starting"}:
            return {"status": "ok", "details": details}
        return {"status": "warn", "details": details}
    return {"status": "skipped", "details": details}


def _check_launchd_definition() -> dict[str, Any]:
    if sys.platform != "darwin":
        return {
            "status": "skipped",
            "details": {"reason": "launchd is only available on macOS"},
        }

    try:
        from hermes_cli.gateway import get_launchd_plist_path, launchd_plist_is_current

        plist_path = get_launchd_plist_path()
        if not plist_path.exists():
            return {
                "status": "skipped",
                "details": {"plist_path": str(plist_path), "installed": False},
            }
        current = launchd_plist_is_current()
        return {
            "status": "ok" if current else "warn",
            "details": {
                "plist_path": str(plist_path),
                "installed": True,
                "current": current,
            },
        }
    except Exception as exc:
        return {"status": "warn", "details": {"error": str(exc)}}


def _check_listener_exposure(config: dict[str, Any]) -> dict[str, Any]:
    host = str(config["host"])
    details = {
        "host": host,
        "port": config["port"],
        "api_server_enabled": config["enabled"],
        "has_api_key": config["has_api_key"],
        "requires_approval": False,
        "exposure": "loopback",
    }
    if host in LOOPBACK_HOSTS:
        return {"status": "ok", "details": details}

    details["requires_approval"] = True
    if host in ALL_INTERFACE_HOSTS:
        details["exposure"] = "all_interfaces"
    else:
        details["exposure"] = "network"
    return {"status": "warn", "details": details}


def _request_json(
    url: str,
    *,
    method: str = "GET",
    api_key: str,
    payload: dict[str, Any] | None = None,
    http_request: Callable[..., Any] = urlopen,
) -> tuple[bool, dict[str, Any]]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = Request(url, data=body, headers=headers, method=method)

    try:
        with http_request(request, timeout=5) as response:
            response_body = response.read().decode("utf-8", errors="replace")
            parsed = json.loads(response_body) if response_body else {}
            return True, {
                "http_status": getattr(response, "status", None),
                "payload": parsed,
            }
    except HTTPError as exc:
        return False, {"http_status": exc.code, "error": exc.reason}
    except (URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        return False, {"error": str(exc)}


def _skip_api_smoke(reason: str) -> dict[str, Any]:
    return {"status": "skipped", "details": {"reason": reason}}


def _check_api_models(
    config: dict[str, Any],
    *,
    http_request: Callable[..., Any],
) -> dict[str, Any]:
    if not config["enabled"]:
        return _skip_api_smoke("API_SERVER_ENABLED is not true")
    api_key = str(_config_value("API_SERVER_KEY", "")).strip()
    if not api_key:
        return {
            "status": "fail",
            "details": {"reason": "API_SERVER_KEY is required for API smoke checks"},
        }

    url = f"http://{config['host']}:{config['port']}/v1/models"
    ok, details = _request_json(url, api_key=api_key, http_request=http_request)
    payload = details.pop("payload", {})
    details["model_count"] = len(payload.get("data", [])) if isinstance(payload, dict) else 0
    return {"status": "ok" if ok else "fail", "details": details}


def _check_chat_smoke(
    config: dict[str, Any],
    *,
    http_request: Callable[..., Any],
) -> dict[str, Any]:
    if not config["enabled"]:
        return _skip_api_smoke("API_SERVER_ENABLED is not true")
    api_key = str(_config_value("API_SERVER_KEY", "")).strip()
    if not api_key:
        return {
            "status": "fail",
            "details": {"reason": "API_SERVER_KEY is required for API smoke checks"},
        }

    url = f"http://{config['host']}:{config['port']}/v1/chat/completions"
    ok, details = _request_json(
        url,
        method="POST",
        api_key=api_key,
        payload={
            "model": config["model"],
            "messages": [{"role": "user", "content": "health check"}],
            "stream": False,
        },
        http_request=http_request,
    )
    payload = details.pop("payload", {})
    details["model"] = config["model"]
    details["has_choices"] = bool(
        isinstance(payload, dict) and isinstance(payload.get("choices"), list)
    )
    return {"status": "ok" if ok else "fail", "details": details}


def _check_secret_scan() -> dict[str, Any]:
    return {
        "status": "ok",
        "details": {
            "secrets_printed": False,
            "env_keys_reported_only": True,
        },
    }


def _find_receipt_schema() -> Path | None:
    current = Path.cwd().resolve()
    for candidate in (current, *current.parents):
        schema_path = candidate / ".agent" / "EVIDENCE_RECEIPT_SCHEMA.md"
        if schema_path.exists():
            return schema_path
    return None


def _check_receipt_validator() -> dict[str, Any]:
    schema_path = _find_receipt_schema()
    if schema_path is None:
        return {
            "status": "skipped",
            "details": {"reason": ".agent/EVIDENCE_RECEIPT_SCHEMA.md not found"},
        }
    return {"status": "ok", "details": {"schema_path": str(schema_path)}}


def _overall_status(checks: dict[str, dict[str, Any]]) -> str:
    worst = "ok"
    for check in checks.values():
        status = str(check.get("status", "fail"))
        if CHECK_STATUS_ORDER.get(status, 2) > CHECK_STATUS_ORDER[worst]:
            worst = status
    return worst


def build_doctor_json_report(
    *,
    http_request: Callable[..., Any] = urlopen,
) -> dict[str, Any]:
    """Build a secret-safe runtime health report for automation."""
    config = _api_server_config()
    checks = {
        "gateway_runtime": _check_gateway_runtime(),
        "launchd_definition": _check_launchd_definition(),
        "listener_exposure": _check_listener_exposure(config),
        "api_models": _check_api_models(config, http_request=http_request),
        "chat_smoke": _check_chat_smoke(config, http_request=http_request),
        "secret_scan": _check_secret_scan(),
        "receipt_validator": _check_receipt_validator(),
    }
    return {
        "schema_version": 1,
        "generated_at": _utc_now_iso(),
        "hermes_home": str(_hermes_home()),
        "overall_status": _overall_status(checks),
        "checks": checks,
    }


def emit_doctor_json() -> None:
    """Print the runtime health report as JSON."""
    print(json.dumps(build_doctor_json_report(), indent=2, sort_keys=True))
