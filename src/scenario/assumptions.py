"""
DecisionSphere — Parametric Assumptions Registry (ASM-001 through ASM-008)
Authoritative implementation of Table 1 from docs/assumptions-and-open-questions.md.
Guarantees strict separation between Phase 6 operational assumptions and Phase 7 financial assumptions.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Set, Union, Optional


@dataclass(frozen=True)
class AssumptionMetadata:
    """
    Immutable representation of an explicitly declared operational coupling parameter.
    """
    id: str
    domain: str
    name: str
    math_symbol: str
    baseline_value: Union[int, float]
    sensitivity_range: Union[tuple, List[Union[int, float]]]
    unit: str
    source_grounding: str
    phase: int  # Phase 6 (operational) or Phase 7 (financial)
    epistemic_tier: str = "ASSUMED"


# The Authoritative 8-Parameter Registry
_REGISTRY_ENTRIES: List[AssumptionMetadata] = [
    AssumptionMetadata(
        id="ASM-001",
        domain="Supply Chain",
        name="Contractual late-delivery penalty",
        math_symbol="C_delay_penalty",
        baseline_value=25.00,
        sensitivity_range=(10.00, 60.00),
        unit="USD / delayed order",
        source_grounding="Standard 3PL carrier SLA delay penalty benchmark.",
        phase=7,
    ),
    AssumptionMetadata(
        id="ASM-002",
        domain="Supply Chain",
        name="Expedited freight shipping surcharge",
        math_symbol="C_expedite_fee",
        baseline_value=15.00,
        sensitivity_range=(5.00, 35.00),
        unit="USD / expedited order",
        source_grounding="Commercial air courier surcharge over ground freight.",
        phase=7,
    ),
    AssumptionMetadata(
        id="ASM-003",
        domain="Supply Chain",
        name="Late-order cancellation / demand-loss factor",
        math_symbol="kappa_stockout",
        baseline_value=0.15,
        sensitivity_range=(0.05, 0.40),
        unit="dimensionless churn ratio",
        source_grounding="E-commerce industry fulfillment delay churn benchmark.",
        phase=7,
    ),
    AssumptionMetadata(
        id="ASM-004",
        domain="Workforce",
        name="Employee replacement / turnover cost",
        math_symbol="C_replacement",
        baseline_value=30000.00,
        sensitivity_range=(15000.00, 60000.00),
        unit="USD / departed employee",
        source_grounding="SHRM benchmark (50% to 75% of median annual compensation).",
        phase=7,
    ),
    AssumptionMetadata(
        id="ASM-005",
        domain="Workforce",
        name="Overtime hourly labor premium rate",
        math_symbol="R_overtime",
        baseline_value=45.00,
        sensitivity_range=(30.00, 75.00),
        unit="USD / overtime hour",
        source_grounding="Standard US FLSA 1.5x premium over $30/hr base rate.",
        phase=7,
    ),
    AssumptionMetadata(
        id="ASM-006",
        domain="Scenario Engine",
        name="Overtime-induced satisfaction decrement",
        math_symbol="Delta_WLB",
        baseline_value=-1,
        sensitivity_range=[-2, -1, 0],
        unit="WorkLifeBalance ordinal scale levels",
        source_grounding="Heuristic parameter for organizational burnout under sustained overtime.",
        phase=6,
    ),
    AssumptionMetadata(
        id="ASM-007",
        domain="Enterprise Normalization",
        name="Order-volume scaling factor",
        math_symbol="gamma_volume",
        baseline_value=1.00,
        sensitivity_range=(0.50, 2.00),
        unit="orders / sales unit",
        source_grounding=(
            "Synthetic normalization bridge between the demand model's predicted retail volume "
            "and the scenario engine's operational order-volume representation. "
            "It is not an empirically learned sales-to-order conversion coefficient."
        ),
        phase=6,
    ),
    AssumptionMetadata(
        id="ASM-008",
        domain="Temporal Synchronization",
        name="Daily-to-monthly planning cycle alignment factor",
        math_symbol="tau_cycle",
        baseline_value=30,
        sensitivity_range=(14, 90),
        unit="days",
        source_grounding="Operational planning cadence aligning daily demand with monthly operations.",
        phase=6,
    ),
]


class AssumptionRegistry:
    """
    Central authoritative repository for all DecisionSphere operational coupling constants.
    """

    def __init__(self):
        self._registry: Dict[str, AssumptionMetadata] = {
            entry.id: entry for entry in _REGISTRY_ENTRIES
        }

    def get(self, asm_id: str) -> AssumptionMetadata:
        asm_id_clean = asm_id.strip().upper()
        if asm_id_clean not in self._registry:
            raise KeyError(
                f"Unknown assumption ID '{asm_id}'. Valid IDs are: {list(self._registry.keys())}"
            )
        return self._registry[asm_id_clean]

    def list_all(self) -> List[AssumptionMetadata]:
        return list(self._registry.values())

    def get_phase_assumptions(self, phase: int) -> List[AssumptionMetadata]:
        return [entry for entry in self._registry.values() if entry.phase == phase]

    def validate_value(self, asm_id: str, value: Union[int, float]) -> bool:
        meta = self.get(asm_id)
        if isinstance(meta.sensitivity_range, list):
            return value in meta.sensitivity_range
        elif isinstance(meta.sensitivity_range, tuple):
            low, high = meta.sensitivity_range
            return low <= value <= high
        return False


# Singleton registry instance
ASM_REGISTRY = AssumptionRegistry()

PHASE_6_OPERATIONAL_ASSUMPTIONS: Set[str] = {"ASM-006", "ASM-007", "ASM-008"}
PHASE_7_FINANCIAL_ASSUMPTIONS: Set[str] = {"ASM-001", "ASM-002", "ASM-003", "ASM-004", "ASM-005"}
