"""
PolicyService Test Suite (Milestone 9.3).
Validates versioned AssumptionPolicy management, baseline initialization,
and analytical contract mapping (ASM-001 to ASM-010).
"""
from __future__ import annotations

import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.core.errors import EntityNotFoundError, ValidationAppError
from backend.app.db.base import Base
from backend.app.models.policy import AssumptionPolicy
from backend.app.services.policy_service import policy_service
from src.business.schema import BusinessAssumptions
from src.recommendation.schema import CRSWeights


@pytest.fixture
def db_session() -> Session:
    """Isolated in-memory SQLite database session."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    yield session

    session.close()
    Base.metadata.drop_all(engine)


def test_get_or_create_default_policy(db_session: Session):
    """Verify default policy (version 1) is created with ASM-001 to ASM-010 baselines."""
    policy = policy_service.get_or_create_default_policy(db_session)
    assert policy.version_number == 1
    assert policy.late_penalty_rate == 25.0       # ASM-001
    assert policy.expedite_fee == 15.0            # ASM-002
    assert policy.stockout_churn_factor == 0.15   # ASM-003
    assert policy.replacement_cost == 30000.0     # ASM-004
    assert policy.overtime_wage_rate == 45.0      # ASM-005
    assert policy.order_scaling_factor == 1.0     # ASM-007
    assert policy.planning_cycle_days == 30       # ASM-008
    assert policy.crs_w_supply == 0.40            # ASM-009
    assert policy.crs_w_workforce == 0.40         # ASM-009
    assert policy.crs_w_demand == 0.20            # ASM-009
    assert policy.tau_risk == 50.0                # ASM-010
    assert policy.cogs_ratio == 0.60

    # Calling again returns existing record without duplicate key error
    policy_again = policy_service.get_or_create_default_policy(db_session)
    assert policy_again.id == policy.id


def test_create_policy_version_and_listing(db_session: Session):
    """Verify creating versioned immutable policies."""
    p1 = policy_service.get_or_create_default_policy(db_session)

    # Create v2 policy with elevated penalty rates and custom CRS weights
    p2_data = {
        "name": "Stricter Logistics Policy",
        "description": "Elevated late penalty rate and expedited surcharge",
        "late_penalty_rate": 50.0,
        "expedite_fee": 30.0,
        "crs_w_supply": 0.50,
        "crs_w_workforce": 0.30,
        "crs_w_demand": 0.20,
        "tau_risk": 45.0,
    }
    p2 = policy_service.create_policy_version(db_session, p2_data)
    assert p2.version_number == 2
    assert p2.late_penalty_rate == 50.0
    assert p2.crs_w_supply == 0.50

    # Ensure p1 remains intact
    reloaded_p1 = policy_service.get_policy_by_version(db_session, 1)
    assert reloaded_p1.late_penalty_rate == 25.0

    # List all policies
    all_policies = policy_service.list_policies(db_session)
    assert len(all_policies) == 2
    assert [p.version_number for p in all_policies] == [1, 2]


def test_policy_simplex_validation(db_session: Session):
    """Verify that creating a policy with invalid simplex sum raises ValidationAppError."""
    invalid_data = {
        "name": "Invalid Weights",
        "crs_w_supply": 0.50,
        "crs_w_workforce": 0.50,
        "crs_w_demand": 0.50,  # Sum = 1.50 != 1.0
    }
    with pytest.raises(ValidationAppError, match="CRS weights must satisfy simplex sum=1.0"):
        policy_service.create_policy_version(db_session, invalid_data)


def test_analytical_contract_conversions(db_session: Session):
    """Verify mapping relational policy to Phase 7 and Phase 8 analytical schema contracts."""
    policy = policy_service.get_or_create_default_policy(db_session)

    biz_assumptions: BusinessAssumptions = policy_service.to_business_assumptions(policy)
    assert biz_assumptions.asm_001_delay_penalty == 25.0
    assert biz_assumptions.asm_002_expedite_fee == 15.0
    assert biz_assumptions.asm_003_cancellation_factor == 0.15
    assert biz_assumptions.asm_004_replacement_cost == 30000.0
    assert biz_assumptions.asm_005_overtime_rate == 45.0
    assert biz_assumptions.cogs_ratio == 0.60

    crs_weights: CRSWeights = policy_service.to_crs_weights(policy)
    assert crs_weights.w_supply == 0.40
    assert crs_weights.w_workforce == 0.40
    assert crs_weights.w_demand == 0.20


def test_policy_not_found(db_session: Session):
    """Verify EntityNotFoundError raised on unknown policy UUID."""
    unknown_id = uuid.uuid4()
    with pytest.raises(EntityNotFoundError):
        policy_service.get_policy_or_404(db_session, unknown_id)
