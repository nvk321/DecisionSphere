"""
Simulation Transaction Atomicity & Rollback Integration Tests (Gate F).
Verifies that any unexpected mid-execution fault during multi-domain simulation
aborts the transaction and rolls back all partially added database records,
leaving zero orphaned runs, predictions, financials, recommendations, or audit records.
"""
from __future__ import annotations

import uuid
from unittest.mock import patch
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from backend.app.models import (
    AuditRecord,
    DomainPrediction,
    FinancialLineItem,
    FinancialResult,
    RecommendationResult,
    SimulationRun,
    StrategicAction,
)
from backend.app.services.simulation_orchestrator import SimulationOrchestrator


@pytest.mark.anyio
async def test_gate_f_simulation_atomicity_and_rollback_through_http(
    async_client: AsyncClient,
    db_session: Session,
):
    """
    Gate F Verification:
    1. Create a base scenario with valid levers.
    2. Inject a simulated fault during relational persistence AFTER partial flushes
       (specifically during recommendation persistence right before db.commit()).
    3. Trigger the simulation via HTTP POST /api/v1/scenarios/{id}/run.
    4. Assert that the HTTP request fails with HTTP 500 / INTERNAL_SERVER_ERROR.
    5. Directly inspect the database session to verify that zero partial entities were committed:
       - 0 SimulationRun records
       - 0 DomainPrediction records
       - 0 FinancialResult records
       - 0 FinancialLineItem records
       - 0 RecommendationResult records
       - 0 AuditRecord records
    6. Verify via HTTP GET /api/v1/simulations/ that the listing returns 0 runs.
    """
    # 1. Create a Scenario
    create_resp = await async_client.post(
        "/api/v1/scenarios/",
        json={"name": "Atomicity Rollback Test Scenario", "initial_levers": {"demand_growth_pct": 10.0}},
    )
    assert create_resp.status_code == 201
    scenario_id = create_resp.json()["id"]

    # 2. Define fault to inject in recommendation persistence (after run & financials are staged)
    original_persist = SimulationOrchestrator._persist_results

    def fault_injected_persist(self, db, version, policy, scenario_res, impact_res, rec_res, duration_ms):
        # Call the original method up to RecommendationResult creation, then raise an intentional fault
        # We simulate a database or memory failure right before commit
        with patch("backend.app.services.simulation_orchestrator.AuditRecord", side_effect=RuntimeError("Simulated Storage Subsystem Crash during Audit Record Creation")):
            return original_persist(self, db, version, policy, scenario_res, impact_res, rec_res, duration_ms)

    # 3. Trigger simulation under fault injection
    with patch.object(SimulationOrchestrator, "_persist_results", fault_injected_persist):
        run_resp = await async_client.post(f"/api/v1/scenarios/{scenario_id}/run")

    # 4. Verify HTTP level response: must be 500 with structured JSON envelope
    assert run_resp.status_code == 500
    err_body = run_resp.json()
    assert "error" in err_body
    assert err_body["error"]["code"] == "INTERNAL_ERROR"

    # 5. Verify database atomicity: zero partial entities committed
    db_session.rollback()  # Sync session state with engine
    assert db_session.query(SimulationRun).count() == 0
    assert db_session.query(DomainPrediction).count() == 0
    assert db_session.query(FinancialResult).count() == 0
    assert db_session.query(FinancialLineItem).count() == 0
    assert db_session.query(RecommendationResult).count() == 0
    assert db_session.query(StrategicAction).count() == 0
    assert db_session.query(AuditRecord).count() == 0

    # 6. Verify HTTP listing query reflects complete atomicity
    list_resp = await async_client.get("/api/v1/simulations/")
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] == 0
    assert list_resp.json()["items"] == []

    # 7. Confirm that after clearing the fault, a subsequent simulation run executes and commits successfully
    retry_resp = await async_client.post(f"/api/v1/scenarios/{scenario_id}/run")
    assert retry_resp.status_code == 201
    assert retry_resp.json()["status"] in {"SUCCESS", "COMPLETED"}

    # Now exactly 1 run exists
    assert db_session.query(SimulationRun).count() == 1
    assert db_session.query(DomainPrediction).count() == 3
    assert db_session.query(FinancialResult).count() == 1
    assert db_session.query(AuditRecord).count() == 1
