"""
Performance router:
  - GET /performance → system execution metrics
"""

from fastapi import APIRouter

from backend.api.v1.models.responses import PerformanceResponse
from backend.api.v1.services.performance_service import get_performance_metrics

router = APIRouter(tags=["Performance"])


@router.get(
    "/performance",
    response_model=PerformanceResponse,
    summary="Get system performance metrics",
)
async def performance() -> PerformanceResponse:
    """
    Reports system execution metrics:
      - time: server uptime
      - memory: process RSS in MB
      - threads: active thread count
    """
    metrics = get_performance_metrics()
    return PerformanceResponse(**metrics)
