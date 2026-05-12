"""Backward-compatible entry point — delegates to the new ETL processor."""
from src.etl.processor import TransactionProcessor
from src.config.settings import AppSettings

if __name__ == "__main__":
    settings = AppSettings()
    processor = TransactionProcessor(settings)
    processor.run_pipeline(settings.raw_transactions_path, settings.processed_transactions_path)
  
