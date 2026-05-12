"""Configuration management using environment variables with pydantic-settings."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """Application settings for VPBank fraud detection pipeline."""

    # Data paths
    data_dir: str = "data"
    raw_transactions_path: str = "data/transactions.csv"
    processed_transactions_path: str = "data/processed_transactions.csv"
    fraud_alerts_path: str = "data/fraud_alerts.csv"

    # Pipeline configuration
    batch_size: int = 10000
    currency_conversion_rate: float = 0.85
    fraud_amount_threshold: float = 10000.0
    max_consecutive_transactions: int = 3
    time_window_minutes: int = 5

    # Database
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "vpbank_fraud"
    db_user: str = "vpbank"
    db_password: str = ""

    # Monitoring
    log_level: str = "INFO"
    log_format: str = "json"
    enable_anomaly_detection: bool = True
    anomaly_contamination: float = 0.01

    # Streaming configuration
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_transaction_topic: str = "vpbank.transactions.raw"
    kafka_alert_topic: str = "vpbank.alerts.fraud"

    model_config = {"env_prefix": "VPBANK_", "env_file": ".env", "extra": "ignore"}

    @property
    def resolved_data_dir(self) -> Path:
        return Path(self.data_dir).resolve()


def load_config(config_path: Optional[Path] = None) -> AppSettings:
    """Load settings with optional YAML override support."""
    settings = AppSettings()

    if config_path and config_path.exists():
        import yaml

        with open(config_path) as f:
            overrides = yaml.safe_load(f) or {}
        for key, value in overrides.items():
            if hasattr(settings, key):
                setattr(settings, key, value)

    return settings