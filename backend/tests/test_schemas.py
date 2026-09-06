"""
Test Suite for Pydantic v2 API Schemas & DTOs (Milestone 9.4).
Verifies Gate E (API Schema Validation Gate), extra="forbid" rejection,
numerical lever boundary limits, simplex constraint enforcement,
and ORM-to-DTO serialization.
"""
import uuid
import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

from backend.app.schemas import (
    AuditProvenanceDTO,
    AuditRecordResponse,
    CRSWeightsDTO,
    CRSWeightSweepRequest,
    DemandShockSweepRequest,
    DomainPredictionResponse,
    EpistemicTier,
    ErrorResponse,
    FinancialResultResponse,
    FinancialSweepRequest,
    FlipThresholdSearchRequest,
    HealthResponse,
    ModelStatusResponse,
    PolicyCreate,
    PolicyResponse,
    RecommendationResponse,
    ScenarioCreate,
    ScenarioLeversSchema,
    ScenarioResponse,
    ScenarioUpdate,
    ScenarioVersionResponse,
    SimulationDetailResponse,
    SimulationRequest,
    SimulationRunSummaryResponse,
    StrategicActionDTO,
)
from backend.app.services import (
    policy_service,
    scenario_service,
    simulation_orchestrator,
)


# ==============================================================================
# 1. Gate E: extra="forbid" Rejection Tests
# ==============================================================================

def test_gate_e_extra_forbid_rejection():
    """
    Gate E: API Schema Validation Gate.
    Inbound request payloads with extraneous keys must be rejected with ValidationError.
    """
    # 1. ScenarioCreate with rogue attribute
    with pytest.raises(ValidationError) as exc_info:
        ScenarioCreate(name="Valid Name", rogue_field="disallowed")
    assert "extra_forbidden" in str(exc_info.value)

    # 2. ScenarioUpdate with rogue attribute
    with pytest.raises(ValidationError) as exc_info:
        ScenarioUpdate(name="New Name", malicious_payload={"drop": "database"})
    assert "extra_forbidden" in str(exc_info.value)

    # 3. ScenarioLeversSchema with rogue attribute
    with pytest.raises(ValidationError) as exc_info:
        ScenarioLeversSchema(demand_growth_pct=10.0, unknown_parameter=42)
    assert "extra_forbidden" in str(exc_info.value)

    # 4. PolicyCreate with rogue attribute
    with pytest.raises(ValidationError) as exc_info:
        PolicyCreate(name="Default", custom_rogue_constant=99.9)
    assert "extra_forbidden" in str(exc_info.value)

    # 5. SimulationRequest with rogue attribute
    with pytest.raises(ValidationError) as exc_info:
        SimulationRequest(scenario_version_id=uuid.uuid4(), unapproved_flag=True)
    assert "extra_forbidden" in str(exc_info.value)

    # 6. FinancialSweepRequest with rogue attribute
    with pytest.raises(ValidationError) as exc_info:
        FinancialSweepRequest(
            parameter_name="asm_001_delay_penalty",
            candidate_values=[10.0, 20.0],
            hack="injection",
        )
    assert "extra_forbidden" in str(exc_info.value)


# ==============================================================================
# 2. Gate E: Numerical Boundary Limits & Format Enforcement
# ==============================================================================

def test_gate_e_scenario_levers_boundary_limits():
    """Verify strict empirical boundaries on ScenarioLeversSchema."""
    # Valid baseline
    valid = ScenarioLeversSchema()
    assert valid.demand_growth_pct == 0.0
    assert valid.epistemic_tier == "ASSUMED"

    # demand_growth_pct bounds [-50.0, 100.0]
    with pytest.raises(ValidationError) as exc:
        ScenarioLeversSchema(demand_growth_pct=-50.1)
    assert "greater_than_equal" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        ScenarioLeversSchema(demand_growth_pct=100.1)
    assert "less_than_equal" in str(exc.value)

    # scheduled_days_offset bounds [-3, 3]
    with pytest.raises(ValidationError) as exc:
        ScenarioLeversSchema(scheduled_days_offset=-4)
    assert "greater_than_equal" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        ScenarioLeversSchema(scheduled_days_offset=4)
    assert "less_than_equal" in str(exc.value)

    # shipping_mode_override valid options
    valid_mode = ScenarioLeversSchema(shipping_mode_override="First Class")
    assert valid_mode.shipping_mode_override == "First Class"

    with pytest.raises(ValidationError) as exc:
        ScenarioLeversSchema(shipping_mode_override="Drone Delivery Express")
    assert "Invalid shipping_mode_override" in str(exc.value)

    # overtime_workforce_pct bounds [0.0, 100.0]
    with pytest.raises(ValidationError):
        ScenarioLeversSchema(overtime_workforce_pct=-0.1)

    with pytest.raises(ValidationError):
        ScenarioLeversSchema(overtime_workforce_pct=100.1)

    # salary_hike_override bounds [0.0, 50.0]
    with pytest.raises(ValidationError):
        ScenarioLeversSchema(salary_hike_override=-1.0)

    with pytest.raises(ValidationError):
        ScenarioLeversSchema(salary_hike_override=50.1)


