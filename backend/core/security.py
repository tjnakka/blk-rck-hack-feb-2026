"""
Security utilities: API key authentication.
"""

import os

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from backend.config import API_KEY

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(key: str | None = Security(api_key_header)) -> str:
    """
    Validate the API key from the X-API-Key header.
    If API_KEY is set to the default dev key, authentication is skipped
    to allow easy local development and hackathon demos.
    """
    # Skip auth in dev mode (default key)
    if API_KEY == "dev-key-change-me":
        return "dev"
    if key is None or key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return key
