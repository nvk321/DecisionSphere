import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Union

DEFAULT_MODEL_PATH = "models/supply_chain/supply_chain_model.joblib"

class SupplyChainInferenceService:
    """
    Production inference service for conditional late-delivery risk prediction.
    Loads the serialized preprocessor, base model, calibrated model, and threshold once.
    Provides single-instance inference, batch scoring, scenario evaluation, and monotonicity diagnostics.
    """
    def __init__(self, model_path: str = DEFAULT_MODEL_PATH):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model artifact bundle not found at {model_path}. Train model first.")
            
        self.model_path = model_path
        self.bundle = joblib.load(model_path)
        
        self.preprocessor = self.bundle["preprocessor"]
        self.base_model = self.bundle["base_model"]
        self.calibrated_model = self.bundle.get("calibrated_model")
        self.decision_threshold = float(self.bundle.get("decision_threshold", 0.5))
        self.feature_names = self.bundle["feature_names"]
        self.numerical_features = self.bundle["numerical_features"]
        self.categorical_features = self.bundle["categorical_features"]
        self.metadata = self.bundle.get("training_metadata", {})

    def predict_risk(self, order_dict: Dict[str, Any], use_calibrated: bool = True) -> Dict[str, Any]:
        """
        Single-order conditional late delivery risk prediction.
        
        Parameters:
        -----------
        order_dict : Dictionary containing order-time attributes.
        use_calibrated : Whether to apply the sigmoid calibration mapping (default True).
        
        Returns:
        --------
        Dictionary conforming to DecisionSphere epistemic contract.
        """
        df_inst = pd.DataFrame([order_dict])
        for col in self.categorical_features:
            if col not in df_inst.columns:
                df_inst[col] = "Unknown"
            else:
                df_inst[col] = df_inst[col].astype(str).str.strip()
                
        for col in self.numerical_features:
            if col not in df_inst.columns:
                df_inst[col] = 0.0
            else:
                df_inst[col] = pd.to_numeric(df_inst[col], errors="coerce").fillna(0.0)
                
        df_inst = df_inst[self.feature_names]
        X_proc = self.preprocessor.transform(df_inst)
        
        raw_prob = float(self.base_model.predict_proba(X_proc)[0, 1])
        
        if use_calibrated and self.calibrated_model is not None:
            cal_prob = float(self.calibrated_model.predict_proba(X_proc)[0, 1])
            final_prob = cal_prob
            is_cal = True
        else:
            final_prob = raw_prob
            is_cal = False
            
        pred_class = int(final_prob >= self.decision_threshold)
        
        return {
            "risk_probability": round(final_prob, 4),
            "raw_probability": round(raw_prob, 4),
            "risk_class": pred_class,
            "decision_threshold": round(self.decision_threshold, 4),
            "is_calibrated": is_cal,
            "epistemic_tier": "PREDICTED",
            "statement": (
                f"Conditional predicted late-delivery risk is {final_prob:.1%}. "
                "Output reflects statistical inference conditioned on order-time features."
            )
        }

    def predict_batch(self, df: pd.DataFrame, use_calibrated: bool = True) -> pd.DataFrame:
        """
        Batch prediction for high-throughput operational evaluation.
        Preserves original DataFrame row indexing and identity.
        """
        df_in = df.copy()
        for col in self.categorical_features:
            if col not in df_in.columns:
                df_in[col] = "Unknown"
            else:
                df_in[col] = df_in[col].astype(str).str.strip()
                
        for col in self.numerical_features:
            if col not in df_in.columns:
                df_in[col] = 0.0
            else:
                df_in[col] = pd.to_numeric(df_in[col], errors="coerce").fillna(0.0)
                
        X_in = df_in[self.feature_names]
        X_proc = self.preprocessor.transform(X_in)
        
        raw_probs = self.base_model.predict_proba(X_proc)[:, 1]
        
        if use_calibrated and self.calibrated_model is not None:
            final_probs = self.calibrated_model.predict_proba(X_proc)[:, 1]
        else:
            final_probs = raw_probs
            
        pred_classes = (final_probs >= self.decision_threshold).astype(int)
        
        results_df = pd.DataFrame(index=df.index)
        results_df["predicted_late_risk_probability"] = np.round(final_probs, 4)
        results_df["predicted_late_risk_raw_probability"] = np.round(raw_probs, 4)
        results_df["predicted_late_risk_class"] = pred_classes
        results_df["epistemic_tier"] = "PREDICTED"
        
        return results_df

    def simulate_scenario(
        self,
        orders_df: pd.DataFrame,
        shipping_mode_override: Optional[str] = None,
        scheduled_days_offset: int = 0,
        use_calibrated: bool = True
    ) -> Dict[str, Any]:
        """
        Executes conditional scenario simulation on a cohort of orders.
        Evaluates how model predictions shift under hypothetical operational interventions.
        
        Does NOT mutate the input DataFrame.
        Does NOT claim that feature modifications cause real-world delivery changes.
        """
        if orders_df.empty:
            raise ValueError("Input orders_df cannot be empty.")
            
        # 1. Evaluate baseline predictions
        base_preds = self.predict_batch(orders_df, use_calibrated=use_calibrated)
        base_mean_prob = float(base_preds["predicted_late_risk_probability"].mean())
        
        # 2. Construct hypothetical scenario DataFrame (isolated copy)
        scenario_df = orders_df.copy()
        scenario_applied = {}
        
        if shipping_mode_override is not None:
            scenario_df["shipping_mode"] = str(shipping_mode_override).strip()
            scenario_applied["shipping_mode_override"] = str(shipping_mode_override)
            
        if scheduled_days_offset != 0:
            if "days_for_shipment_scheduled" in scenario_df.columns:
                scenario_df["days_for_shipment_scheduled"] = np.maximum(
                    0, scenario_df["days_for_shipment_scheduled"] + scheduled_days_offset
                )
            scenario_applied["scheduled_days_offset"] = int(scheduled_days_offset)
            
        # 3. Evaluate scenario predictions
        scen_preds = self.predict_batch(scenario_df, use_calibrated=use_calibrated)
        scen_mean_prob = float(scen_preds["predicted_late_risk_probability"].mean())
        delta_prob = scen_mean_prob - base_mean_prob
        
        return {
            "baseline_mean_probability": round(base_mean_prob, 4),
            "scenario_mean_probability": round(scen_mean_prob, 4),
            "delta_probability": round(delta_prob, 4),
            "scenario_definition": scenario_applied,
            "orders_evaluated": len(orders_df),
            "epistemic_tier": "PREDICTED",
            "interpretation": (
                f"Model-predicted mean late delivery risk shifted from {base_mean_prob:.1%} to {scen_mean_prob:.1%} "
                f"({delta_prob:+.1%}) under the hypothetical feature configuration."
            )
        }

    def evaluate_monotonicity(
        self,
        orders_df: pd.DataFrame,
        scheduled_days_sweep: List[int] = None
    ) -> Dict[str, Any]:
        """
        Empirical diagnostic evaluating whether the model's predicted risk behaves
        monotonically as planned shipping days are varied.
        Does not force monotonicity to pass. Reports empirical findings honestly.
        """
        if scheduled_days_sweep is None:
            scheduled_days_sweep = [0, 1, 2, 4]
            
        sweep_results = []
        for days in scheduled_days_sweep:
            scen_df = orders_df.copy()
            scen_df["days_for_shipment_scheduled"] = days
            preds = self.predict_batch(scen_df)
            mean_p = float(preds["predicted_late_risk_probability"].mean())
            sweep_results.append({"scheduled_days": days, "mean_risk_probability": round(mean_p, 4)})
            
        # Check monotonicity
        probs = [r["mean_risk_probability"] for r in sweep_results]
        is_strictly_decreasing = all(x > y for x, y in zip(probs, probs[1:]))
        is_strictly_increasing = all(x < y for x, y in zip(probs, probs[1:]))
        is_monotonic = is_strictly_decreasing or is_strictly_increasing
        
        behavior = "strictly_decreasing" if is_strictly_decreasing else ("strictly_increasing" if is_strictly_increasing else "non_monotonic")
        
        return {
            "sweep": sweep_results,
            "is_monotonic": is_monotonic,
            "monotonic_direction": behavior,
            "epistemic_tier": "PREDICTED",
            "diagnostic_note": (
                "Empirical measurement of model response to scheduled lead-time variations. "
                "Monotonicity is a diagnostic characteristic, not a required constraint."
            )
        }
