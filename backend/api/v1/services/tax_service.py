"""
Tax service: calculates income tax and NPS tax benefits.

Tax slabs (simplified, INR):
  ₹0 – ₹7,00,000        → 0%
  ₹7,00,001 – ₹10,00,000 → 10%
  ₹10,00,001 – ₹12,00,000 → 15%
  ₹12,00,001 – ₹15,00,000 → 20%
  Above ₹15,00,000        → 30%
"""

from backend.config import TAX_SLABS, NPS_MAX_DEDUCTION, NPS_INCOME_PERCENT_LIMIT
from backend.core.logging import get_logger

logger = get_logger(__name__)


def calculate_tax(annual_income: float) -> float:
    """
    Calculate total income tax based on simplified progressive slabs.

    Args:
        annual_income: Total annual income in INR.

    Returns:
        Total tax amount in INR.
    """
    tax = 0.0

    for lower, upper, rate in TAX_SLABS:
        if annual_income <= lower:
            break
        if upper is None:
            taxable = annual_income - lower
        else:
            taxable = min(annual_income, upper) - lower
        tax += taxable * rate

    return tax


def calculate_nps_tax_benefit(annual_income: float, invested: float) -> float:
    """
    Calculate the tax benefit from NPS investment.

    NPS_Deduction = min(invested, 10% of annual_income, ₹2,00,000)
    Tax_Benefit = Tax(income) - Tax(income - NPS_Deduction)

    Args:
        annual_income: Total annual income in INR.
        invested: Total amount invested in NPS.

    Returns:
        Tax benefit amount in INR.
    """
    nps_deduction = min(
        invested,
        NPS_INCOME_PERCENT_LIMIT * annual_income,
        NPS_MAX_DEDUCTION,
    )

    tax_without_nps = calculate_tax(annual_income)
    tax_with_nps = calculate_tax(annual_income - nps_deduction)

    benefit = tax_without_nps - tax_with_nps
    logger.info(
        f"NPS tax benefit: income={annual_income}, invested={invested}, "
        f"deduction={nps_deduction}, benefit={benefit}"
    )
    return benefit
