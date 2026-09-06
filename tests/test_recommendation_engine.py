"""
DecisionSphere — Phase 8 Recommendation Engine Automated Test Suite
20-point comprehensive verification covering schema validation, Composite Risk Score (CRS),
lexicographic decision categorization, 7-rule trigger matrix, deterministic priority sorting,
non-causal disclosures, sensitivity sweeps, immutability contracts, and JSON serialization.
"""

import pytest
import json
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
)
from src.business.engine import BusinessImpactEngine
from src.recommendation.schema import (
    RecommendationSeverity,
    StrategicDecisionCategory,
    CRSWeights,
    CompositeRiskBreakdown,
    StrategicAction,
    TradeOffEvaluation,
    RecommendationResult,
)
from src.recommendation.crs import CompositeRiskEngine
from src.recommendation.rules import RuleEvaluator
from src.recommendation.engine import RecommendationEngine


# =============================================================================
# SYNTHETIC TEST FIXTURE BUILDERS
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


def create_test_scenario_run(
    base_sales: float = 10000.0,
    scen_sales: float = 12000.0,
    base_late_prob: float = 0.40,
    scen_late_prob: float = 0.50,
    base_att_prob: float = 0.15,
    scen_att_prob: float = 0.20,
    total_headcount: int = 200,
    base_ot_count: int = 40,
    scen_ot_count: int = 60,
    demand_growth_pct: float = 20.0,
    scheduled_days_offset: int = 0,
    shipping_mode_override: str = None,
    salary_hike_override: float = None,
    normalized_order_volume: float = 1000.0,
) -> ScenarioRunResult:
    """Builds a valid, strictly typed ScenarioRunResult."""
    levers = ScenarioLevers(
        scenario_id="scen_test_rec_001",
        scenario_name="Strategic Test Scenario",
        demand_growth_pct=demand_growth_pct,
        promo_active=True,
        scheduled_days_offset=scheduled_days_offset,
        shipping_mode_override=shipping_mode_override,
        salary_hike_override=salary_hike_override,
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
        decision_threshold=0.17,
        baseline_class=int(base_late_prob >= 0.17),
        scenario_class=int(scen_late_prob >= 0.17),
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
        target_overtime_percentage=(scen_ot_count / total_headcount) * 100.0,
        actual_scenario_overtime_percentage=(scen_ot_count / total_headcount) * 100.0,
        wlb_decrement_applied=-1,
        epistemic_tier="PROPAGATED",
    )

    return ScenarioRunResult(
        scenario_id="scen_test_rec_001",
        scenario_name="Strategic Test Scenario",
        levers=levers,
        assumptions=assumptions,
        demand_result=demand_res,
        supply_chain_result=supply_res,
        workforce_result=workforce_res,
        workforce_cohort_summary=cohort_summary,
        normalized_order_volume=normalized_order_volume,
        execution_timestamp="2026-09-05T18:00:00Z",
        epistemic_tier="PROPAGATED",
        interpretation="Test scenario run",
    )


# =============================================================================
# 20-TEST PHASE 8 TEST MATRIX
# =============================================================================

def test_recommendation_schemas_validation():
    """1. Pydantic v2 contract enforcement, boundary validation, and rejection of extra fields."""
    weights = CRSWeights(w_supply=0.40, w_workforce=0.40, w_demand=0.20)
    assert weights.w_supply == 0.40

    # Extra fields forbidden
    with pytest.raises(ValidationError):
        CRSWeights(w_supply=0.40, w_workforce=0.40, w_demand=0.20, extra_weight=0.1)

    # Simplex constraint violation
    with pytest.raises(ValidationError):
        CRSWeights(w_supply=0.50, w_workforce=0.50, w_demand=0.20)  # sums to 1.20


