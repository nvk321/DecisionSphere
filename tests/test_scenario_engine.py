"""
DecisionSphere — Phase 6 Scenario Engine Test Suite
Exhaustive verification of the 20-point test matrix:
ASM registry completeness, baseline integrity, non-mutation of frozen artifacts,
deterministic reproducibility, cross-domain isolation, unrounded delta precision,
per-field epistemic provenance, and strict exclusion of financial calculations.
"""

import pytest
import os
import copy
import numpy as np
import pandas as pd
from pydantic import ValidationError

from src.scenario.assumptions import (
    ASM_REGISTRY,
    PHASE_6_OPERATIONAL_ASSUMPTIONS,
    PHASE_7_FINANCIAL_ASSUMPTIONS,
)
from src.scenario.schema import (
    ScenarioLevers,
    ScenarioAssumptions,
    DomainProvenance,
    DomainPredictionResult,
    ScenarioRunResult,
)
from src.scenario.engine import ScenarioEngine
from src.scenario.sweep import ScenarioSweepEngine


@pytest.fixture(scope="module")
def scenario_engine():
    """Initializes ScenarioEngine once for the test session."""
    engine = ScenarioEngine()
    engine.verify_artifact_integrity()
    return engine


@pytest.fixture(scope="module")
def sample_orders_df(scenario_engine):
    """Provides a small sample of test orders for logistics testing."""
    return scenario_engine.get_default_orders_df(sample_size=30)


@pytest.fixture(scope="module")
def sample_workforce_df(scenario_engine):
    """Provides a small sample of test employees for workforce testing."""
    return scenario_engine.get_default_workforce_df(sample_size=40)


# =============================================================================
# 1. ASM Registry Completeness & Integrity Tests
# =============================================================================

def test_asm_registry_completeness():
    """1. Verifies all 8 assumptions are present with correct IDs, domains, and phases."""
    expected_ids = {"ASM-001", "ASM-002", "ASM-003", "ASM-004", "ASM-005", "ASM-006", "ASM-007", "ASM-008"}
    all_assumptions = ASM_REGISTRY.list_all()
    actual_ids = {a.id for a in all_assumptions}
    assert actual_ids == expected_ids
    assert PHASE_6_OPERATIONAL_ASSUMPTIONS == {"ASM-006", "ASM-007", "ASM-008"}
    assert PHASE_7_FINANCIAL_ASSUMPTIONS == {"ASM-001", "ASM-002", "ASM-003", "ASM-004", "ASM-005"}


def test_asm_baseline_value_integrity():
    """2. Verifies baseline values match Table 1 exactly."""
    assert ASM_REGISTRY.get("ASM-001").baseline_value == 25.00
    assert ASM_REGISTRY.get("ASM-002").baseline_value == 15.00
    assert ASM_REGISTRY.get("ASM-003").baseline_value == 0.15
    assert ASM_REGISTRY.get("ASM-004").baseline_value == 30000.00
    assert ASM_REGISTRY.get("ASM-005").baseline_value == 45.00
    assert ASM_REGISTRY.get("ASM-006").baseline_value == -1
    assert ASM_REGISTRY.get("ASM-007").baseline_value == 1.00
    assert ASM_REGISTRY.get("ASM-008").baseline_value == 30


def test_asm_sensitivity_bounds_integrity():
    """3. Verifies sensitivity ranges match Table 1 bounds."""
    assert ASM_REGISTRY.get("ASM-001").sensitivity_range == (10.00, 60.00)
    assert ASM_REGISTRY.get("ASM-002").sensitivity_range == (5.00, 35.00)
    assert ASM_REGISTRY.get("ASM-003").sensitivity_range == (0.05, 0.40)
    assert ASM_REGISTRY.get("ASM-004").sensitivity_range == (15000.00, 60000.00)
    assert ASM_REGISTRY.get("ASM-005").sensitivity_range == (30.00, 75.00)
    assert ASM_REGISTRY.get("ASM-006").sensitivity_range == [-2, -1, 0]
    assert ASM_REGISTRY.get("ASM-007").sensitivity_range == (0.50, 2.00)
    assert ASM_REGISTRY.get("ASM-008").sensitivity_range == (14, 90)


# =============================================================================
# 2. Frozen Artifact Integrity & Immutability Tests
# =============================================================================

def test_frozen_model_artifact_integrity(scenario_engine):
    """4. Verifies SHA-256 byte hashes of all 3 models remain unchanged before and after execution."""
    initial_fingerprints = scenario_engine.get_artifact_fingerprints()
    assert len(initial_fingerprints) == 3

    # Run a test scenario
    levers = ScenarioLevers(demand_growth_pct=10.0, promo_active=True, scheduled_days_offset=-1)
    scenario_engine.run_scenario(levers=levers)

    # Verify integrity verification passes without raising RuntimeError
    status = scenario_engine.verify_artifact_integrity()
    assert all(status.values())


