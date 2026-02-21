"""
Parser service: calculates ceiling and remanent for expenses.

Ceiling = next multiple of 100 (rounded up).
Remanent = ceiling - amount (the micro-savings amount).
"""

import math

from backend.config import CEILING_MULTIPLE
from backend.core.logging import get_logger
from backend.api.v1.models.transaction import Expense, Transaction

logger = get_logger(__name__)


def calculate_ceiling(amount: float) -> float:
    """Round up to the next multiple of CEILING_MULTIPLE (100)."""
    return math.ceil(amount / CEILING_MULTIPLE) * CEILING_MULTIPLE


def parse_expenses(expenses: list[Expense]) -> list[Transaction]:
    """
    Transform a list of raw expenses into enriched transactions.

    For each expense:
      - ceiling = next multiple of 100 above amount
      - remanent = ceiling - amount
    """
    logger.info(f"Parsing {len(expenses)} expenses")
    transactions: list[Transaction] = []

    for expense in expenses:
        ceiling = calculate_ceiling(expense.amount)
        remanent = ceiling - expense.amount
        transactions.append(
            Transaction(
                date=expense.date,
                amount=expense.amount,
                ceiling=ceiling,
                remanent=remanent,
            )
        )

    return transactions
