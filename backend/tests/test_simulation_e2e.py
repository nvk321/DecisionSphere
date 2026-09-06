"""
End-to-End Asynchronous Simulation Lifecycle & Sensitivity Integration Tests (Gate J).
Uses httpx.AsyncClient with ASGITransport to test real HTTP-level orchestration,
multi-domain prediction cascades, financial statements, recommendation synthesis,
provenance tuples (Gate H), and parameter sweeps.
"""
from __future__ import annotations

import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_async_full_simulation_lifecycle(async_client: AsyncClient):
    """
    Gate J Verification:
    Executes full multi-domain simulation lifecycle through asynchronous HTTP endpoints:
    1. Create scenario topic and parameter version (v1).
    2. Retrieve version history and verify initial configuration.
    3. Run simulation shortcut (POST /api/v1/scenarios/{id}/run).
    4. Validate execution status and duration.
    5. Validate per-domain predictions (Demand, Supply Chain, Workforce).
    6. Validate managerial financial income statement and accounting identities.
    7. Validate synthesized recommendations, CRS decomposition, and strategic actions.
    8. Validate Gate H cryptographic audit provenance tuple.
    """
    # 1. Create Scenario
    scenario_payload = {
        "name": "E2E Strategic Promotion Expansion",
        "description": "Evaluating cross-domain impact of a 20% promotional demand lift with 15% overtime",
        "initial_levers": {
            "demand_growth_pct": 20.0,
            "promo_active": True,
            "scheduled_days_offset": 1,
            "shipping_mode_override": "Standard Class",
            "overtime_workforce_pct": 15.0,
        },
    }
    create_resp = await async_client.post("/api/v1/scenarios/", json=scenario_payload)
    assert create_resp.status_code == 201
    scenario_data = create_resp.json()
    scenario_id = scenario_data["id"]
    assert scenario_data["name"] == scenario_payload["name"]
    assert scenario_data["latest_version"] is not None
    assert scenario_data["latest_version"]["version_number"] == 1
    version_id = scenario_data["latest_version"]["id"]

    # 2. Verify Scenario Versions
    versions_resp = await async_client.get(f"/api/v1/scenarios/{scenario_id}/versions")
    assert versions_resp.status_code == 200
    versions = versions_resp.json()
    assert len(versions) == 1
    assert versions[0]["id"] == version_id
    assert versions[0]["demand_growth_pct"] == 20.0
    assert versions[0]["promo_active"] is True
    assert versions[0]["overtime_workforce_pct"] == 15.0

    # 3. Execute Simulation via Shortcut Endpoint
    run_resp = await async_client.post(f"/api/v1/scenarios/{scenario_id}/run")
    assert run_resp.status_code == 201
    run_data = run_resp.json()

    # 4. Validate Execution Status
    assert run_data["id"] is not None
    assert run_data["status"] in {"SUCCESS", "COMPLETED"}
    assert run_data["duration_ms"] is not None
    assert run_data["duration_ms"] >= 0.0

    # 5. Validate Domain Predictions (Gate 2, 3, 4 Integration)
    predictions = run_data["predictions"]
    assert len(predictions) == 3
    domain_map = {p["domain"]: p for p in predictions}

    assert "DEMAND" in domain_map
    demand_pred = domain_map["DEMAND"]
    assert demand_pred["baseline_value"] > 0.0
    assert demand_pred["scenario_value"] > 0.0
    assert demand_pred["delta_value"] > 0.0  # +20% demand growth + promo ensures positive delta
    assert demand_pred["epistemic_tier"] == "PREDICTED"

    assert "SUPPLY_CHAIN" in domain_map
    sc_pred = domain_map["SUPPLY_CHAIN"]
    assert 0.0 <= sc_pred["baseline_value"] <= 1.0
    assert 0.0 <= sc_pred["scenario_value"] <= 1.0
    assert sc_pred["epistemic_tier"] == "PREDICTED"

    assert "WORKFORCE" in domain_map
    wf_pred = domain_map["WORKFORCE"]
    assert 0.0 <= wf_pred["baseline_value"] <= 1.0
    assert 0.0 <= wf_pred["scenario_value"] <= 1.0
    assert wf_pred["epistemic_tier"] == "PREDICTED"

    # 6. Validate Managerial Accounting Financial Statement (Phase 7 Engine)
    fin = run_data["financial_result"]
    assert fin is not None
    assert fin["epistemic_tier"] == "CALCULATED"
    # Gross revenue delta must be positive with demand expansion
    assert fin["gross_revenue_delta"] > 0.0
    assert fin["realized_revenue_delta"] > 0.0
    assert fin["realized_revenue_delta"] <= fin["gross_revenue_delta"]
    assert fin["cogs_delta"] >= 0.0
    assert fin["supply_chain_cost_delta"] >= 0.0
    assert fin["workforce_cost_delta"] >= 0.0
    assert fin["total_cost_delta"] >= 0.0
    # Net profit delta identity: Realized Revenue Delta - Total Cost Delta
    expected_profit_delta = fin["realized_revenue_delta"] - fin["total_cost_delta"]
    assert abs(fin["net_profit_delta"] - expected_profit_delta) < 1e-4

    # Financial Line Items Disclosure
    assert len(fin["line_items"]) >= 5
    for item in fin["line_items"]:
        assert item["category"] in {"REVENUE", "EXPENSE", "MARGIN"}
        assert item["amount"] is not None
        assert item["epistemic_tier"] == "CALCULATED"

    # 7. Validate Recommendation Engine & Trade-Off Synthesis (Phase 8 Engine)
    rec = run_data["recommendation_result"]
    assert rec is not None
    assert rec["decision_category"] in {
        "PROCEED",
        "PROCEED_WITH_MITIGATIONS",
        "REJECT_RESTRUCTURE",
    }
    assert 0.0 <= rec["composite_risk_score"] <= 100.0
    assert rec["risk_level"] in {"LOW", "MODERATE", "HIGH", "SEVERE"}
    assert 0.0 <= rec["supply_chain_strain"] <= 100.0
    assert 0.0 <= rec["workforce_strain"] <= 100.0
    assert 0.0 <= rec["demand_strain"] <= 100.0
    assert len(rec["executive_briefing"]) > 10
    assert rec["epistemic_tier"] == "RECOMMENDED"

    for action in rec["strategic_actions"]:
        assert action["action_id"].startswith("ACT-")
        assert action["domain"] in {
            "Supply Chain",
            "Workforce",
            "Demand",
            "Financial / Strategic",
            "Executive Governance",
        }
        assert action["severity"] in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
        assert len(action["trigger_rule_id"]) > 0
        assert len(action["expected_trade_off"]) > 0
        assert action["epistemic_tier"] == "RECOMMENDED"

    # 8. Validate Gate H Provenance Signature Tuple
    audit = run_data["audit_record"]
    assert audit is not None
    pt = audit["provenance_tuple"]
    assert str(pt["scenario_version_id"]) == version_id
    assert "demand" in pt["artifact_hashes"]
    assert "supply_chain" in pt["artifact_hashes"]
    assert "workforce" in pt["artifact_hashes"]
    assert pt["policy_version"] >= 1
    assert "git_commit" in pt
    assert "app_version" in pt
    assert "python_version" in pt
    assert "timestamp" in pt


