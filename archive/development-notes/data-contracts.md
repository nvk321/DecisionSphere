# DecisionSphere — Data Contracts & Schema Specifications

To guarantee system stability, prevent type drift, and decouple backend services from client UI components, DecisionSphere defines explicit data contracts.

---

## 1. Scenario Input Contract (`ScenarioInputSchema`)

Defines the parameters submitted by the frontend client to initiate a simulation run:

```json
{
  "scenario_name": "Q4 Holiday Surge with Supplier Logistics Delay",
  "description": "Evaluating 25% demand spike combined with a 5-day supplier shipping delay.",
  "parameters": {
    "demand": {
      "growth_percentage": 25.0,
      "promotion_active": true,
      "target_store_id": null,
      "target_product_family": "GROCERY I"
    },
    "supply_chain": {
      "delay_offset_days": 5,
      "shipping_mode": "Standard Class",
      "order_volume_multiplier": 1.25,
      "expedited_shipping": false
    },
    "workforce": {
      "overtime_workforce_pct": 35.0,
      "attrition_rate_shock": 0.05,
      "temporary_hiring_budget": 15000.0
    }
  }
}
```

### Parameter Validation Rules:
- `demand.growth_percentage`: Float between `-50.0` and `+150.0`.
- `supply_chain.delay_offset_days`: Integer between `0` and `30`.
- `supply_chain.order_volume_multiplier`: Float between `0.5` and `3.0`.
- `workforce.overtime_workforce_pct`: Float between `0.0` and `100.0`.
- `workforce.attrition_rate_shock`: Float between `0.0` and `0.30`.

---

## 2. Model Prediction Outputs

### 2.1 Demand Forecast Output (`DemandForecastResult`)
```json
{
  "horizon_days": 30,
  "baseline_forecast_units": 125400,
  "simulated_forecast_units": 156750,
  "delta_units": 31350,
  "delta_percentage": 25.0,
  "daily_timeline": [
    {
      "date": "2026-10-01",
      "baseline": 4180,
      "simulated": 5225,
      "confidence_lower": 4850,
      "confidence_upper": 5600
    }
  ],
  "model_version": "xgb-demand-v1.0"
}
```

### 2.2 Supply Chain Risk Output (`SupplyChainRiskResult`)
```json
{
  "baseline_late_delivery_risk": 0.54,
  "simulated_late_delivery_risk": 0.78,
  "risk_category": "HIGH",
  "expected_delayed_orders_pct": 78.0,
  "contributing_factors": [
    { "factor": "Days for shipment (scheduled)", "impact": "+0.32" },
    { "factor": "Order Item Quantity", "impact": "+0.18" },
    { "factor": "Shipping Mode (Standard)", "impact": "+0.12" }
  ],
  "model_version": "rf-supplychain-v1.0"
}
```

### 2.3 Workforce Risk Output (`WorkforceRiskResult`)
```json
{
  "baseline_attrition_probability": 0.16,
  "simulated_attrition_probability": 0.28,
  "risk_category": "MEDIUM-HIGH",
  "projected_turnover_headcount": 14,
  "primary_drivers": [
    { "feature": "OverTime", "importance": 0.38 },
    { "feature": "WorkLifeBalance", "importance": -0.24 },
    { "feature": "JobSatisfaction", "importance": -0.19 }
  ],
  "model_version": "gb-hr-v1.0"
}
```

---

## 3. Business Impact Contract (`BusinessImpactResult`)

```json
{
  "financials": {
    "projected_gross_revenue": 313500.0,
    "revenue_gain_vs_baseline": 62700.0,
    "projected_cost_breakdown": {
      "base_procurement_cost": 188100.0,
      "late_delivery_penalties": 14500.0,
      "expedited_freight_surcharges": 8200.0,
      "workforce_overtime_turnover_cost": 16800.0
    },
    "total_additional_operational_cost": 39500.0,
    "net_incremental_profit": 23200.0,
    "profit_margin_pct": 7.4
  },
  "operational_indices": {
    "composite_risk_score": 72.5,
    "supply_chain_bottleneck_index": 82.0,
    "workforce_burnout_index": 68.0
  }
}
```

---

## 4. Recommendation Output Contract (`RecommendationResult`)

```json
{
  "strategic_summary": "Simulated promotional campaign increases revenue by $62.7k, but high supply chain risk (78%) and elevated overtime will incur $39.5k in penalty and churn costs.",
  "recommended_actions": [
    {
      "domain": "Supply Chain",
      "priority": "HIGH",
      "action": "Shift high-priority orders from Standard Class to First Class freight to reduce late delivery probability by an estimated 24%."
    },
    {
      "domain": "Workforce",
      "priority": "MEDIUM",
      "action": "Allocate $8,000 for temporary contract staffing to mitigate overtime spikes and suppress employee turnover risk."
    },
    {
      "domain": "Procurement",
      "priority": "MEDIUM",
      "action": "Advance inventory reorder points by 7 business days to absorb promotional demand shocks."
    }
  ],
  "trade_off_analysis": "Executing the promotion without logistical mitigations reduces expected margin by 63% due to delay penalties and turnover costs."
}
```
