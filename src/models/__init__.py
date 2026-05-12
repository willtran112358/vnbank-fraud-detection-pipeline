"""Data models for VPBank fraud detection domain."""
from .transaction import Transaction, TransactionRecord, FraudAlert

__all__ = ["Transaction", "TransactionRecord", "FraudAlert"]