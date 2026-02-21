"""
Period-related Pydantic models.
Defines q (fixed override), p (extra addition), and k (evaluation grouping) periods.
"""

from pydantic import BaseModel, Field


class QPeriod(BaseModel):
    """A period during which the remanent is replaced with a fixed amount."""

    fixed: float = Field(..., description="Fixed remanent amount during this period")
    start: str = Field(..., description="Period start datetime (inclusive)")
    end: str = Field(..., description="Period end datetime (inclusive)")


class PPeriod(BaseModel):
    """A period during which an extra amount is added to the remanent."""

    extra: float = Field(..., description="Extra amount added to remanent")
    start: str = Field(..., description="Period start datetime (inclusive)")
    end: str = Field(..., description="Period end datetime (inclusive)")


class KPeriod(BaseModel):
    """An evaluation grouping period for summing remanents."""

    start: str = Field(..., description="Period start datetime (inclusive)")
    end: str = Field(..., description="Period end datetime (inclusive)")