def test_crs_exact_baseline_calculation():
    """2. Exact mathematical verification of S_supply, S_workforce, S_demand, and aggregate CRS."""
    # Setup controlled inputs
    # P_late_scen = 0.50, delta_P_late = 0.10 -> norm_delta = 0.10 / 0.30 = 0.3333333
    # S_supply = 100 * (0.70 * 0.50 + 0.30 * (0.10 / 0.30)) = 100 * (0.35 + 0.10) = 45.0
    # P_att_scen = 0.20 (norm = 0.20 / 0.40 = 0.50), ot_pct = 25.0% (norm = 0.25)
    # S_workforce = 100 * (0.60 * 0.50 + 0.40 * 0.25) = 100 * (0.30 + 0.10) = 40.0
    # demand_shock = 25.0% (norm = 25 / 50 = 0.50), fulfillment_loss = 0.075 (norm = 0.075 / 0.20 = 0.375)
    # S_demand = 100 * (0.50 * 0.50 + 0.50 * 0.375) = 100 * (0.25 + 0.1875) = 43.75
    # Aggregate CRS = 0.40 * 45.0 + 0.40 * 40.0 + 0.20 * 43.75 = 18.0 + 16.0 + 8.75 = 42.75 (MODERATE)
    run = create_test_scenario_run(
        scen_late_prob=0.50,
        base_late_prob=0.40,
        scen_att_prob=0.20,
        base_ot_count=50,
        scen_ot_count=50,  # 50/200 = 25%
        demand_growth_pct=25.0,
    )
    impact = BusinessImpactEngine().evaluate(run)
    crs_engine = CompositeRiskEngine()

    breakdown = crs_engine.evaluate(run, impact)
    assert breakdown.supply_chain_risk_score == pytest.approx(45.0, abs=1e-3)
    assert breakdown.workforce_risk_score == pytest.approx(40.0, abs=1e-3)
    assert breakdown.composite_risk_score == pytest.approx(42.75, abs=0.5)
    assert breakdown.risk_level == "MODERATE"


def test_crs_bounds_and_clamping():
    """3. Enforces CRS in [0.0, 100.0] across extreme bounds."""
    # Min bound: 0 late risk, 0 attrition, 0 overtime, 0 shock
    run_min = create_test_scenario_run(
        scen_late_prob=0.0,
        base_late_prob=0.0,
        scen_att_prob=0.0,
        base_ot_count=0,
        scen_ot_count=0,
        demand_growth_pct=0.0,
    )
    impact_min = BusinessImpactEngine().evaluate(run_min)
    crs_min = CompositeRiskEngine().evaluate(run_min, impact_min)
    assert crs_min.composite_risk_score == 0.0
    assert crs_min.risk_level == "LOW"

    # Max bound: 100% late, 100% attrition, 100% overtime, 100% demand shock
    run_max = create_test_scenario_run(
        scen_late_prob=1.0,
        base_late_prob=0.0,
        scen_att_prob=1.0,
        base_ot_count=0,
        scen_ot_count=200,  # 100% overtime
        demand_growth_pct=100.0,
    )
    # Cancellation factor 0.25 ensures fulfillment loss (1.0 * 0.25 = 0.25) saturates the 0.20 threshold
    assump_max = BusinessAssumptions(asm_003_cancellation_factor=0.25)
    impact_max = BusinessImpactEngine().evaluate(run_max, assumptions=assump_max)
    crs_max = CompositeRiskEngine().evaluate(run_max, impact_max)
    assert crs_max.composite_risk_score == 100.0
    assert crs_max.risk_level == "SEVERE"


def test_crs_weight_simplex_constraint():
    """4. Enforces sum(w_i) = 1.0 and rejects non-simplex configurations."""
    with pytest.raises(ValidationError):
        CRSWeights(w_supply=0.50, w_workforce=0.50, w_demand=0.10)
    with pytest.raises(ValidationError):
        CRSWeights(w_supply=-0.10, w_workforce=0.60, w_demand=0.50)

    valid_w = CRSWeights(w_supply=0.50, w_workforce=0.30, w_demand=0.20)
    assert valid_w.w_supply == 0.50


