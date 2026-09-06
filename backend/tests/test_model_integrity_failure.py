"""
Model Integrity Failure & Execution Refusal Integration Tests (Gate I).
Verifies through HTTP that when a model binary has a cryptographic hash mismatch
or is missing from disk, the API refuses simulation execution with structured errors,
and the models status endpoint reports degraded/corrupted artifacts.
Crucially, all tests use in-memory mock patching without touching the tracked .joblib files.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch
import pytest
from httpx import AsyncClient

from backend.app.core.config import get_settings


@pytest.mark.anyio
async def test_gate_i_model_hash_mismatch_refuses_simulation(async_client: AsyncClient):
    """
    Gate I Verification (Hash Mismatch / Corrupted Binary):
    1. Create a base scenario.
    2. In memory, monkeypatch the expected SHA-256 hash for the demand model to a bogus signature.
    3. Verify GET /api/v1/models/status reports status='error' with HASH_MISMATCH.
    4. Verify POST /api/v1/scenarios/{id}/run refuses execution and returns structured error.
    5. Verify zero simulation runs were created.
    6. Verify that after restoring the patch, normal execution succeeds.
    """
    settings = get_settings()

    # 1. Create a Scenario
    scen_resp = await async_client.post(
        "/api/v1/scenarios/",
        json={"name": "Gate I Hash Mismatch Test", "initial_levers": {"demand_growth_pct": 5.0}},
    )
    assert scen_resp.status_code == 201
    scenario_id = scen_resp.json()["id"]

    # 2. Patch expected SHA-256 in memory
    demand_desc = settings.model_descriptors["demand"]
    original_hash = demand_desc.expected_sha256

    try:
        demand_desc.expected_sha256 = "000000000000000000000000000000000000000000000000000000000000BOGUS"

        # 3. GET /api/v1/models/status must report degraded / not verified
        status_resp = await async_client.get("/api/v1/models/status")
        assert status_resp.status_code == 200
        status_data = status_resp.json()
        assert status_data["status"] in {"degraded", "error"}
        assert status_data["models_verified"] is False
        assert status_data["models"]["demand"]["verified"] is False
        assert status_data["models"]["demand"]["status"] == "HASH_MISMATCH"

        # 4. POST simulation run must be refused
        run_resp = await async_client.post(f"/api/v1/scenarios/{scenario_id}/run")
        assert run_resp.status_code in {500, 503}
        err_data = run_resp.json()
        assert "error" in err_data
        assert err_data["error"]["code"] in {"MODEL_INTEGRITY_FAILURE", "INTERNAL_ERROR"}

        # 5. Verify no runs were persisted
        list_resp = await async_client.get("/api/v1/simulations/")
        assert list_resp.status_code == 200
        assert list_resp.json()["total"] == 0

    finally:
        # Restore authoritative hash
        demand_desc.expected_sha256 = original_hash

    # 6. Verify clean recovery after unpatching
    recovery_resp = await async_client.get("/api/v1/models/status")
    assert recovery_resp.status_code == 200
    assert recovery_resp.json()["status"] == "success"
    assert recovery_resp.json()["models_verified"] is True


@pytest.mark.anyio
async def test_gate_i_missing_model_file_refuses_simulation(async_client: AsyncClient):
    """
    Gate I Verification (Missing Model Binary):
    1. Create a base scenario.
    2. In memory, update the workforce model relative_path to a non-existent path in try/finally.
    3. Verify GET /api/v1/models/status reports FILE_NOT_FOUND.
    4. Verify POST /api/v1/scenarios/{id}/run refuses execution with structured error.
    5. Verify zero simulation runs were created.
    """
    settings = get_settings()

    # 1. Create a Scenario
    scen_resp = await async_client.post(
        "/api/v1/scenarios/",
        json={"name": "Gate I Missing File Test", "initial_levers": {"demand_growth_pct": 5.0}},
    )
    assert scen_resp.status_code == 201
    scenario_id = scen_resp.json()["id"]

    # 2. Modify relative_path on workforce descriptor in memory to a missing file path
    wf_desc = settings.model_descriptors["workforce"]
    original_path = wf_desc.relative_path
    try:
        wf_desc.relative_path = "models/nonexistent/missing_model_file.joblib"

        # 3. Check status endpoint
        status_resp = await async_client.get("/api/v1/models/status")
        assert status_resp.status_code == 200
        status_data = status_resp.json()
        assert status_data["status"] in {"degraded", "error"}
        assert status_data["models_verified"] is False
        assert status_data["models"]["workforce"]["verified"] is False
        assert status_data["models"]["workforce"]["status"] == "FILE_NOT_FOUND"

        # 4. Attempt simulation run
        run_resp = await async_client.post(f"/api/v1/scenarios/{scenario_id}/run")
        assert run_resp.status_code in {500, 503}
        err_data = run_resp.json()
        assert "error" in err_data
        assert err_data["error"]["code"] in {"MODEL_NOT_FOUND", "INTERNAL_ERROR"}

        # 5. Verify no runs were persisted
        list_resp = await async_client.get("/api/v1/simulations/")
        assert list_resp.status_code == 200
        assert list_resp.json()["total"] == 0
    finally:
        wf_desc.relative_path = original_path

    # Verify recovery
    recovery_resp = await async_client.get("/api/v1/models/status")
    assert recovery_resp.status_code == 200
    assert recovery_resp.json()["status"] == "success"
    assert recovery_resp.json()["models_verified"] is True


@pytest.mark.anyio
async def test_gate_i_all_three_models_active_and_healthy_in_http_status(async_client: AsyncClient):
    """
    Gate I Verification (Baseline Model Verification):
    Verifies that in uncorrupted operational state, all three models
    (retail demand, supply chain delivery, HR workforce attrition)
    report status='verified', sha256_matched=True, file_exists=True,
    and models_verified=True through the HTTP API.
    """
    resp = await async_client.get("/api/v1/models/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["models_verified"] is True

    for domain in ["demand", "supply_chain", "workforce"]:
        assert domain in data["models"]
        info = data["models"][domain]
        assert info["verified"] is True
        assert info["status"] == "VERIFIED"
        assert info["exists"] is True
        assert info["actual_sha256"] == info["expected_sha256"]
        assert len(info["actual_sha256"]) == 64

