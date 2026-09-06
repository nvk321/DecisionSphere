"""
Unified API v1 Router.
Aggregates all route controllers under the /api/v1 prefix.
"""
from __future__ import annotations

from fastapi import APIRouter

from backend.app.api.v1.endpoints import (
    health,
    policies,
    scenarios,
    sensitivity,
    simulations,
)

api_router = APIRouter()

# Health & Model Artifact Status Probes
api_router.include_router(health.router, tags=["System", "Models"])

# Strategic Scenarios & Parameter Versions
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["Scenarios"])

# Corporate Assumption Policies (ASM-001 through ASM-010)
api_router.include_router(policies.router, prefix="/policies", tags=["Assumption Policies"])

# Simulation Execution & Audit Records
api_router.include_router(simulations.router, prefix="/simulations", tags=["Simulations"])

# Sensitivity Sweeps (Experiment B & Experiment D)
api_router.include_router(sensitivity.router, prefix="/sensitivity", tags=["Sensitivity Analysis"])