def test_gate_e_scenario_create_string_constraints():
    """Verify string validation on ScenarioCreate."""
    # Empty name rejected
    with pytest.raises(ValidationError) as exc:
        ScenarioCreate(name="")
    assert "string_too_short" in str(exc.value)

    # Whitespace-only name stripped and rejected
    with pytest.raises(ValidationError):
        ScenarioCreate(name="   ")

    # Excessive description length rejected (> 2000 chars)
    with pytest.raises(ValidationError) as exc:
        ScenarioCreate(name="Test", description="A" * 2001)
    assert "string_too_long" in str(exc.value)


# ==============================================================================
# 3. Gate E: Assumption Policy Simplex & Parameter Limits
# ==============================================================================

def test_gate_e_policy_simplex_and_financial_bounds():
    """Verify simplex equality constraint and financial parameter ranges on PolicyCreate."""
    # 1. Simplex violation: sum = 1.1 != 1.0
    with pytest.raises(ValidationError) as exc:
        PolicyCreate(name="Invalid Policy", w_supply=0.5, w_workforce=0.4, w_demand=0.2)
    assert "simplex equality" in str(exc.value)

    # 2. Simplex violation: sum = 0.9 != 1.0
    with pytest.raises(ValidationError) as exc:
        PolicyCreate(name="Invalid Policy", w_supply=0.3, w_workforce=0.3, w_demand=0.3)
    assert "simplex equality" in str(exc.value)

    # 3. Valid simplex passes cleanly
    valid_policy = PolicyCreate(
        name="Valid Policy",
        w_supply=0.40,
        w_workforce=0.40,
        w_demand=0.20,
    )
    assert valid_policy.w_supply == 0.40

    # 4. Negative delay penalty
    with pytest.raises(ValidationError):
        PolicyCreate(name="Negative Penalty", asm_001_delay_penalty=-10.0)

    # 5. Cancellation factor > 1.0
    with pytest.raises(ValidationError):
        PolicyCreate(name="Excess Cancellation", asm_003_cancellation_factor=1.05)

    # 6. Replacement cost > 60000.0
    with pytest.raises(ValidationError):
        PolicyCreate(name="Excess Replacement", asm_004_replacement_cost=65000.0)

    # 7. tau_risk out of [0, 100]
    with pytest.raises(ValidationError):
        PolicyCreate(name="Negative Tau", tau_risk=-5.0)

    with pytest.raises(ValidationError):
        PolicyCreate(name="Excess Tau", tau_risk=105.0)


def test_gate_e_crs_weights_dto_simplex():
    """Verify simplex equality validator in CRSWeightsDTO."""
    # Valid
    dto = CRSWeightsDTO(w_supply=0.70, w_workforce=0.20, w_demand=0.10)
    assert dto.w_supply == 0.70

    # Invalid sum
    with pytest.raises(ValidationError) as exc:
        CRSWeightsDTO(w_supply=0.5, w_workforce=0.5, w_demand=0.5)
    assert "must sum to 1.0" in str(exc.value)


def test_gate_e_financial_sweep_parameter_whitelist():
    """Verify whitelist validation on FinancialSweepRequest."""
    # Valid parameter
    valid_req = FinancialSweepRequest(
        parameter_name="asm_001_delay_penalty",
        candidate_values=[10.0, 20.0, 30.0],
    )
    assert valid_req.parameter_name == "asm_001_delay_penalty"

    # Unknown parameter
    with pytest.raises(ValidationError) as exc:
        FinancialSweepRequest(
            parameter_name="invented_speculative_cost",
            candidate_values=[10.0],
        )
    assert "Unknown financial parameter" in str(exc.value)


# ==============================================================================
# 4. ORM-to-DTO Bidirectional Serialization Tests
# ==============================================================================

def test_orm_to_dto_scenario_transformation(db_session: Session):
    """Verify Scenario and ScenarioVersion ORM instances transform cleanly into DTOs."""
    scenario = scenario_service.create_scenario(
        db=db_session,
        name="DTO Transform Scenario",
        description="Scenario for testing DTO transformation",
        initial_levers={"demand_growth_pct": 12.5, "promo_active": True},
    )

    # Validate DTO transformation
    scenario_dto = ScenarioResponse.model_validate(scenario)
    assert scenario_dto.id == scenario.id
    assert scenario_dto.name == "DTO Transform Scenario"
    assert scenario_dto.description == "Scenario for testing DTO transformation"
    assert scenario_dto.is_archived is False
    assert scenario_dto.latest_version is not None
    assert scenario_dto.latest_version.version_number == 1
    assert scenario_dto.latest_version.demand_growth_pct == 12.5
    assert scenario_dto.latest_version.promo_active is True

    # Validate helper levers property
    levers = scenario_dto.latest_version.levers
    assert levers.demand_growth_pct == 12.5
    assert levers.promo_active is True
    assert levers.epistemic_tier == "ASSUMED"


