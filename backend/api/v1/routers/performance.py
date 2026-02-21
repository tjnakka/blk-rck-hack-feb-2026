"""
Performance router:
  - GET /performance → system execution metrics
"""

from fastapi import APIRouter

from backend.api.v1.models.responses import PerformanceResponse
from backend.api.v1.services.performance_service import PerformanceMonitor

router = APIRouter(tags=["Performance"])
monitor = PerformanceMonitor()


@router.get(
    "/performance",
    response_model=PerformanceResponse,
    summary="Get system performance metrics",
)
async def performance() -> PerformanceResponse:
    """Server uptime, RSS memory, and active thread count."""
    return monitor.metrics()
