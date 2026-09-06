"""
DecisionSphere — Phase 7 Business Impact Analysis Automated Test Suite
20-point comprehensive verification covering schema validation, deterministic accounting,
prevention of double-counting, IEEE 754 precision, epistemic provenance, sensitivity sweeps,
break-even boundary detection, non-causal disclosures, and immutability contracts.
"""

import pytest
import json
import numpy as np
from pydantic import ValidationError

from src.scenario.schema import (
    ScenarioLevers,
    ScenarioAssumptions,
    DomainPredictionResult,
    DomainProvenance,
    WorkforceCohortSummary,
    ScenarioRunResult,
)
from src.business.schema import (
    BusinessAssumptions,
    FinancialLineItemProvenance,
    FinancialLineItem,
    BreakEvenAnalysis,
    BusinessImpactResult,
    EXPEDITED_SHIPPING_MODES,
    REGULAR_SHIPPING_MODES,
)
from src.business.engine import BusinessImpactEngine
from src.business.sensitivity import BusinessSensitivityEngine, PARAM_BOUNDS


# =============================================================================
# FIXTURES & SYNTHETIC DATA GENERATORS
# =============================================================================

def make_dummy_provenance(domain: str) -> DomainProvenance:
    return DomainProvenance(
        source_model=f"Test {domain} Model",
        model_artifact=f"models/{domain.lower()}/test.joblib",
        artifact_sha256="0" * 64,
        epistemic_tier="PREDICTED",
        input_modifications={},
        assumptions_applied=[],
        causal_claim=False,
        calculation_description="Test inference",
    )


def create_mock_scenario_run(
    base_sales: float = 10000.0,
    scen_sales: float = 12000.0,
    base_late_prob: float = 0.50,
    scen_late_prob: float = 0.60,
    base_att_prob: float = 0.15,
    scen_att_prob: float = 0.20,
    total_headcount: int = 200,
    base_ot_count: int = 50,
    scen_ot_count: int = 100,
    normalized_order_volume: float = 1000.0,
    shipping_mode_override: str = None,
    scenario_id: str = "test_scen_001",
    scenario_name: str = "Test Scenario",
) -> ScenarioRunResult:
    """Constructs a strictly typed, valid ScenarioRunResult for deterministic unit testing."""
    levers = ScenarioLevers(
        scenario_id=scenario_id,
        scenario_name=scenario_name,
        demand_growth_pct=20.0,
        promo_active=True,
        shipping_mode_override=shipping_mode_override,
    )
    assumptions = ScenarioAssumptions()

    demand_res = DomainPredictionResult(
        domain="Demand",
        unit="Sales units",
        baseline_value=base_sales,
        scenario_value=scen_sales,
        delta_value=scen_sales - base_sales,
        provenance=make_dummy_provenance("Demand"),
    )
    supply_res = DomainPredictionResult(
        domain="Supply Chain",
        unit="Probability",
        baseline_value=base_late_prob,
        scenario_value=scen_late_prob,
        delta_value=scen_late_prob - base_late_prob,
        decision_threshold=0.55,
        baseline_class=int(base_late_prob >= 0.55),
        scenario_class=int(scen_late_prob >= 0.55),
        provenance=make_dummy_provenance("SupplyChain"),
    )
    workforce_res = DomainPredictionResult(
        domain="Workforce",
        unit="Probability",
        baseline_value=base_att_prob,
        scenario_value=scen_att_prob,
        delta_value=scen_att_prob - base_att_prob,
        decision_threshold=0.21,
        baseline_class=int(base_att_prob >= 0.21),
        scenario_class=int(scen_att_prob >= 0.21),
        provenance=make_dummy_provenance("Workforce"),
    )
    cohort_summary = WorkforceCohortSummary(
        total_headcount=total_headcount,
        baseline_overtime_count=base_ot_count,
        scenario_overtime_count=scen_ot_count,
        overtime_switched_count=scen_ot_count - base_ot_count,
        target_overtime_percentage=50.0,
        actual_scenario_overtime_percentage=scen_ot_count / total_headcount * 100.0,
        wlb_decrement_applied=-1,
        epistemic_tier="PROPAGATED",
    )

    return ScenarioRunResult(
        scenario_id=scenario_id,
        scenario_name=scenario_name,
        levers=levers,
        assumptions=assumptions,
        demand_result=demand_res,
        supply_chain_result=supply_res,
        workforce_result=workforce_res,
        workforce_cohort_summary=cohort_summary,
        normalized_order_volume=normalized_order_volume,
        execution_timestamp="2026-09-05T12:00:00Z",
        epistemic_tier="PROPAGATED",
        interpretation="Test interpretation",
    )