@pytest.mark.anyio
async def test_async_simulation_with_custom_policy_and_overrides(async_client: AsyncClient):
    """
    Gate J Multi-Scenario Verification:
    1. Create a custom enterprise assumption policy version with specific freight and delay penalties.
    2. Create a base scenario.
    3. Trigger simulation via POST /api/v1/simulations/run with override_levers.
    4. Confirm override_levers resulted in an auto-incremented immutable ScenarioVersion (v2).
    5. Confirm simulation detail retrieval via GET /api/v1/simulations/{run_id}.
    6. Confirm simulation listing and filtering via GET /api/v1/simulations/?scenario_id={id}.
    """
    # 1. Create custom policy version
    policy_payload = {
        "name": "Peak Freight Disruption Policy FY2026",
        "description": "Adjusted freight rates and penalty factors for peak season",
        "late_penalty_rate": 45.0,
        "expedite_fee": 30.0,
        "stockout_churn_factor": 0.25,
        "replacement_cost": 40000.0,
        "overtime_wage_rate": 60.0,
        "w_supply": 0.50,
        "w_workforce": 0.30,
        "w_demand": 0.20,
        "tau_risk": 55.0,
    }
    policy_resp = await async_client.post("/api/v1/policies/", json=policy_payload)
    assert policy_resp.status_code == 201
    custom_policy = policy_resp.json()
    policy_id = custom_policy["id"]

    # 2. Create base scenario with v1
    scenario_resp = await async_client.post(
        "/api/v1/scenarios/",
        json={"name": "Base Scenario for Policy Overrides", "initial_levers": {"demand_growth_pct": 5.0}},
    )
    assert scenario_resp.status_code == 201
    scenario = scenario_resp.json()
    scenario_id = scenario["id"]
    base_ver_id = scenario["latest_version"]["id"]

    # 3. Trigger simulation with override levers (demand_growth_pct: 35.0)
    sim_request = {
        "scenario_version_id": base_ver_id,
        "policy_id": policy_id,
        "override_levers": {
            "demand_growth_pct": 35.0,
            "promo_active": True,
            "shipping_mode_override": "First Class",
            "overtime_workforce_pct": 20.0,
        },
    }
    run_resp = await async_client.post("/api/v1/simulations/run", json=sim_request)
    assert run_resp.status_code == 201
    run_data = run_resp.json()
    run_id = run_data["id"]

    # 4. Verify that override levers created a new immutable ScenarioVersion
    assert str(run_data["policy_id"]) == policy_id
    new_version_id = str(run_data["scenario_version_id"])
    assert new_version_id != base_ver_id

    # Verify scenario versions list now has 2 versions
    vers_resp = await async_client.get(f"/api/v1/scenarios/{scenario_id}/versions")
    assert vers_resp.status_code == 200
    all_versions = vers_resp.json()
    assert len(all_versions) == 2
    assert all_versions[1]["version_number"] == 2
    assert all_versions[1]["demand_growth_pct"] == 35.0

    # 5. Verify direct retrieval of simulation run by primary key
    get_run_resp = await async_client.get(f"/api/v1/simulations/{run_id}")
    assert get_run_resp.status_code == 200
    fetched_run = get_run_resp.json()
    assert fetched_run["id"] == run_id
    assert fetched_run["scenario_version_id"] == new_version_id
    assert fetched_run["financial_result"]["gross_revenue_delta"] == run_data["financial_result"]["gross_revenue_delta"]

    # 6. Verify listing simulation runs filtered by scenario
    list_runs_resp = await async_client.get(f"/api/v1/simulations/?scenario_id={scenario_id}")
    assert list_runs_resp.status_code == 200
    runs_list = list_runs_resp.json()
    assert runs_list["total"] >= 1
    matching = [r for r in runs_list["items"] if r["id"] == run_id]
    assert len(matching) == 1
    assert matching[0]["decision_category"] is not None


