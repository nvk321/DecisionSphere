"""
Scenario Route Controllers Test Suite (Milestone 9.5).
Verifies HTTP endpoints for scenarios: creation, listing, retrieval,
lever updating (Gate G: Version Immutability), soft deletion, version listing,
shortcut simulation runs, and Gate E schema validation.
"""
from __future__ import annotations

import uuid
import pytest
from fastapi.testclient import TestClient


def test_scenario_crud_lifecycle(client: TestClient):
    """
    Test complete scenario CRUD lifecycle through HTTP endpoints:
    create -> get -> update name -> archive -> list with filters.
    """
    # 1. Create scenario
    create_payload = {
        "name": "Q4 Expansion Scenario",
        "description": "Evaluating 25% retail promotional surge",
        "initial_levers": {
            "demand_growth_pct": 25.0,
            "promo_active": True,
            "scheduled_days_offset": 1,
            "shipping_mode_override": "First Class",
            "overtime_workforce_pct": 20.0,
        },
    }
    create_resp = client.post("/api/v1/scenarios/", json=create_payload)
    assert create_resp.status_code == 201
    created = create_resp.json()
    scenario_id = created["id"]
    assert created["name"] == "Q4 Expansion Scenario"
    assert created["description"] == "Evaluating 25% retail promotional surge"
    assert created["is_archived"] is False
    assert created["latest_version"] is not None
    assert created["latest_version"]["version_number"] == 1
    assert created["latest_version"]["demand_growth_pct"] == 25.0

    # 2. Get scenario by ID
    get_resp = client.get(f"/api/v1/scenarios/{scenario_id}")
    assert get_resp.status_code == 200
    fetched = get_resp.json()
    assert fetched["id"] == scenario_id
    assert fetched["name"] == "Q4 Expansion Scenario"

    # 3. Update scenario metadata without changing levers
    patch_resp = client.patch(
        f"/api/v1/scenarios/{scenario_id}",
        json={"name": "Updated Q4 Expansion Plan"},
    )
    assert patch_resp.status_code == 200
    updated = patch_resp.json()
    assert updated["name"] == "Updated Q4 Expansion Plan"
    # Version number remains 1 because no new levers were provided
    assert updated["latest_version"]["version_number"] == 1

    # 4. Soft-archive scenario
    del_resp = client.delete(f"/api/v1/scenarios/{scenario_id}")
    assert del_resp.status_code == 200
    archived = del_resp.json()
    assert archived["is_archived"] is True

    # 5. List scenarios excluding archived
    list_active = client.get("/api/v1/scenarios/?include_archived=false")
    assert list_active.status_code == 200
    active_items = list_active.json()["items"]
    assert all(s["id"] != scenario_id for s in active_items)

    # 6. List scenarios including archived
    list_all = client.get("/api/v1/scenarios/?include_archived=true")
    assert list_all.status_code == 200
    all_items = list_all.json()["items"]
    assert any(s["id"] == scenario_id for s in all_items)


def test_gate_g_version_immutability_through_http(client: TestClient):
    """
    Gate G: Version Immutability Gate.
    Verifies that updating levers via PATCH creates an immutable new version row (v2)
    while preserving the prior version (v1) with its original parameters.
    """
    # 1. Create scenario with initial levers (v1)
    create_resp = client.post(
        "/api/v1/scenarios/",
        json={
            "name": "Gate G HTTP Test",
            "initial_levers": {"demand_growth_pct": 10.0, "promo_active": False},
        },
    )
    assert create_resp.status_code == 201
    scenario_id = create_resp.json()["id"]

    # 2. Update levers via PATCH (creates v2)
    patch_resp = client.patch(
        f"/api/v1/scenarios/{scenario_id}",
        json={
            "new_levers": {
                "demand_growth_pct": 30.0,
                "promo_active": True,
                "overtime_workforce_pct": 15.0,
            }
        },
    )
    assert patch_resp.status_code == 200
    patched = patch_resp.json()
    assert patched["latest_version"]["version_number"] == 2
    assert patched["latest_version"]["demand_growth_pct"] == 30.0

    # 3. List versions to confirm both v1 and v2 exist
    versions_resp = client.get(f"/api/v1/scenarios/{scenario_id}/versions")
    assert versions_resp.status_code == 200
    versions = versions_resp.json()
    assert len(versions) == 2
    assert versions[0]["version_number"] == 1
    assert versions[0]["demand_growth_pct"] == 10.0
    assert versions[0]["promo_active"] is False

    assert versions[1]["version_number"] == 2
    assert versions[1]["demand_growth_pct"] == 30.0
    assert versions[1]["promo_active"] is True

    # 4. Fetch specific version by ID
    v1_id = versions[0]["id"]
    v1_resp = client.get(f"/api/v1/scenarios/{scenario_id}/versions/{v1_id}")
    assert v1_resp.status_code == 200
    assert v1_resp.json()["version_number"] == 1


