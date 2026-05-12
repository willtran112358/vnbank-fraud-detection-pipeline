"""Fraud detection engine combining rule-based and ML-based approaches."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

import pandas as pd
from sklearn.ensemble import IsolationForest

from src.config import AppSettings
from src.fraud.rules import RuleEngine
from src.logger import get_logger

logger = get_logger(__name__)


class FraudDetector:
    """Multi-layered fraud detection combining rules engine with ML anomaly detection."""

    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self.rule_engine = RuleEngine()
        self._anomaly_model: Optional[IsolationForest] = None
        self._model_trained = False

    def detect_by_rules(self, df: pd.DataFrame) -> pd.DataFrame:
        """Execute rule-based fraud detection against transaction data."""
        logger.info("running_rule_based_detection", transaction_count=len(df))
        alerts = self.rule_engine.evaluate(df)
        logger.info("rule_detection_complete", alerts_generated=len(alerts))
        return alerts

    def _train_anomaly_model(self, df: pd.DataFrame) -> None:
        """Train Isolation Forest for anomaly detection on transaction features."""
        if not self.settings.enable_anomaly_detection:
            return

        features = df[["amount_usd", "hour_of_day", "day_of_week"]].copy()
        features["amount_log"] = features["amount_usd"].apply(lambda x: max(x, 0.01)).apply(
            lambda x: float(pd.np.log(x))
        )

        self._anomaly_model = IsolationForest(
            contamination=self.settings.anomaly_contamination,
            random_state=42,
            n_estimators=100,
        )
        self._anomaly_model.fit(features)
        self._model_trained = True
        logger.info("anomaly_model_trained", features=list(features.columns))

    def detect_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect anomalous transactions using trained ML model."""
        if not self._model_trained:
            self._train_anomaly_model(df)

        if self._anomaly_model is None:
            return pd.DataFrame()

        features = df[["amount_usd", "hour_of_day", "day_of_week"]].copy()
        features["amount_log"] = features["amount_usd"].apply(lambda x: max(x, 0.01)).apply(
            lambda x: float(pd.np.log(x))
        )

        predictions = self._anomaly_model.predict(features)
        anomaly_scores = self._anomaly_model.score_samples(features)

        anomalies = df[predictions == -1].copy()
        anomalies["anomaly_score"] = anomaly_scores[predictions == -1]
        anomalies["rule_name"] = "ml_anomaly_detection"
        anomalies["rule_type"] = "anomaly_score"
        anomalies["severity"] = 0.9
        anomalies["detected_at"] = datetime.utcnow().isoformat()

        alerts = [
            {
                "transaction_id": row["transaction_id"],
                "account_id": row["account_id"],
                "amount": row["amount_usd"],
                "rule_name": row["rule_name"],
                "rule_type": row["rule_type"],
                "severity": row["severity"],
                "description": f"ML anomaly score: {row['anomaly_score']:.4f}",
                "timestamp": row["timestamp"],
                "detected_at": row["detected_at"],
            }
            for _, row in anomalies.iterrows()
        ]

        logger.info("anomaly_detection_complete", anomalies_found=len(alerts))
        return pd.DataFrame(alerts) if alerts else pd.DataFrame()

    def run_detection(self, df: pd.DataFrame) -> pd.DataFrame:
        """Run full detection pipeline: rules + ML anomalies."""
        logger.info("fraud_detection_started")

        rule_alerts = self.detect_by_rules(df)
        anomaly_alerts = self.detect_anomalies(df)

        combined = pd.concat([rule_alerts, anomaly_alerts], ignore_index=True)
        if not combined.empty:
            combined = combined.drop_duplicates(subset=["transaction_id", "rule_name"])

        logger.info("fraud_detection_completed", total_alerts=len(combined))
        return combined

    def save_alerts(self, alerts: pd.DataFrame, output_path: str) -> None:
        """Persist fraud alerts to CSV."""
        import os
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        alerts.to_csv(output_path, index=False)
        logger.info("alerts_saved", path=output_path, count=len(alerts))