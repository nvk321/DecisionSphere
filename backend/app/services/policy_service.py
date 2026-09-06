"""
AssumptionPolicy Application Service (Milestone 9.3).
Manages versioned, immutable corporate parameter policies (ASM-001 through ASM-010)
and maps relational records to Phase 7 and Phase 8 analytical contracts.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.core.errors import EntityNotFoundError, ValidationAppError
from backend.app.models.policy import AssumptionPolicy
from src.business.schema import BusinessAssumptions
from src.recommendation.schema import CRSWeights


class PolicyService:
    """
    Application service managing corporate policies governing financial and risk assumptions.
    """

    @staticmethod
    def get_or_create_default_policy(db: Session) -> AssumptionPolicy:
        """
        Retrieves baseline corporate policy (version 1) or initializes it if not present.
        """
        policy = db.query(AssumptionPolicy).filter_by(version_number=1).first()
        if policy is not None:
            return policy

        # Initialize official baseline corporate policy (ASM-001 to ASM-010)
        policy = AssumptionPolicy(
            version_number=1,
            name="Corporate Baseline Policy",
            description="Authoritative baseline corporate parameter set (ASM-001 to ASM-010).",
            late_penalty_rate=25.0,        # ASM-001
            expedite_fee=15.0,             # ASM-002
            stockout_churn_factor=0.15,    # ASM-003
            replacement_cost=30000.0,      # ASM-004
            overtime_wage_rate=45.0,       # ASM-005
            order_scaling_factor=1.0,      # ASM-007
            planning_cycle_days=30,        # ASM-008
            crs_w_supply=0.40,             # ASM-009
            crs_w_workforce=0.40,          # ASM-009
            crs_w_demand=0.20,             # ASM-009
            tau_risk=50.0,                 # ASM-010
            cogs_ratio=0.60,
        )
        db.add(policy)
        db.commit()
        db.refresh(policy)
        return policy

    @staticmethod
    def get_policy(db: Session, policy_id: uuid.UUID) -> Optional[AssumptionPolicy]:
        """Fetch policy by UUID primary key."""
        return db.query(AssumptionPolicy).filter_by(id=policy_id).first()

    @staticmethod
    def get_policy_or_404(db: Session, policy_id: uuid.UUID) -> AssumptionPolicy:
        """Fetch policy by UUID primary key or raise EntityNotFoundError."""
        policy = PolicyService.get_policy(db, policy_id)
        if not policy:
            raise EntityNotFoundError(f"AssumptionPolicy not found with ID: {policy_id}")
        return policy

    @staticmethod
    def get_policy_by_version(db: Session, version_number: int) -> Optional[AssumptionPolicy]:
        """Fetch policy by explicit version number."""
        return db.query(AssumptionPolicy).filter_by(version_number=version_number).first()

    @staticmethod
    def list_policies(db: Session, skip: int = 0, limit: int = 100) -> List[AssumptionPolicy]:
        """List all versioned corporate policies ordered by version ascending."""
        return (
            db.query(AssumptionPolicy)
            .order_by(AssumptionPolicy.version_number.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def create_policy_version(
        db: Session,
        policy_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> AssumptionPolicy:
        """
        Creates a new immutable policy version.
        Computes next version_number atomically.
        """
        data = dict(policy_data or {})
        data.update(kwargs)

        max_ver = db.query(func.max(AssumptionPolicy.version_number)).scalar()
        next_ver = (max_ver or 0) + 1

        name = data.get("name", f"Policy Version {next_ver}").strip()
        if not name:
            raise ValidationAppError("Policy name cannot be empty")

        # Validate CRS simplex constraint if supplied
        w_supply = float(data.get("crs_w_supply", data.get("w_supply", 0.40)))
        w_workforce = float(data.get("crs_w_workforce", data.get("w_workforce", 0.40)))
        w_demand = float(data.get("crs_w_demand", data.get("w_demand", 0.20)))
        weight_sum = w_supply + w_workforce + w_demand
        if abs(weight_sum - 1.0) > 1e-4:
            raise ValidationAppError(
                f"CRS weights must satisfy simplex sum=1.0 (got {weight_sum:.4f})"
            )

        policy = AssumptionPolicy(
            version_number=next_ver,
            name=name,
            description=data.get("description"),
            late_penalty_rate=float(data.get("late_penalty_rate", 25.0)),
            expedite_fee=float(data.get("expedite_fee", 15.0)),
            stockout_churn_factor=float(data.get("stockout_churn_factor", 0.15)),
            replacement_cost=float(data.get("replacement_cost", 30000.0)),
            overtime_wage_rate=float(data.get("overtime_wage_rate", 45.0)),
            order_scaling_factor=float(data.get("order_scaling_factor", 1.0)),
            planning_cycle_days=int(data.get("planning_cycle_days", 30)),
            crs_w_supply=w_supply,
            crs_w_workforce=w_workforce,
            crs_w_demand=w_demand,
            tau_risk=float(data.get("tau_risk", 50.0)),
            cogs_ratio=float(data.get("cogs_ratio", 0.60)),
        )

        db.add(policy)
        db.commit()
        db.refresh(policy)
        return policy

    @staticmethod
    def to_business_assumptions(policy: AssumptionPolicy) -> BusinessAssumptions:
        """
        Maps relational AssumptionPolicy to Phase 7 BusinessAssumptions contract.
        """
        return BusinessAssumptions(
            asm_001_delay_penalty=policy.late_penalty_rate,
            asm_002_expedite_fee=policy.expedite_fee,
            asm_003_cancellation_factor=policy.stockout_churn_factor,
            asm_004_replacement_cost=policy.replacement_cost,
            asm_005_overtime_rate=policy.overtime_wage_rate,
            cogs_ratio=policy.cogs_ratio,
        )

    @staticmethod
    def to_crs_weights(policy: AssumptionPolicy) -> CRSWeights:
        """
        Maps relational AssumptionPolicy to Phase 8 CRSWeights simplex contract.
        """
        return CRSWeights(
            w_supply=policy.crs_w_supply,
            w_workforce=policy.crs_w_workforce,
            w_demand=policy.crs_w_demand,
        )


policy_service = PolicyService()
