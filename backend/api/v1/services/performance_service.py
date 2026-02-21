"""
Performance service: reports system execution metrics.

Tracks:
  - Server uptime (since application start)
  - Memory usage (RSS of the current process)
  - Active thread count
"""

import threading
import time
from datetime import datetime, timezone

import psutil

from backend.core.logging import get_logger

logger = get_logger(__name__)

# Record the server start time
_start_time: float = time.monotonic()
_start_wall: datetime = datetime.now(timezone.utc)


def get_uptime_str() -> str:
    """
    Get server uptime formatted as "YYYY-MM-DD HH:mm:ss.SSS" with
    epoch base (1970-01-01) as shown in the spec example.
    """
    elapsed_seconds = time.monotonic() - _start_time
    # Convert to hours, minutes, seconds, millis
    hours, remainder = divmod(elapsed_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"1970-01-01 {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}.{millis:03d}"


def get_memory_usage_str() -> str:
    """Get memory usage in MB formatted as 'XX.XX MB'."""
    process = psutil.Process()
    mem_bytes = process.memory_info().rss
    mem_mb = mem_bytes / (1024 * 1024)
    return f"{mem_mb:.2f} MB"


def get_thread_count() -> int:
    """Get the number of active threads."""
    return threading.active_count()


def get_performance_metrics() -> dict:
    """Collect all performance metrics."""
    metrics = {
        "time": get_uptime_str(),
        "memory": get_memory_usage_str(),
        "threads": get_thread_count(),
    }
    logger.info(f"Performance metrics: {metrics}")
    return metrics
