"""
Security Boundaries and Request Authentication Middleware.

Provides a clean, extensible API-key dependency boundary without
premature distributed identity or OAuth bloat.
"""
from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader

from backend.app.core.config import Settings, get_settings

api_key_header_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    provided_key: Optional[str] = Security(api_key_header_scheme),
    settings: Settings = Depends(get_settings),
) -> Optional[str]:
    """
    Extensible API key verification dependency.
    
    If `settings.api_key` is configured, incoming requests must supply a matching
    `X-API-Key` header. If `settings.api_key` is None (default development mode),
    all requests pass through freely.
    """
    expected_key = settings.api_key
    if expected_key is None:
        return provided_key

    if not provided_key or provided_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key in X-API-Key header",
        )

    return provided_key
