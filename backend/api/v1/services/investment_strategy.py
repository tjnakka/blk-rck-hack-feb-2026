"""
Investment strategy pattern with auto-discovery registry.

Each investment type encapsulates its annual rate and tax-benefit logic.
To add a new strategy (e.g. PPF, ELSS):
  1. Subclass ``InvestmentStrategy``
  2. Call ``StrategyRegistry.register("ppf", PPFStrategy)``
  — routers require **zero** changes.

Usage:
    strategy = StrategyRegistry.get("nps")
    benefit  = strategy.tax_benefit(annual_income=600_000, principal=50_000)
    rate     = strategy.rate
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import StrEnum

from backend.config import (
    NPS_RATE,
    INDEX_RATE,
    NPS_MAX_DEDUCTION,
    NPS_INCOME_PERCENT_LIMIT,
)
from backend.api.v1.services.tax_service import TaxCalculator


# ------------------------------------------------------------------
# Abstract base
# ------------------------------------------------------------------


class InvestmentStrategy(ABC):
    """Abstract base for all investment strategies."""

    rate: float

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this investment type."""

    @abstractmethod
    def tax_benefit(self, annual_income: float, principal: float) -> float:
        """
        Return the tax benefit for a given principal investment.

        Args:
            annual_income: Investor's annual income (INR).
            principal:     Amount being invested in this period (INR).

        Returns:
            Tax benefit amount (INR), or 0.0 if not applicable.
        """


# ------------------------------------------------------------------
# Concrete strategies
# ------------------------------------------------------------------


class NPSStrategy(InvestmentStrategy):
    """National Pension Scheme — 7.11 % p.a. with Section 80C/80CCD tax benefit."""

    rate = NPS_RATE

    @property
    def name(self) -> str:
        return "NPS"

    def tax_benefit(self, annual_income: float, principal: float) -> float:
        """
        NPS_Deduction = min(invested, 10 % of annual_income, ₹2,00,000)
        Tax_Benefit   = Tax(income) − Tax(income − NPS_Deduction)
        """
        nps_deduction = min(
            principal,
            NPS_INCOME_PERCENT_LIMIT * annual_income,
            NPS_MAX_DEDUCTION,
        )
        return TaxCalculator.progressive_tax(
            annual_income
        ) - TaxCalculator.progressive_tax(annual_income - nps_deduction)


class IndexStrategy(InvestmentStrategy):
    """NIFTY 50 Index Fund — 14.49 % p.a., no special tax benefit."""

    rate = INDEX_RATE

    @property
    def name(self) -> str:
        return "Index (NIFTY 50)"

    def tax_benefit(self, annual_income: float, principal: float) -> float:
        return 0.0


# ------------------------------------------------------------------
# Enum for type-safe strategy selection
# ------------------------------------------------------------------


class StrategyName(StrEnum):
    """Valid investment strategy identifiers."""

    NPS = "nps"
    INDEX = "index"


# ------------------------------------------------------------------
# Registry — O(1) lookup, zero-change extensibility
# ------------------------------------------------------------------


class StrategyRegistry:
    """
    Central registry mapping ``StrategyName`` values to strategy classes.

    Usage::

        strategy = StrategyRegistry.get(StrategyName.NPS)
    """

    _strategies: dict[StrategyName, type[InvestmentStrategy]] = {}

    @classmethod
    def register(
        cls, name: StrategyName, strategy_cls: type[InvestmentStrategy]
    ) -> None:
        """Register a strategy class under *name*."""
        cls._strategies[name] = strategy_cls

    @classmethod
    def get(cls, name: StrategyName) -> InvestmentStrategy:
        """Return a fresh instance of the strategy registered under *name*."""
        if name not in cls._strategies:
            available = ", ".join(s.value for s in cls._strategies)
            raise ValueError(f"Unknown strategy '{name}'. Available: {available}")
        return cls._strategies[name]()

    @classmethod
    def available(cls) -> list[StrategyName]:
        """Return list of registered strategy names."""
        return sorted(cls._strategies)


# -- Built-in registrations --
StrategyRegistry.register(StrategyName.NPS, NPSStrategy)
StrategyRegistry.register(StrategyName.INDEX, IndexStrategy)