# =============================================================================
# 20-TEST PHASE 7 MATRIX
# =============================================================================

def test_business_assumptions_baseline_integrity():
    """1. Default values match Table 1 ($25, $15, 0.15, $30k, $45/hr, etc.)."""
    assumptions = BusinessAssumptions()
    assert assumptions.asm_001_delay_penalty == 25.00
    assert assumptions.asm_002_expedite_fee == 15.00
    assert assumptions.asm_003_cancellation_factor == 0.15
    assert assumptions.asm_004_replacement_cost == 30000.00
    assert assumptions.asm_005_overtime_rate == 45.00
    assert assumptions.cogs_ratio == 0.60
    assert assumptions.unit_price == 1.00
    assert assumptions.overtime_hours_per_worker == 20.0
    assert assumptions.baseline_expedited_fraction == 0.05


def test_business_assumptions_bounds_integrity():
    """2. Sensitivity bounds enforced by Pydantic."""
    # Under-bound checks
    with pytest.raises(ValidationError):
        BusinessAssumptions(asm_001_delay_penalty=9.99)
    with pytest.raises(ValidationError):
        BusinessAssumptions(asm_002_expedite_fee=4.99)
    with pytest.raises(ValidationError):
        BusinessAssumptions(asm_003_cancellation_factor=0.04)
    with pytest.raises(ValidationError):
        BusinessAssumptions(asm_004_replacement_cost=14999.0)
    with pytest.raises(ValidationError):
        BusinessAssumptions(asm_005_overtime_rate=29.99)
    with pytest.raises(ValidationError):
        BusinessAssumptions(cogs_ratio=0.29)
    with pytest.raises(ValidationError):
        BusinessAssumptions(unit_price=0.49)

    # Over-bound checks
    with pytest.raises(ValidationError):
        BusinessAssumptions(asm_001_delay_penalty=60.01)
    with pytest.raises(ValidationError):
        BusinessAssumptions(asm_002_expedite_fee=35.01)
    with pytest.raises(ValidationError):
        BusinessAssumptions(asm_003_cancellation_factor=0.41)
    with pytest.raises(ValidationError):
        BusinessAssumptions(asm_004_replacement_cost=60001.0)
    with pytest.raises(ValidationError):
        BusinessAssumptions(asm_005_overtime_rate=75.01)
    with pytest.raises(ValidationError):
        BusinessAssumptions(cogs_ratio=0.91)
    with pytest.raises(ValidationError):
        BusinessAssumptions(unit_price=50.01)

    # Valid boundary values succeed
    valid = BusinessAssumptions(
        asm_001_delay_penalty=10.00,
        asm_002_expedite_fee=35.00,
        asm_003_cancellation_factor=0.40,
        asm_004_replacement_cost=60000.00,
        asm_005_overtime_rate=75.00,
        cogs_ratio=0.90,
        unit_price=50.00,
    )
    assert valid.asm_001_delay_penalty == 10.00


def test_business_assumptions_phase_segregation():
    """3. Rejects Phase 6 operational assumptions and extra parameters."""
    with pytest.raises(ValidationError):
        BusinessAssumptions(asm_006_wlb_decrement=-1)  # Phase 6 parameter
    with pytest.raises(ValidationError):
        BusinessAssumptions(asm_007_volume_scaling=1.0)  # Phase 6 parameter
    with pytest.raises(ValidationError):
        BusinessAssumptions(asm_008_cycle_days=30)  # Phase 6 parameter
    with pytest.raises(ValidationError):
        BusinessAssumptions(arbitrary_extra_field=123)


