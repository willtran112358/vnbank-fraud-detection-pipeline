"""Apache Airflow DAG for VPBank fraud detection ETL pipeline."""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from src.config import AppSettings
from src.logger import configure_logging
from src.data_generator import generate_transactions
from src.etl import TransactionProcessor
from src.fraud import FraudDetector

default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
    "email": ["data-engineering@vpbank.com.vn"],
}

settings = AppSettings()
configure_logging(level=settings.log_level, service="airflow-pipeline")


def generate_data_task(**context) -> None:
    """Generate synthetic transaction data for pipeline execution."""
    generate_transactions(
        num_records=context.get("num_records", 10000),
        file_path=settings.raw_transactions_path,
    )


def run_etl_task() -> None:
    """Execute the ETL processing pipeline."""
    processor = TransactionProcessor(settings)
    processor.run_pipeline(
        settings.raw_transactions_path,
        settings.processed_transactions_path,
    )


def run_fraud_detection_task() -> None:
    """Execute fraud detection on processed transactions."""
    import pandas as pd

    detector = FraudDetector(settings)
    df = pd.read_csv(settings.processed_transactions_path)
    alerts = detector.run_detection(df)
    detector.save_alerts(alerts, settings.fraud_alerts_path)


with DAG(
    "vpbank_fraud_detection_pipeline",
    default_args=default_args,
    description="VPBank end-to-end fraud detection ETL pipeline",
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=["vpbank", "fraud", "etl"],
) as dag:

    generate_data = PythonOperator(
        task_id="generate_synthetic_data",
        python_callable=generate_data_task,
        op_kwargs={"num_records": 10000},
    )

    run_etl = PythonOperator(
        task_id="run_etl_pipeline",
        python_callable=run_etl_task,
    )

    run_fraud_detection = PythonOperator(
        task_id="run_fraud_detection",
        python_callable=run_fraud_detection_task,
    )

    generate_data >> run_etl >> run_fraud_detection