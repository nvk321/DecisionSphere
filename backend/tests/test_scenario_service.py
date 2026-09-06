"""
ScenarioService and Gate G Version Immutability Test Suite (Milestone 9.3).
"""
from __future__ import annotations

import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.core.errors import EntityNotFoundError, ValidationAppError
from backend.app.db.base import Base
from backend.app.models.scenario import Scenario, ScenarioVersion
from backend.app.services.scenario_service import scenario_service
from src.scenario.schema import ScenarioLevers


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


def test_create_scenario_without_initial_version(db_session: Session):
    """Verify creating a scenario container without an initial version."""
    scenario = scenario_service.create_scenario(
        db=db_session,
        name="Q4 Black Friday Strategy",
        description="Evaluating seasonal promotional shock",
    )
    assert isinstance(scenario.id, uuid.UUID)
    assert scenario.name == "Q4 Black Friday Strategy"
    assert scenario.is_archived is False
    assert len(scenario.versions) == 0


def test_create_scenario_with_initial_version(db_session: Session):
    """Verify creating a scenario container with an initial v1 snapshot."""
    levers = ScenarioLevers(
        scenario_name="Initial Levers",
        demand_growth_pct=15.0,
        promo_active=True,
        scheduled_days_offset=-1,
        shipping_mode_override="Standard Class",
        overtime_workforce_pct=25.0,
    )
    scenario = scenario_service.create_scenario(
        db=db_session,
        name="Promotional Campaign",
        initial_levers=levers,
    )
    assert len(scenario.versions) == 1
    v1 = scenario.versions[0]
    assert v1.version_number == 1
    assert v1.demand_growth_pct == 15.0
    assert v1.promo_active is True
    assert v1.scheduled_days_offset == -1


def test_gate_g_version_immutability(db_session: Session):
    """
    Gate G: Version Immutability Gate.
    Modifying scenario levers must create an immutable ScenarioVersion row
    with an incremented version number, leaving prior versions completely unchanged.
    """
    # 1. Create base scenario with v1
    v1_levers = {"demand_growth_pct": 10.0, "promo_active": False}
    scenario = scenario_service.create_scenario(
        db=db_session,
        name="Lifecycle Versioning Scenario",
        initial_levers=v1_levers,
    )
    v1 = scenario_service.get_latest_version(db_session, scenario.id)
    assert v1 is not None
    assert v1.version_number == 1
    assert v1.demand_growth_pct == 10.0
    v1_id = v1.id

    # 2. Add v2 with updated parameters (demand shock increased to 25%)
    v2_levers = {"demand_growth_pct": 25.0, "promo_active": True}
    v2 = scenario_service.create_scenario_version(
        db=db_session,
        scenario_id=scenario.id,
        levers=v2_levers,
    )
    assert v2.version_number == 2
    assert v2.demand_growth_pct == 25.0
    assert v2.promo_active is True

    # 3. Add v3 with freight mode override
    v3_levers = {"demand_growth_pct": 25.0, "promo_active": True, "shipping_mode_override": "First Class"}
    v3 = scenario_service.create_scenario_version(
        db=db_session,
        scenario_id=scenario.id,
        levers=v3_levers,
    )
    assert v3.version_number == 3
    assert v3.shipping_mode_override == "First Class"

    # 4. Verify that v1 and v2 remain completely unchanged (immutable historical records)
    reloaded_v1 = scenario_service.get_scenario_version(db_session, v1_id)
    assert reloaded_v1 is not None
    assert reloaded_v1.version_number == 1
    assert reloaded_v1.demand_growth_pct == 10.0
    assert reloaded_v1.promo_active is False
    assert reloaded_v1.shipping_mode_override is None

    # 5. Verify get_latest_version points to v3
    latest = scenario_service.get_latest_version(db_session, scenario.id)
    assert latest is not None
    assert latest.version_number == 3
    assert latest.shipping_mode_override == "First Class"


def test_archive_scenario(db_session: Session):
    """Verify archiving hides scenario from active listings without dropping versions."""
    scenario = scenario_service.create_scenario(
        db=db_session,
        name="Scenario to Archive",
        initial_levers={"demand_growth_pct": 5.0},
    )
    assert scenario.is_archived is False

    archived = scenario_service.archive_scenario(db_session, scenario.id)
    assert archived.is_archived is True

    # Active listing excludes archived by default
    active_scenarios = scenario_service.list_scenarios(db_session, include_archived=False)
    assert all(s.id != scenario.id for s in active_scenarios)

    # Including archived lists it
    all_scenarios = scenario_service.list_scenarios(db_session, include_archived=True)
    assert any(s.id == scenario.id for s in all_scenarios)


def test_scenario_errors_and_validation(db_session: Session):
    """Verify EntityNotFoundError and ValidationAppError handling."""
    # Blank name raises ValidationAppError
    with pytest.raises(ValidationAppError):
        scenario_service.create_scenario(db_session, name="   ")

    # Non-existent scenario lookup raises EntityNotFoundError
    unknown_id = uuid.uuid4()
    with pytest.raises(EntityNotFoundError):
        scenario_service.get_scenario_or_404(db_session, unknown_id)

    # Creating version on non-existent scenario raises EntityNotFoundError
    with pytest.raises(EntityNotFoundError):
        scenario_service.create_scenario_version(db_session, unknown_id, {"demand_growth_pct": 10.0})
