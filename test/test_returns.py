"""
Test type: Unit test
Validation: Compound interest, inflation adjustment, and returns calculation
Command: pytest test/test_returns.py -v
"""

from backend.api.v1.services.returns_service import (
    calculate_investment_years,
    compound_interest,
    inflation_adjust,
    calculate_returns,
)
from backend.api.v1.models.period import KPeriod


class TestInvestmentYears:
    """Unit tests for investment years calculation."""

    def test_young_investor(self):
        assert calculate_investment_years(29) == 31

    def test_retirement_age(self):
        """At retirement age, use minimum 5 years."""
        assert calculate_investment_years(60) == 5

    def test_beyond_retirement(self):
        assert calculate_investment_years(65) == 5

    def test_very_young(self):
        assert calculate_investment_years(20) == 40


class TestCompoundInterest:
    """Unit tests for compound interest calculation."""

    def test_nps_spec_example(self):
        """145 invested at 7.11% for 31 years."""
        result = compound_interest(145, 0.0711, 31)
        assert abs(result - 1219.45) < 1.0  # within ±1 of spec

    def test_zero_principal(self):
        assert compound_interest(0, 0.0711, 31) == 0

    def test_zero_years(self):
        assert compound_interest(145, 0.0711, 0) == 145


class TestInflationAdjust:
    """Unit tests for inflation adjustment."""

    def test_nps_spec_example(self):
        """1219.45 adjusted for 5.5% inflation over 31 years."""
        future = compound_interest(145, 0.0711, 31)
        real = inflation_adjust(future, 0.055, 31)
        assert abs(real - 231.9) < 1.0  # within ±1 of spec

    def test_zero_inflation(self):
        assert inflation_adjust(1000, 0, 10) == 1000


class TestCalculateReturns:
    """Unit tests for the full returns pipeline."""

    def test_nps_spec_example(self):
        """Validate against the spec example from requirements.md."""
        k_period_sums = [
            (KPeriod(start="2023-01-01 00:00:00", end="2023-12-31 23:59:59"), 145.0),
            (KPeriod(start="2023-03-01 00:00:00", end="2023-11-30 23:59:59"), 75.0),
        ]
        result = calculate_returns(
            k_period_sums=k_period_sums,
            rate=0.0711,
            age=29,
            inflation_pct=5.5,
            annual_income=600_000,
            is_nps=True,
        )

        assert len(result) == 2
        assert result[0].amount == 145.0
        assert result[0].profit == 86.88
        assert result[0].taxBenefit == 0.0
        assert result[1].amount == 75.0
        assert result[1].profit == 44.94
        assert result[1].taxBenefit == 0.0

    def test_index_no_tax_benefit(self):
        k_period_sums = [
            (KPeriod(start="2023-01-01 00:00:00", end="2023-12-31 23:59:59"), 145.0),
        ]
        result = calculate_returns(
            k_period_sums=k_period_sums,
            rate=0.1449,
            age=29,
            inflation_pct=5.5,
            annual_income=600_000,
            is_nps=False,
        )
        assert result[0].taxBenefit == 0.0
        assert result[0].profit > 0
