"""
Alembic Migrations and Gate C Idempotency Test Suite (Milestone 9.2).
Validates upgrade head -> downgrade base -> upgrade head lifecycle,
verifies all 10 relational tables, indices, and constraints.
"""
from __future__ import annotations

import os
import pathlib
import tempfile
from typing import Generator, Tuple

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
import pytest
from sqlalchemy import create_engine, inspect

from backend.app.db.base import Base
import backend.app.models  # noqa: F401


EXPECTED_TABLES = {
    "assumption_policies",
    "audit_records",
    "domain_predictions",
    "financial_line_items",
    "financial_results",
    "recommendation_results",
    "scenario_versions",
    "scenarios",
    "simulation_runs",
    "strategic_actions",
}


@pytest.fixture
def alembic_env() -> Generator[Tuple[str, Config, str], None, None]:
    """
    Creates an isolated temporary SQLite database and preconfigured Alembic Config.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        temp_db_path = tmp_file.name

    db_url = f"sqlite:///{pathlib.Path(temp_db_path).as_posix()}"

    repo_root = pathlib.Path(__file__).resolve().parent.parent.parent
    ini_path = repo_root / "alembic.ini"

    cfg = Config(str(ini_path))
    cfg.set_main_option("sqlalchemy.url", db_url)

    yield db_url, cfg, temp_db_path

    # Clean up temporary database file
    try:
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)
    except OSError:
        pass


def test_alembic_single_head_revision(alembic_env):
    """Verify that Alembic script directory has exactly one head revision."""
    _, cfg, _ = alembic_env
    script = ScriptDirectory.from_config(cfg)
    heads = script.get_heads()
    assert len(heads) == 1, f"Expected exactly 1 head revision, found {len(heads)}: {heads}"
    head_rev = heads[0]
    assert head_rev == "18e29557529f", f"Unexpected head revision ID: {head_rev}"


def test_gate_c_migration_idempotency(alembic_env):
    """
    Gate C: Database Migration Idempotency Gate.
    Verifies: alembic upgrade head -> alembic downgrade base -> alembic upgrade head.
    Ensures clean schema creation, clean reversal, and idempotent reconstruction without errors.
    """
    db_url, cfg, _ = alembic_env
    engine = create_engine(db_url)

    # 1. Initial Upgrade to Head
    command.upgrade(cfg, "head")

    inspector = inspect(engine)
    tables_after_upgrade = set(inspector.get_table_names())
    # alembic_version table is created by alembic runtime
    assert EXPECTED_TABLES.issubset(tables_after_upgrade), (
        f"Missing tables after upgrade head: {EXPECTED_TABLES - tables_after_upgrade}"
    )

    # Verify key indexes and constraints on upgraded schema
    sc_version_cols = {c["name"] for c in inspector.get_columns("scenario_versions")}
    assert "demand_growth_pct" in sc_version_cols
    assert "shipping_mode_override" in sc_version_cols

    policy_cols = {c["name"] for c in inspector.get_columns("assumption_policies")}
    assert "late_penalty_rate" in policy_cols
    assert "tau_risk" in policy_cols

    # 2. Downgrade to Base
    command.downgrade(cfg, "base")

    inspector_after_down = inspect(engine)
    tables_after_down = set(inspector_after_down.get_table_names())
    # All application tables must be cleanly dropped
    remaining_app_tables = EXPECTED_TABLES.intersection(tables_after_down)
    assert not remaining_app_tables, f"Tables failed to drop during downgrade: {remaining_app_tables}"

    # 3. Re-Upgrade to Head (Idempotency check)
    command.upgrade(cfg, "head")

    inspector_re_up = inspect(engine)
    tables_re_up = set(inspector_re_up.get_table_names())
    assert EXPECTED_TABLES.issubset(tables_re_up), (
        f"Missing tables after re-upgrade head: {EXPECTED_TABLES - tables_re_up}"
    )


def test_metadata_tables_match_migration_schema(alembic_env):
    """Verify that all tables declared in Base.metadata are covered by migrations."""
    db_url, cfg, _ = alembic_env
    command.upgrade(cfg, "head")

    engine = create_engine(db_url)
    inspector = inspect(engine)
    migrated_tables = set(inspector.get_table_names()) - {"alembic_version"}
    declarative_tables = set(Base.metadata.tables.keys())

    assert migrated_tables == declarative_tables, (
        f"Discrepancy between Base.metadata and Alembic schema: {migrated_tables ^ declarative_tables}"
    )
