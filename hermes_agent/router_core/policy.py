from typing import Callable, Sequence, Tuple

from hermes_agent.router_core.types import Decision, Risk, Sensitivity


_LOCAL_PROVIDERS = {"local"}
_CLOUD_PROVIDERS = {"deepseek", "gemini", "openai", "openai_codex"}
_KNOWN_PROVIDERS = _LOCAL_PROVIDERS | _CLOUD_PROVIDERS


def _is_cloud(provider: str) -> bool:
    return provider in _CLOUD_PROVIDERS


def decide(sensitivity, risk, target_provider: str) -> Decision:
    if not isinstance(sensitivity, Sensitivity):
        return Decision.DENY
    if not isinstance(risk, Risk):
        return Decision.DENY
    if target_provider not in _KNOWN_PROVIDERS:
        return Decision.DENY

    rules: Sequence[Tuple[Callable[[], bool], Decision]] = (
        (lambda: risk == Risk.R4_CRITICAL, Decision.REQUIRE_HUMAN_APPROVAL),
        (lambda: sensitivity == Sensitivity.S4_SECRET, Decision.REQUIRE_LOCAL_ONLY),
        (
            lambda: sensitivity == Sensitivity.S3_CONFIDENTIAL
            and target_provider == "deepseek",
            Decision.DENY,
        ),
        (
            lambda: risk == Risk.R3_HIGH
            and _is_cloud(target_provider)
            and target_provider != "openai_codex",
            Decision.DENY,
        ),
        (
            lambda: sensitivity == Sensitivity.S3_CONFIDENTIAL
            and _is_cloud(target_provider),
            Decision.REQUIRE_HUMAN_APPROVAL,
        ),
        (
            lambda: sensitivity == Sensitivity.S2_INTERNAL
            and target_provider == "deepseek",
            Decision.REQUIRE_REDACTION,
        ),
    )

    for predicate, decision in rules:
        if predicate():
            return decision
    return Decision.ALLOW
