"""
Health & Machine Learning Model Artifact Verification Endpoints.
"""
from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, Request
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.core.config import Settings, get_settings
from backend.app.db.session import get_db_session
from backend.app.schemas.health import HealthResponse, ModelArtifactStatus, ModelStatusResponse

logger = logging.getLogger("decisionsphere.api.health")
router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="System Liveness & Readiness Probe")
def health_probe(
    request: Request,
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db_session),
) -> HealthResponse:
    """
    Liveness and readiness health check probe.
    Verifies service status, database connectivity, and ML model file integrity.
    """
    # 1. Verify model artifacts
    models_report = settings.verify_model_artifacts()
    all_models_ok = all(item["verified"] for item in models_report.values())

    # 2. Check database connectivity
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        logger.warning("Database connectivity probe failed: %s", exc)
        db_status = "disconnected"

    overall_status = "healthy" if all_models_ok else "degraded"

    return HealthResponse(
        status=overall_status,
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
        database=db_status,
        models_verified=all_models_ok,
        models=models_report,
    )


@router.get(
    "/models/status",
    response_model=ModelStatusResponse,
    summary="Machine Learning Model Integrity Verification",
)
def model_status(
    settings: Settings = Depends(get_settings),
) -> ModelStatusResponse:
    """
    Authoritative verification endpoint inspecting demand, supply chain,
    and workforce ML model files and validating SHA-256 fingerprints.
    """
    models_report = settings.verify_model_artifacts()
    all_models_ok = all(item["verified"] for item in models_report.values())

    model_dtos = {
        key: ModelArtifactStatus(
            name=data["name"],
            path=data["path"],
            exists=data["exists"],
            verified=data["verified"],
            expected_sha256=data["expected_sha256"],
            actual_sha256=data["actual_sha256"],
            status=data["status"],
        )
        for key, data in models_report.items()
    }

    return ModelStatusResponse(
        status="success" if all_models_ok else "degraded",
        all_verified=all_models_ok,
        models_verified=all_models_ok,
        models=model_dtos,
    )
