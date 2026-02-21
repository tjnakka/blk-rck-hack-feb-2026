"""
Returns service: calculates investment returns with compound interest
and inflation adjustment.

Formulas:
  A = P * (1 + r/n)^(n*t)   where n=1 (annual compounding)
  A_real = A / (1 + inflation)^t

Investment options:
  - NPS: 7.11% annual, with tax benefit
  - Index (NIFTY 50): 14.49% annual, no tax benefit
"""

from backend.config import NPS_RATE, INDEX_RATE, RETIREMENT_AGE, MIN_INVESTMENT_YEARS
from backend.core.logging import get_logger
from backend.api.v1.models.period import KPeriod
from backend.api.v1.models.responses import SavingsByDate
from backend.api.v1.services.tax_service import calculate_nps_tax_benefit

logger = get_logger(__name__)


def calculate_investment_years(age: int) -> int:
    """
    Calculate the number of years to invest until retirement.
    Minimum of MIN_INVESTMENT_YEARS (5) if already at or beyond retirement age.
    """
    return max(RETIREMENT_AGE - age, MIN_INVESTMENT_YEARS)


def compound_interest(principal: float, rate: float, years: int) -> float:
    """
    Calculate compound interest with annual compounding (n=1).
    A = P * (1 + r)^t
    """
    return principal * ((1 + rate) ** years)


def inflation_adjust(amount: float, inflation_rate: float, years: int) -> float:
    """
    Adjust a future amount for inflation.
    A_real = A / (1 + inflation)^t

    Args:
        amount: Future nominal amount.
        inflation_rate: Annual inflation as a decimal (e.g. 0.055 for 5.5%).
        years: Number of years.
    """
    return amount / ((1 + inflation_rate) ** years)


def calculate_returns(
    k_period_sums: list[tuple[KPeriod, float]],
    rate: float,
    age: int,
    inflation_pct: float,
    annual_income: float,
    is_nps: bool = False,
) -> list[SavingsByDate]:
    """
    Calculate returns for each k period.

    Args:
        k_period_sums: List of (KPeriod, summed_remanent) pairs.
        rate: Annual interest rate (decimal).
        age: Current age of investor.
        inflation_pct: Inflation rate as percentage (e.g. 5.5).
        annual_income: Annual income for tax calculations.
        is_nps: Whether this is NPS (for tax benefit calculation).

    Returns:
        List of SavingsByDate results, one per k period.
    """
    years = calculate_investment_years(age)
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

        future_value = compound_interest(principal, rate, years)
        real_value = inflation_adjust(future_value, inflation_rate, years)
        profit = round(real_value - principal, 2)

        tax_benefit = 0.0
        if is_nps:
            tax_benefit = round(calculate_nps_tax_benefit(annual_income, principal), 2)

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
        f"Calculated returns for {len(results)} k periods (rate={rate}, years={years})"
    )
    return results
