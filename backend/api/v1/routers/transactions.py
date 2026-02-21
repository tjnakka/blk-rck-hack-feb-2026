"""
Transaction routers:
  - POST /transactions:parse     → parse expenses into transactions
  - POST /transactions:validator  → validate transactions
  - POST /transactions:filter     → filter by temporal constraints
"""

from fastapi import APIRouter

from backend.core.logging import get_logger
from backend.api.v1.models.transaction import (
    Expense,
    Transaction,
    InvalidTransaction,
    ValidFilteredTransaction,
)
from backend.api.v1.models.requests import ValidatorRequest, FilterRequest
from backend.api.v1.models.responses import ValidatorResponse, FilterResponse
from backend.api.v1.services.parser_service import parse_expenses
from backend.api.v1.services.validator_service import validate_transactions
from backend.api.v1.services.period_service import (
    apply_q_periods,
    apply_p_periods,
    check_in_k_period,
)

logger = get_logger(__name__)

router = APIRouter(tags=["Transactions"])


@router.post(
    "/transactions:parse",
    response_model=list[Transaction],
    summary="Parse expenses into enriched transactions",
)
async def parse(expenses: list[Expense]) -> list[Transaction]:
    """
    Receives a list of Expenses and returns transactions enriched with
    ceiling (next multiple of 100) and remanent (ceiling - amount).
    """
    return parse_expenses(expenses)


@router.post(
    "/transactions:validator",
    response_model=ValidatorResponse,
    summary="Validate transactions",
)
async def validator(request: ValidatorRequest) -> ValidatorResponse:
    """
    Validates transactions: rejects negative amounts and duplicates.
    Returns valid and invalid transaction lists.
    """
    valid, invalid = validate_transactions(request.transactions)
    return ValidatorResponse(valid=valid, invalid=invalid)


@router.post(
    "/transactions:filter",
    response_model=FilterResponse,
    summary="Filter transactions by temporal constraints",
)
async def filter_transactions(request: FilterRequest) -> FilterResponse:
    """
    Full pipeline:
      1. Parse expenses → transactions (ceiling/remanent)
      2. Validate (negative amounts, duplicates)
      3. Apply q periods (fixed override)
      4. Apply p periods (extra addition)
      5. Check k-period membership

    Returns valid (with inKPeriod flag) and invalid transactions.
    """
    # Step 1: Parse
    parsed = parse_expenses(request.transactions)

    # Step 2: Validate
    valid, invalid = validate_transactions(parsed)

    # Step 3: Apply q periods
    valid = apply_q_periods(valid, request.q)

    # Step 4: Apply p periods
    valid = apply_p_periods(valid, request.p)

    # Step 5: Check k-period membership and build response
    valid_filtered = [
        ValidFilteredTransaction(
            date=txn.date,
            amount=txn.amount,
            ceiling=txn.ceiling,
            remanent=txn.remanent,
            inKPeriod=check_in_k_period(txn.date, request.k),
        )
        for txn in valid
    ]

    return FilterResponse(valid=valid_filtered, invalid=invalid)
