from hermes_agent.router_core.ledger import BudgetCaps, BudgetLedger


PRICE_TABLE = {
    "openai": {
        "test-model": {
            "input_per_million": 1.0,
            "output_per_million": 2.0,
        }
    }
}


def make_ledger(tmp_path):
    return BudgetLedger(path=tmp_path / "router_budget.sqlite3", price_table=PRICE_TABLE)


def test_single_task_cap_enforced(tmp_path):
    ledger = make_ledger(tmp_path)
    caps = BudgetCaps(single_task_cap=0.0001, daily_cap=10.0, monthly_hard_cap=10.0)

    result = ledger.check_and_reserve(
        "x" * 2000,
        max_output_tokens=2000,
        provider="openai",
        model="test-model",
        caps=caps,
    )

    assert result.allowed is False
    assert result.reason == "single_task_cap_exceeded"


def test_daily_and_monthly_caps_enforced(tmp_path):
    ledger = make_ledger(tmp_path)
    daily_caps = BudgetCaps(single_task_cap=10.0, daily_cap=0.002, monthly_hard_cap=10.0)

    first = ledger.check_and_reserve(
        "x" * 1000,
        max_output_tokens=500,
        provider="openai",
        model="test-model",
        caps=daily_caps,
    )
    second = ledger.check_and_reserve(
        "x" * 1000,
        max_output_tokens=500,
        provider="openai",
        model="test-model",
        caps=daily_caps,
    )

    assert first.allowed is True
    assert second.allowed is False
    assert second.reason == "daily_cap_exceeded"

    monthly_ledger = make_ledger(tmp_path / "monthly")
    monthly_caps = BudgetCaps(single_task_cap=10.0, daily_cap=10.0, monthly_hard_cap=0.002)
    monthly_first = monthly_ledger.check_and_reserve(
        "x" * 1000,
        max_output_tokens=500,
        provider="openai",
        model="test-model",
        caps=monthly_caps,
    )
    monthly_second = monthly_ledger.check_and_reserve(
        "x" * 1000,
        max_output_tokens=500,
        provider="openai",
        model="test-model",
        caps=monthly_caps,
    )

    assert monthly_first.allowed is True
    assert monthly_second.allowed is False
    assert monthly_second.reason == "monthly_hard_cap_exceeded"


def test_soft_warning_event_and_persistence(tmp_path):
    db_path = tmp_path / "router_budget.sqlite3"
    ledger = BudgetLedger(path=db_path, price_table=PRICE_TABLE)
    caps = BudgetCaps(
        single_task_cap=10.0,
        daily_cap=10.0,
        monthly_hard_cap=10.0,
        monthly_soft_warning=0.0005,
    )

    reservation = ledger.check_and_reserve(
        "x" * 1000,
        max_output_tokens=500,
        provider="openai",
        model="test-model",
        caps=caps,
    )
    ledger.record_actual(reservation.reservation_id, actual_cost=0.0012)
    reopened = BudgetLedger(path=db_path, price_table=PRICE_TABLE)

    assert reservation.allowed is True
    assert reservation.event == {
        "type": "budget_soft_warning",
        "provider": "openai",
        "model": "test-model",
        "threshold": 0.0005,
    }
    assert reopened.monthly_spent() == 0.0012
