"""
Datetime parsing utility.
All temporal data uses the format: "YYYY-MM-DD HH:mm:ss"
"""

from datetime import datetime

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def parse_datetime(value: str) -> datetime:
    """Parse a datetime string in the standard format."""
    return datetime.strptime(value.strip(), DATETIME_FORMAT)
