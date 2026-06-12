from hermes_agent.router_core.explain import build_explanation
from hermes_agent.router_core.policy import decide
from hermes_agent.router_core.secret_scan import scan_text
from hermes_agent.router_core.types import Risk, Sensitivity


def test_explanation_schema_keys_present():
    scan = scan_text("hello")
    decision = decide(Sensitivity.S0_PUBLIC, Risk.R0_TRIVIAL, "openai")

    explanation = build_explanation(
        input_text="hello",
        sensitivity=Sensitivity.S0_PUBLIC,
        risk=Risk.R0_TRIVIAL,
        decision=decision,
        target_provider="openai",
        reasons=["public input"],
        scan_result=scan,
        clamp_applied=False,
        budget={
            "estimated_cost": 0.0,
            "daily_spent": 0.0,
            "monthly_spent": 0.0,
            "caps": {},
        },
        timestamp="2026-06-12T00:00:00Z",
    )

    assert set(explanation) == {
        "input_hash",
        "sensitivity",
        "risk",
        "decision",
        "target_provider",
        "reasons",
        "redaction_count",
        "clamp_applied",
        "budget",
        "timestamp",
    }


def test_explanation_is_deterministic_for_same_input():
    scan = scan_text("hello")
    kwargs = {
        "input_text": "hello",
        "sensitivity": Sensitivity.S0_PUBLIC,
        "risk": Risk.R0_TRIVIAL,
        "decision": decide(Sensitivity.S0_PUBLIC, Risk.R0_TRIVIAL, "openai"),
        "target_provider": "openai",
        "reasons": ["public input"],
        "scan_result": scan,
        "clamp_applied": False,
        "budget": {
            "estimated_cost": 0.0,
            "daily_spent": 0.0,
            "monthly_spent": 0.0,
            "caps": {},
        },
        "timestamp": "2026-06-12T00:00:00Z",
    }

    assert build_explanation(**kwargs) == build_explanation(**kwargs)