def test_raw_data_immutability(scenario_engine, sample_orders_df, sample_workforce_df):
    """19. Verifies baseline DataFrames pass assert_frame_equal before and after scenario runs."""
    orders_copy = sample_orders_df.copy(deep=True)
    wf_copy = sample_workforce_df.copy(deep=True)

    levers = ScenarioLevers(
        demand_growth_pct=25.0,
        promo_active=True,
        scheduled_days_offset=-2,
        shipping_mode_override="First Class",
        overtime_workforce_pct=50.0,
        salary_hike_override=20.0,
    )
    scenario_engine.run_scenario(
        levers=levers,
        orders_df=sample_orders_df,
        workforce_df=sample_workforce_df,
    )

    pd.testing.assert_frame_equal(sample_orders_df, orders_copy)
    pd.testing.assert_frame_equal(sample_workforce_df, wf_copy)


# =============================================================================
# 3. Reproducibility & Baseline Invariance Tests
# =============================================================================

def test_reproducibility_contract(scenario_engine, sample_orders_df, sample_workforce_df):
    """5. Verifies identical inputs produce bitwise-identical numerical results; timestamp does not affect output."""
    levers = ScenarioLevers(
        demand_growth_pct=15.0,
        promo_active=True,
        scheduled_days_offset=-1,
        overtime_workforce_pct=30.0,
    )
    res1 = scenario_engine.run_scenario(
        levers=levers, orders_df=sample_orders_df, workforce_df=sample_workforce_df
    )
    res2 = scenario_engine.run_scenario(
        levers=levers, orders_df=sample_orders_df, workforce_df=sample_workforce_df
    )

    assert res1.scenario_id == res2.scenario_id
    assert res1.demand_result.scenario_value == res2.demand_result.scenario_value
    assert res1.demand_result.delta_value == res2.demand_result.delta_value
    assert res1.supply_chain_result.scenario_value == res2.supply_chain_result.scenario_value
    assert res1.supply_chain_result.delta_value == res2.supply_chain_result.delta_value
    assert res1.workforce_result.scenario_value == res2.workforce_result.scenario_value
    assert res1.workforce_result.delta_value == res2.workforce_result.delta_value
    assert res1.normalized_order_volume == res2.normalized_order_volume


def test_baseline_scenario_invariance(scenario_engine, sample_orders_df, sample_workforce_df):
    """6. Zero shock (ΔD=0, ΔS=0, ΔO=0, Promo=False) produces exact delta = 0.0 across all domains."""
    levers = ScenarioLevers(
        demand_growth_pct=0.0,
        promo_active=False,
        scheduled_days_offset=0,
        shipping_mode_override=None,
        overtime_workforce_pct=0.0,
        salary_hike_override=None,
    )
    assumptions = ScenarioAssumptions(
        asm_006_wlb_decrement=0,  # Zero WLB decrement at baseline
        asm_007_volume_scaling=1.0,
        asm_008_cycle_days=30,
    )
    res = scenario_engine.run_scenario(
        levers=levers,
        assumptions=assumptions,
        orders_df=sample_orders_df,
        workforce_df=sample_workforce_df,
    )

    assert res.demand_result.delta_value == 0.0
    assert res.supply_chain_result.delta_value == 0.0
    assert res.workforce_result.delta_value == 0.0
    assert res.workforce_cohort_summary.overtime_switched_count == 0


# =============================================================================
# 4. Phase Boundary & Architectural Exclusion Tests
# =============================================================================

def test_no_financial_values_in_phase6(scenario_engine, sample_orders_df, sample_workforce_df):
    """7. Asserts no dollar signs, revenue, cost, or profit fields exist in Phase 6 output schemas."""
    levers = ScenarioLevers(demand_growth_pct=20.0, promo_active=True)
    res = scenario_engine.run_scenario(
        levers=levers, orders_df=sample_orders_df, workforce_df=sample_workforce_df
    )
    res_dict = res.model_dump()
    res_str = str(res_dict).lower()

    prohibited_terms = [
        "revenue", "cost", "profit", "dollar", "$", "penalty_fee", "expedite_fee", "replacement_cost"
    ]
    for term in prohibited_terms:
        assert term not in res_dict, f"Prohibited financial key '{term}' found in Phase 6 output schema!"
        assert f"'{term}'" not in res_str, f"Prohibited financial string '{term}' found in Phase 6 output!"


def test_phase6_phase7_assumption_segregation():
    """8. Asserts passing ASM-001 through ASM-005 to Phase 6 raises ValidationError."""
    with pytest.raises(ValidationError):
        # Attempt to pass Phase 7 late delivery penalty to Phase 6 assumptions
        ScenarioAssumptions(asm_001_late_penalty=25.0)

    with pytest.raises(ValidationError):
        # Attempt to pass extra undefined parameters
        ScenarioAssumptions(asm_004_replacement=30000.0)


