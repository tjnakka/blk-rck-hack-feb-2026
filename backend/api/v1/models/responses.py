"""
Response models for API endpoints.
"""

from pydantic import BaseModel, Field

from .transaction import Transaction, InvalidTransaction, ValidFilteredTransaction


class ValidatorResponse(BaseModel):
    """Output from the transaction validator endpoint."""

    valid: list[Transaction]
    invalid: list[InvalidTransaction]


class FilterResponse(BaseModel):
    """Output from the temporal constraints filter endpoint."""

    valid: list[ValidFilteredTransaction]
    invalid: list[InvalidTransaction]


class SavingsByDate(BaseModel):
    """Investment results for a single k period."""

    start: str
    end: str
    amount: float = Field(..., description="Sum of remanents in this period")
    profit: float = Field(..., description="Inflation-adjusted profit")
    taxBenefit: float = Field(0.0, description="Tax benefit (NPS only, 0 for index)")


class ReturnsResponse(BaseModel):
    """Output from the returns calculation endpoints."""

    totalTransactionAmount: float = Field(
        ..., description="Sum of valid transaction amounts"
    )
    totalCeiling: float = Field(..., description="Sum of valid transaction ceilings")
    savingsByDates: list[SavingsByDate]


class PerformanceResponse(BaseModel):
    """Output from the performance endpoint."""

    time: str = Field(..., description="Server uptime in HH:mm:ss.SSS format")
    memory: str = Field(..., description="Memory usage in MB, e.g. '25.11 MB'")
    threads: int = Field(..., description="Number of active threads")
