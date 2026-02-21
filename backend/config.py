"""
Application configuration.
All constants and environment-driven settings live here.
"""

import os

# ---------- Server ----------
PORT: int = int(os.getenv("PORT", "5477"))
HOST: str = os.getenv("HOST", "0.0.0.0")

# ---------- Security ----------
API_KEY: str = os.getenv("API_KEY", "dev-key-change-me")

# ---------- Investment Rates (annual) ----------
NPS_RATE: float = 0.0711
INDEX_RATE: float = 0.1449

# ---------- Retirement ----------
RETIREMENT_AGE: int = 60
MIN_INVESTMENT_YEARS: int = 5

# ---------- NPS Tax Benefit Limits ----------
NPS_MAX_DEDUCTION: float = 200_000.0
NPS_INCOME_PERCENT_LIMIT: float = 0.10

# ---------- Tax Slabs (simplified, INR) ----------
# Each tuple: (lower_bound, upper_bound_exclusive, rate)
# upper_bound_exclusive = None means no upper limit
TAX_SLABS: list[tuple[float, float | None, float]] = [
    (0, 700_000, 0.00),
    (700_000, 1_000_000, 0.10),
    (1_000_000, 1_200_000, 0.15),
    (1_200_000, 1_500_000, 0.20),
    (1_500_000, None, 0.30),
]

# ---------- Ceiling Rounding ----------
CEILING_MULTIPLE: int = 100
