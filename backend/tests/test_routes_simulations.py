"""
Simulation Route Controllers Test Suite (Milestone 9.5).
Verifies multi-domain simulation execution through HTTP endpoints:
atomic persistence (Gate F), provenance signature tuple (Gate H),
run lookup, summary listing with pagination, and schema validation (Gate E).
"""
from __future__ import annotations

import uuid
import pytest
from fastapi.testclient import TestClient


def test_simulation_execution_and_gate_h_provenance(client: TestClient):
    """
    Verify POST /api/v1/simulations/run executes the complete multi-domain pipeline
    and persists the full relational tree with the 8-element provenance tuple.
    """
    # 1. Setup scenario with version
    sc_resp = client.post(
        "/api/v1/scenarios/",
        json={"name": "Simulation Route Test", "initial_levers": {"demand_growth_pct": 20.0}},
    )
    assert sc_resp.status_code == 201
    version_id = sc_resp.json()["latest_version"]["id"]

    # 2. Trigger simulation run
    sim_resp = client.post(
        "/api/v1/simulations/run",
        json={"scenario_version_id": version_id},
    )
    assert sim_resp.status_code == 201
    run = sim_resp.json()
    run_id = run["id"]

    # 3. Inspect Domain Predictions (PREDICTED)
    assert len(run["predictions"]) == 3
    domains = {p["domain"] for p in run["predictions"]}
    assert domains == {"DEMAND", "SUPPLY_CHAIN", "WORKFORCE"}
    for p in run["predictions"]:
        assert p["epistemic_tier"] == "PREDICTED"
        assert p["baseline_value"] is not None
        assert p["scenario_value"] is not None

    # 4. Inspect Financial Results (CALCULATED)
    fin = run["financial_result"]
    assert fin is not None
    assert fin["epistemic_tier"] == "CALCULATED"
    assert fin["net_profit_delta"] is not None
    assert len(fin["line_items"]) == 7

    # 5. Inspect Recommendation Results (RECOMMENDED)
    rec = run["recommendation_result"]
    assert rec is not None
    assert rec["epistemic_tier"] == "RECOMMENDED"
    assert rec["decision_category"] in {"PROCEED", "PROCEED_WITH_MITIGATIONS", "REJECT_RESTRUCTURE"}
    assert 0.0 <= rec["composite_risk_score"] <= 100.0

    # 6. Inspect Gate H: 8-Element Provenance Signature Tuple
    audit = run["audit_record"]
    assert audit is not None
    prov = audit["provenance_tuple"]
    assert prov["scenario_version_id"] == version_id
    assert len(prov["artifact_hashes"]) == 3
    assert prov["policy_version"] == 1
    assert prov["git_commit"] is not None
    assert prov["app_version"] is not None
    assert prov["python_version"] is not None
    assert prov["migration_revision"] is not None
    assert prov["timestamp"] is not None

    # 7. Lookup simulation by ID
    get_resp = client.get(f"/api/v1/simulations/{run_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == run_id


def test_simulation_listing_and_filtering(client: TestClient):
    """Verify GET /api/v1/simulations/ returns paginated run summaries."""
    sc_resp = client.post(
        "/api/v1/scenarios/",
        json={"name": "Listing Test Scenario", "initial_levers": {"demand_growth_pct": 5.0}},
    )
    scenario_id = sc_resp.json()["id"]

    # Run two simulations
    client.post(f"/api/v1/scenarios/{scenario_id}/run")
    client.post(f"/api/v1/scenarios/{scenario_id}/run")

    # List all runs
    list_resp = client.get("/api/v1/simulations/?limit=10")
    assert list_resp.status_code == 200
    data = list_resp.json()
    assert "items" in data
    assert len(data["items"]) >= 2
    for item in data["items"]:
        assert item["id"] is not None
        assert item["execution_status"] in {"SUCCESS", "COMPLETED"}

    # Filter by scenario ID
    filtered_resp = client.get(f"/api/v1/simulations/?scenario_id={scenario_id}")
    assert filtered_resp.status_code == 200
    filtered_items = filtered_resp.json()["items"]
    assert len(filtered_items) >= 2


def test_simulation_errors_and_gate_e_rejection(client: TestClient):
    """Verify 404 on missing simulation run and 422 on invalid simulation requests."""
    # 404 for missing run
    missing_id = uuid.uuid4()
    resp_404 = client.get(f"/api/v1/simulations/{missing_id}")
    assert resp_404.status_code == 404
    assert resp_404.json()["error"]["code"] == "RESOURCE_NOT_FOUND"

    # 422 when scenario_version_id is missing in POST /simulations/run
    resp_no_ver = client.post("/api/v1/simulations/run", json={})
    assert resp_no_ver.status_code == 422

    # Gate E extra="forbid" rejection
    resp_rogue = client.post(
        "/api/v1/simulations/run",
        json={"scenario_version_id": str(uuid.uuid4()), "unapproved_rogue_flag": True},
    )
    assert resp_rogue.status_code == 422
    assert resp_rogue.json()["error"]["code"] == "VALIDATION_ERROR"
