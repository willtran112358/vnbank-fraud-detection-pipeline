"""Configurable fraud detection rule engine with extensible rule types."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

import pandas as pd


class FraudRuleType(str, Enum):
    """Classification of fraud detection rules."""

    AMOUNT_THRESHOLD = "amount_threshold"
    RAPID_CONSECUTIVE = "rapid_consecutive"
    VELOCITY_CHECK = "velocity_check"
    LOCATION_ANOMALY = "location_anomaly"
    AMOUNT_ANOMALY = "amount_anomaly"
    DUPLICATE_CHECK = "duplicate_check"


@dataclass
class Rule:
    """A single configurable fraud detection rule."""

    name: str
    rule_type: FraudRuleType
    severity: float = 0.5
    enabled: bool = True
    params: dict[str, Any] = field(default_factory=dict)
    description: str = ""


class RuleEngine:
    """Executes a collection of fraud detection rules against transaction data."""

    def __init__(self, rules: list[Rule] | None = None) -> None:
        self.rules = rules or self._default_rules()

    @staticmethod
    def _default_rules() -> list[Rule]:
        return [
            Rule(
                name="high_value_transaction",
                rule_type=FraudRuleType.AMOUNT_THRESHOLD,
                severity=0.7,
                params={"threshold": 10000.0},
                description="Flag transactions exceeding value threshold",
            ),
            Rule(
                name="rapid_consecutive_tx",
                rule_type=FraudRuleType.RAPID_CONSECUTIVE,
                severity=0.8,
                params={"max_count": 3, "window_minutes": 5},
                description="Flag rapid consecutive transactions from same account",
            ),
            Rule(
                name="high_velocity_account",
                rule_type=FraudRuleType.VELOCITY_CHECK,
                severity=0.6,
                params={"max_per_hour": 10},
                description="Flag accounts exceeding transaction velocity",
            ),
        ]

    def evaluate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Run all enabled rules against the transaction dataframe."""
        alerts = []
        for rule in self.rules:
            if not rule.enabled:
                continue
            rule_alerts = self._execute_rule(rule, df)
            alerts.extend(rule_alerts)
        return pd.DataFrame(alerts) if alerts else pd.DataFrame()

    def _execute_rule(self, rule: Rule, df: pd.DataFrame) -> list[dict]:
        """Execute a single rule and return matching alert records."""
        from datetime import datetime

        if rule.rule_type == FraudRuleType.AMOUNT_THRESHOLD:
            threshold = rule.params.get("threshold", 10000.0)
            matches = df[df["amount_usd"] > threshold]
            return [
                {
                    "transaction_id": row["transaction_id"],
                    "account_id": row["account_id"],
                    "amount": row["amount_usd"],
                    "rule_name": rule.name,
                    "rule_type": rule.rule_type.value,
                    "severity": rule.severity,
                    "description": f"Transaction ${row['amount_usd']:.2f} exceeds threshold ${threshold:.2f}",
                    "timestamp": row["timestamp"],
                    "detected_at": datetime.utcnow().isoformat(),
                }
                for _, row in matches.iterrows()
            ]

        elif rule.rule_type == FraudRuleType.RAPID_CONSECUTIVE:
            max_count = rule.params.get("max_count", 3)
            window = rule.params.get("window_minutes", 5)
            from datetime import timedelta

            alerts = []
            for account_id, group in df.sort_values("timestamp").groupby("account_id"):
                group = group.reset_index(drop=True)
                for i in range(len(group)):
                    window_end = group.iloc[i]["timestamp"] + timedelta(minutes=window)
                    count_in_window = ((group["timestamp"] >= group.iloc[i]["timestamp"]) & (group["timestamp"] <= window_end)).sum()
                    if count_in_window > max_count:
                        alerts.append({
                            "transaction_id": group.iloc[i]["transaction_id"],
                            "account_id": account_id,
                            "amount": group.iloc[i]["amount_usd"],
                            "rule_name": rule.name,
                            "rule_type": rule.rule_type.value,
                            "severity": rule.severity,
                            "description": f"Account {account_id[:8]}...: {count_in_window} transactions in {window}min",
                            "timestamp": group.iloc[i]["timestamp"],
                            "detected_at": datetime.utcnow().isoformat(),
                        })
            return alerts

        return []