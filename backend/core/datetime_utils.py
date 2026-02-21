"""
Datetime parsing and formatting utilities.
All temporal data uses the format: "YYYY-MM-DD HH:mm:ss"
"""

from datetime import datetime

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def parse_datetime(value: str) -> datetime:
    """Parse a datetime string in the standard format."""
    return datetime.strptime(value.strip(), DATETIME_FORMAT)


def format_datetime(dt: datetime) -> str:
    """Format a datetime object to the standard string format."""
    return dt.strftime(DATETIME_FORMAT)


def is_within_period(date_str: str, start_str: str, end_str: str) -> bool:
    """Check if a date falls within a period [start, end] (inclusive)."""
    dt = parse_datetime(date_str)
    start = parse_datetime(start_str)
    end = parse_datetime(end_str)
    return start <= dt <= end
