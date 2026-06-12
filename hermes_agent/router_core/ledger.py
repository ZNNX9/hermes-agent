import math
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from hermes_agent.router_core.prices_placeholder import PRICE_TABLE


def _default_path() -> str:
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(repo_root, "var", "router_budget.sqlite3")


def _utc_day() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _utc_month() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class BudgetCaps:
    single_task_cap: float
    daily_cap: float
    monthly_hard_cap: float
    monthly_soft_warning: Optional[float] = None

    def as_dict(self) -> Dict[str, Optional[float]]:
        return {
            "single_task_cap": self.single_task_cap,
            "daily_cap": self.daily_cap,
            "monthly_hard_cap": self.monthly_hard_cap,
            "monthly_soft_warning": self.monthly_soft_warning,
        }


@dataclass(frozen=True)
class BudgetCheck:
    allowed: bool
    reason: str
    estimated_cost: float
    reservation_id: str = ""
    daily_spent: float = 0.0
    monthly_spent: float = 0.0
    event: Optional[Dict[str, Any]] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "estimated_cost": self.estimated_cost,
            "reservation_id": self.reservation_id,
            "daily_spent": self.daily_spent,
            "monthly_spent": self.monthly_spent,
            "event": self.event,
        }


class BudgetLedger:
    def __init__(
        self,
        path: Optional[str] = None,
        price_table: Optional[Dict[str, Dict[str, Dict[str, float]]]] = None,
    ) -> None:
        self.path = str(path or _default_path())
        self.price_table = price_table if price_table is not None else PRICE_TABLE
        parent = os.path.dirname(self.path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                create table if not exists budget_ledger (
                    id integer primary key autoincrement,
                    provider text not null,
                    model text not null,
                    day text not null,
                    month text not null,
                    estimated_cost real not null,
                    actual_cost real,
                    status text not null,
                    created_at text not null
                )
                """
            )

    def estimate_cost(
        self,
        text: str,
        max_output_tokens: int,
        provider: str,
        model: str,
    ) -> float:
        input_tokens = math.ceil(len(text) / 4)
        output_tokens = max(0, int(max_output_tokens))
        prices = self.price_table.get(provider, {}).get(model, {})
        input_price = float(prices.get("input_per_million", 0.0))
        output_price = float(prices.get("output_per_million", 0.0))
        return (
            input_tokens * input_price / 1_000_000
            + output_tokens * output_price / 1_000_000
        )

    def _spent(self, column: str, value: str) -> float:
        if column not in {"day", "month"}:
            raise ValueError("unsupported ledger period")
        with self._connect() as connection:
            row = connection.execute(
                f"""
                select coalesce(sum(coalesce(actual_cost, estimated_cost)), 0.0)
                from budget_ledger
                where {column} = ? and status in ('reserved', 'actual')
                """,
                (value,),
            ).fetchone()
        return float(row[0] or 0.0)

    def daily_spent(self, day: Optional[str] = None) -> float:
        return self._spent("day", day or _utc_day())

    def monthly_spent(self, month: Optional[str] = None) -> float:
        return self._spent("month", month or _utc_month())

    def check_and_reserve(
        self,
        text: str,
        max_output_tokens: int,
        provider: str,
        model: str,
        caps: BudgetCaps,
    ) -> BudgetCheck:
        estimate = self.estimate_cost(text, max_output_tokens, provider, model)
        day = _utc_day()
        month = _utc_month()
        daily = self.daily_spent(day)
        monthly = self.monthly_spent(month)

        if estimate > caps.single_task_cap:
            return BudgetCheck(False, "single_task_cap_exceeded", estimate, daily_spent=daily, monthly_spent=monthly)
        if daily + estimate > caps.daily_cap:
            return BudgetCheck(False, "daily_cap_exceeded", estimate, daily_spent=daily, monthly_spent=monthly)
        if monthly + estimate > caps.monthly_hard_cap:
            return BudgetCheck(False, "monthly_hard_cap_exceeded", estimate, daily_spent=daily, monthly_spent=monthly)

        event = None
        if caps.monthly_soft_warning is not None and monthly + estimate >= caps.monthly_soft_warning:
            event = {
                "type": "budget_soft_warning",
                "provider": provider,
                "model": model,
                "threshold": caps.monthly_soft_warning,
            }

        with self._connect() as connection:
            cursor = connection.execute(
                """
                insert into budget_ledger (
                    provider, model, day, month, estimated_cost, actual_cost, status, created_at
                )
                values (?, ?, ?, ?, ?, null, 'reserved', ?)
                """,
                (provider, model, day, month, estimate, _utc_timestamp()),
            )
            reservation_id = str(cursor.lastrowid)

        return BudgetCheck(
            True,
            "allowed",
            estimate,
            reservation_id=reservation_id,
            daily_spent=daily + estimate,
            monthly_spent=monthly + estimate,
            event=event,
        )

    def record_actual(self, reservation_id: str, actual_cost: float) -> None:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                update budget_ledger
                set actual_cost = ?, status = 'actual'
                where id = ?
                """,
                (float(actual_cost), reservation_id),
            )
            if cursor.rowcount != 1:
                raise ValueError("unknown reservation_id")
