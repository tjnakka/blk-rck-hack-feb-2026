"""
Transaction routers:
  - POST /transactions:parse     → parse expenses into transactions
  - POST /transactions:validator  → validate transactions
  - POST /transactions:filter     → filter by temporal constraints
"""

from fastapi import APIRouter

from backend.api.v1.models.transaction import Expense, Transaction
from backend.api.v1.models.requests import ValidatorRequest, FilterRequest
from backend.api.v1.models.responses import ValidatorResponse, FilterResponse
from backend.api.v1.services.transaction_pipeline import TransactionPipeline

router = APIRouter(tags=["Transactions"])
pipeline = TransactionPipeline()


@router.post(
    "/transactions:parse",
    response_model=list[Transaction],
    summary="Parse expenses into enriched transactions",
)
async def parse(expenses: list[Expense]) -> list[Transaction]:
    """Parse raw expenses into enriched transactions (ceiling / remanent)."""
    return pipeline.parse(expenses)


@router.post(
    "/transactions:validator",
    response_model=ValidatorResponse,
    summary="Validate transactions",
)
async def validator(request: ValidatorRequest) -> ValidatorResponse:
    """Reject negative amounts and duplicates."""
    valid, invalid = pipeline.validate(request.transactions)
    return ValidatorResponse(valid=valid, invalid=invalid)


@router.post(
    "/transactions:filter",
    response_model=FilterResponse,
    summary="Filter transactions by temporal constraints",
)
async def filter_transactions(request: FilterRequest) -> FilterResponse:
    """Full pipeline → parse → validate → Q → P → K membership."""
    valid, invalid = pipeline.run(request.transactions, request.q, request.p)
    valid_filtered = pipeline.mark_k_membership(valid, request.k)
    return FilterResponse(valid=valid_filtered, invalid=invalid)