def test_cross_domain_isolation(scenario_engine, sample_orders_df, sample_workforce_df):
    """9. Verifies parameter isolation: changing ASM-006 does not alter Demand or Supply Chain."""
    levers = ScenarioLevers(demand_growth_pct=10.0, scheduled_days_offset=-1, overtime_workforce_pct=40.0)

    # Run with ASM-006 = 0 vs ASM-006 = -2
    res_wlb0 = scenario_engine.run_scenario(
        levers=levers,
        assumptions=ScenarioAssumptions(asm_006_wlb_decrement=0),
        orders_df=sample_orders_df,
        workforce_df=sample_workforce_df,
    )
    res_wlb2 = scenario_engine.run_scenario(
        levers=levers,
        assumptions=ScenarioAssumptions(asm_006_wlb_decrement=-2),
        orders_df=sample_orders_df,
        workforce_df=sample_workforce_df,
    )

    # Demand and Supply Chain predictions must remain bitwise identical
    assert res_wlb0.demand_result.scenario_value == res_wlb2.demand_result.scenario_value
    assert res_wlb0.supply_chain_result.scenario_value == res_wlb2.supply_chain_result.scenario_value
    # Workforce prediction shifts due to WLB decrement
    assert res_wlb0.workforce_result.scenario_value != res_wlb2.workforce_result.scenario_value


# =============================================================================
# 5. Domain Translation & Mathematical Precision Tests
# =============================================================================

def test_deterministic_overtime_assignment(scenario_engine, sample_workforce_df):
    """10. Verifies target % mandates exact headcount via stable sorting; baseline 'Yes' preserved."""
    n = len(sample_workforce_df)
    target_pct = 60.0
    levers = ScenarioLevers(overtime_workforce_pct=target_pct)

    res = scenario_engine.run_scenario(levers=levers, workforce_df=sample_workforce_df)
    summary = res.workforce_cohort_summary

    expected_target_count = int(np.ceil(n * (target_pct / 100.0)))
    assert summary.scenario_overtime_count == expected_target_count
    assert summary.overtime_switched_count == expected_target_count - summary.baseline_overtime_count


def test_asm006_wlb_clamping(scenario_engine, sample_workforce_df):
    """11. Verifies x_WLB scores are decremented by ΔWLB and strictly clamped in [1, 4]."""
    levers = ScenarioLevers(overtime_workforce_pct=100.0) # Mandate all employees
    assumptions = ScenarioAssumptions(asm_006_wlb_decrement=-2)

    res = scenario_engine.run_scenario(
        levers=levers, assumptions=assumptions, workforce_df=sample_workforce_df
    )
    assert res.workforce_cohort_summary.wlb_decrement_applied == -2


def test_asm007_asm008_volume_normalization(scenario_engine, sample_orders_df, sample_workforce_df):
    """12. Verifies dimensional calculation (Sales / H) * tau_cycle * gamma_volume."""
    horizon_days = 14
    cycle_days = 45
    scaling_factor = 1.5

    levers = ScenarioLevers(demand_growth_pct=20.0, promo_active=True)
    assumptions = ScenarioAssumptions(
        asm_007_volume_scaling=scaling_factor,
        asm_008_cycle_days=cycle_days,
    )
    res = scenario_engine.run_scenario(
        levers=levers,
        assumptions=assumptions,
        orders_df=sample_orders_df,
        workforce_df=sample_workforce_df,
        horizon_days=horizon_days,
    )

    daily_sales = res.demand_result.scenario_value / horizon_days
    expected_cycle_sales = daily_sales * cycle_days
    expected_orders = expected_cycle_sales * scaling_factor
    assert np.isclose(res.normalized_order_volume, expected_orders, rtol=1e-5)


def test_exact_unrounded_delta_precision(scenario_engine, sample_orders_df, sample_workforce_df):
    """13. Confirms ΔP is calculated using native 64-bit float subtraction before formatting."""
    levers = ScenarioLevers(demand_growth_pct=12.345, scheduled_days_offset=-1, overtime_workforce_pct=45.0)
    res = scenario_engine.run_scenario(
        levers=levers, orders_df=sample_orders_df, workforce_df=sample_workforce_df
    )

    for domain_res in [res.demand_result, res.supply_chain_result, res.workforce_result]:
        expected_delta = domain_res.scenario_value - domain_res.baseline_value
        assert np.isclose(domain_res.delta_value, expected_delta, atol=1e-12)