def test_scenario_simulation_run_shortcut(client: TestClient):
    """
    Verify POST /api/v1/scenarios/{id}/run shortcut executes multi-domain simulation
    and returns a complete SimulationDetailResponse.
    """
    create_resp = client.post(
        "/api/v1/scenarios/",
        json={"name": "Simulation Shortcut Test", "initial_levers": {"demand_growth_pct": 15.0}},
    )
    assert create_resp.status_code == 201
    scenario_id = create_resp.json()["id"]

    run_resp = client.post(f"/api/v1/scenarios/{scenario_id}/run")
    assert run_resp.status_code == 201
    run_data = run_resp.json()

    assert run_data["id"] is not None
    assert run_data["status"] in {"SUCCESS", "COMPLETED"}
    assert len(run_data["predictions"]) == 3
    assert run_data["financial_result"] is not None
    assert run_data["financial_result"]["net_profit_delta"] is not None
    assert run_data["recommendation_result"] is not None
    assert run_data["recommendation_result"]["decision_category"] in {
        "PROCEED",
        "PROCEED_WITH_MITIGATIONS",
        "REJECT_RESTRUCTURE",
    }
    assert run_data["audit_record"] is not None


def test_scenario_errors_and_gate_e_rejection(client: TestClient):
    """
    Verify 404 on missing scenario, 422 on invalid name, and Gate E rogue field rejection.
    """
    # 1. 404 for non-existent scenario
    missing_id = uuid.uuid4()
    resp_404 = client.get(f"/api/v1/scenarios/{missing_id}")
    assert resp_404.status_code == 404
    err = resp_404.json()
    assert err["error"]["code"] == "RESOURCE_NOT_FOUND"

    # 2. 422 for empty scenario name
    resp_empty = client.post("/api/v1/scenarios/", json={"name": "   "})
    assert resp_empty.status_code == 422

    # 3. Gate E: extra="forbid" on ScenarioCreate
    resp_rogue = client.post(
        "/api/v1/scenarios/",
        json={"name": "Valid Name", "malicious_injected_column": "drop database"},
    )
    assert resp_rogue.status_code == 422
    assert resp_rogue.json()["error"]["code"] == "VALIDATION_ERROR"


def test_scenario_archive_and_filtering(client: TestClient):
    """Verify DELETE soft-archives scenario and list filtering respects include_archived."""
    created = client.post("/api/v1/scenarios/", json={"name": "Archive Target"}).json()
    s_id = created["id"]

    # Archive scenario
    del_resp = client.delete(f"/api/v1/scenarios/{s_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["is_archived"] is True

    # Check that default listing does not include it
    list_active = client.get("/api/v1/scenarios/?include_archived=false").json()
    active_ids = [s["id"] for s in list_active["items"]]
    assert s_id not in active_ids

    # Check that listing with include_archived=true includes it
    list_all = client.get("/api/v1/scenarios/?include_archived=true").json()
    all_ids = [s["id"] for s in list_all["items"]]
    assert s_id in all_ids


def test_scenario_version_lookup_cross_scenario_rejection(client: TestClient):
    """Verify requesting Scenario A's version using Scenario B's path returns 404."""
    scen_a = client.post(
        "/api/v1/scenarios/",
        json={"name": "Scenario Alpha", "initial_levers": {"demand_growth_pct": 5.0}},
    ).json()
    scen_b = client.post(
        "/api/v1/scenarios/",
        json={"name": "Scenario Beta", "initial_levers": {"demand_growth_pct": 10.0}},
    ).json()

    ver_a_id = scen_a["latest_version"]["id"]
    # Attempt to fetch version of A using scenario B's route
    mismatch_resp = client.get(f"/api/v1/scenarios/{scen_b['id']}/versions/{ver_a_id}")
    assert mismatch_resp.status_code == 404
    assert mismatch_resp.json()["error"]["code"] == "RESOURCE_NOT_FOUND"
