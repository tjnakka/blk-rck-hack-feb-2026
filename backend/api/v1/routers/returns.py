"""
Returns routers:
  - POST /returns:nps    → NPS investment returns with tax benefit
  - POST /returns:index  → Index fund (NIFTY 50) investment returns
"""

from fastapi import APIRouter

from backend.config import NPS_RATE, INDEX_RATE
from backend.core.logging import get_logger
from backend.api.v1.models.requests import ReturnsRequest
from backend.api.v1.models.responses import ReturnsResponse
from backend.api.v1.services.parser_service import parse_expenses
from backend.api.v1.services.validator_service import validate_transactions
from backend.api.v1.services.period_service import (
    apply_q_periods,
    apply_p_periods,
    group_by_k_periods,
)
from backend.api.v1.services.returns_service import calculate_returns

logger = get_logger(__name__)

router = APIRouter(tags=["Returns"])


def _process_returns(
    request: ReturnsRequest, rate: float, is_nps: bool
) -> ReturnsResponse:
    """
    Shared pipeline for both NPS and Index returns:
      1. Parse expenses → transactions
      2. Validate (reject negatives, duplicates)
      3. Apply q periods
      4. Apply p periods
      5. Group by k periods
      6. Calculate compound returns with inflation adjustment
    """
    # Step 1: Parse
    parsed = parse_expenses(request.transactions)

    # Step 2: Validate
    valid, _ = validate_transactions(parsed)

    # Step 3-4: Apply period rules
    valid = apply_q_periods(valid, request.q)
    valid = apply_p_periods(valid, request.p)

    # Totals from valid transactions (before k grouping)
    total_amount = sum(txn.amount for txn in valid)
    total_ceiling = sum(txn.ceiling for txn in valid)

    # Step 5: Group by k periods
    k_period_sums = group_by_k_periods(valid, request.k)

    # Step 6: Calculate returns
    annual_income = request.wage * 12  # wage is monthly
    savings = calculate_returns(
        k_period_sums=k_period_sums,
        rate=rate,
        age=request.age,
        inflation_pct=request.inflation,
        annual_income=annual_income,
        is_nps=is_nps,
    )

    return ReturnsResponse(
        totalTransactionAmount=total_amount,
        totalCeiling=total_ceiling,
        savingsByDates=savings,
    )


@router.post(
    "/returns:nps",
    response_model=ReturnsResponse,
    summary="Calculate NPS investment returns",
)
async def returns_nps(request: ReturnsRequest) -> ReturnsResponse:
    """
    Calculate returns using the National Pension Scheme (NPS) rate (7.11%).
    Includes tax benefit calculation based on simplified tax slabs.
    """
    return _process_returns(request, NPS_RATE, is_nps=True)


@router.post(
    "/returns:index",
    response_model=ReturnsResponse,
    summary="Calculate Index Fund (NIFTY 50) returns",
)
async def returns_index(request: ReturnsRequest) -> ReturnsResponse:
    """
    Calculate returns using the NIFTY 50 Index Fund rate (14.49%).
    No tax benefit applies to index fund investments.
    """
    return _process_returns(request, INDEX_RATE, is_nps=False)
