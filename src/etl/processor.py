"""Core transaction ETL processor with configurable transformation rules."""

from __future__ import annotations

import pandas as pd
from pathlib import Path
from typing import Optional
from decimal import Decimal

from src.config import AppSettings
from src.logger import get_logger

logger = get_logger(__name__)


class TransactionProcessor:
    """Processes raw banking transactions through configurable ETL pipeline stages."""

    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self._conversion_rate = settings.currency_conversion_rate

    def extract(self, input_path: str | Path) -> pd.DataFrame:
        """Extract raw transactions from CSV source."""
        path = Path(input_path)
        if not path.exists():
            raise FileNotFoundError(f"Transaction source not found: {path}")

        logger.info("extracting_raw_transactions", source=str(path))
        df = pd.read_csv(path)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        logger.info("transactions_loaded", count=len(df))
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply transformation rules to raw transaction data.

        Transformations:
        - Filter completed transactions only
        - Currency conversion (VND → USD)
        - Feature engineering (hour, day, weekend)
        - Data quality checks
        """
        initial_count = len(df)

        # Stage 1: Quality filters
        df = df[df["status"] == "completed"].copy()
        logger.info("filtered_completed_transactions", before=initial_count, after=len(df))

        # Stage 2: Currency conversion
        df["amount_original"] = df["amount"].astype(float)
        df["amount_usd"] = (df["amount_original"] * self._conversion_rate).round(2)

        # Stage 3: Temporal feature engineering
        df["processing_date"] = df["timestamp"].dt.strftime("%Y-%m-%d")
        df["hour_of_day"] = df["timestamp"].dt.hour
        df["day_of_week"] = df["timestamp"].dt.dayofweek
        df["is_weekend"] = df["day_of_week"].isin([5, 6])

        # Stage 4: Sort for consistency
        df = df.sort_values(["account_id", "timestamp"]).reset_index(drop=True)

        logger.info("transformation_complete", input_rows=initial_count, output_rows=len(df))
        return df

    def load(self, df: pd.DataFrame, output_path: str | Path) -> None:
        """Write processed transactions to target storage."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        logger.info("processed_data_written", path=str(path), rows=len(df))

    def run_pipeline(self, input_path: str | Path, output_path: str | Path) -> pd.DataFrame:
        """Execute the full ETL pipeline end-to-end."""
        logger.info("pipeline_started", input=str(input_path), output=str(output_path))
        raw = self.extract(input_path)
        transformed = self.transform(raw)
        self.load(transformed, output_path)
        logger.info("pipeline_completed", rows=len(transformed))
        return transformed