"""
DecisionSphere FastAPI Application Factory & Main Entry Point.

Configures correlation ID propagation, CORS, centralized exception handlers,
and foundation health probes. Starts cleanly without external database dependencies.
"""
from __future__ import annotations

import time
import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.core.config import Settings, get_settings
from backend.app.core.errors import setup_exception_handlers
from backend.app.core.logging import get_logger, set_request_id, setup_logging

logger = get_logger("decisionsphere.main")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware extracting or generating X-Request-ID and propagating it
    into logging context and response headers.
    """

    async def dispatch(self, request: Request, call_next):
        # Read or generate request ID
        req_id = request.headers.get("X-Request-ID")
        if not req_id:
            req_id = f"req-{uuid.uuid4().hex[:12]}"

        # Bind to async contextvar
        token = set_request_id(req_id)
        start_time = time.perf_counter()

        try:
            response: Response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            response.headers["X-Request-ID"] = req_id
            response.headers["X-Response-Time-MS"] = f"{duration_ms:.2f}"
            return response
        finally:
            set_request_id(None)


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    """
    Application factory instantiating and configuring the FastAPI service.
    """
    if settings is None:
        settings = get_settings()

    # Configure structured logging
    setup_logging(log_level=settings.log_level, json_format=settings.log_json)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "DecisionSphere REST API: Scenario-Based Strategic Planning "
            "and Multi-Domain Risk Evaluation Platform."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    )

    # Attach Correlation ID middleware first so all downstream components see request_id
    app.add_middleware(CorrelationIdMiddleware)

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Response-Time-MS"],
    )

    # Register centralized exception handlers
    setup_exception_handlers(app, debug=settings.debug)

    # Mount Unified API v1 router
    from backend.app.api.v1.api_router import api_router
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    # Root redirect / heartbeat
    @app.get("/", summary="Root Heartbeat", tags=["System"])
    async def root_heartbeat() -> Dict[str, str]:
        return {
            "app": settings.app_name,
            "version": settings.app_version,
            "status": "running",
            "docs_url": "/docs",
        }

    logger.info("DecisionSphere FastAPI application instantiated successfully [env=%s]", settings.app_env)
    return app


# Default application instance for Uvicorn
app = create_app()
