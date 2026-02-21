"""
V1 API router aggregator.
Combines all v1 sub-routers into a single router.
"""

from fastapi import APIRouter

from backend.api.v1.routers import transactions, returns, performance

router = APIRouter()

router.include_router(transactions.router)
router.include_router(returns.router)
router.include_router(performance.router)
