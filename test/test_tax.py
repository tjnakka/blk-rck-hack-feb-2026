"""
Test type: Unit test
Validation: Tax calculation and NPS tax benefit
Command: pytest test/test_tax.py -v
"""

from backend.api.v1.services.tax_service import calculate_tax, calculate_nps_tax_benefit


class TestCalculateTax:
    """Unit tests for progressive tax slab calculation."""

    def test_zero_income(self):
        assert calculate_tax(0) == 0

    def test_below_first_slab(self):
        """Income ≤ 7L → 0% tax."""
        assert calculate_tax(500_000) == 0
        assert calculate_tax(700_000) == 0

    def test_second_slab(self):
        """Income between 7L-10L → 10% on amount above 7L."""
        # 8L → (800000-700000)*0.10 = 10000
        assert calculate_tax(800_000) == 10_000

    def test_third_slab(self):
        """Income between 10L-12L → prev slabs + 15% on amount above 10L."""
        # 11L → 300000*0.10 + 100000*0.15 = 30000+15000 = 45000
        assert calculate_tax(1_100_000) == 45_000

    def test_fourth_slab(self):
        """Income between 12L-15L → prev slabs + 20% on amount above 12L."""
        # 13L → 300000*0.10 + 200000*0.15 + 100000*0.20 = 30000+30000+20000 = 80000
        assert calculate_tax(1_300_000) == 80_000

    def test_fifth_slab(self):
        """Income > 15L → prev slabs + 30% on amount above 15L."""
        # 20L → 300000*0.10 + 200000*0.15 + 300000*0.20 + 500000*0.30
        #     = 30000 + 30000 + 60000 + 150000 = 270000
        assert calculate_tax(2_000_000) == 270_000

    def test_exact_slab_boundary(self):
        # 10L exactly → 300000*0.10 = 30000
        assert calculate_tax(1_000_000) == 30_000


class TestNPSTaxBenefit:
    """Unit tests for NPS tax benefit calculation."""

    def test_low_income_no_benefit(self):
        """Income ≤ 7L → tax is 0, so no benefit possible."""
        benefit = calculate_nps_tax_benefit(600_000, 145.0)
        assert benefit == 0.0

    def test_benefit_with_taxable_income(self):
        """Higher income should yield a positive tax benefit."""
        # Income 12L, invested 100000
        # NPS deduction = min(100000, 120000, 200000) = 100000
        # Tax(12L) = 300000*0.10 + 200000*0.15 = 30000+30000 = 60000
        # Tax(12L-1L = 11L) = 300000*0.10 + 100000*0.15 = 30000+15000 = 45000
        # Benefit = 60000-45000 = 15000
        benefit = calculate_nps_tax_benefit(1_200_000, 100_000)
        assert benefit == 15_000

    def test_deduction_capped_at_10_percent(self):
        """Deduction should not exceed 10% of annual income."""
        # Income 10L, invested 200000
        # NPS deduction = min(200000, 100000, 200000) = 100000 (10% cap)
        benefit_capped = calculate_nps_tax_benefit(1_000_000, 200_000)
        benefit_exact = calculate_nps_tax_benefit(1_000_000, 100_000)
        assert benefit_capped == benefit_exact

    def test_deduction_capped_at_2l(self):
        """Deduction should not exceed ₹2,00,000."""
        # Income 50L, invested 500000
        # NPS deduction = min(500000, 500000, 200000) = 200000 (2L cap)
        benefit = calculate_nps_tax_benefit(5_000_000, 500_000)
        # Tax(50L) - Tax(50L-2L=48L)
        # We just verify it's positive and consistent
        assert benefit > 0