@pytest.mark.anyio
async def test_async_parameter_sweeps_e2e(async_client: AsyncClient):
    """
    Gate J Sensitivity & Scientific Experiment Sweeps:
    1. Demand Shock Sensitivity Curve (Experiment B).
    2. Financial Parameter Sweep over ASM-001 (Experiment D).
    3. CRS Domain Weights Simplex Sweep.
    4. Tipping Point Binary Search.
    """
    # 1. Experiment B: Demand Shock Sweep
    demand_sweep_payload = {
        "shock_percentages": [-15.0, 0.0, 15.0, 30.0],
        "base_levers": {"demand_growth_pct": 0.0, "promo_active": False},
    }
    demand_resp = await async_client.post("/api/v1/sensitivity/demand-sweep", json=demand_sweep_payload)
    assert demand_resp.status_code == 200
    demand_items = demand_resp.json()
    assert len(demand_items) == 4

    # Verify monotonic relationship in projected sales
    projected_sales = [item["demand_forecast"] for item in demand_items]
    assert projected_sales == sorted(projected_sales)
    for item in demand_items:
        assert 0.0 <= item["late_delivery_risk"] <= 1.0
        assert 0.0 <= item["workforce_attrition_risk"] <= 1.0
        assert item["epistemic_tier"] == "PREDICTED"

    # 2. Experiment D: Financial Parameter Sweep (asm_001_delay_penalty)
    fin_sweep_payload = {
        "parameter_name": "asm_001_delay_penalty",
        "candidate_values": [15.0, 25.0, 40.0, 55.0],
    }
    fin_resp = await async_client.post("/api/v1/sensitivity/financial-sweep", json=fin_sweep_payload)
    assert fin_resp.status_code == 200
    fin_items = fin_resp.json()
    assert len(fin_items) == 4

    # As late penalty rate increases, net profit decreases monotonically
    net_profits = [item["net_profit_delta"] for item in fin_items]
    assert net_profits == sorted(net_profits, reverse=True)
    for item in fin_items:
        assert item["parameter_name"] == "asm_001_delay_penalty"
        assert item["epistemic_tier"] == "CALCULATED"

    # 3. CRS Domain Weights Simplex Sweep
    crs_sweep_payload = {
        "candidate_weights": [
            {"w_supply": 0.40, "w_workforce": 0.40, "w_demand": 0.20},
            {"w_supply": 0.60, "w_workforce": 0.20, "w_demand": 0.20},
            {"w_supply": 0.20, "w_workforce": 0.60, "w_demand": 0.20},
        ],
        "tau_risk": 50.0,
    }
    crs_resp = await async_client.post("/api/v1/sensitivity/crs-weight-sweep", json=crs_sweep_payload)
    assert crs_resp.status_code == 200
    crs_items = crs_resp.json()
    assert len(crs_items) == 3
    for item in crs_items:
        assert 0.0 <= item["composite_risk_score"] <= 100.0
        assert item["risk_level"] in {"LOW", "MODERATE", "HIGH", "SEVERE"}
        assert item["decision_category"] in {"PROCEED", "PROCEED_WITH_MITIGATIONS", "REJECT_RESTRUCTURE"}
        assert item["epistemic_tier"] == "CALCULATED"

    # 4. Tipping Point Binary Search
    tip_payload = {
        "parameter_name": "asm_001_delay_penalty",
        "candidate_values": [15.0, 25.0, 35.0, 45.0, 55.0],
    }
    tip_resp = await async_client.post("/api/v1/sensitivity/tipping-point", json=tip_payload)
    assert tip_resp.status_code == 200
    tip_data = tip_resp.json()
    assert "parameter_name" in tip_data
    assert tip_data["parameter_name"] == "asm_001_delay_penalty"
    assert tip_data["epistemic_tier"] == "RECOMMENDED"
    assert isinstance(tip_data["flip_detected"], bool)


