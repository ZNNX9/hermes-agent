import json
import sqlite3

from hermes_agent.router_core.classifier import MockClassifier, classify_with_scanner
from hermes_agent.router_core.explain import build_explanation
from hermes_agent.router_core.ledger import BudgetCaps, BudgetLedger
from hermes_agent.router_core.policy import decide
from hermes_agent.router_core.secret_scan import scan_text
from hermes_agent.router_core.types import Risk, Sensitivity


SECRET_FIXTURES = [
    "sk-abcdefghijklmnopqrstuvwxyzABCDEF123456",
    "AKIAIOSFODNN7EXAMPLE",
    "AIzaSyA1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p",
    "ghp_abcdefghijklmnopqrstuvwxyzABCDEF123456",
    "123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi",
    "PAYMENT_API_TOKEN=qzW9XkLmN8pQrStUvWxYz123456789AB",
    "abandon ability able about above absent absorb abstract absurd abuse access accident",
]


PRICE_TABLE = {
    "openai": {
        "test-model": {
            "input_per_million": 1.0,
            "output_per_million": 2.0,
        }
    }
}


def test_pipeline_outputs_never_include_raw_secret(tmp_path):
    db_path = tmp_path / "router_budget.sqlite3"
    ledger = BudgetLedger(path=db_path, price_table=PRICE_TABLE)
    caps = BudgetCaps(single_task_cap=10.0, daily_cap=10.0, monthly_hard_cap=10.0)

    produced = []
    for secret in SECRET_FIXTURES:
        scan = scan_text(f"please route {secret}")
        classifier_result = classify_with_scanner(
            scan,
            MockClassifier(
                sensitivity=Sensitivity.S0_PUBLIC,
                risk=Risk.R1_LOW,
                rationale="mock",
            ),
        )
        decision = classifier_result.decision_override or decide(
            classifier_result.sensitivity,
            classifier_result.risk,
            "openai",
        )
        reservation = ledger.check_and_reserve(
            scan.redacted_text,
            max_output_tokens=128,
            provider="openai",
            model="test-model",
            caps=caps,
        )
        ledger.record_actual(reservation.reservation_id, actual_cost=0.0)
        explanation = build_explanation(
            input_text=f"please route {secret}",
            sensitivity=classifier_result.sensitivity,
            risk=classifier_result.risk,
            decision=decision,
            target_provider="openai",
            reasons=[classifier_result.rationale],
            scan_result=scan,
            clamp_applied=classifier_result.clamp_applied,
            budget={
                "estimated_cost": reservation.estimated_cost,
                "daily_spent": ledger.daily_spent(),
                "monthly_spent": ledger.monthly_spent(),
                "caps": caps.as_dict(),
            },
            timestamp="2026-06-12T00:00:00Z",
        )
        produced.append(json.dumps(explanation, sort_keys=True))
        produced.append(json.dumps(scan.redacted_text))
        produced.append(json.dumps(reservation.as_dict(), sort_keys=True))

    with sqlite3.connect(db_path) as connection:
        rows = connection.execute("select * from budget_ledger").fetchall()
    produced.append(json.dumps(rows, sort_keys=True, default=str))
    payload = "\n".join(produced)

    for secret in SECRET_FIXTURES:
        assert secret not in payload
