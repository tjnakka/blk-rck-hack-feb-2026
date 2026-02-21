"""
Period service: applies q, p, and k period rules to transactions.

Processing order (per spec):
  1. Calculate ceiling and remanent (done by parser_service)
  2. Apply q period rules (fixed amount override)
  3. Apply p period rules (extra amount addition)
  4. Group by k periods
"""

from backend.core.logging import get_logger
from backend.core.datetime_utils import parse_datetime, is_within_period
from backend.api.v1.models.transaction import Transaction
from backend.api.v1.models.period import QPeriod, PPeriod, KPeriod

logger = get_logger(__name__)


def apply_q_periods(
    transactions: list[Transaction], q_periods: list[QPeriod]
) -> list[Transaction]:
    """
    Apply q-period rules: if a transaction date falls within a q period,
    replace its remanent with the q period's fixed amount.

    If multiple q periods match, use the one with the latest start.
    If tied on start, use the first in the input list.
    """
    if not q_periods:
        return transactions

    result: list[Transaction] = []
    for txn in transactions:
        matching_q: QPeriod | None = None

        for q in q_periods:
            if is_within_period(txn.date, q.start, q.end):
                if matching_q is None:
                    matching_q = q
                else:
                    # Pick the one with the latest start
                    if parse_datetime(q.start) > parse_datetime(matching_q.start):
                        matching_q = q

        if matching_q is not None:
            result.append(
                Transaction(
                    date=txn.date,
                    amount=txn.amount,
                    ceiling=txn.ceiling,
                    remanent=matching_q.fixed,
                )
            )
        else:
            result.append(txn)

    return result


def apply_p_periods(
    transactions: list[Transaction], p_periods: list[PPeriod]
) -> list[Transaction]:
    """
    Apply p-period rules: if a transaction date falls within p periods,
    add the sum of all matching extras to the remanent.

    p rules add on top of any q-rule result (they don't replace).
    """
    if not p_periods:
        return transactions

    result: list[Transaction] = []
    for txn in transactions:
        total_extra = 0.0

        for p in p_periods:
            if is_within_period(txn.date, p.start, p.end):
                total_extra += p.extra

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


def group_by_k_periods(
    transactions: list[Transaction], k_periods: list[KPeriod]
) -> list[tuple[KPeriod, float]]:
    """
    For each k period, sum the remanents of all transactions
    whose dates fall within [start, end] (inclusive).

    A transaction may belong to multiple k periods.
    Returns list of (k_period, summed_remanent) in the same order as k_periods.
    """
    results: list[tuple[KPeriod, float]] = []

    for k in k_periods:
        total = 0.0
        for txn in transactions:
            if is_within_period(txn.date, k.start, k.end):
                total += txn.remanent
        results.append((k, total))

    return results


def check_in_k_period(date_str: str, k_periods: list[KPeriod]) -> bool:
    """Check if a transaction date falls within any k period."""
    return any(is_within_period(date_str, k.start, k.end) for k in k_periods)
