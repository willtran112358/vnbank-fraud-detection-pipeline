"""Data enrichment layer for transaction records with external data sources."""

from __future__ import annotations

import pandas as pd
from src.logger import get_logger

logger = get_logger(__name__)


class DataEnricher:
    """Enriches processed transactions with additional context and features."""

    @staticmethod
    def add_rolling_statistics(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
        """Add rolling window statistics per account for velocity analysis."""
        result = df.copy()
        result["tx_count_rolling"] = (
            result.groupby("account_id")["transaction_id"]
            .rolling(window, min_periods=1)
            .count()
            .reset_index(level=0, drop=True)
        )
        result["amount_rolling_avg"] = (
            result.groupby("account_id")["amount_usd"]
            .rolling(window, min_periods=1)
            .mean()
            .reset_index(level=0, drop=True)
        )
        result["amount_rolling_std"] = (
            result.groupby("account_id")["amount_usd"]
            .rolling(window, min_periods=1)
            .std()
            .reset_index(level=0, drop=True)
            .fillna(0)
        )
        return result

    @staticmethod
    def add_location_risk_score(df: pd.DataFrame) -> pd.DataFrame:
        """Assign risk scores based on transaction location patterns."""
        risk_locations = {"high_risk": ["Havana", "Pyongyang", "Tehran"], "medium_risk": ["Moscow", "Beijing"]}

        def score_location(loc: str) -> float:
            if loc in risk_locations["high_risk"]:
                return 0.8
            elif loc in risk_locations["medium_risk"]:
                return 0.4
            return 0.1

        result = df.copy()
        result["location_risk_score"] = result["location"].apply(score_location)
        return result