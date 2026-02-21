"""
Transaction-related Pydantic models.
Defines the core data structures for expenses and enriched transactions.
"""

from pydantic import BaseModel, Field


class Expense(BaseModel):
    """Raw expense input from the user."""

    date: str = Field(
        ..., description="Datetime string in 'YYYY-MM-DD HH:mm:ss' format"
    )
    amount: float = Field(..., description="Expense amount")


class Transaction(BaseModel):
    """Enriched transaction with ceiling and remanent calculated."""

    date: str
    amount: float
    ceiling: float
    remanent: float


class InvalidTransaction(BaseModel):
    """A transaction that failed validation, with an error message."""

    date: str
    amount: float
    ceiling: float | None = None
    remanent: float | None = None
    message: str = Field(..., description="Explanation of the validation error")


class ValidFilteredTransaction(BaseModel):
    """A valid transaction after temporal filtering, with k-period membership."""

    date: str
    amount: float
    ceiling: float
    remanent: float
    inKPeriod: bool = Field(
        ..., description="Whether this transaction falls in any k period"
    )
