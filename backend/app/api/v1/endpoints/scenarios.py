"""
Scenario Lifecycle & Version Management Route Controllers.
Provides RESTful endpoints for scenario CRUD, immutable version history, and simulation runs.
"""
from __future__ import annotations

import logging
from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.core.errors import AppException, EntityNotFoundError
from backend.app.db.session import get_db_session
from backend.app.schemas.common import PaginatedResponse
from backend.app.schemas.scenario import (
    ScenarioCreate,
    ScenarioResponse,
    ScenarioUpdate,
    ScenarioVersionResponse,
)
from backend.app.schemas.simulation import (
    SimulationDetailResponse,
    SimulationRequest,
)
from backend.app.services.policy_service import policy_service
from backend.app.services.scenario_service import scenario_service
from backend.app.services.simulation_orchestrator import simulation_orchestrator

logger = logging.getLogger("decisionsphere.api.scenarios")
router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedResponse[ScenarioResponse],
    summary="List Scenarios",
)
def list_scenarios(
    skip: int = Query(default=0, ge=0, description="Offset for pagination"),
    limit: int = Query(default=100, ge=1, le=500, description="Page limit"),
    include_archived: bool = Query(default=False, description="Whether to include archived scenarios"),
    db: Session = Depends(get_db_session),
) -> PaginatedResponse[ScenarioResponse]:
    """
    List strategic scenarios ordered by creation timestamp descending.
    """
    scenarios = scenario_service.list_scenarios(
        db=db,
        skip=skip,
        limit=limit,
        include_archived=include_archived,
    )
    items = [ScenarioResponse.model_validate(s) for s in scenarios]
    return PaginatedResponse[ScenarioResponse](
        items=items,
        total=len(items),
        skip=skip,
        limit=limit,
    )


@router.post(
    "/",
    response_model=ScenarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Scenario",
)
def create_scenario(
    payload: ScenarioCreate,
    db: Session = Depends(get_db_session),
) -> ScenarioResponse:
    """
    Create a new strategic scenario and optionally its initial parameter version (v1).
    """
    scenario = scenario_service.create_scenario(
        db=db,
        name=payload.name,
        description=payload.description,
        initial_levers=payload.initial_levers.model_dump() if payload.initial_levers else None,
    )
    return ScenarioResponse.model_validate(scenario)


@router.get(
    "/{scenario_id}",
    response_model=ScenarioResponse,
    summary="Get Scenario by ID",
)
def get_scenario(
    scenario_id: uuid.UUID,
    db: Session = Depends(get_db_session),
) -> ScenarioResponse:
    """
    Fetch scenario metadata and its latest parameter version by primary key.
    """
    scenario = scenario_service.get_scenario_or_404(db, scenario_id)
    return ScenarioResponse.model_validate(scenario)


@router.patch(
    "/{scenario_id}",
    response_model=ScenarioResponse,
    summary="Update Scenario Metadata or Levers",
)
def update_scenario(
    scenario_id: uuid.UUID,
    payload: ScenarioUpdate,
    db: Session = Depends(get_db_session),
) -> ScenarioResponse:
    """
    Update scenario metadata (name, description) and/or submit new levers.
    Enforces Gate G (Version Immutability): submitting new levers increments version_number
    into a new immutable ScenarioVersion record while preserving prior versions.
    """
    scenario = scenario_service.update_scenario(
        db=db,
        scenario_id=scenario_id,
        name=payload.name,
        description=payload.description,
        new_levers=payload.new_levers.model_dump() if payload.new_levers else None,
    )
    return ScenarioResponse.model_validate(scenario)


@router.delete(
    "/{scenario_id}",
    response_model=ScenarioResponse,
    summary="Archive Scenario",
)
def archive_scenario(
    scenario_id: uuid.UUID,
    db: Session = Depends(get_db_session),
) -> ScenarioResponse:
    """
    Soft-archive a scenario without deleting historical versions or simulation runs.
    """
    scenario = scenario_service.archive_scenario(db, scenario_id)
    return ScenarioResponse.model_validate(scenario)


@router.get(
    "/{scenario_id}/versions",
    response_model=List[ScenarioVersionResponse],
    summary="List Scenario Versions",
)
def list_scenario_versions(
    scenario_id: uuid.UUID,
    db: Session = Depends(get_db_session),
) -> List[ScenarioVersionResponse]:
    """
    List all immutable parameter versions for a strategic scenario in chronological order.
    """
    versions = scenario_service.get_scenario_versions(db, scenario_id)
    return [ScenarioVersionResponse.model_validate(v) for v in versions]


@router.get(
    "/{scenario_id}/versions/{version_id}",
    response_model=ScenarioVersionResponse,
    summary="Get Specific Scenario Version",
)
def get_scenario_version(
    scenario_id: uuid.UUID,
    version_id: uuid.UUID,
    db: Session = Depends(get_db_session),
) -> ScenarioVersionResponse:
    """
    Fetch a specific immutable scenario version by UUID.
    """
    version = scenario_service.get_scenario_version_or_404(db, version_id)
    if version.scenario_id != scenario_id:
        raise EntityNotFoundError(
            f"ScenarioVersion {version_id} does not belong to Scenario {scenario_id}"
        )
    return ScenarioVersionResponse.model_validate(version)


@router.post(
    "/{scenario_id}/run",
    response_model=SimulationDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Run Simulation for Scenario",
)
async def run_scenario_simulation(
    scenario_id: uuid.UUID,
    payload: Optional[SimulationRequest] = None,
    db: Session = Depends(get_db_session),
) -> SimulationDetailResponse:
    """
    Shortcut endpoint executing a complete multi-domain simulation for a scenario.
    If override_levers are supplied, creates a new immutable ScenarioVersion before running.
    Binds to specified policy_id or defaults to corporate baseline policy (ASM-001 to ASM-010).
    """
    scenario_service.get_scenario_or_404(db, scenario_id)

    # 1. Resolve ScenarioVersion
    if payload and payload.override_levers is not None:
        version = scenario_service.create_scenario_version(
            db=db,
            scenario_id=scenario_id,
            levers=payload.override_levers.model_dump(),
        )
    elif payload and payload.scenario_version_id is not None:
        version = scenario_service.get_scenario_version_or_404(db, payload.scenario_version_id)
        if version.scenario_id != scenario_id:
            raise EntityNotFoundError(
                f"ScenarioVersion {payload.scenario_version_id} does not belong to Scenario {scenario_id}"
            )
    else:
        version = scenario_service.get_latest_version(db, scenario_id)
        if version is None:
            # Initialize initial version v1 if scenario was created without levers
            version = scenario_service.create_scenario_version(db=db, scenario_id=scenario_id, levers={})

    # 2. Resolve Policy
    policy_id = payload.policy_id if payload else None
    if policy_id is None:
        policy = policy_service.get_or_create_default_policy(db)
        policy_id = policy.id
    else:
        policy_service.get_policy_or_404(db, policy_id)

    # 3. Offload execution asynchronously to threadpool (ADR-006) and persist atomically (Gate F)
    try:
        run = await simulation_orchestrator.execute_and_persist_async(
            db=db,
            scenario_version_id=version.id,
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
