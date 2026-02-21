"""
TaxCalculator — progressive income-tax computation.

Tax slabs (simplified, INR):
  ₹0 – ₹7,00,000        → 0 %
  ₹7,00,001 – ₹10,00,000 → 10 %
  ₹10,00,001 – ₹12,00,000 → 15 %
  ₹12,00,001 – ₹15,00,000 → 20 %
  Above ₹15,00,000        → 30 %
"""

from backend.config import TAX_SLABS
from backend.core.logging import get_logger

logger = get_logger(__name__)


class TaxCalculator:
    """Stateless calculator for Indian progressive income-tax slabs."""

    @staticmethod
    def progressive_tax(annual_income: float) -> float:
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
