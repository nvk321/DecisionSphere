"""
DecisionSphere — Phase 6 Scenario Engine Orchestrator
Executes multi-domain scenario translation, parameter propagation, and independent inference
across frozen predictive models while preserving cryptographic integrity, baseline immutability,
and strict 6-tier epistemic boundaries.
"""

import os
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple

import numpy as np
import pandas as pd

from src.models.demand.inference import DemandForecaster
from src.models.supply_chain.inference import SupplyChainInferenceService
from src.models.workforce.inference import WorkforceInferenceService
from src.scenario.schema import (
    ScenarioLevers,
    ScenarioAssumptions,
    DomainProvenance,
    DomainPredictionResult,
    WorkforceCohortSummary,
    ScenarioRunResult,
)
from src.scenario.assumptions import ASM_REGISTRY


DEFAULT_DEMAND_PATH = "models/demand/demand_model.joblib"
DEFAULT_SUPPLY_PATH = "models/supply_chain/supply_chain_model.joblib"
DEFAULT_WORKFORCE_PATH = "models/workforce/workforce_model.joblib"


def _compute_sha256(filepath: str) -> str:
    """Computes SHA-256 hex digest of a file on disk."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Model artifact not found at '{filepath}'")
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


class ScenarioEngine:
    """
    Central orchestration engine for DecisionSphere multi-domain scenario simulation.
    
    Guarantees:
    - Cryptographic model artifact integrity verification.
    - Zero mutation of baseline datasets or model weights.
    - Strict epistemic tagging: OBSERVED, PREDICTED, ASSUMED, PROPAGATED, CALCULATED.
    - Deterministic overtime assignment mapping for workforce cohorts.
    - Absolute exclusion of financial calculations (strictly deferred to Phase 7).
    """

    def __init__(
        self,
        demand_artifact_path: str = DEFAULT_DEMAND_PATH,
        supply_artifact_path: str = DEFAULT_SUPPLY_PATH,
        workforce_artifact_path: str = DEFAULT_WORKFORCE_PATH,
    ):
        self.demand_artifact_path = demand_artifact_path
        self.supply_artifact_path = supply_artifact_path
        self.workforce_artifact_path = workforce_artifact_path

        # 1. Compute and register cryptographic fingerprints
        self._artifact_hashes = {
            "demand": _compute_sha256(demand_artifact_path),
            "supply_chain": _compute_sha256(supply_artifact_path),
            "workforce": _compute_sha256(workforce_artifact_path),
        }

        # 2. Instantiate isolated inference services
        self.demand_service = DemandForecaster(artifact_path=demand_artifact_path)
        self.supply_service = SupplyChainInferenceService(model_path=supply_artifact_path)
        self.workforce_service = WorkforceInferenceService(model_path=workforce_artifact_path)

        # 3. Cached evaluation datasets (loaded on demand)
        self._cached_demand_context: Optional[Dict[str, Any]] = None
        self._cached_orders_df: Optional[pd.DataFrame] = None
        self._cached_workforce_df: Optional[pd.DataFrame] = None

    def verify_artifact_integrity(self) -> Dict[str, bool]:
        """
        Re-hashes the model artifacts on disk to verify zero modification.
        """
        current_hashes = {
            "demand": _compute_sha256(self.demand_artifact_path),
            "supply_chain": _compute_sha256(self.supply_artifact_path),
            "workforce": _compute_sha256(self.workforce_artifact_path),
        }
        status = {}
        for key in self._artifact_hashes:
            match = current_hashes[key] == self._artifact_hashes[key]
            if not match:
                raise RuntimeError(
                    f"Model artifact '{key}' was modified! "
                    f"Expected SHA-256: {self._artifact_hashes[key]}, Found: {current_hashes[key]}"
                )
            status[key] = match
        return status

    def get_artifact_fingerprints(self) -> Dict[str, str]:
        """Returns the cryptographic SHA-256 fingerprints of the loaded models."""
        return dict(self._artifact_hashes)

    def get_default_demand_context(self) -> Dict[str, Any]:
        """
        Generates standard baseline demand evaluation context (Store 1, 35-day history).
        """
        if self._cached_demand_context is None:
            dates = pd.date_range("2015-06-01", periods=35, freq="D")
            sales = [5000.0 + np.sin(i) * 500 for i in range(35)]
            hist_df = pd.DataFrame({"Date": dates, "Sales": sales})
            metadata = {
                "StoreType_Encoded": 0,
                "Assortment_Encoded": 0,
                "LogCompetitionDistance": 8.0,
                "CompetitionOpen": 1,
                "Promo2": 0,
                "Promo2Active": 0,
                "SchoolHoliday": 0,
                "StateHoliday_Encoded": 0,
            }
            self._cached_demand_context = {
                "store_id": 1,
                "store_metadata": metadata,
                "history_series": hist_df,
                "start_date": "2015-07-06",
            }
        return self._cached_demand_context

    def get_default_orders_df(self, sample_size: int = 100) -> pd.DataFrame:
        """
        Loads a representative sample of test orders from the DataCo chronological holdout.
        """
        if self._cached_orders_df is None:
            from src.data.dataco_loader import load_dataco_raw
            from src.data.dataco_features import create_dataco_features, split_chronological_dataco

            df_raw = load_dataco_raw()
            df_feat = create_dataco_features(df_raw)
            _, _, test_df = split_chronological_dataco(df_feat)
            self._cached_orders_df = test_df.head(sample_size).copy()
        return self._cached_orders_df.copy()

    def get_default_workforce_df(self, sample_size: int = 221) -> pd.DataFrame:
        """
        Loads the representative test holdout cohort from the IBM HR benchmark.
        """
        if self._cached_workforce_df is None:
            from src.data.ibm_hr_loader import load_ibm_hr_raw
            from src.data.ibm_hr_features import create_ibm_hr_features, split_stratified_ibm_hr

            df_raw = load_ibm_hr_raw()
            df_feat = create_ibm_hr_features(df_raw)
            _, _, test_df = split_stratified_ibm_hr(df_feat, random_state=42)
            self._cached_workforce_df = test_df.head(sample_size).copy()
        return self._cached_workforce_df.copy()

    def run_scenario(
        self,
        levers: ScenarioLevers,
        assumptions: Optional[ScenarioAssumptions] = None,
        demand_context: Optional[Dict[str, Any]] = None,
        orders_df: Optional[pd.DataFrame] = None,
        workforce_df: Optional[pd.DataFrame] = None,
        horizon_days: int = 14,
    ) -> ScenarioRunResult:
        """
        Executes an end-to-end multi-domain scenario simulation.
        
        Parameters:
        -----------
        levers : Strongly typed ScenarioLevers defining user shocks.
        assumptions : Optional ScenarioAssumptions (defaults to Table 1 baselines).
        demand_context : Optional Store context dictionary.
        orders_df : Optional DataFrame of orders for logistics evaluation.
        workforce_df : Optional DataFrame of employees for workforce evaluation.
        horizon_days : Forecast horizon in days (default 14).
        
        Returns:
        --------
        ScenarioRunResult with unrounded deltas and cryptographic provenance.
        """
        if assumptions is None:
            assumptions = ScenarioAssumptions()

        # 1. Pre-execution integrity & immutability verification
        self.verify_artifact_integrity()

        # 2. Derive deterministic scenario identifier if not provided
        if levers.scenario_id:
            scenario_id = levers.scenario_id
        else:
            canonical_repr = {
                "levers": levers.model_dump(exclude={"scenario_id"}),
                "assumptions": assumptions.model_dump(),
            }
            canonical_bytes = json.dumps(canonical_repr, sort_keys=True).encode("utf-8")
            scenario_id = f"scen_{hashlib.sha256(canonical_bytes).hexdigest()[:10]}"

        # 3. Load or validate input cohorts
        if demand_context is None:
            demand_context = self.get_default_demand_context()
        if orders_df is None:
            orders_df = self.get_default_orders_df()
        if workforce_df is None:
            workforce_df = self.get_default_workforce_df()

        # Capture initial checksums to verify immutability
        orders_input_copy = orders_df.copy(deep=True)
        workforce_input_copy = workforce_df.copy(deep=True)

        # =========================================================================
        # DOMAIN 1: RETAIL DEMAND EVALUATION (Rossmann Forecaster)
        # =========================================================================
        base_promo = [0] * horizon_days
        sim_promo = [1 if levers.promo_active else 0] * horizon_days

        base_demand = self.demand_service.predict_horizon(
            store_id=demand_context["store_id"],
            store_metadata=demand_context["store_metadata"],
            history_series=demand_context["history_series"],
            start_date=demand_context["start_date"],
            horizon_days=horizon_days,
            promo_schedule=base_promo,
        )
        base_sales = float(base_demand["total_projected_sales_units"])

        sim_demand = self.demand_service.predict_horizon(
            store_id=demand_context["store_id"],
            store_metadata=demand_context["store_metadata"],
            history_series=demand_context["history_series"],
            start_date=demand_context["start_date"],
            horizon_days=horizon_days,
            promo_schedule=sim_promo,
        )
        sim_sales_raw = float(sim_demand["total_projected_sales_units"])
        
        # Apply demand growth shock percentage
        sim_sales = float(sim_sales_raw * (1.0 + levers.demand_growth_pct / 100.0))
        demand_delta = sim_sales - base_sales

        # Calculate Normalized Monthly Volume via ASM-008
        daily_rate = sim_sales / horizon_days
        normalized_cycle_volume = daily_rate * assumptions.asm_008_cycle_days

        # Calculate Normalized Dispatch Orders via ASM-007
        normalized_order_volume = normalized_cycle_volume * assumptions.asm_007_volume_scaling

        demand_provenance = DomainProvenance(
            source_model="Retail Demand Forecasting (XGBoost Regressor)",
            model_artifact=self.demand_artifact_path,
            artifact_sha256=self._artifact_hashes["demand"],
            epistemic_tier="PREDICTED",
            input_modifications={
                "promo_active": levers.promo_active,
                "demand_growth_pct": levers.demand_growth_pct,
            },
            assumptions_applied=["ASM-007", "ASM-008"],
            causal_claim=False,
            calculation_description=(
                f"Recursive autoregressive multi-step sales forecast over {horizon_days} days. "
                f"Volume normalized to {assumptions.asm_008_cycle_days}-day planning cycle via ASM-008 "
                f"and scaled by ASM-007."
            ),
        )

        demand_result = DomainPredictionResult(
            domain="Demand",
            unit="Sales units",
            baseline_value=base_sales,
            scenario_value=sim_sales,
            delta_value=demand_delta,
            provenance=demand_provenance,
        )

        # =========================================================================
        # DOMAIN 2: SUPPLY CHAIN DELIVERY RISK EVALUATION (DataCo Calibrated XGBoost)
        # =========================================================================
        # 1. Baseline prediction on unmutated copy
        base_supply_preds = self.supply_service.predict_batch(orders_df, use_calibrated=True)
        base_late_prob = float(base_supply_preds["predicted_late_risk_probability"].mean())
        sc_threshold = round(float(self.supply_service.decision_threshold), 4)
        base_sc_class = int(base_late_prob >= sc_threshold)

        # 2. Construct isolated scenario orders DataFrame
        scenario_orders_df = orders_df.copy(deep=True)
        sc_mods = {}

        if levers.scheduled_days_offset != 0:
            if "days_for_shipment_scheduled" in scenario_orders_df.columns:
                scenario_orders_df["days_for_shipment_scheduled"] = np.maximum(
                    0, scenario_orders_df["days_for_shipment_scheduled"] + levers.scheduled_days_offset
                )
            sc_mods["scheduled_days_offset"] = levers.scheduled_days_offset

        if levers.shipping_mode_override is not None:
            scenario_orders_df["shipping_mode"] = levers.shipping_mode_override
            sc_mods["shipping_mode_override"] = levers.shipping_mode_override

        # 3. Scenario prediction
        scen_supply_preds = self.supply_service.predict_batch(scenario_orders_df, use_calibrated=True)
        scen_late_prob = float(scen_supply_preds["predicted_late_risk_probability"].mean())
        scen_sc_class = int(scen_late_prob >= sc_threshold)
        late_delta = scen_late_prob - base_late_prob

        sc_stmt = None
        if base_sc_class != scen_sc_class:
            sc_stmt = (
                f"Late-risk classification shifted from {base_sc_class} to {scen_sc_class} "
                f"at decision threshold tau* = {sc_threshold:.2f}."
            )

        supply_provenance = DomainProvenance(
            source_model="Supply Chain Late Delivery Risk (Calibrated XGBoost)",
            model_artifact=self.supply_artifact_path,
            artifact_sha256=self._artifact_hashes["supply_chain"],
            epistemic_tier="PREDICTED",
            input_modifications=sc_mods,
            assumptions_applied=[],
            causal_claim=False,
            calculation_description=(
                f"Mean Sigmoid-calibrated late-delivery probability across {len(orders_df)} orders. "
                "Output reflects statistical inference conditioned on order attributes and schedule offsets."
            ),
        )

        supply_result = DomainPredictionResult(
            domain="Supply Chain",
            unit="Probability (0.0 to 1.0)",
            baseline_value=base_late_prob,
            scenario_value=scen_late_prob,
            delta_value=late_delta,
            decision_threshold=sc_threshold,
            baseline_class=base_sc_class,
            scenario_class=scen_sc_class,
            classification_change_statement=sc_stmt,
            provenance=supply_provenance,
        )

        # =========================================================================
        # DOMAIN 3: WORKFORCE ATTRITION RISK EVALUATION (IBM HR Calibrated XGBoost)
        # =========================================================================
        # 1. Baseline prediction on unmutated copy
        base_wf_preds = self.workforce_service.predict_batch(workforce_df, use_calibrated=True)
        base_att_prob = float(base_wf_preds["predicted_attrition_probability"].mean())
        wf_threshold = round(float(self.workforce_service.decision_threshold), 4)
        base_wf_class = int(base_att_prob >= wf_threshold)

        # 2. Deterministic Overtime Assignment Mapping
        scenario_wf_df = workforce_df.copy(deep=True)
        n_headcount = len(scenario_wf_df)

        base_ot_mask = (scenario_wf_df["OverTime"].astype(str).str.strip() == "Yes")
        k_base = int(base_ot_mask.sum())
        target_pct = levers.overtime_workforce_pct
        target_count_float = n_headcount * (target_pct / 100.0)
        k_target = int(np.ceil(np.round(target_count_float, 9)))
        switched_count = 0

        if k_target > k_base:
            needed = k_target - k_base
            # Deterministically select first `needed` employees currently at OverTime == 'No'
            candidate_indices = scenario_wf_df.index[~base_ot_mask][:needed]
            scenario_wf_df.loc[candidate_indices, "OverTime"] = "Yes"
            switched_count = len(candidate_indices)
            actual_ot_count = k_target
        else:
            # Baseline already meets or exceeds target; preserve existing assignments
            actual_ot_count = k_base

        actual_ot_pct = round((actual_ot_count / n_headcount) * 100.0, 2)

        # 3. Apply ASM-006: Heuristic WorkLifeBalance decrement for overtime workers
        scen_ot_mask = (scenario_wf_df["OverTime"].astype(str).str.strip() == "Yes")
        if assumptions.asm_006_wlb_decrement != 0 and scen_ot_mask.any():
            scenario_wf_df.loc[scen_ot_mask, "WorkLifeBalance"] = np.clip(
                scenario_wf_df.loc[scen_ot_mask, "WorkLifeBalance"] + assumptions.asm_006_wlb_decrement,
                1,
                4,
            )

        wf_mods = {
            "target_overtime_pct": target_pct,
            "switched_employees_count": switched_count,
            "actual_overtime_pct": actual_ot_pct,
            "asm_006_wlb_decrement": assumptions.asm_006_wlb_decrement,
        }

        # 4. Apply salary hike override if specified
        if levers.salary_hike_override is not None:
            scenario_wf_df["PercentSalaryHike"] = levers.salary_hike_override
            wf_mods["salary_hike_override"] = levers.salary_hike_override

        # 5. Scenario prediction
        scen_wf_preds = self.workforce_service.predict_batch(scenario_wf_df, use_calibrated=True)
        scen_att_prob = float(scen_wf_preds["predicted_attrition_probability"].mean())
        scen_wf_class = int(scen_att_prob >= wf_threshold)
        att_delta = scen_att_prob - base_att_prob

        wf_stmt = None
        if base_wf_class != scen_wf_class:
            wf_stmt = (
                f"Attrition-risk classification shifted from {base_wf_class} to {scen_wf_class} "
                f"at decision threshold tau* = {wf_threshold:.2f}."
            )

        cohort_summary = WorkforceCohortSummary(
            total_headcount=n_headcount,
            baseline_overtime_count=k_base,
            scenario_overtime_count=actual_ot_count,
            overtime_switched_count=switched_count,
            target_overtime_percentage=target_pct,
            actual_scenario_overtime_percentage=actual_ot_pct,
            wlb_decrement_applied=assumptions.asm_006_wlb_decrement,
            epistemic_tier="PROPAGATED",
        )

        workforce_provenance = DomainProvenance(
            source_model="Workforce Attrition Risk (Calibrated XGBoost)",
            model_artifact=self.workforce_artifact_path,
            artifact_sha256=self._artifact_hashes["workforce"],
            epistemic_tier="PREDICTED",
            input_modifications=wf_mods,
            assumptions_applied=["ASM-006"],
            causal_claim=False,
            calculation_description=(
                f"Mean Sigmoid-calibrated attrition probability across cohort of {n_headcount} employees. "
                "OverTime assigned deterministically; WorkLifeBalance adjusted via ASM-006. "
                "Output reflects statistical inference conditioned on employee operational configurations."
            ),
        )

        workforce_result = DomainPredictionResult(
            domain="Workforce",
            unit="Probability (0.0 to 1.0)",
            baseline_value=base_att_prob,
            scenario_value=scen_att_prob,
            delta_value=att_delta,
            decision_threshold=wf_threshold,
            baseline_class=base_wf_class,
            scenario_class=scen_wf_class,
            classification_change_statement=wf_stmt,
            provenance=workforce_provenance,
        )

        # =========================================================================
        # POST-EXECUTION IMMUTABILITY AND INTEGRITY CHECKS
        # =========================================================================
        pd.testing.assert_frame_equal(orders_df, orders_input_copy)
        pd.testing.assert_frame_equal(workforce_df, workforce_input_copy)
        self.verify_artifact_integrity()

        # Non-causal multi-domain synthesis statement
        interpretation = (
            f"Multi-domain scenario '{levers.scenario_name}' (ID: {scenario_id}) executed across 3 independent "
            f"predictive domains. Demand forecast shifted by {demand_delta:+.1f} units; "
            f"Supply chain late delivery risk shifted by {late_delta:+.2%}; "
            f"Workforce mean attrition risk shifted by {att_delta:+.2%}. "
            "All shifts represent conditional statistical predictions under explicitly declared operational assumptions. "
            "No causal claims or financial valuations are inferred."
        )

        return ScenarioRunResult(
            scenario_id=scenario_id,
            scenario_name=levers.scenario_name,
            levers=levers,
            assumptions=assumptions,
            demand_result=demand_result,
            supply_chain_result=supply_result,
            workforce_result=workforce_result,
            workforce_cohort_summary=cohort_summary,
            normalized_order_volume=normalized_order_volume,
            execution_timestamp=datetime.now(timezone.utc).isoformat(),
            epistemic_tier="PROPAGATED",
            interpretation=interpretation,
        )
