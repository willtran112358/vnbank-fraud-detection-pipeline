"""Production-grade synthetic transaction data generator with realistic distribution patterns."""

from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from typing import Optional

from faker import Faker

from src.logger import get_logger

logger = get_logger(__name__)

fake = Faker()

TRANSACTION_TYPES = ["deposit", "withdrawal", "transfer", "payment"]
STATUSES = ["completed", "completed", "completed", "completed", "pending", "failed"]
LOCATIONS = [
    "Ho Chi Minh City", "Hanoi", "Da Nang", "Hai Phong", "Can Tho",
    "Bangkok", "Singapore", "Kuala Lumpur", "Tokyo", "Seoul",
    "New York", "London", "Sydney", "Hong Kong", "Paris",
]


def generate_transaction(timestamp: Optional[datetime] = None) -> dict:
    """Generate a single realistic banking transaction."""
    amount = random.choices(
        population=[round(random.uniform(10, 500), 2),
                     round(random.uniform(500, 5000), 2),
                     round(random.uniform(5000, 50000), 2),
                     round(random.uniform(50000, 200000), 2)],
        weights=[0.4, 0.35, 0.2, 0.05],
        k=1
    )[0]

    return {
        "transaction_id": fake.uuid4(),
        "account_id": fake.uuid4(),
        "timestamp": (timestamp or fake.date_time_between(start_date="-6m", end_date="now")).isoformat(),
        "amount": amount,
        "transaction_type": random.choice(TRANSACTION_TYPES),
        "location": random.choice(LOCATIONS),
        "status": random.choice(STATUSES),
    }


def generate_transactions(num_records: int, file_path: str) -> None:
    """Generate synthetic transaction dataset and write to CSV."""
    logger.info("generating_synthetic_data", records=num_records, output=file_path)

    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        sample = generate_transaction()
        writer = csv.DictWriter(file, fieldnames=list(sample.keys()))
        writer.writeheader()

        for i in range(num_records):
            writer.writerow(generate_transaction())
            if (i + 1) % 5000 == 0:
                logger.info("generation_progress", written=i + 1)

    logger.info("data_generation_complete", records=num_records, file=file_path)


if __name__ == "__main__":
    generate_transactions(10000, "data/transactions.csv")