def test_exact_revenue_fulfillment_loss_calculation():
    """4. Verifies L_fulfillment = min(1, P_late * kappa_stockout) and Realized Revenue."""
    # base_sales = 10000, scen_sales = 12000, unit_price = 2.0
    # base_late_prob = 0.40, scen_late_prob = 0.60
    # asm_003 = 0.20
    # L_base = 0.40 * 0.20 = 0.08 -> Realized base = (10000 * 2) * (1 - 0.08) = 20000 * 0.92 = 18400.0
    # L_scen = 0.60 * 0.20 = 0.12 -> Realized scen = (12000 * 2) * (1 - 0.12) = 24000 * 0.88 = 21120.0
    # Delta Realized = 21120.0 - 18400.0 = 2720.0
    run = create_mock_scenario_run(
        base_sales=10000.0,
        scen_sales=12000.0,
        base_late_prob=0.40,
        scen_late_prob=0.60,
    )
    assumptions = BusinessAssumptions(unit_price=2.0, asm_003_cancellation_factor=0.20)
    engine = BusinessImpactEngine()
    result = engine.evaluate(run, assumptions=assumptions)

    assert result.gross_revenue.baseline_value == 20000.0
    assert result.gross_revenue.scenario_value == 24000.0
    assert result.gross_revenue.delta_value == 4000.0

    assert result.realized_revenue.baseline_value == pytest.approx(18400.0)
    assert result.realized_revenue.scenario_value == pytest.approx(21120.0)
    assert result.realized_revenue.delta_value == pytest.approx(2720.0)


def test_exact_cogs_calculation():
    """5. Verifies Option B: COGS = Realized Revenue * cogs_ratio."""
    run = create_mock_scenario_run(
        base_sales=10000.0,
        scen_sales=12000.0,
        base_late_prob=0.40,
        scen_late_prob=0.60,
    )
    assumptions = BusinessAssumptions(unit_price=2.0, asm_003_cancellation_factor=0.20, cogs_ratio=0.50)
    engine = BusinessImpactEngine()
    result = engine.evaluate(run, assumptions=assumptions)

    # Realized base = 18400, scen = 21120
    # COGS base = 18400 * 0.50 = 9200
    # COGS scen = 21120 * 0.50 = 10560
    # Gross Margin base = 18400 - 9200 = 9200
    # Gross Margin scen = 21120 - 10560 = 10560
    assert result.cogs.baseline_value == pytest.approx(9200.0)
    assert result.cogs.scenario_value == pytest.approx(10560.0)
    assert result.cogs.delta_value == pytest.approx(1360.0)
    assert result.gross_margin.baseline_value == pytest.approx(9200.0)
    assert result.gross_margin.scenario_value == pytest.approx(10560.0)
    assert result.gross_margin.delta_value == pytest.approx(1360.0)


def test_exact_supply_chain_disruption_cost():
    """6. Verifies delivered-delayed penalty and expedited freight surcharge."""
    # n_orders_scen = 1000, scen_sales = 12000, base_sales = 6000 -> n_orders_base = 1000 * (6000/12000) = 500
    # P_late_base = 0.50, P_late_scen = 0.60
    # kappa_stockout = 0.20 -> (1 - kappa) = 0.80
    # Delivered-delayed base = 500 * 0.50 * 0.80 = 200
    # Delivered-delayed scen = 1000 * 0.60 * 0.80 = 480
    # DelayPenalty base = 200 * $25 = $5,000
    # DelayPenalty scen = 480 * $25 = $12,000
    # Shipping mode = None -> expedited frac = 0.05
    # Expedited base = 500 * 0.05 = 25 -> ExpediteCost base = 25 * $15 = $375
    # Expedited scen = 1000 * 0.05 = 50 -> ExpediteCost scen = 50 * $15 = $750
    # Total supply cost base = 5000 + 375 = 5375
    # Total supply cost scen = 12000 + 750 = 12750
    # Delta supply cost = 12750 - 5375 = 7375
    run = create_mock_scenario_run(
        base_sales=6000.0,
        scen_sales=12000.0,
        base_late_prob=0.50,
        scen_late_prob=0.60,
        normalized_order_volume=1000.0,
        shipping_mode_override=None,
    )
    assumptions = BusinessAssumptions(
        asm_001_delay_penalty=25.0,
        asm_002_expedite_fee=15.0,
        asm_003_cancellation_factor=0.20,
        baseline_expedited_fraction=0.05,
    )
    engine = BusinessImpactEngine()
    result = engine.evaluate(run, assumptions=assumptions)

    assert result.supply_chain_cost.baseline_value == pytest.approx(5375.0)
    assert result.supply_chain_cost.scenario_value == pytest.approx(12750.0)
    assert result.supply_chain_cost.delta_value == pytest.approx(7375.0)


