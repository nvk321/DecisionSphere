"""
Health & System Status Pydantic v2 Schemas.
Provides schemas for liveness/readiness probes and cryptographic model artifact inspection.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import Field

from backend.app.schemas.common import BaseSchema


class ModelArtifactStatus(BaseSchema):
    """Integrity and signature status of an individual serialized model file."""
    name: str = Field(..., description="Human-readable model name")
    path: str = Field(..., description="Filesystem path to model artifact")
    exists: bool = Field(..., description="True if file exists on disk")
    verified: bool = Field(..., description="True if SHA-256 matches frozen baseline")
    expected_sha256: str = Field(..., description="Authoritative cryptographic SHA-256 signature")
    actual_sha256: Optional[str] = Field(None, description="Actual SHA-256 signature computed on disk")
    status: str = Field(..., description="Verification status: VERIFIED, HASH_MISMATCH, FILE_NOT_FOUND")


class ModelStatusResponse(BaseSchema):
    """Aggregate model verification report across all 3 domains."""
    status: str = Field(..., description="Overall model health status: OK, DEGRADED, ERROR")
    models: Dict[str, ModelArtifactStatus] = Field(..., description="Per-model verification records")
    all_verified: bool = Field(True, description="True if all three models are verified")
    models_verified: Optional[bool] = Field(None, description="Alias for all_verified")


class HealthResponse(BaseSchema):
    """Service liveness and readiness probe response."""
    status: str = Field(..., description="Service status: 'healthy' or 'unhealthy'")
    app_name: str = Field(..., description="Application name")
    version: str = Field(..., description="Application semantic version")
    database: str = Field(..., description="Database connection state: 'connected' or 'disconnected'")
    models_verified: bool = Field(..., description="True if all ML model binaries match frozen fingerprints")
    models: Optional[Dict[str, Any]] = Field(default=None, description="Per-model artifact status dictionary")
    environment: Optional[str] = Field(default="development", description="Runtime environment")
