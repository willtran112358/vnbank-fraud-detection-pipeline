"""Unit tests for the ETL processor module."""

import pandas as pd
import pytest
from datetime import datetime

from src.config import AppSettings
from src.etl.processor import TransactionProcessor


@pytest.fixture
def settings() -> AppSettings:
    return AppSettings(currency_conversion_rate=0.85)


@pytest.fixture
def processor(settings: AppSettings) -> TransactionProcessor:
    return TransactionProcessor(settings)


@pytest.fixture
def sample_transactions() -> pd.DataFrame:
    return pd.DataFrame({
        "transaction_id": ["tx1", "tx2", "tx3", "tx4"],
        "account_id": ["acc1", "acc1", "acc2", "acc2"],
        "timestamp": [
            datetime(2024, 1, 1, 10, 0, 0),
            datetime(2024, 1, 1, 11, 0, 0),
            datetime(2024, 1, 2, 10, 0, 0),
            datetime(2024, 1, 2, 11, 0, 0),
        ],
        "amount": [100.0, 5000.0, 25000.0, 100.0],
        "transaction_type": ["deposit", "transfer", "withdrawal", "payment"],
        "location": ["HCMC", "Hanoi", "Singapore", "Tokyo"],
        "status": ["completed", "completed", "completed", "failed"],
    })


class TestTransactionProcessor:
    """Test suite for TransactionProcessor."""

    def test_transform_filters_completed_only(self, processor: TransactionProcessor, sample_transactions: pd.DataFrame):
        result = processor.transform(sample_transactions)
        assert len(result) == 3  # 3 completed, 1 failed
        assert "failed" not in result["status"].values

    def test_transform_adds_currency_conversion(self, processor: TransactionProcessor, sample_transactions: pd.DataFrame):
        result = processor.transform(sample_transactions)
        assert "amount_usd" in result.columns
        assert "amount_original" in result.columns
        expected_usd = round(100.0 * 0.85, 2)
        assert result.iloc[0]["amount_usd"] == expected_usd

    def test_transform_adds_temporal_features(self, processor: TransactionProcessor, sample_transactions: pd.DataFrame):
        result = processor.transform(sample_transactions)
        assert "processing_date" in result.columns
        assert "hour_of_day" in result.columns
        assert "day_of_week" in result.columns
        assert "is_weekend" in result.columns
        assert result.iloc[0]["hour_of_day"] == 10

    def test_extract_raises_on_missing_file(self, processor: TransactionProcessor):
        with pytest.raises(FileNotFoundError):
            processor.extract("nonexistent_file.csv")