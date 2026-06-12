from hermes_agent.router_core.policy import decide
from hermes_agent.router_core.types import Decision, Risk, Sensitivity


PROVIDERS = ("deepseek", "gemini", "openai", "openai_codex", "local")


def expected_decision(sensitivity, risk, provider):
    if risk == Risk.R4_CRITICAL:
        return Decision.REQUIRE_HUMAN_APPROVAL
    if sensitivity == Sensitivity.S4_SECRET:
        return Decision.REQUIRE_LOCAL_ONLY
    if sensitivity == Sensitivity.S3_CONFIDENTIAL and provider == "deepseek":
        return Decision.DENY
    if risk == Risk.R3_HIGH and provider != "openai_codex" and provider != "local":
        return Decision.DENY
    if sensitivity == Sensitivity.S3_CONFIDENTIAL and provider != "local":
        return Decision.REQUIRE_HUMAN_APPROVAL
    if sensitivity == Sensitivity.S2_INTERNAL and provider == "deepseek":
        return Decision.REQUIRE_REDACTION
    return Decision.ALLOW


def test_full_sensitivity_risk_provider_matrix():
    for sensitivity in Sensitivity:
        for risk in Risk:
            for provider in PROVIDERS:
                assert decide(sensitivity, risk, provider) == expected_decision(
                    sensitivity, risk, provider
                )


def test_explicit_policy_landmarks():
    assert decide(Sensitivity.S3_CONFIDENTIAL, Risk.R1_LOW, "deepseek") == Decision.DENY
    assert (
        decide(Sensitivity.S4_SECRET, Risk.R1_LOW, "openai")
        == Decision.REQUIRE_LOCAL_ONLY
    )
    assert (
        decide(Sensitivity.S1_LOW, Risk.R4_CRITICAL, "gemini")
        == Decision.REQUIRE_HUMAN_APPROVAL
    )
    assert decide(Sensitivity.S2_INTERNAL, Risk.R1_LOW, "deepseek") == (
        Decision.REQUIRE_REDACTION
    )


def test_unknown_enum_or_provider_denies():
    assert decide("S0_PUBLIC", Risk.R0_TRIVIAL, "openai") == Decision.DENY
    assert decide(Sensitivity.S0_PUBLIC, "R0_TRIVIAL", "openai") == Decision.DENY
    assert decide(Sensitivity.S0_PUBLIC, Risk.R0_TRIVIAL, "unknown") == Decision.DENY