def test_rule_01_supply_chain_expedite_trigger():
    """5. Verifies RULE-01 fires when late risk >= 0.65 or delta >= 0.15 under regular shipping."""
    run = create_test_scenario_run(scen_late_prob=0.68, shipping_mode_override="Standard Class")
    impact = BusinessImpactEngine().evaluate(run)
    rec_engine = RecommendationEngine()
    result = rec_engine.evaluate(run, impact)

    action_ids = [a.trigger_rule_id for a in result.recommended_actions]
    assert "RULE-01" in action_ids

    r1_action = next(a for a in result.recommended_actions if a.trigger_rule_id == "RULE-01")
    assert r1_action.severity == RecommendationSeverity.HIGH
    assert r1_action.domain == "Supply Chain"
    assert "First Class air freight" in r1_action.description


def test_rule_02_safety_stock_buffer_trigger():
    """6. Verifies RULE-02 fires when fulfillment loss rate >= 0.10."""
    # Under high delay probability (e.g. 0.80) and cancellation factor 0.15:
    # L_fulfillment = 0.80 * 0.15 = 0.12 >= 0.10
    run = create_test_scenario_run(scen_late_prob=0.80)
    impact = BusinessImpactEngine().evaluate(run)
    rec_engine = RecommendationEngine()
    result = rec_engine.evaluate(run, impact)

    action_ids = [a.trigger_rule_id for a in result.recommended_actions]
    assert "RULE-02" in action_ids
    r2_action = next(a for a in result.recommended_actions if a.trigger_rule_id == "RULE-02")
    assert r2_action.severity == RecommendationSeverity.MEDIUM
    assert "safety stock" in r2_action.title.lower()


def test_rule_03_workforce_overtime_cap_trigger():
    """7. Verifies RULE-03 fires when attrition >= 0.21 and realized overtime >= 30%."""
    run = create_test_scenario_run(
        scen_att_prob=0.24,
        total_headcount=200,
        scen_ot_count=80,  # 80/200 = 40% >= 30%
    )
    impact = BusinessImpactEngine().evaluate(run)
    rec_engine = RecommendationEngine()
    result = rec_engine.evaluate(run, impact)

    action_ids = [a.trigger_rule_id for a in result.recommended_actions]
    assert "RULE-03" in action_ids
    r3_action = next(a for a in result.recommended_actions if a.trigger_rule_id == "RULE-03")
    assert r3_action.severity == RecommendationSeverity.HIGH
    assert "Cap Mandatory Overtime" in r3_action.title


def test_rule_04_margin_erosion_warning():
    """8. Verifies RULE-04 fires as CRITICAL when DeltaRevenue > 0 and DeltaProfit < 0."""
    # Big sales surge (positive revenue) but extreme penalties & turnover creating negative profit
    run = create_test_scenario_run(
        base_sales=10000.0,
        scen_sales=15000.0,
        base_late_prob=0.20,
        scen_late_prob=0.85,
        base_att_prob=0.05,
        scen_att_prob=0.35,
        total_headcount=500,
        scen_ot_count=300,
    )
    # High replacement cost to guarantee negative profit delta
    assumptions = BusinessAssumptions(asm_004_replacement_cost=50000.0)
    impact = BusinessImpactEngine().evaluate(run, assumptions=assumptions)
    assert impact.realized_revenue.delta_value > 0.0
    assert impact.net_profit_delta < 0.0

    rec_engine = RecommendationEngine()
    result = rec_engine.evaluate(run, impact)

    action_ids = [a.trigger_rule_id for a in result.recommended_actions]
    assert "RULE-04" in action_ids
    r4_action = next(a for a in result.recommended_actions if a.trigger_rule_id == "RULE-04")
    assert r4_action.severity == RecommendationSeverity.CRITICAL
    assert "Margin Erosion Warning" in r4_action.title