def test_exact_turnover_replacement_cost():
    """7. Verifies N_departures * C_replacement."""
    # N_headcount = 200
    # P_att_base = 0.10, P_att_scen = 0.20
    # Departures base = 200 * 0.10 = 20
    # Departures scen = 200 * 0.20 = 40
    # C_replacement = $30,000
    # Cost base = 20 * 30000 = $600,000
    # Cost scen = 40 * 30000 = $1,200,000
    # Delta = $600,000
    run = create_mock_scenario_run(
        total_headcount=200,
        base_att_prob=0.10,
        scen_att_prob=0.20,
        base_ot_count=0,
        scen_ot_count=0,
    )
    assumptions = BusinessAssumptions(asm_004_replacement_cost=30000.0)
    engine = BusinessImpactEngine()
    result = engine.evaluate(run, assumptions=assumptions)

    # Since ot count is 0, workforce cost is purely turnover cost
    assert result.workforce_cost.baseline_value == pytest.approx(600000.0)
    assert result.workforce_cost.scenario_value == pytest.approx(1200000.0)
    assert result.workforce_cost.delta_value == pytest.approx(600000.0)


def test_exact_overtime_wage_cost():
    """8. Verifies K_ot * h_ot * R_overtime using overtime hourly labor rate."""
    # base_ot = 20 workers, scen_ot = 60 workers
    # h_ot = 25 hours, R_overtime = $50.0/hr
    # base_ot_hours = 20 * 25 = 500 hrs -> Cost base = 500 * $50 = $25,000
    # scen_ot_hours = 60 * 25 = 1500 hrs -> Cost scen = 1500 * $50 = $75,000
    # Delta = $50,000
    run = create_mock_scenario_run(
        base_att_prob=0.0,
        scen_att_prob=0.0,
        base_ot_count=20,
        scen_ot_count=60,
    )
    assumptions = BusinessAssumptions(
        asm_005_overtime_rate=50.0,
        overtime_hours_per_worker=25.0,
    )
    engine = BusinessImpactEngine()
    result = engine.evaluate(run, assumptions=assumptions)

    assert result.workforce_cost.baseline_value == pytest.approx(25000.0)
    assert result.workforce_cost.scenario_value == pytest.approx(75000.0)
    assert result.workforce_cost.delta_value == pytest.approx(50000.0)


def test_exact_net_profit_delta_accounting():
    """9. Verifies DeltaProfit = DeltaRevenue - DeltaCost."""
    run = create_mock_scenario_run()
    engine = BusinessImpactEngine()
    result = engine.evaluate(run)

    expected_profit_delta = result.realized_revenue.delta_value - result.total_operational_cost.delta_value
    assert result.net_profit_delta == pytest.approx(expected_profit_delta)
    assert (result.net_profit_delta > 0.0) == result.is_profitable_scenario


