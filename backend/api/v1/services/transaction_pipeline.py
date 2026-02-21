"""
TransactionPipeline — single class consolidating parsing, validation,
and period-application logic that was previously spread across
parser_service, validator_service, and period_service.

Usage:
    pipeline = TransactionPipeline()
    valid, invalid = pipeline.run(expenses, q_periods, p_periods)
    filtered       = pipeline.mark_k_membership(valid, k_periods)
    grouped        = pipeline.group_by_k(valid, k_periods)
"""

from __future__ import annotations

import math
from datetime import datetime
from typing import Callable

from backend.config import CEILING_MULTIPLE
from backend.core.logging import get_logger
from backend.core.datetime_utils import parse_datetime
from backend.api.v1.models.transaction import (
    Expense,
    Transaction,
    InvalidTransaction,
    ValidFilteredTransaction,
)
from backend.api.v1.models.period import QPeriod, PPeriod, KPeriod

logger = get_logger(__name__)


class TransactionPipeline:
    """
    Encapsulates the full parse → validate → period-adjust pipeline.

    Design patterns used:
      • Template Method — ``_apply_transform`` provides the skeleton for
        iterating transactions and conditionally modifying remanent; Q and P
        differ only in the transform function.
      • Facade — ``run()`` exposes a single call replacing the duplicated
        multi-step orchestration that lived in two separate routers.
    """

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _ceiling(amount: float) -> float:
        """Round *amount* up to the next multiple of ``CEILING_MULTIPLE``."""
        return math.ceil(amount / CEILING_MULTIPLE) * CEILING_MULTIPLE

    def parse(self, expenses: list[Expense]) -> list[Transaction]:
        """Transform raw expenses into enriched transactions."""
        logger.info("Parsing %d expenses", len(expenses))
        return [
            Transaction(
                date=e.date,
                amount=e.amount,
                ceiling=(c := self._ceiling(e.amount)),
                remanent=c - e.amount,
            )
            for e in expenses
        ]

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @staticmethod
    def validate(
        transactions: list[Transaction],
    ) -> tuple[list[Transaction], list[InvalidTransaction]]:
        """
        Validate transactions.

        Rules:
          1. Negative amounts → rejected.
          2. Duplicate dates  → rejected (first occurrence kept).
        """
        logger.info("Validating %d transactions", len(transactions))
        valid: list[Transaction] = []
        invalid: list[InvalidTransaction] = []
        seen_dates: set[str] = set()

        for txn in transactions:
            if txn.amount < 0:
                invalid.append(
                    InvalidTransaction(
                        date=txn.date,
                        amount=txn.amount,
                        ceiling=txn.ceiling,
                        remanent=txn.remanent,
                        message="Negative amounts are not allowed",
                    )
                )
                continue

            if txn.date in seen_dates:
                invalid.append(
                    InvalidTransaction(
                        date=txn.date,
                        amount=txn.amount,
                        ceiling=txn.ceiling,
                        remanent=txn.remanent,
                        message="Duplicate transaction",
                    )
                )
                continue

            seen_dates.add(txn.date)
            valid.append(txn)

        logger.info(
            "Validation complete: %d valid, %d invalid", len(valid), len(invalid)
        )
        return valid, invalid

    # ------------------------------------------------------------------
    # Period application (Template Method)
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_transform(
        transactions: list[Transaction],
        transform: Callable[[Transaction, datetime], float | None],
    ) -> list[Transaction]:
        """
        Generic iterator for period transforms.

        *transform(txn, txn_dt)* returns a new remanent value if the
        transaction should be modified, or ``None`` to keep it unchanged.
        """
        result: list[Transaction] = []
        for txn in transactions:
            txn_dt = parse_datetime(txn.date)
            new_remanent = transform(txn, txn_dt)
            if new_remanent is not None:
                result.append(
                    Transaction(
                        date=txn.date,
                        amount=txn.amount,
                        ceiling=txn.ceiling,
                        remanent=new_remanent,
                    )
                )
            else:
                result.append(txn)
        return result

    def apply_periods(
        self,
        transactions: list[Transaction],
        q_periods: list[QPeriod],
        p_periods: list[PPeriod],
    ) -> list[Transaction]:
        """Apply Q-period overrides then P-period additions in order."""
        txns = self._apply_q(transactions, q_periods)
        txns = self._apply_p(txns, p_periods)
        return txns

    # -- Q transform ---------------------------------------------------

    @staticmethod
    def _apply_q(
        transactions: list[Transaction], q_periods: list[QPeriod]
    ) -> list[Transaction]:
        """
        Replace remanent with the Q period's *fixed* value.
        Priority: latest start wins (sorted descending, first match taken).
        """
        if not q_periods:
            return transactions

        # Pre-parse once: (start_dt, end_dt, fixed), sorted desc by start
        parsed = sorted(
            [
                (parse_datetime(q.start), parse_datetime(q.end), q.fixed)
                for q in q_periods
            ],
            key=lambda t: t[0],
            reverse=True,
        )

        result: list[Transaction] = []
        for txn in transactions:
            txn_dt = parse_datetime(txn.date)
            match: float | None = None
            for start_dt, end_dt, fixed in parsed:
                if start_dt <= txn_dt <= end_dt:
                    match = fixed
                    break
            if match is not None:
                result.append(
                    Transaction(
                        date=txn.date,
                        amount=txn.amount,
                        ceiling=txn.ceiling,
                        remanent=match,
                    )
                )
            else:
                result.append(txn)
        return result

    # -- P transform ---------------------------------------------------

    @staticmethod
    def _apply_p(
        transactions: list[Transaction], p_periods: list[PPeriod]
    ) -> list[Transaction]:
        """
        Add the sum of all matching P period *extra* values to remanent.
        All matching periods contribute (additive).
        """
        if not p_periods:
            return transactions

        parsed = [
            (parse_datetime(p.start), parse_datetime(p.end), p.extra) for p in p_periods
        ]

        result: list[Transaction] = []
        for txn in transactions:
            txn_dt = parse_datetime(txn.date)
            total_extra = sum(
                extra
                for start_dt, end_dt, extra in parsed
                if start_dt <= txn_dt <= end_dt
            )
            if total_extra > 0:
                result.append(
                    Transaction(
                        date=txn.date,
                        amount=txn.amount,
                        ceiling=txn.ceiling,
                        remanent=txn.remanent + total_extra,
                    )
                )
            else:
                result.append(txn)
        return result

    # ------------------------------------------------------------------
    # K-period operations (pre-parsed datetimes — O(n+k) not O(n×k))
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_k_periods(
        k_periods: list[KPeriod],
    ) -> list[tuple[datetime, datetime, KPeriod]]:
        """Pre-parse k-period boundaries once."""
        return [(parse_datetime(k.start), parse_datetime(k.end), k) for k in k_periods]

    def group_by_k(
        self, transactions: list[Transaction], k_periods: list[KPeriod]
    ) -> list[tuple[KPeriod, float]]:
        """Sum remanents per K period. A transaction may belong to multiple."""
        parsed_ks = self._parse_k_periods(k_periods)
        results: list[tuple[KPeriod, float]] = []

        for k_start, k_end, k in parsed_ks:
            total = 0.0
            for txn in transactions:
                txn_dt = parse_datetime(txn.date)
                if k_start <= txn_dt <= k_end:
                    total += txn.remanent
            results.append((k, total))

        return results

    def mark_k_membership(
        self,
        transactions: list[Transaction],
        k_periods: list[KPeriod],
    ) -> list[ValidFilteredTransaction]:
        """Tag each transaction with whether it falls in any K period."""
        parsed_ks = self._parse_k_periods(k_periods)

        return [
            ValidFilteredTransaction(
                date=txn.date,
                amount=txn.amount,
                ceiling=txn.ceiling,
                remanent=txn.remanent,
                inKPeriod=any(
                    k_start <= parse_datetime(txn.date) <= k_end
                    for k_start, k_end, _ in parsed_ks
                ),
            )
            for txn in transactions
        ]

    # ------------------------------------------------------------------
    # Full pipeline facade
    # ------------------------------------------------------------------

    def run(
        self,
        expenses: list[Expense],
        q_periods: list[QPeriod],
        p_periods: list[PPeriod],
    ) -> tuple[list[Transaction], list[InvalidTransaction]]:
        """
        Execute the complete pipeline:
          1. Parse expenses → transactions
          2. Validate (negatives, duplicates)
          3. Apply Q periods (fixed override)
          4. Apply P periods (extra addition)

        Returns ``(valid, invalid)`` ready for K-period operations.
        """
        parsed = self.parse(expenses)
        valid, invalid = self.validate(parsed)
        valid = self.apply_periods(valid, q_periods, p_periods)
        return valid, invalid