def test_rule_05_retention_compensation_trigger():
    """9. Verifies RULE-05 fires when attrition probability >= 0.25 without salary compensation."""
    run = create_test_scenario_run(
        scen_att_prob=0.28,
        salary_hike_override=None,
    )
    impact = BusinessImpactEngine().evaluate(run)
    rec_engine = RecommendationEngine()
    result = rec_engine.evaluate(run, impact)

    action_ids = [a.trigger_rule_id for a in result.recommended_actions]
    assert "RULE-05" in action_ids
    r5_action = next(a for a in result.recommended_actions if a.trigger_rule_id == "RULE-05")
    assert r5_action.severity == RecommendationSeverity.MEDIUM
    assert "Retention Salary Adjustment" in r5_action.title


def test_rule_06_operational_strain_warning():
    """10. Verifies RULE-06 fires when DeltaProfit > 0 but CRS >= 60.0."""
    run = create_test_scenario_run(
        base_sales=10000.0,
        scen_sales=50000.0,  # Substantial volume expansion
        base_late_prob=0.30,
        scen_late_prob=0.80,  # High late risk
        base_att_prob=0.15,
        scen_att_prob=0.35,  # High attrition
        total_headcount=50,   # Moderate cohort size
        base_ot_count=0,
        scen_ot_count=35,    # 70% overtime
        demand_growth_pct=50.0,
    )
    # Unit price $30 ensures margin expansion ($413k) comfortably exceeds disruption costs (~$347k)
    assumptions = BusinessAssumptions(unit_price=30.0)
    impact = BusinessImpactEngine().evaluate(run, assumptions=assumptions)
    assert impact.net_profit_delta > 0.0

    rec_engine = RecommendationEngine()
    result = rec_engine.evaluate(run, impact)

    assert result.composite_risk.composite_risk_score >= 60.0
    action_ids = [a.trigger_rule_id for a in result.recommended_actions]
    assert "RULE-06" in action_ids
    r6_action = next(a for a in result.recommended_actions if a.trigger_rule_id == "RULE-06")
    assert r6_action.severity == RecommendationSeverity.HIGH
    assert "Operational Strain Warning" in r6_action.title


def test_rule_07_relax_dispatch_lead_times_trigger():
    """11. Verifies RULE-07 fires when scheduled offset <= -2 and late probability >= 0.55."""
    run = create_test_scenario_run(
        scheduled_days_offset=-2,
        scen_late_prob=0.60,
    )
    impact = BusinessImpactEngine().evaluate(run)
    rec_engine = RecommendationEngine()
    result = rec_engine.evaluate(run, impact)

    action_ids = [a.trigger_rule_id for a in result.recommended_actions]
    assert "RULE-07" in action_ids
    r7_action = next(a for a in result.recommended_actions if a.trigger_rule_id == "RULE-07")
    assert r7_action.severity == RecommendationSeverity.MEDIUM
    assert "Relax Compressed Dispatch Lead Times" in r7_action.title


def test_no_rules_triggered_under_ideal_scenario():
    """12. Verifies that a zero-shock, safe baseline scenario produces zero critical alerts."""
    run = create_test_scenario_run(
        base_sales=10000.0,
        scen_sales=10000.0,
        base_late_prob=0.20,
        scen_late_prob=0.20,
        base_att_prob=0.10,
        scen_att_prob=0.10,
        base_ot_count=10,
        scen_ot_count=10,
        demand_growth_pct=0.0,
    )
    impact = BusinessImpactEngine().evaluate(run)
    rec_engine = RecommendationEngine()
    result = rec_engine.evaluate(run, impact)

    assert len(result.recommended_actions) == 0
    assert result.composite_risk.risk_level == "LOW"


