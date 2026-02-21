"""
Test type: Unit test
Validation: q, p, and k period application logic
Command: pytest test/test_periods.py -v
"""

from backend.api.v1.services.transaction_pipeline import TransactionPipeline
from backend.api.v1.models.transaction import Transaction
from backend.api.v1.models.period import QPeriod, PPeriod, KPeriod

pipeline = TransactionPipeline()


def _txn(date: str, amount: float, ceiling: float, remanent: float) -> Transaction:
    return Transaction(date=date, amount=amount, ceiling=ceiling, remanent=remanent)


class TestApplyQPeriods:
    """Unit tests for q-period fixed amount override."""

    def test_q_replaces_remanent(self):
        txns = [_txn("2023-07-15 10:00:00", 620, 700, 80)]
        q = [QPeriod(fixed=0, start="2023-07-01 00:00:00", end="2023-07-31 23:59:59")]
        result = pipeline.apply_periods(txns, q, [])
        assert result[0].remanent == 0

    def test_q_no_match_unchanged(self):
        txns = [_txn("2023-06-15 10:00:00", 250, 300, 50)]
        q = [QPeriod(fixed=0, start="2023-07-01 00:00:00", end="2023-07-31 23:59:59")]
        result = pipeline.apply_periods(txns, q, [])
        assert result[0].remanent == 50

    def test_multiple_q_latest_start_wins(self):
        txns = [_txn("2023-07-15 10:00:00", 620, 700, 80)]
        q = [
            QPeriod(fixed=10, start="2023-07-01 00:00:00", end="2023-07-31 23:59:59"),
            QPeriod(fixed=20, start="2023-07-10 00:00:00", end="2023-07-31 23:59:59"),
        ]
        result = pipeline.apply_periods(txns, q, [])
        assert result[0].remanent == 20  # latest start wins

    def test_empty_q(self):
        txns = [_txn("2023-07-15 10:00:00", 620, 700, 80)]
        result = pipeline.apply_periods(txns, [], [])
        assert result[0].remanent == 80


class TestApplyPPeriods:
    """Unit tests for p-period extra amount addition."""

    def test_p_adds_extra(self):
        txns = [_txn("2023-10-12 20:15:30", 250, 300, 50)]
        p = [PPeriod(extra=25, start="2023-10-01 08:00:00", end="2023-12-31 19:59:59")]
        result = pipeline.apply_periods(txns, [], p)
        assert result[0].remanent == 75

    def test_p_no_match_unchanged(self):
        txns = [_txn("2023-06-15 10:00:00", 250, 300, 50)]
        p = [PPeriod(extra=25, start="2023-10-01 08:00:00", end="2023-12-31 19:59:59")]
        result = pipeline.apply_periods(txns, [], p)
        assert result[0].remanent == 50

    def test_multiple_p_extras_summed(self):
        txns = [_txn("2023-10-12 20:15:30", 250, 300, 50)]
        p = [
            PPeriod(extra=25, start="2023-10-01 08:00:00", end="2023-12-31 19:59:59"),
            PPeriod(extra=10, start="2023-10-01 00:00:00", end="2023-11-30 23:59:59"),
        ]
        result = pipeline.apply_periods(txns, [], p)
        assert result[0].remanent == 85  # 50 + 25 + 10

    def test_p_after_q_adds_on_top(self):
        """p rules should add on top of q-rule result."""
        txns = [_txn("2023-07-15 10:00:00", 620, 700, 0)]  # q already set to 0
        p = [PPeriod(extra=30, start="2023-07-01 00:00:00", end="2023-07-31 23:59:59")]
        result = pipeline.apply_periods(txns, [], p)
        assert result[0].remanent == 30  # 0 + 30


class TestGroupByKPeriods:
    """Unit tests for k-period grouping."""

    def test_spec_example(self):
        """Validate k-period grouping from the problem.md example."""
        txns = [
            _txn("2023-02-28 15:49:20", 375, 400, 25),
            _txn("2023-07-01 21:59:00", 620, 700, 0),  # after q
            _txn("2023-10-12 20:15:30", 250, 300, 75),  # after p
            _txn("2023-12-17 08:09:45", 480, 500, 45),  # after p
        ]
        k = [
            KPeriod(start="2023-01-01 00:00:00", end="2023-12-31 23:59:59"),
            KPeriod(start="2023-03-01 00:00:00", end="2023-11-30 23:59:59"),
        ]
        result = pipeline.group_by_k(txns, k)
        assert result[0][1] == 145.0  # full year: 25 + 0 + 75 + 45
        assert result[1][1] == 75.0  # Mar-Nov: 0 + 75

    def test_empty_k(self):
        txns = [_txn("2023-07-15 10:00:00", 620, 700, 80)]
        result = pipeline.group_by_k(txns, [])
        assert result == []

    def test_transaction_in_multiple_k(self):
        txns = [_txn("2023-07-15 10:00:00", 620, 700, 80)]
        k = [
            KPeriod(start="2023-01-01 00:00:00", end="2023-12-31 23:59:59"),
            KPeriod(start="2023-07-01 00:00:00", end="2023-07-31 23:59:59"),
        ]
        result = pipeline.group_by_k(txns, k)
        assert result[0][1] == 80
        assert result[1][1] == 80  # same txn in both


class TestCheckInKPeriod:
    """Unit tests for k-period membership check."""

    def test_in_period(self):
        k = [KPeriod(start="2023-01-01 00:00:00", end="2023-12-31 23:59:59")]
        txn = _txn("2023-06-15 12:00:00", 100, 100, 0)
        result = pipeline.mark_k_membership([txn], k)
        assert result[0].inKPeriod is True

    def test_not_in_period(self):
        k = [KPeriod(start="2023-07-01 00:00:00", end="2023-07-31 23:59:59")]
        txn = _txn("2023-06-15 12:00:00", 100, 100, 0)
        result = pipeline.mark_k_membership([txn], k)
        assert result[0].inKPeriod is False
