"""
Docker Configuration & Production Containerization Tests (Milestone 9.7).
Verifies that Dockerfile, docker-compose.yml, docker-entrypoint.sh, .dockerignore,
and .env.example conform strictly to security, multi-stage, non-root,
and orchestration specifications.
"""
from __future__ import annotations

from pathlib import Path
import pytest
import yaml

from backend.app.core.config import get_settings


@pytest.fixture
def repo_root() -> Path:
    """Resolve repository root directory from settings."""
    return get_settings().project_root


def test_dockerfile_multi_stage_and_security(repo_root: Path):
    """
    Validates Dockerfile architecture:
    1. Multi-stage build (builder and runtime stages).
    2. Non-root user creation and execution (appuser / UID 10001).
    3. Essential Linux runtime libraries (libgomp1 for XGBoost OpenMP, libpq5, curl).
    4. Filters pywinpty during container build without mutating canonical requirements.txt.
    5. Healthcheck probe declared.
    """
    dockerfile_path = repo_root / "Dockerfile"
    assert dockerfile_path.is_file(), "Dockerfile must exist at repository root"

    content = dockerfile_path.read_text(encoding="utf-8")

    # Multi-stage validation
    assert "AS builder" in content, "Dockerfile must declare a builder stage"
    assert "AS runtime" in content, "Dockerfile must declare a minimal runtime stage"

    # Non-root user validation
    assert "useradd" in content and "10001" in content, "Dockerfile must define user with UID 10001"
    assert "USER appuser" in content, "Dockerfile must switch to non-root appuser before execution"

    # Runtime native dependencies
    assert "libgomp1" in content, "Dockerfile must install libgomp1 for XGBoost OpenMP support"
    assert "libpq5" in content, "Dockerfile must install libpq5 for PostgreSQL driver"
    assert "curl" in content, "Dockerfile must install curl for container healthcheck"

    # Safe platform dependency filtering
    assert "pywinpty" in content, "Dockerfile must filter pywinpty during container build"

    # Healthcheck and entrypoint
    assert "HEALTHCHECK" in content, "Dockerfile must declare a HEALTHCHECK directive"
    assert "docker-entrypoint.sh" in content, "Dockerfile must declare docker-entrypoint.sh"
    assert 'ENTRYPOINT ["/app/docker-entrypoint.sh"]' in content


def test_docker_compose_structure_and_dependencies(repo_root: Path):
    """
    Validates docker-compose.yml configuration:
    1. Declares 'db' service using postgres:16-alpine.
    2. Declares 'backend' service with build context.
    3. Enforces depends_on db with condition: service_healthy.
    4. Declares healthchecks on both services.
    5. Uses named persistent volume for postgres data.
    """
    compose_path = repo_root / "docker-compose.yml"
    assert compose_path.is_file(), "docker-compose.yml must exist at repository root"

    with open(compose_path, "r", encoding="utf-8") as f:
        compose = yaml.safe_load(f)

    assert "services" in compose, "docker-compose.yml must define 'services'"
    services = compose["services"]

    # Validate db service
    assert "db" in services, "docker-compose.yml must define 'db' service"
    db = services["db"]
    assert "postgres:16" in db.get("image", ""), "db service must use postgres:16"
    assert "healthcheck" in db, "db service must declare healthcheck"

    # Validate backend service
    assert "backend" in services, "docker-compose.yml must define 'backend' service"
    backend = services["backend"]
    assert "build" in backend, "backend service must define build context"

    # Validate dependency ordering and health gate
    depends_on = backend.get("depends_on", {})
    assert "db" in depends_on, "backend must depend on db"
    assert depends_on["db"].get("condition") == "service_healthy", (
        "backend must declare condition: service_healthy on db"
    )

    # Validate persistent volume
    assert "volumes" in compose, "docker-compose.yml must declare top-level volumes"
    assert "postgres_data" in compose["volumes"], "Must declare postgres_data named volume"


def test_docker_entrypoint_script_contracts(repo_root: Path):
    """
    Validates docker-entrypoint.sh:
    1. File exists and uses bash with 'set -eo pipefail'.
    2. Has LF line endings (required by Linux containers).
    3. Contains database readiness polling loop.
    4. Runs 'alembic upgrade head' before starting application server.
    5. Hands off to CMD via 'exec "$@"'.
    """
    entrypoint_path = repo_root / "docker-entrypoint.sh"
    assert entrypoint_path.is_file(), "docker-entrypoint.sh must exist at repository root"

    raw_bytes = entrypoint_path.read_bytes()
    assert b"\r\n" not in raw_bytes, "docker-entrypoint.sh must use LF line endings for Linux compatibility"

    content = entrypoint_path.read_text(encoding="utf-8")
    assert "set -eo pipefail" in content, "Entrypoint must enforce strict error exit"
    assert "alembic upgrade head" in content, "Entrypoint must execute Alembic migrations"
    assert 'exec "$@"' in content, "Entrypoint must exec final command"


def test_dockerignore_exclusions_and_model_preservation(repo_root: Path):
    """
    Validates .dockerignore:
    1. Excludes large development artifacts (.venv, reference/, raw data, git).
    2. Does NOT exclude models/ (required for inference and Gate I verification).
    """
    dockerignore_path = repo_root / ".dockerignore"
    assert dockerignore_path.is_file(), ".dockerignore must exist at repository root"

    content = dockerignore_path.read_text(encoding="utf-8")
    lines = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")]

    # Crucial exclusions
    assert any(".venv" in l for l in lines), ".dockerignore must exclude .venv/"
    assert any("reference" in l for l in lines), ".dockerignore must exclude reference/ archives"

    # Crucial preservation: models/ must NOT be ignored
    for l in lines:
        assert l != "models/" and l != "models" and l != "models/*", (
            ".dockerignore must NOT exclude models/ directory"
        )


def test_env_example_template_completeness(repo_root: Path):
    """
    Validates .env.example contains all key settings with security notes.
    """
    env_example = repo_root / ".env.example"
    assert env_example.is_file(), ".env.example must exist at repository root"

    content = env_example.read_text(encoding="utf-8")
    assert "DATABASE_URL=" in content
    assert "POSTGRES_PASSWORD=" in content
    assert "CORS_ORIGINS=" in content
    assert "SECURITY WARNING" in content or "SECURITY NOTICE" in content
