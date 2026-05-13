"""Data models for VNBank fraud detection domain."""
from .transaction import Transaction, TransactionRecord, FraudAlert

__all__ = ["Transaction", "TransactionRecord", "FraudAlert"]