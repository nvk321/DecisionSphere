"""
SensitivityService Test Suite (Milestone 9.3).
Validates 1D parameter sweeps, CRS weight sweeps, and recommendation flip threshold searches.
"""
from __future__ import annotations

import pytest
from backend.app.services.sensitivity_service import sensitivity_service
from backend.app.services.simulation_orchestrator import simulation_orchestrator
from backend.app.services.policy_service import policy_service
from backend.app.services.scenario_service import scenario_service
from src.recommendation.schema import CRSWeights
from src.scenario.schema import ScenarioLevers
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from backend.app.db.base import Base


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


def test_demand_shock_sweep():
    """Verify 1D sweep across retail demand shock percentages (Experiment B)."""
    base_levers = ScenarioLevers(demand_growth_pct=0.0, promo_active=False)
    shocks = [-10.0, 0.0, 10.0]

    results = sensitivity_service.run_demand_shock_sweep(
        base_levers=base_levers,
        shock_percentages=shocks,
    )
    assert len(results) == 3
    assert results[0]["demand_shock_pct"] == -10.0
    assert results[1]["demand_shock_pct"] == 0.0
    assert results[2]["demand_shock_pct"] == 10.0

    # Monotonicity check on sales response
    assert results[0]["projected_sales_units"] < results[1]["projected_sales_units"] < results[2]["projected_sales_units"]


def test_financial_parameter_sweep(db_session: Session):
    """Verify 1D sweep across financial coupling parameter (Experiment D)."""
    scenario = scenario_service.create_scenario(
        db=db_session,
        name="Financial Sensitivity Scenario",
        initial_levers={"demand_growth_pct": 10.0},
    )
    version = scenario_service.get_latest_version(db_session, scenario.id)
    policy = policy_service.get_or_create_default_policy(db_session)

    sc_res, _, _, _ = simulation_orchestrator.run_analytical_pipeline(version, policy)

    sweep_results = sensitivity_service.run_financial_parameter_sweep(
        scenario_run=sc_res,
        parameter_name="asm_001_delay_penalty",
        candidate_values=[15.0, 25.0, 35.0, 45.0],
    )
    assert len(sweep_results) == 4
    # Penalty increase must strictly decrease net profit delta
    assert sweep_results[0]["net_profit_delta"] > sweep_results[-1]["net_profit_delta"]


def test_crs_weight_sweep_and_boundary_flip(db_session: Session):
    """Verify CRS domain weight sweeps and recommendation flip threshold detection."""
    scenario = scenario_service.create_scenario(
        db=db_session,
        name="CRS Weight Sweep Scenario",
        initial_levers={"demand_growth_pct": 10.0, "promo_active": True},
    )
    version = scenario_service.get_latest_version(db_session, scenario.id)
    policy = policy_service.get_or_create_default_policy(db_session)

    sc_res, fin_res, _, _ = simulation_orchestrator.run_analytical_pipeline(version, policy)

    candidate_weights = [
        CRSWeights(w_supply=0.70, w_workforce=0.20, w_demand=0.10),
        CRSWeights(w_supply=0.20, w_workforce=0.70, w_demand=0.10),
        CRSWeights(w_supply=0.333, w_workforce=0.333, w_demand=0.334),
    ]

    sweep_results = sensitivity_service.run_crs_weight_sweep(
        scenario_run=sc_res,
        business_impact=fin_res,
        candidate_weights=candidate_weights,
    )
    assert len(sweep_results) == 3
    for entry in sweep_results:
        assert 0.0 <= entry["composite_risk_score"] <= 100.0
        assert entry["decision_category"] in {"PROCEED", "PROCEED_WITH_MITIGATIONS", "REJECT_RESTRUCTURE"}

    # Flip threshold search across replacement cost
    base_assumptions = policy_service.to_business_assumptions(policy)
    flip_analysis = sensitivity_service.find_recommendation_flip_threshold(
        scenario_run=sc_res,
        base_assumptions=base_assumptions,
        parameter_name="asm_004_replacement_cost",
        candidate_values=[15000.0, 30000.0, 45000.0, 60000.0],
    )
    if flip_analysis is not None:
        assert flip_analysis["parameter_name"] == "asm_004_replacement_cost"
        assert flip_analysis["previous_category"] != flip_analysis["new_category"]
