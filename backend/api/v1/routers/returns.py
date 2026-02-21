"""
Returns routers:
  - POST /returns:nps    → NPS investment returns with tax benefit
  - POST /returns:index  → Index fund (NIFTY 50) investment returns
"""

from fastapi import APIRouter

from backend.api.v1.models.requests import ReturnsRequest
from backend.api.v1.models.responses import ReturnsResponse
from backend.api.v1.services.transaction_pipeline import TransactionPipeline
from backend.api.v1.services.returns_service import ReturnsCalculator
from backend.api.v1.services.investment_strategy import StrategyRegistry, StrategyName

router = APIRouter(tags=["Returns"])
pipeline = TransactionPipeline()
calculator = ReturnsCalculator()


def _process_returns(
    request: ReturnsRequest, strategy_name: StrategyName
) -> ReturnsResponse:
    """Shared pipeline for all investment strategies."""
    strategy = StrategyRegistry.get(strategy_name)
    valid, _ = pipeline.run(request.transactions, request.q, request.p)

    total_amount = sum(txn.amount for txn in valid)
    total_ceiling = sum(txn.ceiling for txn in valid)
    k_period_sums = pipeline.group_by_k(valid, request.k)

    savings = calculator.calculate(
        k_period_sums=k_period_sums,
        strategy=strategy,
        age=request.age,
        inflation_pct=request.inflation,
        annual_income=request.wage * 12,
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
    """NPS (7.11 %) with tax benefit."""
    return _process_returns(request, StrategyName.NPS)


@router.post(
    "/returns:index",
    response_model=ReturnsResponse,
    summary="Calculate Index Fund (NIFTY 50) returns",
)
async def returns_index(request: ReturnsRequest) -> ReturnsResponse:
    """NIFTY 50 Index Fund (14.49 %), no tax benefit."""
    return _process_returns(request, StrategyName.INDEX)