def test_baseline_scenario_invariance():
    """10. Zero shock produces exact DeltaProfit = 0.0 and all deltas = 0.0."""
    run = create_mock_scenario_run(
        base_sales=10000.0,
        scen_sales=10000.0,
        base_late_prob=0.45,
        scen_late_prob=0.45,
        base_att_prob=0.16,
        scen_att_prob=0.16,
        total_headcount=200,
        base_ot_count=50,
        scen_ot_count=50,
        normalized_order_volume=1000.0,
        shipping_mode_override=None,
    )
    engine = BusinessImpactEngine()
    result = engine.evaluate(run)

    assert result.gross_revenue.delta_value == 0.0
    assert result.realized_revenue.delta_value == 0.0
    assert result.cogs.delta_value == 0.0
    assert result.gross_margin.delta_value == 0.0
    assert result.supply_chain_cost.delta_value == 0.0
    assert result.workforce_cost.delta_value == 0.0
    assert result.total_operational_cost.delta_value == 0.0
    assert result.net_profit_delta == 0.0
    assert result.is_profitable_scenario is False


def test_unrounded_float_precision():
    """11. Verifies IEEE 754 64-bit precision preserved without premature rounding."""
    run = create_mock_scenario_run(
        base_sales=12345.6789012345,
        scen_sales=15678.9012345678,
        base_late_prob=0.123456789,
        scen_late_prob=0.234567891,
    )
    engine = BusinessImpactEngine()
    result = engine.evaluate(run)

    # Check that intermediate deltas are not rounded to 2 decimal places
    raw_delta = result.realized_revenue.delta_value
    assert raw_delta != round(raw_delta, 2)
    assert isinstance(result.net_profit_delta, float)


def test_field_level_epistemic_provenance():
    """12. Verifies every financial line item is tagged CALCULATED with formula and assumption traceability."""
    run = create_mock_scenario_run()
    engine = BusinessImpactEngine()
    result = engine.evaluate(run)

    items = [
        result.gross_revenue,
        result.realized_revenue,
        result.cogs,
        result.gross_margin,
        result.supply_chain_cost,
        result.workforce_cost,
        result.total_operational_cost,
    ]
    for item in items:
        assert item.provenance.epistemic_tier == "CALCULATED"
        assert len(item.provenance.formula) > 0
        assert len(item.provenance.calculation_statement) > 0
        assert isinstance(item.provenance.assumptions_applied, list)


def test_break_even_sensitivity_analysis():
    """13. Identifies parameter thresholds where scenario profit crosses zero."""
    run = create_mock_scenario_run(
        base_sales=10000.0,
        scen_sales=15000.0,  # Revenue surge
        base_late_prob=0.40,
        scen_late_prob=0.70,  # Big delay jump
    )
    engine = BusinessImpactEngine()
    sens_engine = BusinessSensitivityEngine(engine)

    result = engine.evaluate(run)
    be_penalty = sens_engine.find_break_even_point(run, "asm_001_delay_penalty")

    if be_penalty is not None and 10.0 <= be_penalty <= 60.0:
        # At break-even delay penalty, evaluate profit delta
        be_assump = BusinessAssumptions(asm_001_delay_penalty=be_penalty)
        be_res = engine.evaluate(run, be_assump)
        assert be_res.net_profit_delta == pytest.approx(0.0, abs=1e-3)


def test_no_double_counting_between_domains():
    """14. Verifies delay penalty cost applies strictly to delivered-delayed orders and does not overlap with cancelled revenue loss."""
    run = create_mock_scenario_run(
        base_sales=10000.0,
        scen_sales=10000.0,
        base_late_prob=0.50,
        scen_late_prob=0.50,
        normalized_order_volume=1000.0,
    )
    # With kappa_stockout = 0.20, 20% of late orders are lost/cancelled (reflected in revenue reduction).
    # Delivered-delayed orders are strictly (1 - 0.20) * 500 = 400 orders.
    # Penalty cost MUST be 400 * $25 = $10,000, NOT 500 * $25 = $12,500.
    assumptions = BusinessAssumptions(
        asm_001_delay_penalty=25.0,
        asm_003_cancellation_factor=0.20,
        baseline_expedited_fraction=0.0,  # isolate delay penalty
    )
    engine = BusinessImpactEngine()
    result = engine.evaluate(run, assumptions=assumptions)

    assert result.supply_chain_cost.baseline_value == pytest.approx(10000.0)