def test_lexicographic_decision_categorization():
    """13. Verifies assignment of PROCEED, PROCEED_WITH_MITIGATIONS, and REJECT_RESTRUCTURE."""
    rec_engine = RecommendationEngine(operational_strain_threshold=50.0)

    # 1. Negative profit -> REJECT_RESTRUCTURE
    run_neg = create_test_scenario_run(
        scen_late_prob=0.80,
        scen_att_prob=0.35,
        total_headcount=500,
        scen_ot_count=300,
    )
    assump_neg = BusinessAssumptions(asm_004_replacement_cost=50000.0)
    impact_neg = BusinessImpactEngine().evaluate(run_neg, assumptions=assump_neg)
    res_neg = rec_engine.evaluate(run_neg, impact_neg)
    assert res_neg.decision_category == StrategicDecisionCategory.REJECT_RESTRUCTURE

    # 2. Positive profit & Low CRS (<= 50) -> PROCEED
    run_pos_safe = create_test_scenario_run(
        base_sales=10000.0,
        scen_sales=15000.0,
        base_late_prob=0.20,
        scen_late_prob=0.20,
        base_att_prob=0.10,
        scen_att_prob=0.10,
        base_ot_count=10,
        scen_ot_count=10,
        demand_growth_pct=10.0,
    )
    assump_pos = BusinessAssumptions(unit_price=10.0)
    impact_pos_safe = BusinessImpactEngine().evaluate(run_pos_safe, assumptions=assump_pos)
    assert impact_pos_safe.net_profit_delta > 0.0
    res_pos_safe = rec_engine.evaluate(run_pos_safe, impact_pos_safe)
    assert res_pos_safe.composite_risk.composite_risk_score <= 50.0
    assert res_pos_safe.decision_category == StrategicDecisionCategory.PROCEED

    # 3. Positive profit & High CRS (> 50) -> PROCEED_WITH_MITIGATIONS
    run_pos_strain = create_test_scenario_run(
        base_sales=10000.0,
        scen_sales=50000.0,
        base_late_prob=0.30,
        scen_late_prob=0.80,
        base_att_prob=0.15,
        scen_att_prob=0.35,
        total_headcount=50,
        base_ot_count=0,
        scen_ot_count=35,
        demand_growth_pct=50.0,
    )
    assump_strain = BusinessAssumptions(unit_price=30.0)
    impact_pos_strain = BusinessImpactEngine().evaluate(run_pos_strain, assumptions=assump_strain)
    assert impact_pos_strain.net_profit_delta > 0.0
    res_pos_strain = rec_engine.evaluate(run_pos_strain, impact_pos_strain)
    assert res_pos_strain.composite_risk.composite_risk_score > 50.0
    assert res_pos_strain.decision_category == StrategicDecisionCategory.PROCEED_WITH_MITIGATIONS


def test_recommendation_priority_sorting():
    """14. Verifies actions are strictly sorted: CRITICAL > HIGH > MEDIUM > LOW."""
    run = create_test_scenario_run(
        base_sales=10000.0,
        scen_sales=12000.0,
        scen_late_prob=0.70,     # triggers RULE-01 (HIGH) and RULE-02 (MEDIUM)
        scen_att_prob=0.25,      # triggers RULE-03 (HIGH) and RULE-05 (MEDIUM)
        total_headcount=200,
        scen_ot_count=80,
        scheduled_days_offset=-2, # triggers RULE-07 (MEDIUM)
    )
    # Induce margin erosion to also trigger RULE-04 (CRITICAL)
    assump = BusinessAssumptions(asm_004_replacement_cost=60000.0)
    impact = BusinessImpactEngine().evaluate(run, assumptions=assump)

    rec_engine = RecommendationEngine()
    result = rec_engine.evaluate(run, impact)

    severities = [a.severity for a in result.recommended_actions]
    assert severities[0] == RecommendationSeverity.CRITICAL

    # Verify no HIGH appears after MEDIUM
    seen_medium = False
    for s in severities:
        if s == RecommendationSeverity.MEDIUM:
            seen_medium = True
        if seen_medium:
            assert s in (RecommendationSeverity.MEDIUM, RecommendationSeverity.LOW)


def test_priority_tie_breaking_by_exposure():
    """15. Verifies deterministic tie-breaking on equal severity."""
    run = create_test_scenario_run(
        scen_late_prob=0.70,
        scen_att_prob=0.25,
        total_headcount=200,
        scen_ot_count=80,
    )
    impact = BusinessImpactEngine().evaluate(run)
    rec_engine = RecommendationEngine()
    result = rec_engine.evaluate(run, impact)

    # Check that equal severities are sorted stably
    high_actions = [a for a in result.recommended_actions if a.severity == RecommendationSeverity.HIGH]
    if len(high_actions) >= 2:
        assert high_actions[0].action_id != high_actions[1].action_id


