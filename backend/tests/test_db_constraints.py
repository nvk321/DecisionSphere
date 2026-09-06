"""
Database Relational Constraints, Uniqueness, and Cascade Integrity Tests (Gate D).
Verifies that relational foreign keys, version uniqueness constraints, and cascade deletions
behave consistently across scenarios, versions, policies, and simulation results trees.
"""
from __future__ import annotations

import uuid
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

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


def test_scenario_cascade_delete_versions(db_session: Session):
    """
    Gate D Verification:
    Deleting a Scenario entity must cascade delete all associated ScenarioVersion records.
    """
    scenario = Scenario(name="Cascade Target Scenario")
    db_session.add(scenario)
    db_session.flush()

    v1 = ScenarioVersion(scenario_id=scenario.id, version_number=1, demand_growth_pct=10.0)
    v2 = ScenarioVersion(scenario_id=scenario.id, version_number=2, demand_growth_pct=20.0)
    db_session.add_all([v1, v2])
    db_session.commit()

    assert db_session.query(ScenarioVersion).filter_by(scenario_id=scenario.id).count() == 2

    # Delete parent scenario
    db_session.delete(scenario)
    db_session.commit()

    # Child versions must be removed by cascade
    assert db_session.query(ScenarioVersion).filter_by(scenario_id=scenario.id).count() == 0


def test_scenario_version_unique_constraint(db_session: Session):
    """
    Gate D Verification:
    Duplicate version_number for the same scenario must violate the unique constraint.
    """
    scenario = Scenario(name="Version Uniqueness Scenario")
    db_session.add(scenario)
    db_session.flush()

    v1a = ScenarioVersion(scenario_id=scenario.id, version_number=1, demand_growth_pct=5.0)
    db_session.add(v1a)
    db_session.commit()

    v1b = ScenarioVersion(scenario_id=scenario.id, version_number=1, demand_growth_pct=15.0)
    db_session.add(v1b)
    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_policy_version_unique_constraint(db_session: Session):
    """
    Gate D Verification:
    Duplicate version_number on AssumptionPolicy must violate uniqueness constraint.
    """
    p1 = AssumptionPolicy(version_number=101, name="Policy 101a")
    db_session.add(p1)
    db_session.commit()

    p2 = AssumptionPolicy(version_number=101, name="Policy 101b")
    db_session.add(p2)
    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_financial_result_cascade_line_items(db_session: Session):
    """
    Gate D Verification:
    Deleting a FinancialResult entity must cascade delete all associated FinancialLineItem records.
    """
    scenario = Scenario(name="Fin Cascade Scenario")
    db_session.add(scenario)
    db_session.flush()

    version = ScenarioVersion(scenario_id=scenario.id, version_number=1)
    policy = AssumptionPolicy(version_number=201, name="Policy 201")
    db_session.add_all([version, policy])
    db_session.flush()

    run = SimulationRun(
        scenario_version_id=version.id,
        policy_id=policy.id,
        execution_status="SUCCESS",
        execution_duration_ms=125.0,
    )
    db_session.add(run)
    db_session.flush()

    fin = FinancialResult(
        simulation_run_id=run.id,
        gross_revenue_delta=1000.0,
        realized_revenue_delta=950.0,
        cogs_delta=600.0,
        gross_margin_delta=350.0,
        supply_chain_cost_delta=50.0,
        workforce_cost_delta=40.0,
        total_cost_delta=690.0,
        net_profit_delta=260.0,
    )
    db_session.add(fin)
    db_session.flush()

    item1 = FinancialLineItem(
        financial_result_id=fin.id,
        category="REVENUE",
        line_item_name="Gross Revenue",
        amount=1000.0,
    )
    item2 = FinancialLineItem(
        financial_result_id=fin.id,
        category="EXPENSE",
        line_item_name="COGS",
        amount=600.0,
    )
    db_session.add_all([item1, item2])
    db_session.commit()

    assert db_session.query(FinancialLineItem).filter_by(financial_result_id=fin.id).count() == 2

    # Delete financial result
    db_session.delete(fin)
    db_session.commit()

    # Associated line items must be removed
    assert db_session.query(FinancialLineItem).filter_by(financial_result_id=fin.id).count() == 0


def test_recommendation_result_cascade_strategic_actions(db_session: Session):
    """
    Gate D Verification:
    Deleting a RecommendationResult entity must cascade delete all child StrategicAction records.
    """
    scenario = Scenario(name="Rec Cascade Scenario")
    db_session.add(scenario)
    db_session.flush()

    version = ScenarioVersion(scenario_id=scenario.id, version_number=1)
    policy = AssumptionPolicy(version_number=301, name="Policy 301")
    db_session.add_all([version, policy])
    db_session.flush()

    run = SimulationRun(
        scenario_version_id=version.id,
        policy_id=policy.id,
        execution_status="SUCCESS",
        execution_duration_ms=125.0,
    )
    db_session.add(run)
    db_session.flush()

    rec = RecommendationResult(
        simulation_run_id=run.id,
        decision_category="PROCEED_WITH_MITIGATIONS",
        composite_risk_score=55.0,
        risk_level="MODERATE",
        supply_chain_strain=60.0,
        workforce_strain=50.0,
        demand_strain=40.0,
        executive_briefing="Test Briefing",
    )
    db_session.add(rec)
    db_session.flush()

    action = StrategicAction(
        recommendation_result_id=rec.id,
        action_id="ACT-SC-001",
        domain="SUPPLY_CHAIN",
        severity="HIGH",
        title="Expedite Critical Freight",
        description="Shift affected shipments to premium carrier",
        trigger_rule_id="RULE-01",
        expected_trade_off="Elevated expedite fee per order",
    )
    db_session.add(action)
    db_session.commit()

    assert db_session.query(StrategicAction).filter_by(recommendation_result_id=rec.id).count() == 1

    # Delete recommendation result
    db_session.delete(rec)
    db_session.commit()

    # Strategic action must be removed by cascade
    assert db_session.query(StrategicAction).filter_by(recommendation_result_id=rec.id).count() == 0
