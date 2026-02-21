"""
ReturnsCalculator — encapsulates compound-interest investment returns
with inflation adjustment.

Formulas:
  A      = P × (1 + r)^t           (annual compounding, n = 1)
  A_real = A / (1 + inflation)^t

The three helper functions (investment years, compound interest, and
inflation adjustment) are private implementation details of the single
public ``calculate()`` method.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.config import RETIREMENT_AGE, MIN_INVESTMENT_YEARS
from backend.core.logging import get_logger
from backend.api.v1.models.period import KPeriod
from backend.api.v1.models.responses import SavingsByDate

if TYPE_CHECKING:
    from backend.api.v1.services.investment_strategy import InvestmentStrategy

logger = get_logger(__name__)


class ReturnsCalculator:
    """
    Single-responsibility class for investment-return calculations.

    Public API:
        ``calculate(k_period_sums, strategy, age, inflation_pct, annual_income)``
    """

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _investment_years(age: int) -> int:
        """Years until retirement, minimum ``MIN_INVESTMENT_YEARS``."""
        return max(RETIREMENT_AGE - age, MIN_INVESTMENT_YEARS)

    @staticmethod
    def _compound(principal: float, rate: float, years: int) -> float:
        """A = P × (1 + r)^t"""
        return principal * ((1 + rate) ** years)

    @staticmethod
    def _inflation_adjust(amount: float, inflation_rate: float, years: int) -> float:
        """A_real = A / (1 + inflation)^t"""
        return amount / ((1 + inflation_rate) ** years)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def calculate(
        self,
        k_period_sums: list[tuple[KPeriod, float]],
        strategy: "InvestmentStrategy",
        age: int,
        inflation_pct: float,
        annual_income: float,
    ) -> list[SavingsByDate]:
        """
        Calculate returns for each K period using *strategy*.

        Args:
            k_period_sums: ``[(KPeriod, summed_remanent), …]``
            strategy:      Provides ``rate`` and ``tax_benefit()``.
            age:           Current age of investor.
            inflation_pct: Inflation rate as a percentage (e.g. 5.5).
            annual_income: Annual income for tax calculations (INR).

        Returns:
            One ``SavingsByDate`` per K period.
        """
        years = self._investment_years(age)
        inflation_rate = inflation_pct / 100.0
        results: list[SavingsByDate] = []

        for k_period, principal in k_period_sums:
            if principal <= 0:
                results.append(
                    SavingsByDate(
                        start=k_period.start,
                        end=k_period.end,
                        amount=principal,
                        profit=0.0,
                        taxBenefit=0.0,
                    )
                )
                continue

            future_value = self._compound(principal, strategy.rate, years)
            real_value = self._inflation_adjust(future_value, inflation_rate, years)
            profit = round(real_value - principal, 2)
            tax_benefit = round(strategy.tax_benefit(annual_income, principal), 2)

            results.append(
                SavingsByDate(
                    start=k_period.start,
                    end=k_period.end,
                    amount=principal,
                    profit=profit,
                    taxBenefit=tax_benefit,
                )
            )

        logger.info(
            "Calculated returns for %d k periods (strategy=%s, rate=%s, years=%d)",
            len(results),
            strategy.name,
            strategy.rate,
            years,
        )
        return results
