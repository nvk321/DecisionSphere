"""
AssumptionPolicy Management Route Controllers.
Provides RESTful endpoints for versioned corporate assumption policies (ASM-001 through ASM-010).
"""
from __future__ import annotations

import logging
from typing import List
import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db_session
from backend.app.schemas.policy import PolicyCreate, PolicyResponse
from backend.app.services.policy_service import policy_service

logger = logging.getLogger("decisionsphere.api.policies")
router = APIRouter()


@router.get(
    "/",
    response_model=List[PolicyResponse],
    summary="List Assumption Policies",
)
def list_policies(
    skip: int = Query(default=0, ge=0, description="Offset for pagination"),
    limit: int = Query(default=100, ge=1, le=500, description="Page limit"),
    db: Session = Depends(get_db_session),
) -> List[PolicyResponse]:
    """
    List all corporate assumption policies ordered by version number descending.
    """
    policies = policy_service.list_policies(db=db, skip=skip, limit=limit)
    return [PolicyResponse.model_validate(p) for p in policies]


@router.get(
    "/default",
    response_model=PolicyResponse,
    summary="Get Active Corporate Baseline Policy",
)
def get_default_policy(
    db: Session = Depends(get_db_session),
) -> PolicyResponse:
    """
    Retrieves the authoritative corporate baseline policy (version 1)
    or initializes it if not yet present in the database.
    NOTE: Registered before /{policy_id} to prevent path resolution shadowing.
    """
    policy = policy_service.get_or_create_default_policy(db)
    return PolicyResponse.model_validate(policy)


@router.get(
    "/{policy_id}",
    response_model=PolicyResponse,
    summary="Get Assumption Policy by ID",
)
def get_policy(
    policy_id: uuid.UUID,
    db: Session = Depends(get_db_session),
) -> PolicyResponse:
    """
    Fetch a specific immutable corporate assumption policy by primary key.
    """
    policy = policy_service.get_policy_or_404(db, policy_id)
    return PolicyResponse.model_validate(policy)


@router.post(
    "/",
    response_model=PolicyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Assumption Policy Version",
)
def create_policy_version(
    payload: PolicyCreate,
    db: Session = Depends(get_db_session),
) -> PolicyResponse:
    """
    Create a new immutable corporate assumption policy version.
    Strictly validates simplex equality constraint (w_supply + w_workforce + w_demand = 1.0)
    and non-negative financial rates before persistence.
    """
    # Map from DTO to service kwargs
    policy = policy_service.create_policy_version(
        db=db,
        name=payload.name,
        description=payload.description,
        late_penalty_rate=payload.late_penalty_rate,
        expedite_fee=payload.expedite_fee,
        stockout_churn_factor=payload.stockout_churn_factor,
        replacement_cost=payload.replacement_cost,
        overtime_wage_rate=payload.overtime_wage_rate,
        order_scaling_factor=payload.order_scaling_factor,
        planning_cycle_days=payload.planning_cycle_days,
        crs_w_supply=payload.w_supply,
        crs_w_workforce=payload.w_workforce,
        crs_w_demand=payload.w_demand,
        tau_risk=payload.tau_risk,
        cogs_ratio=payload.cogs_ratio,
    )
    return PolicyResponse.model_validate(policy)