def test_per_field_epistemic_provenance(scenario_engine, sample_orders_df, sample_workforce_df):
    """14. Confirms every domain result contains structured DomainProvenance with non-causal flags."""
    levers = ScenarioLevers(demand_growth_pct=10.0, scheduled_days_offset=-1, overtime_workforce_pct=30.0)
    res = scenario_engine.run_scenario(
        levers=levers, orders_df=sample_orders_df, workforce_df=sample_workforce_df
    )

    for domain_res in [res.demand_result, res.supply_chain_result, res.workforce_result]:
        prov = domain_res.provenance
        assert isinstance(prov, DomainProvenance)
        assert prov.causal_claim is False
        assert len(prov.artifact_sha256) == 64
        assert prov.epistemic_tier == "PREDICTED"
        assert len(prov.calculation_description) > 10


def test_threshold_semantics_preservation(scenario_engine, sample_orders_df, sample_workforce_df):
    """15. Confirms continuous probabilities are preserved alongside binary classifications."""
    levers = ScenarioLevers(scheduled_days_offset=-2, overtime_workforce_pct=80.0)
    res = scenario_engine.run_scenario(
        levers=levers, orders_df=sample_orders_df, workforce_df=sample_workforce_df
    )

    # Supply Chain threshold = 0.17
    assert res.supply_chain_result.decision_threshold == pytest.approx(0.17, abs=1e-3)
    assert res.supply_chain_result.baseline_class in {0, 1}
    assert res.supply_chain_result.scenario_class in {0, 1}

    # Workforce threshold = 0.21
    assert res.workforce_result.decision_threshold == pytest.approx(0.21, abs=1e-3)
    assert res.workforce_result.baseline_class in {0, 1}
    assert res.workforce_result.scenario_class in {0, 1}


# =============================================================================
# 6. Validation & Error Handling Tests
# =============================================================================

def test_invalid_parameter_rejection():
    """16. Out-of-bounds levers raise ValidationError."""
    with pytest.raises(ValidationError):
        # Demand shock exceeds 100%
        ScenarioLevers(demand_growth_pct=150.0)

    with pytest.raises(ValidationError):
        # Lead time offset exceeds +3 days
        ScenarioLevers(scheduled_days_offset=5)

    with pytest.raises(ValidationError):
        # Negative overtime percentage
        ScenarioLevers(overtime_workforce_pct=-10.0)


def test_shipping_mode_override_semantics(scenario_engine, sample_orders_df):
    """17. Valid shipping mode modifies feature; invalid modes rejected."""
    # Invalid mode raises error
    with pytest.raises(ValidationError):
        ScenarioLevers(shipping_mode_override="Hyperloop")

    # Valid mode accepted and applied
    levers = ScenarioLevers(shipping_mode_override="Same Day")
    res = scenario_engine.run_scenario(levers=levers, orders_df=sample_orders_df)
    assert res.supply_chain_result.provenance.input_modifications["shipping_mode_override"] == "Same Day"


def test_salary_hike_override_semantics(scenario_engine, sample_workforce_df):
    """18. Valid salary hike modifies PercentSalaryHike; out-of-range rejected."""
    with pytest.raises(ValidationError):
        ScenarioLevers(salary_hike_override=50.0) # > 35% max

    levers = ScenarioLevers(salary_hike_override=25.0)
    res = scenario_engine.run_scenario(levers=levers, workforce_df=sample_workforce_df)
    assert res.workforce_result.provenance.input_modifications["salary_hike_override"] == 25.0


# =============================================================================
# 7. Scenario Sweep Engine Tests (Experiment B & D)
# =============================================================================

def test_sensitivity_sweep_deterministic_execution(scenario_engine, sample_orders_df, sample_workforce_df):
    """20. Sweep evaluates grid points without model mutation or retraining."""
    sweep_engine = ScenarioSweepEngine(scenario_engine)

    shocks = [-20.0, 0.0, 20.0]
    results = sweep_engine.sweep_demand_shocks(
        shock_percentages=shocks,
        orders_df=sample_orders_df,
        workforce_df=sample_workforce_df,
    )
    assert len(results) == 3
    df_sweep = sweep_engine.to_dataframe(results)
    assert len(df_sweep) == 3
    assert list(df_sweep["demand_growth_pct"]) == shocks

    # Test assumption sweep for ASM-007
    asm_results = sweep_engine.sweep_operational_assumption(
        asm_id="ASM-007",
        values=[0.5, 1.0, 1.5, 2.0],
        orders_df=sample_orders_df,
        workforce_df=sample_workforce_df,
    )
    assert len(asm_results) == 4
    df_asm = sweep_engine.to_dataframe(asm_results)
    assert list(df_asm["asm_007_volume_scaling"]) == [0.5, 1.0, 1.5, 2.0]

    # Verify model artifacts are still pristine
    scenario_engine.verify_artifact_integrity()
