"""Techcombank Fraud Detection Pipeline — CLI entry point."""

from __future__ import annotations

import click
from pathlib import Path

from src.config import AppSettings, load_config
from src.logger import configure_logging, get_logger
from src.data_generator import generate_transactions
from src.etl import TransactionProcessor
from src.fraud import FraudDetector
from src.monitoring import FraudDashboard

logger = get_logger(__name__)


@click.group()
@click.option("--config", "-c", type=click.Path(exists=True), help="Config file path")
@click.option("--log-level", default=None, help="Override log level")
@click.pass_context
def cli(ctx: click.Context, config: str | None, log_level: str | None) -> None:
    """Techcombank Fraud Detection Pipeline — production-grade transaction monitoring."""
    ctx.ensure_object(dict)

    settings = load_config(Path(config) if config else None)
    if log_level:
        settings.log_level = log_level

    configure_logging(level=settings.log_level, log_format=settings.log_format)
    ctx.obj["settings"] = settings


@cli.command()
@click.argument("num_records", type=int, default=10000)
@click.option("--output", "-o", default="data/transactions.csv", help="Output path")
@click.pass_context
def generate(ctx: click.Context, num_records: int, output: str) -> None:
    """Generate synthetic transaction data."""
    generate_transactions(num_records, output)


@cli.command()
@click.option("--input", "-i", default="data/transactions.csv", help="Input CSV path")
@click.option("--output", "-o", default="data/processed_transactions.csv", help="Output CSV path")
@click.pass_context
def etl(ctx: click.Context, input: str, output: str) -> None:
    """Run ETL pipeline on transaction data."""
    settings = ctx.obj["settings"]
    processor = TransactionProcessor(settings)
    processor.run_pipeline(input, output)


@cli.command()
@click.option("--input", "-i", default="data/processed_transactions.csv", help="Input CSV path")
@click.option("--output", "-o", default="data/fraud_alerts.csv", help="Alerts output path")
@click.pass_context
def detect(ctx: click.Context, input: str, output: str) -> None:
    """Run fraud detection on processed transactions."""
    import pandas as pd

    settings = ctx.obj["settings"]
    detector = FraudDetector(settings)
    df = pd.read_csv(input)
    alerts = detector.run_detection(df)
    detector.save_alerts(alerts, output)


@cli.command()
@click.option("--transactions", "-t", default="data/processed_transactions.csv")
@click.option("--alerts", "-a", default="data/fraud_alerts.csv")
def dashboard(transactions: str, alerts: str) -> None:
    """Launch the fraud monitoring dashboard."""
    FraudDashboard.run(transactions, alerts)


@cli.command()
@click.option("--num-records", "-n", type=int, default=10000)
@click.pass_context
def run_all(ctx: click.Context, num_records: int) -> None:
    """Run the complete pipeline: generate → ETL → detect."""
    settings = ctx.obj["settings"]

    logger.info("pipeline_orchestration_started")

    # Step 1: Generate
    generate_transactions(num_records, settings.raw_transactions_path)

    # Step 2: ETL
    processor = TransactionProcessor(settings)
    processed = processor.run_pipeline(
        settings.raw_transactions_path, settings.processed_transactions_path
    )

    # Step 3: Fraud detection
    import pandas as pd
    detector = FraudDetector(settings)
    df = pd.read_csv(settings.processed_transactions_path)
    alerts = detector.run_detection(df)
    detector.save_alerts(alerts, settings.fraud_alerts_path)

    logger.info("pipeline_orchestration_completed")


if __name__ == "__main__":
    cli()