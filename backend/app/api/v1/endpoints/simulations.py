"""
Simulation Run & Orchestration Route Controllers.
Coordinates multi-domain pipeline execution, relational persistence (Gate F & H), and audit retrieval.
"""
from __future__ import annotations

import logging
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.core.errors import AppException, ValidationAppError
from backend.app.db.session import get_db_session
from backend.app.schemas.common import PaginatedResponse
from backend.app.schemas.simulation import (
    SimulationDetailResponse,
    SimulationRequest,
    SimulationRunSummaryResponse,
)
from backend.app.services.policy_service import policy_service
from backend.app.services.scenario_service import scenario_service
from backend.app.services.simulation_orchestrator import simulation_orchestrator

logger = logging.getLogger("decisionsphere.api.simulations")
router = APIRouter()


@router.post(
    "/run",
    response_model=SimulationDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Execute Multi-Domain Simulation Run",
)
async def run_simulation(
    payload: SimulationRequest,
    db: Session = Depends(get_db_session),
) -> SimulationDetailResponse:
    """
    Execute and persist an atomic multi-domain strategic planning simulation run.
    Integrates Demand Forecasting (Phase 2), Delivery Risk (Phase 3), Workforce Risk (Phase 4),
    Cross-Domain Coupling (Phase 6), Business Impact (Phase 7), and Recommendations (Phase 8).
    Enforces Gate F (Transaction Atomicity), Gate H (Provenance Tuple), and Gate I (Model Integrity).
    """
    # 1. Resolve target scenario version
    if payload.scenario_version_id is None:
        raise ValidationAppError(
            "scenario_version_id is required to trigger a simulation run. "
            "To execute for a scenario directly, use POST /api/v1/scenarios/{id}/run."
        )

    base_version = scenario_service.get_scenario_version_or_404(db, payload.scenario_version_id)

    # 2. If temporary override levers are supplied, create a new immutable ScenarioVersion
    if payload.override_levers is not None:
        target_version = scenario_service.create_scenario_version(
            db=db,
            scenario_id=base_version.scenario_id,
            levers=payload.override_levers.model_dump(),
        )
    else:
        target_version = base_version

    # 3. Resolve AssumptionPolicy
    if payload.policy_id is None:
        policy = policy_service.get_or_create_default_policy(db)
        policy_id = policy.id
    else:
        policy = policy_service.get_policy_or_404(db, payload.policy_id)
        policy_id = policy.id

    # 4. Offload execution asynchronously to threadpool (ADR-006) and persist atomically (Gate F)
    try:
        run = await simulation_orchestrator.execute_and_persist_async(
            db=db,
            scenario_version_id=target_version.id,
            policy_id=policy_id,
        )
    except AppException:
        raise
    except Exception as exc:
        raise AppException(
            message=f"Simulation execution failed: {str(exc)}",
            code="INTERNAL_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from exc

    return SimulationDetailResponse.model_validate(run)


@router.get(
    "/{run_id}",
    response_model=SimulationDetailResponse,
    summary="Get Simulation Run Details",
)
def get_simulation_run(
    run_id: uuid.UUID,
    db: Session = Depends(get_db_session),
) -> SimulationDetailResponse:
    """
    Fetch the complete relational tree of an executed simulation run:
    per-domain ML predictions, managerial accounting waterfall, prioritized recommendations,
    and the 8-element cryptographic provenance record (Gate H).
    """
    run = simulation_orchestrator.get_simulation_run_or_404(db, run_id)
    return SimulationDetailResponse.model_validate(run)


@router.get(
    "/",
    response_model=PaginatedResponse[SimulationRunSummaryResponse],
    summary="List Simulation Runs",
)
def list_simulation_runs(
    scenario_id: Optional[uuid.UUID] = Query(default=None, description="Filter by parent scenario ID"),
    skip: int = Query(default=0, ge=0, description="Offset for pagination"),
    limit: int = Query(default=50, ge=1, le=200, description="Page limit"),
    db: Session = Depends(get_db_session),
) -> PaginatedResponse[SimulationRunSummaryResponse]:
    """
    List historical simulation runs with summary aggregates (decision category, CRS, profit delta).
    """
    runs = simulation_orchestrator.list_simulation_runs(
        db=db,
        scenario_id=scenario_id,
        skip=skip,
        limit=limit,
    )
    items = [SimulationRunSummaryResponse.model_validate(r) for r in runs]
    return PaginatedResponse[SimulationRunSummaryResponse](
        items=items,
        total=len(items),
        skip=skip,
        limit=limit,
    )
