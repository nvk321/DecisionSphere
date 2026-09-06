"""
Centralized Error Handling and Exception Architecture.

Defines standard application exceptions and registers FastAPI handlers
guaranteeing a uniform, predictable JSON error shape across all endpoints.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.core.logging import get_request_id

logger = logging.getLogger("decisionsphere.errors")


class AppException(Exception):
    """
    Base domain exception for DecisionSphere application services.
    """
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class ModelIntegrityError(AppException):
    """Raised when an ML model artifact fails SHA-256 cryptographic verification."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            code="MODEL_INTEGRITY_FAILURE",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details,
        )


class ModelNotFoundError(AppException):
    """Raised when an ML model artifact file is missing on the filesystem."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            code="MODEL_NOT_FOUND",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details,
        )


class EntityNotFoundError(AppException):
    """Raised when a requested resource (scenario, version, policy) is not found."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


class ValidationAppError(AppException):
    """Raised when business logic parameter constraints are violated."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            code="INVALID_PARAMETER",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class ConfigurationError(AppException):
    """Raised when environment or path configuration is invalid."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


def format_error_response(
    code: str,
    message: str,
    status_code: int,
    request_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    """Format and return uniform error response structure."""
    payload = {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id or get_request_id(),
        }
    }
    if details:
        payload["error"]["details"] = details

    return JSONResponse(status_code=status_code, content=payload)


def setup_exception_handlers(app: FastAPI, debug: bool = False) -> None:
    """Register centralized exception handlers on the FastAPI application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        logger.warning(
            "Application exception: %s (code=%s, status=%d)",
            exc.message,
            exc.code,
            exc.status_code,
            extra={"details": exc.details},
        )
        return format_error_response(
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.info("Request validation failed on %s: %s", request.url.path, exc.errors())
        return format_error_response(
            code="VALIDATION_ERROR",
            message="Request payload failed schema validation",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"errors": jsonable_encoder(exc.errors())},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        code = "HTTP_ERROR"
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            code = "NOT_FOUND"
        elif exc.status_code == status.HTTP_401_UNAUTHORIZED:
            code = "UNAUTHORIZED"
        elif exc.status_code == status.HTTP_403_FORBIDDEN:
            code = "FORBIDDEN"

        return format_error_response(
            code=code,
            message=str(exc.detail),
            status_code=exc.status_code,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        req_id = get_request_id()
        logger.exception("Unhandled server exception on %s [request_id=%s]: %s", request.url.path, req_id, exc)
        message = str(exc) if debug else "An internal server error occurred. Please quote the request ID."
        return format_error_response(
            code="INTERNAL_SERVER_ERROR",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            request_id=req_id,
        )