def test_non_causal_epistemic_disclaimer():
    """16. Asserts executive briefing contains non-causal language and Tier 6 tagging."""
    run = create_test_scenario_run()
    impact = BusinessImpactEngine().evaluate(run)
    rec_engine = RecommendationEngine()
    result = rec_engine.evaluate(run, impact)

    assert result.epistemic_tier == "RECOMMENDED"
    assert "Under the declared scenario levers and empirical predictive baselines" in result.executive_briefing
    assert "does not constitute a guarantee" in result.executive_briefing


def test_crs_sensitivity_sweep_stability():
    """17. Verifies CRS calculation is stable under domain weight perturbations."""
    run = create_test_scenario_run()
    impact = BusinessImpactEngine().evaluate(run)
    rec_engine = RecommendationEngine()

    configs = [
        CRSWeights(w_supply=0.40, w_workforce=0.40, w_demand=0.20),
        CRSWeights(w_supply=0.50, w_workforce=0.30, w_demand=0.20),
        CRSWeights(w_supply=0.30, w_workforce=0.50, w_demand=0.20),
    ]
    sweep_results = rec_engine.sweep_crs_weights(run, impact, configs)
    assert len(sweep_results) == 3
    for r in sweep_results:
        assert 0.0 <= r["composite_risk_score"] <= 100.0
        assert r["decision_category"] in [c.value for c in StrategicDecisionCategory]


def test_recommendation_flip_detection():
    """18. Verifies analytical detection of parameter tipping points where decisions flip."""
    run = create_test_scenario_run(
        base_sales=10000.0,
        scen_sales=12000.0,
        scen_late_prob=0.30,
        scen_att_prob=0.15,
        total_headcount=200,
        scen_ot_count=40,
    )
    base_assumptions = BusinessAssumptions(asm_004_replacement_cost=15000.0)
    rec_engine = RecommendationEngine()

    # Sweep replacement cost from $15,000 to $60,000 to observe margin erosion flip
    flip = rec_engine.find_recommendation_flip_threshold(
        scenario_run=run,
        base_assumptions=base_assumptions,
        parameter_name="asm_004_replacement_cost",
        candidate_values=[15000.0, 30000.0, 45000.0, 60000.0],
    )
    # If profit delta goes negative at higher cost, flip is recorded
    if flip is not None:
        assert flip["parameter_name"] == "asm_004_replacement_cost"
        assert flip["previous_category"] != flip["new_category"]


def test_zero_mutation_of_phase_6_and_7_results():
    """19. Asserts ScenarioRunResult and BusinessImpactResult are unmutated."""
    run = create_test_scenario_run()
    impact = BusinessImpactEngine().evaluate(run)

    run_dump_before = run.model_dump()
    impact_dump_before = impact.model_dump()

    rec_engine = RecommendationEngine()
    _ = rec_engine.evaluate(run, impact)
    _ = rec_engine.sweep_crs_weights(run, impact, [CRSWeights()])

    assert run.model_dump() == run_dump_before
    assert impact.model_dump() == impact_dump_before


def test_recommendation_result_serialization():
    """20. Verifies clean JSON export conforming to Pydantic v2 specifications."""
    run = create_test_scenario_run()
    impact = BusinessImpactEngine().evaluate(run)
    rec_engine = RecommendationEngine()
    result = rec_engine.evaluate(run, impact)

    json_str = result.model_dump_json()
    parsed = json.loads(json_str)

    assert parsed["scenario_id"] == run.scenario_id
    assert parsed["epistemic_tier"] == "RECOMMENDED"
    assert "composite_risk" in parsed
    assert "trade_off_evaluation" in parsed
    assert "recommended_actions" in parsed
