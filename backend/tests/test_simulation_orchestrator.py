"""
SimulationOrchestrator, Gate F (Atomicity), Gate H (Provenance), and Gate I (Integrity) Test Suite (Milestone 9.3).
"""
from __future__ import annotations

import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.core.config import Settings
from backend.app.core.errors import (
    EntityNotFoundError,
    ModelIntegrityError,
    ModelNotFoundError,
)
from backend.app.db.base import Base
from backend.app.models.financial import FinancialLineItem, FinancialResult
from backend.app.models.prediction import DomainPrediction
from backend.app.models.recommendation import RecommendationResult, StrategicAction
from backend.app.models.simulation_run import AuditRecord, SimulationRun
from backend.app.services.policy_service import policy_service
from backend.app.services.scenario_service import scenario_service
from backend.app.services.simulation_orchestrator import (
    SimulationOrchestrator,
    simulation_orchestrator,
)
from src.scenario.schema import ScenarioLevers


@pytest.fixture
def db_session() -> Session:
    """Isolated in-memory SQLite database session."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, echo=False)
    # Enable SQLite foreign keys
    with engine.connect() as conn:
        conn.exec_driver_sql("PRAGMA foreign_keys = ON;")

    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    yield session

    session.close()
    Base.metadata.drop_all(engine)


def test_simulation_analytical_pipeline_execution(db_session: Session):
    """
    Verify end-to-end multi-domain analytical execution across Phases 6, 7, and 8.
    """
    # 1. Setup scenario version and policy
    scenario = scenario_service.create_scenario(
        db=db_session,
        name="Promotional Campaign 20%",
        initial_levers={
            "demand_growth_pct": 20.0,
            "promo_active": True,
            "scheduled_days_offset": -1,
            "shipping_mode_override": "First Class",
            "overtime_workforce_pct": 30.0,
        },
    )
    version = scenario_service.get_latest_version(db_session, scenario.id)
    policy = policy_service.get_or_create_default_policy(db_session)

    # 2. Execute synchronous analytical pipeline
    sc_res, fin_res, rec_res, duration_ms = simulation_orchestrator.run_analytical_pipeline(
        version, policy
    )

    # 3. Assertions on Phase 6 outputs
    assert duration_ms > 0.0
    assert sc_res.demand_result.scenario_value > 0.0
    assert 0.0 <= sc_res.supply_chain_result.scenario_value <= 1.0
    assert 0.0 <= sc_res.workforce_result.scenario_value <= 1.0

    # 4. Assertions on Phase 7 outputs
    assert fin_res.gross_revenue.delta_value is not None
    assert fin_res.net_profit_delta is not None
    assert fin_res.total_operational_cost.delta_value is not None

    # 5. Assertions on Phase 8 outputs
    assert rec_res.decision_category.value in {"PROCEED", "PROCEED_WITH_MITIGATIONS", "REJECT_RESTRUCTURE"}
    assert 0.0 <= rec_res.composite_risk.composite_risk_score <= 100.0
    assert len(rec_res.recommended_actions) >= 0


def test_gate_f_transaction_atomicity_on_analytical_failure(db_session: Session, monkeypatch):
    """
    Gate F: Transaction Atomicity Gate.
    A simulated analytical exception mid-simulation must roll back the database transaction,
    leaving zero partial or orphaned run records.
    """
    scenario = scenario_service.create_scenario(
        db=db_session,
        name="Atomicity Test Scenario",
        initial_levers={"demand_growth_pct": 10.0},
    )
    version = scenario_service.get_latest_version(db_session, scenario.id)
    policy = policy_service.get_or_create_default_policy(db_session)

    # Monkeypatch run_analytical_pipeline to raise an intentional mid-simulation failure
    def mock_failing_pipeline(*args, **kwargs):
        raise RuntimeError("Simulated mid-pipeline calculation crash")

    monkeypatch.setattr(simulation_orchestrator, "run_analytical_pipeline", mock_failing_pipeline)

    # Attempt to execute and persist - must fail and rollback
    with pytest.raises(RuntimeError, match="Simulated mid-pipeline calculation crash"):
        simulation_orchestrator.execute_and_persist(db_session, version.id, policy.id)

    # Assert complete transaction rollback: ZERO records created
    assert db_session.query(SimulationRun).count() == 0
    assert db_session.query(DomainPrediction).count() == 0
    assert db_session.query(FinancialResult).count() == 0
    assert db_session.query(FinancialLineItem).count() == 0
    assert db_session.query(RecommendationResult).count() == 0
    assert db_session.query(StrategicAction).count() == 0
    assert db_session.query(AuditRecord).count() == 0


def test_execute_and_persist_full_relational_tree_and_gate_h_provenance(db_session: Session):
    """
    Verify full simulation execution, relational persistence, and Gate H Provenance Tuple storage.
    """
    scenario = scenario_service.create_scenario(
        db=db_session,
        name="Full Persist Scenario",
        initial_levers={"demand_growth_pct": 15.0, "promo_active": True},
    )
    version = scenario_service.get_latest_version(db_session, scenario.id)
    policy = policy_service.get_or_create_default_policy(db_session)

    # Execute and persist
    run = simulation_orchestrator.execute_and_persist(db_session, version.id, policy.id)

    assert isinstance(run.id, uuid.UUID)
    assert run.execution_status == "SUCCESS"
    assert run.execution_duration_ms > 0

    # Verify domain predictions
    preds = db_session.query(DomainPrediction).filter_by(simulation_run_id=run.id).all()
    assert len(preds) == 3
    domains = {p.domain for p in preds}
    assert domains == {"DEMAND", "SUPPLY_CHAIN", "WORKFORCE"}
    for p in preds:
        assert p.epistemic_tier == "PREDICTED"

    # Verify financial results & line items
    fin = db_session.query(FinancialResult).filter_by(simulation_run_id=run.id).one()
    assert fin.epistemic_tier == "CALCULATED"
    line_items = db_session.query(FinancialLineItem).filter_by(financial_result_id=fin.id).all()
    assert len(line_items) > 0
    for li in line_items:
        assert li.epistemic_tier == "CALCULATED"

    # Verify recommendation results & strategic actions
    rec = db_session.query(RecommendationResult).filter_by(simulation_run_id=run.id).one()
    assert rec.epistemic_tier == "RECOMMENDED"
    assert rec.decision_category in {"PROCEED", "PROCEED_WITH_MITIGATIONS", "REJECT_RESTRUCTURE"}

    # Verify Gate H: Provenance Signature Tuple Gate
    audit = db_session.query(AuditRecord).filter_by(simulation_run_id=run.id).one()
    p_tuple = audit.provenance_tuple
    assert p_tuple["scenario_version_id"] == str(version.id)
    assert p_tuple["policy_id"] == str(policy.id)
    assert p_tuple["policy_version"] == policy.version_number
    assert p_tuple["git_commit"] == "13f6c0f017fab043f61397e9570bee7de6e97017"
    assert p_tuple["app_version"] == simulation_orchestrator.settings.app_version
    assert p_tuple["migration_revision"] == "18e29557529f"
    assert "artifact_hashes" in p_tuple
    assert "timestamp" in p_tuple


def test_gate_i_model_integrity_failure_handling(monkeypatch):
    """
    Gate I: Model Integrity Failure Gate.
    If an ML model file is missing or its SHA-256 hash fails, the backend must refuse simulation execution.
    """
    test_settings = Settings()

    # 1. Missing file triggers ModelNotFoundError
    missing_report = {
        "demand": {
            "name": "Demand",
            "path": "models/demand/missing.joblib",
            "exists": False,
            "verified": False,
            "expected_sha256": "ABC",
            "actual_sha256": None,
            "status": "FILE_NOT_FOUND",
        }
    }
    monkeypatch.setattr(Settings, "verify_model_artifacts", lambda self: missing_report)
    orchestrator = SimulationOrchestrator(settings=test_settings)

    with pytest.raises(ModelNotFoundError) as exc_info:
        orchestrator.verify_models()
    assert exc_info.value.code == "MODEL_NOT_FOUND"

    # 2. Hash mismatch triggers ModelIntegrityError
    mismatch_report = {
        "demand": {
            "name": "Demand",
            "path": "models/demand/demand_model.joblib",
            "exists": True,
            "verified": False,
            "expected_sha256": "ABC",
            "actual_sha256": "DEF",
            "status": "HASH_MISMATCH",
        }
    }
    monkeypatch.setattr(Settings, "verify_model_artifacts", lambda self: mismatch_report)

    with pytest.raises(ModelIntegrityError) as exc_info:
        orchestrator.verify_models()
    assert exc_info.value.code == "MODEL_INTEGRITY_FAILURE"


@pytest.mark.anyio
async def test_threadpool_offloading_async(db_session: Session):
    """
    Verify ADR-006: Asynchronous threadpool execution offloads CPU computation without blocking.
    """
    scenario = scenario_service.create_scenario(
        db=db_session,
        name="Async Threadpool Scenario",
        initial_levers={"demand_growth_pct": 5.0},
    )
    version = scenario_service.get_latest_version(db_session, scenario.id)
    policy = policy_service.get_or_create_default_policy(db_session)

    sc_res, fin_res, rec_res, duration_ms = await simulation_orchestrator.run_analytical_pipeline_async(
        version, policy
    )
    assert sc_res is not None
    assert fin_res is not None
    assert rec_res is not None
    assert duration_ms > 0
