"""
Centralized Application Settings and Model Configuration.

All paths are resolved relative to a reliable repository root anchor,
eliminating current-working-directory ambiguity.
"""
from __future__ import annotations

from functools import lru_cache
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Authoritative path anchors
CORE_DIR = Path(__file__).resolve().parent
APP_DIR = CORE_DIR.parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent


class ModelArtifactDescriptor(BaseModel):
    """
    Metadata and verification contract for a serialized machine learning model.
    """
    key: str
    name: str
    relative_path: str
    expected_sha256: str
    domain: str
    algorithm: str

    def resolve_path(self, root: Path = PROJECT_ROOT) -> Path:
        """Resolve absolute filesystem path anchored to project root."""
        return (root / self.relative_path).resolve()

    def compute_sha256(self, root: Path = PROJECT_ROOT) -> str:
        """Compute SHA-256 byte hash of the artifact file."""
        artifact_path = self.resolve_path(root)
        if not artifact_path.exists():
            raise FileNotFoundError(f"Model artifact not found: {artifact_path}")
        hasher = hashlib.sha256()
        with open(artifact_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest().upper()

    def verify(self, root: Path = PROJECT_ROOT) -> Tuple[bool, str]:
        """
        Verify that artifact exists on disk and its SHA-256 matches expected fingerprint.
        Returns: (is_valid, actual_hash_or_error_status)
        """
        artifact_path = self.resolve_path(root)
        if not artifact_path.exists():
            return False, "FILE_NOT_FOUND"
        actual_hash = self.compute_sha256(root)
        is_valid = actual_hash == self.expected_sha256.upper()
        return is_valid, actual_hash


class Settings(BaseSettings):
    """
    Application Settings for DecisionSphere Backend Service.
    Driven by environment variables with sensible development defaults.
    """
    # Environment & Metadata
    app_name: str = "DecisionSphere Strategic Decision Support API"
    app_version: str = "1.0.0-phase9"
    app_env: str = Field(default="development", description="development | testing | production")
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # Server Bindings
    host: str = "0.0.0.0"
    port: int = 8000

    # Path Anchors
    project_root: Path = PROJECT_ROOT
    backend_dir: Path = BACKEND_DIR
    models_dir: Path = PROJECT_ROOT / "models"
    data_dir: Path = PROJECT_ROOT / "data"

    # Logging
    log_level: str = "INFO"
    log_json: bool = True

    # Database Configuration Placeholder for Phase 9.1+
    database_url: str = Field(
        default="postgresql://decisionsphere:decisionsphere_dev_password@localhost:5432/decisionsphere_db",
        description="PostgreSQL connection URI",
    )

    # CORS Whitelist
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # Security Boundary (Single-user / Review 2 evaluation)
    api_key: Optional[str] = None
    api_key_header_name: str = "X-API-Key"

    # Authoritative Frozen Model Descriptors
    model_descriptors: Dict[str, ModelArtifactDescriptor] = {
        "demand": ModelArtifactDescriptor(
            key="demand",
            name="Retail Demand Forecasting XGBoost Regressor",
            relative_path="models/demand/demand_model.joblib",
            expected_sha256="FB438C03A742202657BB4EF9196FF17E004BC090E99218F02985DC7720F41941",
            domain="commercial",
            algorithm="XGBRegressor",
        ),
        "supply_chain": ModelArtifactDescriptor(
            key="supply_chain",
            name="DataCo Delivery Risk Calibrated XGBoost Classifier",
            relative_path="models/supply_chain/supply_chain_model.joblib",
            expected_sha256="0052E641CF355257ABB332703C3E6A46C65E9AB10A975227D83CF77D7E689B59",
            domain="logistics",
            algorithm="CalibratedClassifierCV(XGBClassifier)",
        ),
        "workforce": ModelArtifactDescriptor(
            key="workforce",
            name="IBM HR Attrition Calibrated XGBoost Classifier",
            relative_path="models/workforce/workforce_model.joblib",
            expected_sha256="4B195C7BEE3AB8F4AFE75CCD0C75FFF0C8E18B9FCA88A00305E165A010109918",
            domain="workforce",
            algorithm="CalibratedClassifierCV(XGBClassifier)",
        ),
    }

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def verify_model_artifacts(self) -> Dict[str, Dict[str, Any]]:
        """
        Verify all three ML model artifacts against authoritative SHA-256 signatures.
        Returns detailed report per model key.
        """
        report = {}
        for key, descriptor in self.model_descriptors.items():
            resolved_path = descriptor.resolve_path(self.project_root)
            exists = resolved_path.exists()
            if not exists:
                report[key] = {
                    "name": descriptor.name,
                    "path": str(resolved_path),
                    "exists": False,
                    "verified": False,
                    "expected_sha256": descriptor.expected_sha256,
                    "actual_sha256": None,
                    "status": "FILE_NOT_FOUND",
                }
                continue

            actual_sha256 = descriptor.compute_sha256(self.project_root)
            verified = actual_sha256 == descriptor.expected_sha256.upper()
            report[key] = {
                "name": descriptor.name,
                "path": str(resolved_path),
                "exists": True,
                "verified": verified,
                "expected_sha256": descriptor.expected_sha256,
                "actual_sha256": actual_sha256,
                "status": "VERIFIED" if verified else "HASH_MISMATCH",
            }
        return report

    def all_models_verified(self) -> bool:
        """Quick boolean probe confirming all 3 model artifacts pass SHA-256 verification."""
        report = self.verify_model_artifacts()
        return all(item["verified"] for item in report.values())


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached accessor for application settings."""
    return Settings()
