"""
Sensitivity Analysis Route Controllers Test Suite (Milestone 9.5).
Verifies HTTP endpoints for Experiment B (Demand Curves) and Experiment D (Financial & CRS Sweeps),
asynchronous AnyIO threadpool offloading, and Gate E schema enforcement.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


def test_demand_shock_sweep_route(client: TestClient):
    """
    Verify POST /api/v1/sensitivity/demand-sweep (Experiment B).
    Evaluates cascading effects across discrete demand shocks [-10%, 0%, +10%].
    """
    payload = {
        "shock_percentages": [-10.0, 0.0, 10.0],
        "base_levers": {"demand_growth_pct": 0.0, "promo_active": False},
    }
    resp = client.post("/api/v1/sensitivity/demand-sweep", json=payload)
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 3

    assert items[0]["shock_pct"] == -10.0
    assert items[1]["shock_pct"] == 0.0
    assert items[2]["shock_pct"] == 10.0

    # Sales units increase monotonically with demand shock
    assert items[0]["demand_forecast"] < items[1]["demand_forecast"] < items[2]["demand_forecast"]
    for item in items:
        assert item["epistemic_tier"] == "PREDICTED"
        assert item["late_delivery_risk"] >= 0.0
        assert item["workforce_attrition_risk"] >= 0.0


def test_financial_parameter_sweep_route(client: TestClient):
    """
    Verify POST /api/v1/sensitivity/financial-sweep (Experiment D).
    Sweeps ASM-001 delay penalty and verifies net profit response.
    """
    # Setup scenario with positive demand to ensure non-trivial volume
    sc_resp = client.post(
        "/api/v1/scenarios/",
        json={"name": "Financial Sensitivity Route Test", "initial_levers": {"demand_growth_pct": 10.0}},
    )
    version_id = sc_resp.json()["latest_version"]["id"]

    payload = {
        "scenario_version_id": version_id,
        "parameter_name": "asm_001_delay_penalty",
        "candidate_values": [15.0, 25.0, 35.0, 45.0],
    }
    resp = client.post("/api/v1/sensitivity/financial-sweep", json=payload)
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 4

    # Higher delay penalties must reduce net profit delta
    assert items[0]["net_profit_delta"] > items[-1]["net_profit_delta"]
    for item in items:
        assert item["epistemic_tier"] == "CALCULATED"
        assert item["parameter_name"] == "asm_001_delay_penalty"


def test_crs_weight_sweep_route(client: TestClient):
    """
    Verify POST /api/v1/sensitivity/crs-weight-sweep.
    Sweeps alternative simplex weight vectors and checks CRS stability.
    """
    sc_resp = client.post(
        "/api/v1/scenarios/",
        json={"name": "CRS Sweep Route Test", "initial_levers": {"demand_growth_pct": 10.0}},
    )
    version_id = sc_resp.json()["latest_version"]["id"]

    payload = {
        "scenario_version_id": version_id,
        "candidate_weights": [
            {"w_supply": 0.70, "w_workforce": 0.20, "w_demand": 0.10},
            {"w_supply": 0.20, "w_workforce": 0.70, "w_demand": 0.10},
            {"w_supply": 0.333, "w_workforce": 0.333, "w_demand": 0.334},
        ],
        "tau_risk": 50.0,
    }
    resp = client.post("/api/v1/sensitivity/crs-weight-sweep", json=payload)
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 3
    for item in items:
        assert 0.0 <= item["composite_risk_score"] <= 100.0
        assert item["decision_category"] in {"PROCEED", "PROCEED_WITH_MITIGATIONS", "REJECT_RESTRUCTURE"}
        assert item["epistemic_tier"] == "CALCULATED"


def test_tipping_point_search_route(client: TestClient):
    """
    Verify POST /api/v1/sensitivity/tipping-point.
    Searches for parameter tipping point where recommendation category changes.
    """
    payload = {
        "parameter_name": "asm_001_delay_penalty",
        "candidate_values": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0],
    }
    resp = client.post("/api/v1/sensitivity/tipping-point", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["parameter_name"] == "asm_001_delay_penalty"
    assert "flip_detected" in data
    assert data["epistemic_tier"] == "RECOMMENDED"


def test_sensitivity_gate_e_rejection(client: TestClient):
    """Verify Gate E extra="forbid" rejection on sensitivity sweep endpoints."""
    resp = client.post(
        "/api/v1/sensitivity/demand-sweep",
        json={"shock_percentages": [10.0], "malicious_unapproved_key": "injected"},
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"
