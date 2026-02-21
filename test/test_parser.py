"""
Test type: Unit test
Validation: Ceiling and remanent calculation logic
Command: pytest test/test_parser.py -v
"""

from backend.api.v1.services.transaction_pipeline import TransactionPipeline
from backend.api.v1.models.transaction import Expense

pipeline = TransactionPipeline()


class TestCalculateCeiling:
    """Unit tests for the ceiling calculation function."""

    def test_ceiling_rounds_up(self):
        assert pipeline._ceiling(250) == 300

    def test_ceiling_rounds_up_375(self):
        assert pipeline._ceiling(375) == 400

    def test_ceiling_rounds_up_620(self):
        assert pipeline._ceiling(620) == 700

    def test_ceiling_rounds_up_480(self):
        assert pipeline._ceiling(480) == 500

    def test_ceiling_exact_multiple(self):
        """Exact multiples of 100 should remain unchanged."""
        assert pipeline._ceiling(300) == 300

    def test_ceiling_zero(self):
        assert pipeline._ceiling(0) == 0

    def test_ceiling_small_amount(self):
        assert pipeline._ceiling(1) == 100

    def test_ceiling_large_amount(self):
        assert pipeline._ceiling(499999) == 500000

    def test_ceiling_decimal(self):
        assert pipeline._ceiling(250.5) == 300


class TestParseExpenses:
    """Unit tests for the parse method."""

    def test_parse_spec_example(self):
        """Validate against the spec example from requirements.md."""
        expenses = [
            Expense(date="2023-10-12 20:15:30", amount=250),
            Expense(date="2023-02-28 15:49:20", amount=375),
            Expense(date="2023-07-01 21:59:00", amount=620),
            Expense(date="2023-12-17 08:09:45", amount=480),
        ]
        result = pipeline.parse(expenses)

        assert len(result) == 4
        assert result[0].ceiling == 300 and result[0].remanent == 50
        assert result[1].ceiling == 400 and result[1].remanent == 25
        assert result[2].ceiling == 700 and result[2].remanent == 80
        assert result[3].ceiling == 500 and result[3].remanent == 20

    def test_parse_empty_list(self):
        assert pipeline.parse([]) == []

    def test_parse_preserves_dates(self):
        expenses = [Expense(date="2023-01-01 00:00:00", amount=150)]
        result = pipeline.parse(expenses)
        assert result[0].date == "2023-01-01 00:00:00"
