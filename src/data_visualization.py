"""Backward-compatible entry point — delegates to the new monitoring dashboard."""
from src.monitoring.dashboard import FraudDashboard

if __name__ == "__main__":
    FraudDashboard.run(
        transactions_path="data/processed_transactions.csv",
        alerts_path="data/fraud_alerts.csv",
    )
