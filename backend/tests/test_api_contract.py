"""
API Contract & Router Integration Tests (Milestone 9.5).
Verifies that the unified API router is mounted correctly in main.py,
health and model endpoints return expected payloads, and OpenAPI schema
contains all documented endpoint paths.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


def test_root_heartbeat(client: TestClient):
    """Verify root GET / returns healthy heartbeat."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "DecisionSphere" in data["app"]


def test_api_v1_health_probe(client: TestClient):
    """Verify GET /api/v1/health probe returns healthy status with models verified."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["models_verified"] is True
    assert "version" in data


def test_api_v1_models_status(client: TestClient):
    """Verify GET /api/v1/models/status returns verification status for all 3 models."""
    response = client.get("/api/v1/models/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["models_verified"] is True
    assert set(data["models"].keys()) == {"demand", "supply_chain", "workforce"}
    for key, model in data["models"].items():
        assert model["verified"] is True
        assert model["exists"] is True
        assert model["status"] == "VERIFIED"


def test_openapi_schema_contains_all_v1_endpoints(client: TestClient):
    """
    Verify that the OpenAPI JSON specification contains all registered route endpoints.
    Catches route registration omissions and prefix mismatches.
    """
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    openapi = response.json()
    assert "paths" in openapi
    paths = openapi["paths"]

    expected_endpoints = [
        # Health & Models
        "/api/v1/health",
        "/api/v1/models/status",
        # Scenarios
        "/api/v1/scenarios/",
        "/api/v1/scenarios/{scenario_id}",
        "/api/v1/scenarios/{scenario_id}/versions",
        "/api/v1/scenarios/{scenario_id}/versions/{version_id}",
        "/api/v1/scenarios/{scenario_id}/run",
        # Policies
        "/api/v1/policies/",
        "/api/v1/policies/default",
        "/api/v1/policies/{policy_id}",
        # Simulations
        "/api/v1/simulations/",
        "/api/v1/simulations/run",
        "/api/v1/simulations/{run_id}",
        # Sensitivity
        "/api/v1/sensitivity/demand-sweep",
        "/api/v1/sensitivity/financial-sweep",
        "/api/v1/sensitivity/crs-weight-sweep",
        "/api/v1/sensitivity/tipping-point",
    ]

    for expected_path in expected_endpoints:
        assert expected_path in paths, f"Expected endpoint path '{expected_path}' missing from OpenAPI schema"


def test_api_docs_ui_rendered(client: TestClient):
    """Verify Swagger UI is accessible at /docs."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger-ui" in response.text.lower()


def test_api_redoc_ui_rendered(client: TestClient):
    """Verify ReDoc UI is accessible at /redoc."""
    response = client.get("/redoc")
    assert response.status_code == 200
    assert "redoc" in response.text.lower()


def test_structured_error_envelope_for_unhandled_routes(client: TestClient):
    """Verify 404 on unhandled route returns structured ErrorResponse JSON envelope."""
    response = client.get("/api/v1/non-existent-endpoint-test-404")
    assert response.status_code == 404
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == "NOT_FOUND"
    assert "message" in body["error"]
    assert "request_id" in body["error"]


def test_method_not_allowed_error_shape(client: TestClient):
    """Verify 405 on invalid method returns structured ErrorResponse envelope."""
    response = client.post("/api/v1/health")
    assert response.status_code == 405
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == "HTTP_ERROR"
    assert "message" in body["error"]