@pytest.mark.anyio
async def test_async_concurrent_simulations_lifecycle(async_client: AsyncClient):
    """
    Gate J Concurrency & Asynchronous Isolation:
    Creates two distinct scenarios and runs simulations across them concurrently,
    verifying that anyio threadpool execution and relational persistence handle
    overlapping async requests without cross-talk or race conditions.
    """
    import anyio

    # 1. Create two independent scenarios
    scen_a_resp = await async_client.post(
        "/api/v1/scenarios/",
        json={"name": "Concurrent Scenario A", "initial_levers": {"demand_growth_pct": 10.0}},
    )
    scen_b_resp = await async_client.post(
        "/api/v1/scenarios/",
        json={"name": "Concurrent Scenario B", "initial_levers": {"demand_growth_pct": -10.0}},
    )
    assert scen_a_resp.status_code == 201
    assert scen_b_resp.status_code == 201

    id_a = scen_a_resp.json()["id"]
    id_b = scen_b_resp.json()["id"]

    # 2. Run both concurrently via anyio task group
    results = {}

    async def run_scenario(key: str, s_id: str):
        resp = await async_client.post(f"/api/v1/scenarios/{s_id}/run")
        results[key] = resp

    async with anyio.create_task_group() as tg:
        tg.start_soon(run_scenario, "A", id_a)
        tg.start_soon(run_scenario, "B", id_b)

    # 3. Verify both succeeded with distinct runs and isolated outputs
    assert results["A"].status_code == 201
    assert results["B"].status_code == 201

    run_a = results["A"].json()
    run_b = results["B"].json()

    assert run_a["id"] != run_b["id"]
    assert run_a["status"] == "SUCCESS"
    assert run_b["status"] == "SUCCESS"

    # Demand for +10% shock should exceed demand for -10% shock
    rev_a = run_a["financial_result"]["gross_revenue_delta"]
    rev_b = run_b["financial_result"]["gross_revenue_delta"]
    assert rev_a > rev_b

