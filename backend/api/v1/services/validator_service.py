"""
Validator service: validates transactions for negative amounts and duplicates.

Validation rules:
  1. Negative amounts → invalid with message "Negative amounts are not allowed"
  2. Duplicate dates → invalid with message "Duplicate transaction"
  3. All else → valid
"""

from backend.core.logging import get_logger
from backend.api.v1.models.transaction import Transaction, InvalidTransaction

logger = get_logger(__name__)


def validate_transactions(
    transactions: list[Transaction],
) -> tuple[list[Transaction], list[InvalidTransaction]]:
    """
    Validate a list of transactions.

    Returns:
        (valid, invalid) tuple of transaction lists.
    """
    logger.info(f"Validating {len(transactions)} transactions")

    valid: list[Transaction] = []
    invalid: list[InvalidTransaction] = []
    seen_dates: set[str] = set()

    for txn in transactions:
        # Rule 1: Negative amounts
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

        # Rule 2: Duplicate dates
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

    logger.info(f"Validation complete: {len(valid)} valid, {len(invalid)} invalid")
    return valid, invalid
