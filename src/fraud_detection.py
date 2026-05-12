"""Backward-compatible entry point — delegates to the new fraud detector."""
import pandas as pd
from src.fraud.detector import FraudDetector
from src.config.settings import AppSettings

if __name__ == "__main__":
    settings = AppSettings()
    detector = FraudDetector(settings)
    df = pd.read_csv(settings.processed_transactions_path)
    alerts = detector.run_detection(df)
    detector.save_alerts(alerts, settings.fraud_alerts_path)
    print(f"Detected {len(alerts)} fraudulent transactions.")
