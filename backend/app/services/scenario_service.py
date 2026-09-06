"""
Scenario and ScenarioVersion Application Service (Milestone 9.3).
Manages scenario lifecycle, listing, archiving, and immutable versioning (Gate G).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
import uuid

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from backend.app.core.errors import EntityNotFoundError, ValidationAppError
from backend.app.models.scenario import Scenario, ScenarioVersion
from src.scenario.schema import ScenarioLevers


class ScenarioService:
    """
    Application service managing Scenarios and immutable ScenarioVersions.
    """

    @staticmethod
    def create_scenario(
        db: Session,
        name: str,
        description: Optional[str] = None,
        initial_levers: Optional[Union[Dict[str, Any], ScenarioLevers]] = None,
    ) -> Scenario:
        """
        Creates a new strategic scenario topic and optionally an initial version (v1).
        """
        clean_name = name.strip() if name else ""
        if not clean_name:
            raise ValidationAppError("Scenario name cannot be empty")

        scenario = Scenario(
            name=clean_name,
            description=description,
            is_archived=False,
        )
        db.add(scenario)
        db.flush()  # Populates scenario.id

        if initial_levers is not None:
            ScenarioService.create_scenario_version(db, scenario.id, initial_levers)

        db.commit()
        db.expire_all()
        return ScenarioService.get_scenario_or_404(db, scenario.id)

    @staticmethod
    def get_scenario(db: Session, scenario_id: uuid.UUID) -> Optional[Scenario]:
        """Fetch scenario by primary key."""
        return db.query(Scenario).filter_by(id=scenario_id).first()

    @staticmethod
    def get_scenario_or_404(db: Session, scenario_id: uuid.UUID) -> Scenario:
        """Fetch scenario by primary key or raise EntityNotFoundError."""
        scenario = ScenarioService.get_scenario(db, scenario_id)
        if not scenario:
            raise EntityNotFoundError(f"Scenario not found with ID: {scenario_id}")
        return scenario

    @staticmethod
    def list_scenarios(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        include_archived: bool = False,
    ) -> List[Scenario]:
        """List scenarios ordered by creation date descending."""
        query = db.query(Scenario)
        if not include_archived:
            query = query.filter(Scenario.is_archived == False)  # noqa: E712
        return query.order_by(Scenario.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def archive_scenario(db: Session, scenario_id: uuid.UUID) -> Scenario:
        """Archive a scenario without deleting historical versions or simulation runs."""
        scenario = ScenarioService.get_scenario_or_404(db, scenario_id)
        scenario.is_archived = True
        scenario.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(scenario)
        return scenario

    @staticmethod
    def update_scenario(
        db: Session,
        scenario_id: uuid.UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        new_levers: Optional[Union[Dict[str, Any], ScenarioLevers]] = None,
    ) -> Scenario:
        """
        Updates scenario metadata (name, description) and/or creates a new immutable version
        if new_levers are provided (Gate G: Version Immutability).
        """
        scenario = ScenarioService.get_scenario_or_404(db, scenario_id)
        if name is not None:
            clean_name = name.strip()
            if not clean_name:
                raise ValidationAppError("Scenario name cannot be empty")
            scenario.name = clean_name
        if description is not None:
            scenario.description = description
        if new_levers is not None:
            ScenarioService.create_scenario_version(db, scenario_id, new_levers)
        scenario.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.expire_all()
        return ScenarioService.get_scenario_or_404(db, scenario_id)

    @staticmethod
    def get_scenario_versions(db: Session, scenario_id: uuid.UUID) -> List[ScenarioVersion]:
        """Fetch all versions for a scenario, ordered by version_number ascending."""
        ScenarioService.get_scenario_or_404(db, scenario_id)
        return (
            db.query(ScenarioVersion)
            .filter_by(scenario_id=scenario_id)
            .order_by(ScenarioVersion.version_number.asc())
            .all()
        )

    @staticmethod
    def create_scenario_version(
        db: Session,
        scenario_id: uuid.UUID,
        levers: Union[Dict[str, Any], ScenarioLevers],
    ) -> ScenarioVersion:
        """
        Creates an immutable ScenarioVersion (Gate G: Version Immutability).
        Automatically increments version_number to max_version + 1.
        Prior versions remain strictly untouched.
        """
        scenario = ScenarioService.get_scenario_or_404(db, scenario_id)

        # Determine next version number atomically
        max_ver = (
            db.query(func.max(ScenarioVersion.version_number))
            .filter(ScenarioVersion.scenario_id == scenario_id)
            .scalar()
        )
        next_version = (max_ver or 0) + 1

        # Extract parameters from ScenarioLevers model or dict
        if isinstance(levers, ScenarioLevers):
            lever_dict = levers.model_dump()
        elif isinstance(levers, dict):
            lever_dict = levers
        else:
            raise ValidationAppError(f"Unsupported levers type: {type(levers).__name__}")

        version = ScenarioVersion(
            scenario_id=scenario.id,
            version_number=next_version,
            demand_growth_pct=float(lever_dict.get("demand_growth_pct", 0.0)),
            promo_active=bool(lever_dict.get("promo_active", False)),
            scheduled_days_offset=int(lever_dict.get("scheduled_days_offset", 0)),
            shipping_mode_override=lever_dict.get("shipping_mode_override"),
            overtime_workforce_pct=float(lever_dict.get("overtime_workforce_pct", 0.0)),
            salary_hike_override=float(lever_dict.get("salary_hike_override", 0.0) or 0.0),
            unit_price=float(lever_dict.get("unit_price", 1.0)),
        )

        db.add(version)
        scenario.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(version)
        return version

    @staticmethod
    def get_scenario_version(db: Session, version_id: uuid.UUID) -> Optional[ScenarioVersion]:
        """Fetch scenario version by ID."""
        return db.query(ScenarioVersion).filter_by(id=version_id).first()

    @staticmethod
    def get_scenario_version_or_404(db: Session, version_id: uuid.UUID) -> ScenarioVersion:
        """Fetch scenario version by ID or raise EntityNotFoundError."""
        version = ScenarioService.get_scenario_version(db, version_id)
        if not version:
            raise EntityNotFoundError(f"ScenarioVersion not found with ID: {version_id}")
        return version

    @staticmethod
    def get_latest_version(db: Session, scenario_id: uuid.UUID) -> Optional[ScenarioVersion]:
        """Get the latest immutable version for a given scenario."""
        return (
            db.query(ScenarioVersion)
            .filter_by(scenario_id=scenario_id)
            .order_by(ScenarioVersion.version_number.desc())
            .first()
        )


scenario_service = ScenarioService()
