"""
Tests for Application Factory, Health Probes, Correlation ID, and Error Contracts.
Verifies Gates 9.0-B, 9.0-C, 9.0-G, 9.0-H.
"""
import pytest
from fastapi.testclient import TestClient

from backend.app.core.config import Settings
from backend.app.core.errors import ModelIntegrityError
from backend.app.main import app, create_app


@pytest.fixture
def client():
    """Synchronous test client for FastAPI application."""
    return TestClient(app)


def test_gate_9_0_b_backend_import():
    """Gate 9.0-B: Verify backend package and app factory import cleanly."""
    from backend.app.main import app as imported_app, create_app as imported_factory
    assert imported_app is not None
    assert callable(imported_factory)


def test_gate_9_0_c_application_startup_without_postgres(client):
    """Gate 9.0-C: Verify app starts cleanly and serves root heartbeat without DB."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "DecisionSphere" in data["app"]
    assert "version" in data


def test_health_check_probe(client):
    """Verify /api/v1/health returns healthy status and verifies ML models."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "models" in data
    assert set(data["models"].keys()) == {"demand", "supply_chain", "workforce"}
    for key, model_info in data["models"].items():
        assert model_info["verified"] is True
        assert model_info["status"] == "VERIFIED"


def test_models_status_endpoint(client):
    """Verify /api/v1/models/status returns full artifact verification dictionary."""
    response = client.get("/api/v1/models/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "models" in data
    assert len(data["models"]) == 3


def test_gate_9_0_g_correlation_id_generated_when_absent(client):
    """Gate 9.0-G: Verify X-Request-ID is generated and attached to response when omitted."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert "x-request-id" in response.headers
    req_id = response.headers["x-request-id"]
    assert req_id.startswith("req-")


def test_gate_9_0_g_correlation_id_propagated_when_supplied(client):
    """Gate 9.0-G: Verify custom X-Request-ID is echoed back and preserved."""
    custom_id = "test-custom-tracking-id-999"
    response = client.get("/api/v1/health", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    assert response.headers["x-request-id"] == custom_id


def test_gate_9_0_h_error_contract_on_404(client):
    """Gate 9.0-H: Verify 404 response produces standardized error contract."""
    response = client.get("/api/v1/non_existent_route")
    assert response.status_code == 404
    payload = response.json()
    assert "error" in payload
    error = payload["error"]
    assert error["code"] == "NOT_FOUND"
    assert "request_id" in error
    assert "message" in error


def test_gate_9_0_h_error_contract_on_app_exception():
    """Gate 9.0-H: Verify custom AppException produces standardized error structure."""
    test_settings = Settings(app_env="testing")
    test_app = create_app(test_settings)

    @test_app.get("/api/v1/test-error")
    def trigger_error():
        raise ModelIntegrityError(
            message="Demand model hash mismatch",
            details={"key": "demand", "expected": "ABC"},
        )

    test_client = TestClient(test_app)
    response = test_client.get("/api/v1/test-error")
    assert response.status_code == 503
    payload = response.json()
    assert "error" in payload
    error = payload["error"]
    assert error["code"] == "MODEL_INTEGRITY_FAILURE"
    assert error["message"] == "Demand model hash mismatch"
    assert error["details"] == {"key": "demand", "expected": "ABC"}
    assert "request_id" in error


def test_cors_headers(client):
    """Verify CORS middleware responds with correct headers for whitelisted origin."""
    response = client.get(
        "/api/v1/health",
        headers={"Origin": "http://localhost:3000"},
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
