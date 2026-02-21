"""
Period-related Pydantic models.

Hierarchy:
  BasePeriod        — shared start/end fields
  ├── QPeriod       — fixed-amount override
  ├── PPeriod       — extra-amount addition
  └── KPeriod       — evaluation grouping
"""

from pydantic import BaseModel, Field


class BasePeriod(BaseModel):
    """Common base for all temporal periods."""

    start: str = Field(..., description="Period start datetime (inclusive)")
    end: str = Field(..., description="Period end datetime (inclusive)")


class QPeriod(BasePeriod):
    """A period during which the remanent is replaced with a fixed amount."""

    fixed: float = Field(..., description="Fixed remanent amount during this period")


class PPeriod(BasePeriod):
    """A period during which an extra amount is added to the remanent."""

    extra: float = Field(..., description="Extra amount added to remanent")


class KPeriod(BasePeriod):
    """An evaluation grouping period for summing remanents."""
