"""
Database Model & Relational Constraints Test Suite (Milestone 9.1).
Validates schema creation, relationships, unique constraints, and cascade deletions.
"""
from datetime import datetime, timezone
import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from backend.app.db.base import Base
from backend.app.models import (
    AssumptionPolicy,
    AuditRecord,
    DomainPrediction,
    FinancialLineItem,
    FinancialResult,
    RecommendationResult,
    Scenario,
    ScenarioVersion,
    SimulationRun,
    StrategicAction,
)


@pytest.fixture
def db_session():
    """Create an isolated in-memory SQLite database session for unit testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    # Enable SQLite foreign key support
    with engine.connect() as conn:
        conn.exec_driver_sql("PRAGMA foreign_keys = ON;")

    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    yield session

    session.close()
    Base.metadata.drop_all(engine)


def test_scenario_and_version_creation(db_session: Session):
    """Verify Scenario and ScenarioVersion creation, defaults, and relationships."""
    scenario = Scenario(
        name="Q4 Black Friday Promotion",
        description="Evaluating 25% demand shock with Standard Class freight",
    )
    db_session.add(scenario)
    db_session.commit()

    assert isinstance(scenario.id, uuid.UUID)
    assert scenario.is_archived is False
    assert scenario.created_at is not None

    version = ScenarioVersion(
        scenario_id=scenario.id,
        version_number=1,
        demand_growth_pct=25.0,
        promo_active=True,
        scheduled_days_offset=-1,
        shipping_mode_override="Standard Class",
        overtime_workforce_pct=40.0,
        unit_price=1.0,
    )
    db_session.add(version)
    db_session.commit()

    assert version.id is not None
    assert len(scenario.versions) == 1
    assert scenario.versions[0].demand_growth_pct == 25.0
    assert scenario.versions[0].scenario.name == "Q4 Black Friday Promotion"


def test_scenario_version_unique_constraint(db_session: Session):
    """Verify unique constraint prevents duplicate version numbers within same scenario."""
    scenario = Scenario(name="Unique Version Test")
    db_session.add(scenario)
    db_session.commit()

    v1 = ScenarioVersion(scenario_id=scenario.id, version_number=1, demand_growth_pct=10.0)
    db_session.add(v1)
    db_session.commit()

    # Attempt to insert duplicate version_number=1 for same scenario
    v1_dup = ScenarioVersion(scenario_id=scenario.id, version_number=1, demand_growth_pct=20.0)
    db_session.add(v1_dup)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_scenario_cascade_delete(db_session: Session):
    """Verify deleting a Scenario cascades to all its ScenarioVersions."""
    scenario = Scenario(name="Cascade Delete Test")
    db_session.add(scenario)
    db_session.commit()

    v1 = ScenarioVersion(scenario_id=scenario.id, version_number=1)
    v2 = ScenarioVersion(scenario_id=scenario.id, version_number=2)
    db_session.add_all([v1, v2])
    db_session.commit()

    assert db_session.query(ScenarioVersion).filter_by(scenario_id=scenario.id).count() == 2

    # Delete parent scenario
    db_session.delete(scenario)
    db_session.commit()

    assert db_session.query(ScenarioVersion).filter_by(scenario_id=scenario.id).count() == 0


def test_assumption_policy_creation_and_defaults(db_session: Session):
    """Verify AssumptionPolicy default parameter values match ASM-001 through ASM-010."""
    policy = AssumptionPolicy(
        version_number=1,
        name="Baseline Corporate Policy 2026",
    )
    db_session.add(policy)
    db_session.commit()

    assert policy.late_penalty_rate == 25.0  # ASM-001
    assert policy.expedite_fee == 15.0       # ASM-002
    assert policy.stockout_churn_factor == 0.15  # ASM-003
    assert policy.replacement_cost == 30000.0   # ASM-004
    assert policy.overtime_wage_rate == 45.0    # ASM-005
    assert policy.order_scaling_factor == 1.0   # ASM-007
    assert policy.planning_cycle_days == 30     # ASM-008
    assert policy.crs_w_supply == 0.40          # ASM-009
    assert policy.crs_w_workforce == 0.40       # ASM-009
    assert policy.crs_w_demand == 0.20          # ASM-009
    assert policy.tau_risk == 50.0              # ASM-010
    assert policy.cogs_ratio == 0.60


def test_full_simulation_run_relational_tree(db_session: Session):
    """Verify end-to-end relational mapping across simulation runs, predictions, financials, and actions."""
    # 1. Parent Scenario & Version
    scenario = Scenario(name="Multi-Domain Campaign")
    db_session.add(scenario)
    db_session.commit()

    version = ScenarioVersion(scenario_id=scenario.id, version_number=1, demand_growth_pct=30.0)
    db_session.add(version)

    # 2. Policy
    policy = AssumptionPolicy(version_number=100)
    db_session.add(policy)
    db_session.commit()

    # 3. Simulation Run
    run = SimulationRun(
        scenario_version_id=version.id,
        policy_id=policy.id,
        execution_status="SUCCESS",
        execution_duration_ms=312.45,
    )
    db_session.add(run)
    db_session.commit()

    # 4. Domain Predictions
    p_demand = DomainPrediction(
        simulation_run_id=run.id,
        domain="DEMAND",
        metric_name="mean_sales",
        baseline_value=8000.0,
        scenario_value=10400.0,
        delta_value=2400.0,
    )
    p_sc = DomainPrediction(
        simulation_run_id=run.id,
        domain="SUPPLY_CHAIN",
        metric_name="late_delivery_probability",
        baseline_value=0.548,
        scenario_value=0.682,
        delta_value=0.134,
    )
    db_session.add_all([p_demand, p_sc])

    # 5. Financial Result & Line Items
    fin_result = FinancialResult(
        simulation_run_id=run.id,
        gross_revenue_delta=2400.0,
        realized_revenue_delta=2154.0,
        cogs_delta=1292.4,
        gross_margin_delta=861.6,
        supply_chain_cost_delta=3500.0,
        workforce_cost_delta=12000.0,
        total_cost_delta=16792.4,
        net_profit_delta=-14638.4,
    )
    db_session.add(fin_result)
    db_session.commit()

    line_item1 = FinancialLineItem(
        financial_result_id=fin_result.id,
        category="PENALTY",
        line_item_name="Carrier Late Delivery Penalties",
        amount=3500.0,
    )
    line_item2 = FinancialLineItem(
        financial_result_id=fin_result.id,
        category="TURNOVER",
        line_item_name="Employee Replacement Recruitment",
        amount=12000.0,
    )
    db_session.add_all([line_item1, line_item2])

    # 6. Recommendation Result & Strategic Actions
    rec_result = RecommendationResult(
        simulation_run_id=run.id,
        decision_category="REJECT_RESTRUCTURE",
        composite_risk_score=68.5,
        risk_level="HIGH",
        supply_chain_strain=72.0,
        workforce_strain=65.0,
        demand_strain=68.5,
        primary_vulnerability="Overtime turnover costs exceed promotional margin",
        executive_briefing="Reject scenario: sales uplift destroys capital.",
    )
    db_session.add(rec_result)
    db_session.commit()

    action = StrategicAction(
        recommendation_result_id=rec_result.id,
        action_id="ACT-01",
        domain="WORKFORCE",
        severity="HIGH",
        title="Cap Mandatory Overtime",
        description="Limit overtime to 20h per worker to arrest attrition risk.",
        trigger_rule_id="RULE-03",
        expected_trade_off="Reduces employee attrition at cost of dispatch throughput.",
    )
    db_session.add(action)

    # 7. Audit Record (Provenance Tuple)
    audit = AuditRecord(
        simulation_run_id=run.id,
        provenance_tuple={
            "scenario_version_id": str(version.id),
            "policy_version_id": str(policy.id),
            "git_commit": "13f6c0f017fab043f61397e9570bee7de6e97017",
            "app_version": "1.0.0-phase9",
            "python_version": "3.13.5",
        },
    )
    db_session.add(audit)
    db_session.commit()

    # 8. Assertions on Navigation
    loaded_run = db_session.query(SimulationRun).filter_by(id=run.id).one()
    assert len(loaded_run.domain_predictions) == 2
    assert loaded_run.financial_result is not None
    assert loaded_run.financial_result.net_profit_delta == -14638.4
    assert len(loaded_run.financial_result.line_items) == 2
    assert loaded_run.recommendation_result is not None
    assert loaded_run.recommendation_result.decision_category == "REJECT_RESTRUCTURE"
    assert len(loaded_run.recommendation_result.strategic_actions) == 1
    assert loaded_run.audit_record is not None
    assert loaded_run.audit_record.provenance_tuple["git_commit"] == "13f6c0f017fab043f61397e9570bee7de6e97017"

    # 9. Cascade delete of simulation run removes child records
    db_session.delete(loaded_run)
    db_session.commit()

    assert db_session.query(DomainPrediction).filter_by(simulation_run_id=run.id).count() == 0
    assert db_session.query(FinancialResult).filter_by(simulation_run_id=run.id).count() == 0
    assert db_session.query(RecommendationResult).filter_by(simulation_run_id=run.id).count() == 0
    assert db_session.query(AuditRecord).filter_by(simulation_run_id=run.id).count() == 0
