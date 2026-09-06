"""
Tests for Centralized Application Settings & Model Configuration (Gates 9.0-D, 9.0-E, 9.0-F).
"""
import os
from pathlib import Path
import pytest

from backend.app.core.config import (
    ModelArtifactDescriptor,
    PROJECT_ROOT,
    Settings,
    get_settings,
)


def test_settings_default_values():
    """Gate 9.0-D: Verify settings load with expected defaults."""
    settings = Settings()
    assert settings.app_name == "DecisionSphere Strategic Decision Support API"
    assert settings.app_version == "1.0.0-phase9"
    assert settings.app_env in ["development", "testing", "production"]
    assert settings.api_v1_prefix == "/api/v1"
    assert "http://localhost:3000" in settings.cors_origins
    assert settings.api_key is None


def test_settings_env_override(monkeypatch):
    """Gate 9.0-D: Verify settings respect environment variable overrides."""
    monkeypatch.setenv("APP_NAME", "Custom DecisionSphere Test API")
    monkeypatch.setenv("APP_ENV", "testing")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("PORT", "9000")

    custom_settings = Settings()
    assert custom_settings.app_name == "Custom DecisionSphere Test API"
    assert custom_settings.app_env == "testing"
    assert custom_settings.debug is True
    assert custom_settings.port == 9000


def test_path_resolution_independent_of_cwd(tmp_path, monkeypatch):
    """Gate 9.0-E: Verify path resolution anchors to PROJECT_ROOT regardless of cwd."""
    settings = get_settings()
    assert settings.project_root == PROJECT_ROOT
    assert settings.models_dir == PROJECT_ROOT / "models"
    assert settings.data_dir == PROJECT_ROOT / "data"

    # Simulate changing working directory to a temporary folder
    monkeypatch.chdir(tmp_path)
    # Re-verify that descriptor resolves back to actual project root
    for key, descriptor in settings.model_descriptors.items():
        resolved_path = descriptor.resolve_path(settings.project_root)
        assert resolved_path.is_absolute()
        assert resolved_path.exists(), f"Model {key} path {resolved_path} must exist"


def test_model_artifact_verification_success():
    """Gate 9.0-F: Verify that all three frozen models pass SHA-256 integrity verification."""
    settings = get_settings()
    report = settings.verify_model_artifacts()

    assert set(report.keys()) == {"demand", "supply_chain", "workforce"}

    for key in ["demand", "supply_chain", "workforce"]:
        item = report[key]
        assert item["exists"] is True, f"Model {key} file does not exist on disk"
        assert item["verified"] is True, f"Model {key} hash verification failed: {item}"
        assert item["status"] == "VERIFIED"
        assert item["actual_sha256"] == item["expected_sha256"].upper()

    assert settings.all_models_verified() is True


def test_model_artifact_verification_missing_file(tmp_path):
    """Verify descriptor behavior when artifact file does not exist."""
    desc = ModelArtifactDescriptor(
        key="test_model",
        name="Test Model",
        relative_path="non_existent/model.joblib",
        expected_sha256="ABCDEF123456",
        domain="test",
        algorithm="None",
    )
    is_valid, status_str = desc.verify(tmp_path)
    assert is_valid is False
    assert status_str == "FILE_NOT_FOUND"


def test_model_artifact_verification_mismatch(tmp_path):
    """Verify descriptor behavior when artifact file hash does not match expected."""
    fake_file = tmp_path / "fake_model.joblib"
    fake_file.write_bytes(b"corrupted or altered model content")

    desc = ModelArtifactDescriptor(
        key="fake_model",
        name="Fake Corrupted Model",
        relative_path="fake_model.joblib",
        expected_sha256="0000000000000000000000000000000000000000000000000000000000000000",
        domain="test",
        algorithm="None",
    )
    is_valid, actual_hash = desc.verify(tmp_path)
    assert is_valid is False
    assert actual_hash != desc.expected_sha256