def test_orm_to_dto_policy_transformation(db_session: Session):
    """Verify AssumptionPolicy ORM instance transforms cleanly into PolicyResponse DTO."""
    policy = policy_service.get_or_create_default_policy(db_session)

    policy_dto = PolicyResponse.model_validate(policy)
    assert policy_dto.id == policy.id
    assert policy_dto.name == policy.name
    assert policy_dto.asm_001_delay_penalty == 25.0
    assert policy_dto.asm_002_expedite_fee == 15.0
    assert policy_dto.asm_003_cancellation_factor == 0.15
    assert policy_dto.asm_004_replacement_cost == 30000.0
    assert policy_dto.asm_005_overtime_rate == 45.0
    assert policy_dto.cogs_ratio == 0.60
    assert policy_dto.w_supply == 0.40
    assert policy_dto.w_workforce == 0.40
    assert policy_dto.w_demand == 0.20
    assert policy_dto.tau_risk == 50.0


def test_orm_to_dto_simulation_detail_transformation(db_session: Session):
    """
    Verify complete SimulationRun relational tree transforms into SimulationDetailResponse.
    Validates epistemic tier tags and Gate H provenance tuple.
    """
    scenario = scenario_service.create_scenario(
        db=db_session,
        name="Simulation DTO Test",
        initial_levers={"demand_growth_pct": 10.0},
    )
    version = scenario_service.get_latest_version(db_session, scenario.id)
    policy = policy_service.get_or_create_default_policy(db_session)

    # Execute simulation and persist
    run = simulation_orchestrator.execute_and_persist(db_session, version.id, policy.id)

    # Transform to DTO
    detail_dto = SimulationDetailResponse.model_validate(run)
    assert detail_dto.id == run.id
    assert detail_dto.status in {"SUCCESS", "COMPLETED"}
    assert detail_dto.duration_ms is not None
    assert detail_dto.duration_ms > 0.0

    # 1. Predictions DTO
    assert len(detail_dto.predictions) == 3
    domains = {p.domain for p in detail_dto.predictions}
    assert domains == {"DEMAND", "SUPPLY_CHAIN", "WORKFORCE"}
    for pred in detail_dto.predictions:
        assert pred.epistemic_tier == "PREDICTED"
        assert pred.delta_value is not None

    # 2. Financial Result DTO
    assert detail_dto.financial_result is not None
    fin = detail_dto.financial_result
    assert fin.epistemic_tier == "CALCULATED"
    assert fin.net_profit_delta is not None
    assert len(fin.line_items) == 7
    for item in fin.line_items:
        assert item.epistemic_tier == "CALCULATED"
        assert item.category in {"REVENUE", "EXPENSE", "MARGIN"}

    # 3. Recommendation Result DTO
    assert detail_dto.recommendation_result is not None
    rec = detail_dto.recommendation_result
    assert rec.epistemic_tier == "RECOMMENDED"
    assert rec.decision_category in {"PROCEED", "PROCEED_WITH_MITIGATIONS", "REJECT_RESTRUCTURE"}
    assert 0.0 <= rec.composite_risk_score <= 100.0
    assert rec.risk_level in {"LOW", "MODERATE", "HIGH", "SEVERE"}
    assert len(rec.strategic_actions) >= 0
    for action in rec.strategic_actions:
        assert action.epistemic_tier == "RECOMMENDED"
        assert action.severity in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}

    # 4. Audit Record & Gate H Provenance Tuple
    assert detail_dto.audit_record is not None
    audit = detail_dto.audit_record
    assert len(audit.model_hashes) == 3
    assert "demand" in audit.model_hashes
    assert "supply_chain" in audit.model_hashes
    assert "workforce" in audit.model_hashes

    # Validate provenance tuple matches AuditProvenanceDTO
    prov_dto = AuditProvenanceDTO.model_validate(audit.provenance_tuple)
    assert prov_dto.scenario_version_id == version.id
    assert prov_dto.policy_id == policy.id
    assert prov_dto.policy_version == policy.version_number
    assert len(prov_dto.artifact_hashes) == 3
    assert prov_dto.git_commit is not None


# ==============================================================================
# 5. Common Error & Health Schema Tests
# ==============================================================================

def test_error_and_health_schemas():
    """Verify ErrorResponse, HealthResponse, and ModelStatusResponse schemas."""
    # ErrorResponse
    err = ErrorResponse(
        error_code="VALIDATION_ERROR",
        message="Request failed validation",
        details=[{"loc": ["body", "demand_growth_pct"], "msg": "Out of range", "type": "value_error"}],
        request_id="req-123-abc",
    )
    assert err.error_code == "VALIDATION_ERROR"
    assert err.request_id == "req-123-abc"

    # HealthResponse
    health = HealthResponse(
        status="healthy",
        app_name="DecisionSphere API",
        version="0.1.0",
        database="connected",
        models_verified=True,
    )
    assert health.status == "healthy"
    assert health.models_verified is True

    # EpistemicTier enum completeness
    expected_tiers = {"OBSERVED", "PREDICTED", "ASSUMED", "PROPAGATED", "CALCULATED", "RECOMMENDED"}
    actual_tiers = {tier.value for tier in EpistemicTier}
    assert actual_tiers == expected_tiers