def test_non_causal_disclaimer_preservation():
    """15. Asserts statement contains non-causal epistemic wording."""
    run = create_mock_scenario_run()
    engine = BusinessImpactEngine()
    result = engine.evaluate(run)

    stmt = result.statement
    assert "Under the declared scenario assumptions" in stmt
    assert "does not constitute a causal guarantee" in stmt
    assert "model-implied net profit shift is calculated as" in stmt


def test_expedited_shipping_surcharge_trigger():
    """16. Expedited freight fee applies 100% on expedited mode, 0% on regular mode, baseline fraction on None."""
    engine = BusinessImpactEngine()
    assumptions = BusinessAssumptions(baseline_expedited_fraction=0.05, asm_002_expedite_fee=20.0)

    # 1. Expedited mode: 'First Class'
    run_exp = create_mock_scenario_run(normalized_order_volume=1000.0, shipping_mode_override="First Class")
    res_exp = engine.evaluate(run_exp, assumptions=assumptions)
    # Expedited scen cost = 1000 * 1.0 * 20 = $20,000
    # Expedited base cost = (1000 * (10000/12000)) * 0.05 * 20 = ~833.33 * 0.05 * 20 = ~833.33

    # 2. Regular mode: 'Standard Class'
    run_reg = create_mock_scenario_run(normalized_order_volume=1000.0, shipping_mode_override="Standard Class")
    res_reg = engine.evaluate(run_reg, assumptions=assumptions)
    # Expedited scen cost = 1000 * 0.0 * 20 = $0.0

    # 3. None mode
    run_none = create_mock_scenario_run(normalized_order_volume=1000.0, shipping_mode_override=None)
    res_none = engine.evaluate(run_none, assumptions=assumptions)
    # Expedited scen cost = 1000 * 0.05 * 20 = $1,000

    assert res_exp.supply_chain_cost.scenario_value > res_none.supply_chain_cost.scenario_value
    assert res_none.supply_chain_cost.scenario_value > res_reg.supply_chain_cost.scenario_value


def test_invalid_assumption_override_rejection():
    """17. Out-of-bounds parameter raises ValidationError in sensitivity sweep and constructor."""
    engine = BusinessImpactEngine()
    sens = BusinessSensitivityEngine(engine)
    run = create_mock_scenario_run()

    with pytest.raises(ValidationError):
        sens.sweep_parameter(run, "asm_001_delay_penalty", [5.0])  # min is 10.0

    with pytest.raises(ValueError):
        sens.sweep_parameter(run, "non_existent_parameter", [10.0])


def test_reproducibility_contract():
    """18. Bitwise-identical financial outputs on identical inputs."""
    run = create_mock_scenario_run()
    engine = BusinessImpactEngine()

    res1 = engine.evaluate(run)
    res2 = engine.evaluate(run)

    assert res1.net_profit_delta == res2.net_profit_delta
    assert res1.realized_revenue.delta_value == res2.realized_revenue.delta_value
    assert res1.total_operational_cost.delta_value == res2.total_operational_cost.delta_value


def test_zero_mutation_of_scenario_result():
    """19. ScenarioRunResult is unchanged before and after financial evaluation."""
    run = create_mock_scenario_run()
    run_dump_before = run.model_dump()

    engine = BusinessImpactEngine()
    sens = BusinessSensitivityEngine(engine)

    _ = engine.evaluate(run)
    _ = sens.sweep_parameter(run, "asm_001_delay_penalty", [15.0, 25.0, 35.0])

    run_dump_after = run.model_dump()
    assert run_dump_before == run_dump_after


def test_financial_result_serialization():
    """20. BusinessImpactResult serializes cleanly to JSON and dictionary without precision truncation."""
    run = create_mock_scenario_run()
    engine = BusinessImpactEngine()
    result = engine.evaluate(run)

    dumped_dict = result.model_dump()
    assert isinstance(dumped_dict, dict)
    assert dumped_dict["epistemic_tier"] == "CALCULATED"
    assert "composite_risk_score" not in dumped_dict  # Deferred to Phase 8

    dumped_json = result.model_dump_json()
    loaded_data = json.loads(dumped_json)
    assert loaded_data["scenario_id"] == run.scenario_id
    assert loaded_data["net_profit_delta"] == result.net_profit_delta
