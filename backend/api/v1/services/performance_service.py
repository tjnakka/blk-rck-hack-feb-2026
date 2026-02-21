"""
PerformanceMonitor — reports system execution metrics.

Tracks:
  - Server uptime (since application start)
  - Memory usage (RSS of the current process)
  - Active thread count
"""

import threading
from datetime import datetime, timezone

import psutil

from backend.core.logging import get_logger
from backend.api.v1.models.responses import PerformanceResponse

logger = get_logger(__name__)


class PerformanceMonitor:
    """
    Collects system execution metrics.

    Public API:
        ``metrics()`` → ``PerformanceResponse``
    """

    @staticmethod
    def _current_time() -> str:
        """Current UTC datetime formatted as 'YYYY-MM-DD HH:mm:ss.SSS'."""
        now = datetime.now(timezone.utc)
        return now.strftime("%Y-%m-%d %H:%M:%S.") + f"{now.microsecond // 1000:03d}"

    @staticmethod
    def _memory() -> str:
        """Memory usage in MB formatted as 'XX.XX MB'."""
        process = psutil.Process()
        mem_bytes = process.memory_info().rss
        mem_mb = mem_bytes / (1024 * 1024)
        return f"{mem_mb:.2f} MB"

    @staticmethod
    def _threads() -> int:
        """Number of active threads."""
        return threading.active_count()

    def metrics(self) -> PerformanceResponse:
        """Collect all performance metrics in a single call."""
        result = PerformanceResponse(
            time=self._current_time(),
            memory=self._memory(),
            threads=self._threads(),
        )
        logger.info(
            "Performance metrics: time=%s, memory=%s, threads=%d",
            result.time,
            result.memory,
            result.threads,
        )
        return result
