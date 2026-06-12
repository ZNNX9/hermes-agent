import hashlib
from typing import Any, Dict, Iterable

from hermes_agent.router_core.types import Decision, Risk, RouteExplanation, ScanResult, Sensitivity


def _enum_name(value: Any) -> str:
    return value.name if hasattr(value, "name") else str(value)


def _safe_budget(budget: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "estimated_cost": budget.get("estimated_cost", 0.0),
        "daily_spent": budget.get("daily_spent", 0.0),
        "monthly_spent": budget.get("monthly_spent", 0.0),
        "caps": dict(budget.get("caps", {})),
    }


def build_explanation(
    input_text: str,
    sensitivity: Sensitivity,
    risk: Risk,
    decision: Decision,
    target_provider: str,
    reasons: Iterable[str],
    scan_result: ScanResult,
    clamp_applied: bool,
    budget: Dict[str, Any],
    timestamp: str,
) -> Dict[str, Any]:
    explanation = RouteExplanation(
        input_hash=hashlib.sha256(input_text.encode("utf-8")).hexdigest(),
        sensitivity=sensitivity,
        risk=risk,
        decision=decision,
        target_provider=target_provider,
        reasons=[str(reason) for reason in reasons],
        redaction_count=scan_result.redaction_count,
        clamp_applied=bool(clamp_applied),
        budget=_safe_budget(budget),
        timestamp=timestamp,
    )
    data = explanation.as_dict()
    data["sensitivity"] = _enum_name(sensitivity)
    data["risk"] = _enum_name(risk)
    data["decision"] = _enum_name(decision)
    return data
