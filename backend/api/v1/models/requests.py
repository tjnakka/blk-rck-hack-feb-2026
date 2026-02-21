"""
Request models for API endpoints.
"""

from pydantic import BaseModel, Field

from .transaction import Expense, Transaction
from .period import QPeriod, PPeriod, KPeriod


class ValidatorRequest(BaseModel):
    """Input for the transaction validator endpoint."""

    wage: float = Field(..., description="Monthly wage")
    transactions: list[Transaction] = Field(
        ..., description="List of enriched transactions"
    )


class FilterRequest(BaseModel):
    """Input for the temporal constraints filter endpoint."""

    q: list[QPeriod] = Field(
        default_factory=list, description="Fixed-amount override periods"
    )
    p: list[PPeriod] = Field(
        default_factory=list, description="Extra-amount addition periods"
    )
    k: list[KPeriod] = Field(
        default_factory=list, description="Evaluation grouping periods"
    )
    wage: float = Field(..., description="Monthly wage")
    transactions: list[Expense] = Field(..., description="Raw expense transactions")


class ReturnsRequest(BaseModel):
    """Input for the returns calculation endpoints (NPS and Index)."""

    age: int = Field(..., description="Current age of the investor")
    wage: float = Field(..., description="Monthly wage")
    inflation: float = Field(
        ..., description="Annual inflation rate as percentage (e.g. 5.5)"
    )
    q: list[QPeriod] = Field(
        default_factory=list, description="Fixed-amount override periods"
    )
    p: list[PPeriod] = Field(
        default_factory=list, description="Extra-amount addition periods"
    )
    k: list[KPeriod] = Field(
        default_factory=list, description="Evaluation grouping periods"
    )
    transactions: list[Expense] = Field(..., description="Raw expense transactions")
