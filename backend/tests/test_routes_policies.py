"""
AssumptionPolicy Route Controllers Test Suite (Milestone 9.5).
Verifies corporate policy endpoints: default retrieval, listing, lookup by ID,
creation with simplex constraints, and Gate E schema enforcement.
"""
from __future__ import annotations

import uuid
import pytest
from fastapi.testclient import TestClient


def test_default_policy_endpoint(client: TestClient):
    """
    Verify GET /api/v1/policies/default returns the authoritative baseline corporate policy.
    Tests route ordering constraint: /default must resolve before /{policy_id}.
    """
    response = client.get("/api/v1/policies/default")
    assert response.status_code == 200
    policy = response.json()
    assert policy["version_number"] == 1
    assert policy["name"] == "Corporate Baseline Policy"
    assert policy["late_penalty_rate"] == 25.0
    assert policy["expedite_fee"] == 15.0
    assert policy["stockout_churn_factor"] == 0.15
    assert policy["replacement_cost"] == 30000.0
    assert policy["overtime_wage_rate"] == 45.0
    assert policy["crs_w_supply"] == 0.40
    assert policy["crs_w_workforce"] == 0.40
    assert policy["crs_w_demand"] == 0.20
    assert policy["tau_risk"] == 50.0


def test_list_and_get_policy_by_id(client: TestClient):
    """Verify policy listing and single-policy retrieval by primary key."""
    # Ensure default policy exists first
    client.get("/api/v1/policies/default")

    # List policies
    list_resp = client.get("/api/v1/policies/")
    assert list_resp.status_code == 200
    policies = list_resp.json()
    assert len(policies) >= 1

    policy_id = policies[0]["id"]
    get_resp = client.get(f"/api/v1/policies/{policy_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == policy_id


def test_create_policy_version_with_valid_simplex(client: TestClient):
    """
    Verify POST /api/v1/policies/ creates an immutable policy version when simplex is satisfied:
    w_supply (0.50) + w_workforce (0.30) + w_demand (0.20) == 1.0.
    """
    # Ensure baseline v1 exists
    client.get("/api/v1/policies/default")

    payload = {
        "name": "Supply-Constrained Operations Policy",
        "description": "Heightened freight surcharge and supply weight for peak logistics disruption",
        "late_penalty_rate": 35.0,
        "expedite_fee": 25.0,
        "stockout_churn_factor": 0.20,
        "replacement_cost": 35000.0,
        "overtime_wage_rate": 55.0,
        "w_supply": 0.50,
        "w_workforce": 0.30,
        "w_demand": 0.20,
        "tau_risk": 55.0,
    }
    create_resp = client.post("/api/v1/policies/", json=payload)
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["name"] == "Supply-Constrained Operations Policy"
    assert created["version_number"] > 1
    assert created["crs_w_supply"] == 0.50
    assert created["crs_w_workforce"] == 0.30
    assert created["crs_w_demand"] == 0.20


def test_policy_simplex_violation_rejection(client: TestClient):
    """
    Verify POST /api/v1/policies/ rejects simplex equality violation (sum != 1.0) with HTTP 422.
    """
    invalid_payload = {
        "name": "Simplex Violating Policy",
        "w_supply": 0.60,
        "w_workforce": 0.60,
        "w_demand": 0.20,  # Sum = 1.40 != 1.0
    }
    resp = client.post("/api/v1/policies/", json=invalid_payload)
    assert resp.status_code == 422
    assert "simplex equality" in str(resp.json())


def test_policy_errors_and_gate_e_rejection(client: TestClient):
    """
    Verify 404 for missing policy and 422 for Gate E extra forbidden field.
    """
    missing_id = uuid.uuid4()
    resp_404 = client.get(f"/api/v1/policies/{missing_id}")
    assert resp_404.status_code == 404
    assert resp_404.json()["error"]["code"] == "RESOURCE_NOT_FOUND"

    resp_rogue = client.post(
        "/api/v1/policies/",
        json={"name": "Valid Policy", "rogue_injected_column": "drop table"},
    )
    assert resp_rogue.status_code == 422
    assert resp_rogue.json()["error"]["code"] == "VALIDATION_ERROR"


def test_policy_simplex_weight_bounds(client: TestClient):
    """Verify negative weight rejection (w_supply < 0.0) with HTTP 422."""
    negative_weight_payload = {
        "name": "Negative Weight Policy",
        "w_supply": -0.10,
        "w_workforce": 0.60,
        "w_demand": 0.50,
    }
    resp = client.post("/api/v1/policies/", json=negative_weight_payload)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"
