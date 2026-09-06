"""
Extracts the exact authoritative values for the canonical Review 2 scenario.
"""
import sys
sys.path.insert(0, ".")
from src.scenario.schema import ScenarioLevers
from src.scenario.engine import ScenarioEngine
from src.business.engine import BusinessImpactEngine
from src.recommendation.engine import RecommendationEngine

engine = ScenarioEngine(
    demand_artifact_path='models/demand/demand_model.joblib',
    supply_artifact_path='models/supply_chain/supply_chain_model.joblib',
    workforce_artifact_path='models/workforce/workforce_model.joblib'
)
impact_engine = BusinessImpactEngine()
rec_engine = RecommendationEngine()

# Canonical Review 2 Scenario
levers = ScenarioLevers(
    scenario_id='canonical_review_2',
    scenario_name='Review 2 Canonical: +15% Demand, Standard SLA, 40% Overtime',
    demand_growth_pct=15.0,
    promo_active=True,
    scheduled_days_offset=0,
    shipping_mode_override='Standard Class',
    overtime_workforce_pct=40.0,
    salary_hike_override=None
)

s = engine.run_scenario(levers=levers)
i = impact_engine.evaluate(s)
r = rec_engine.evaluate(s, i)

d_pct = (s.demand_result.delta_value / s.demand_result.baseline_value) * 100

print("=== EXACT CANONICAL REVIEW 2 RUN VALUES ===")
print(f"Demand Baseline Units      : {s.demand_result.baseline_value:,.2f}")
print(f"Demand Scenario Units      : {s.demand_result.scenario_value:,.2f}")
print(f"Demand Delta Units         : {s.demand_result.delta_value:+,.2f} ({d_pct:+.2f}%)")
print(f"Late Delivery Baseline Rate: {s.supply_chain_result.baseline_value*100:.2f}%")
print(f"Late Delivery Scenario Rate: {s.supply_chain_result.scenario_value*100:.2f}%")
print(f"Late Delivery Delta Rate   : {s.supply_chain_result.delta_value*100:+.2f} pp")
print(f"Attrition Baseline Rate    : {s.workforce_result.baseline_value*100:.2f}%")
print(f"Attrition Scenario Rate    : {s.workforce_result.scenario_value*100:.2f}%")
print(f"Attrition Delta Rate       : {s.workforce_result.delta_value*100:+.2f} pp")
print("--------------------------------------------------")
print(f"Gross Revenue Delta        : ${i.gross_revenue.delta_value:+,.2f}")
print(f"Realized Revenue Delta     : ${i.realized_revenue.delta_value:+,.2f}")
print(f"COGS Delta                 : ${i.cogs.delta_value:+,.2f}")
print(f"Logistics Cost Delta       : ${i.supply_chain_cost.delta_value:+,.2f}")
print(f"Workforce Cost Delta       : ${i.workforce_cost.delta_value:+,.2f}")
print(f"Net Profit Delta           : ${i.net_profit_delta:+,.2f}")
print("--------------------------------------------------")
print(f"Decision Category          : {r.decision_category.value}")
print(f"Composite Risk Score       : {r.composite_risk.composite_risk_score:.2f}")
print(f"Risk Level                 : {r.composite_risk.risk_level}")
print(f"Supply Strain Sub-score    : {r.composite_risk.supply_chain_risk_score:.2f}")
print(f"Workforce Strain Sub-score : {r.composite_risk.workforce_risk_score:.2f}")
print(f"Demand Strain Sub-score    : {r.composite_risk.demand_execution_risk_score:.2f}")
print(f"Executive Briefing         : {r.executive_briefing}")
print("Triggered Strategic Actions:")
for a in r.recommended_actions:
    print(f"  - [{a.trigger_rule_id}] {a.action_id}: {a.title} ({a.severity.value})")
