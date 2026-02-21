"""
Test type: Unit test
Validation: Transaction validation rules (negative amounts, duplicates)
Command: pytest test/test_validator.py -v
"""

from backend.api.v1.services.transaction_pipeline import TransactionPipeline
from backend.api.v1.models.transaction import Transaction

pipeline = TransactionPipeline()


def _txn(
    date: str, amount: float, ceiling: float = 0, remanent: float = 0
) -> Transaction:
    return Transaction(date=date, amount=amount, ceiling=ceiling, remanent=remanent)


class TestValidateTransactions:
    """Unit tests for the validate method."""

    def test_all_valid(self):
        txns = [
            _txn("2023-01-15 10:30:00", 2000, 300, 50),
            _txn("2023-03-20 14:45:00", 3500, 400, 70),
        ]
        valid, invalid = pipeline.validate(txns)
        assert len(valid) == 2
        assert len(invalid) == 0

    def test_negative_amount_rejected(self):
        txns = [
            _txn("2023-01-15 10:30:00", 2000, 300, 50),
            _txn("2023-07-10 09:15:00", -250, 200, 30),
        ]
        valid, invalid = pipeline.validate(txns)
        assert len(valid) == 1
        assert len(invalid) == 1
        assert invalid[0].message == "Negative amounts are not allowed"

    def test_duplicate_date_rejected(self):
        txns = [
            _txn("2023-01-15 10:30:00", 2000, 300, 50),
            _txn("2023-01-15 10:30:00", 3000, 300, 50),
        ]
        valid, invalid = pipeline.validate(txns)
        assert len(valid) == 1
        assert len(invalid) == 1
        assert invalid[0].message == "Duplicate transaction"

    def test_spec_example(self):
        """Validate against the spec example from requirements.md."""
        txns = [
            _txn("2023-01-15 10:30:00", 2000, 300, 50),
            _txn("2023-03-20 14:45:00", 3500, 400, 70),
            _txn("2023-06-10 09:15:00", 1500, 200, 30),
            _txn("2023-07-10 09:15:00", -250, 200, 30),
        ]
        valid, invalid = pipeline.validate(txns)
        assert len(valid) == 3
        assert len(invalid) == 1
        assert invalid[0].amount == -250

    def test_empty_list(self):
        valid, invalid = pipeline.validate([])
        assert valid == []
        assert invalid == []
