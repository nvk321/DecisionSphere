import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional

from src.data.ibm_hr_features import (
    ALL_PREDICTOR_FEATURES,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
)

DEFAULT_WORKFORCE_MODEL_PATH = "models/workforce/workforce_model.joblib"


class WorkforceInferenceService:
    """
    Production-grade inference service for the Phase 4 Workforce Attrition Pipeline.
    Encapsulates preprocessing, base XGBoost inference, Sigmoid calibration,
    threshold classification, and non-causal scenario simulation.
    """

    def __init__(self, model_path: str = DEFAULT_WORKFORCE_MODEL_PATH):
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Workforce model bundle not found at '{model_path}'. "
                "Ensure training pipeline has been executed."
            )
        bundle = joblib.load(model_path)
        self.preprocessor = bundle["preprocessor"]
        self.base_model = bundle["base_model"]
        self.calibrated_model = bundle.get("calibrated_model")
        self.decision_threshold = float(bundle.get("decision_threshold", 0.50))
        self.feature_names = bundle.get("feature_names", ALL_PREDICTOR_FEATURES)
        self.numerical_features = bundle.get("numerical_features", NUMERICAL_FEATURES)
        self.categorical_features = bundle.get("categorical_features", CATEGORICAL_FEATURES)
        self.training_metadata = bundle.get("training_metadata", {})

    def predict_attrition(
        self,
        employee_dict: Dict[str, Any],
        use_calibrated: bool = True,
    ) -> Dict[str, Any]:
        """
        Single-employee conditional attrition probability prediction.
        
        Parameters:
        -----------
        employee_dict : Dictionary containing employee attributes.
        use_calibrated : Whether to use Sigmoid calibrated probability (default True).
        
        Returns:
        --------
        Dict conforming to DecisionSphere epistemic contract.
        """
        df_inst = pd.DataFrame([employee_dict])
        
        # Robust type coercion
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
            "attrition_probability": round(final_prob, 4),
            "raw_probability": round(raw_prob, 4),
            "attrition_class": pred_class,
            "decision_threshold": round(self.decision_threshold, 4),
            "is_calibrated": is_cal,
            "epistemic_tier": "PREDICTED",
            "statement": (
                f"Conditional predicted attrition probability is {final_prob:.1%}. "
                "Output reflects statistical inference conditioned on employee attributes and workload configuration."
            ),
        }

    def predict_batch(
        self,
        df: pd.DataFrame,
        use_calibrated: bool = True,
    ) -> pd.DataFrame:
        """
        Batch prediction preserving original DataFrame row indexing and ordering.
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
            is_cal = True
        else:
            final_probs = raw_probs
            is_cal = False
            
        pred_classes = (final_probs >= self.decision_threshold).astype(int)
        
        results_df = pd.DataFrame(index=df.index)
        results_df["predicted_attrition_probability"] = np.round(final_probs, 4)
        results_df["predicted_attrition_raw_probability"] = np.round(raw_probs, 4)
        results_df["predicted_attrition_class"] = pred_classes
        results_df["epistemic_tier"] = "PREDICTED"
        results_df["is_calibrated"] = is_cal
        
        return results_df

    def simulate_scenario(
        self,
        employees_df: pd.DataFrame,
        overtime_override: Optional[str] = None,
        salary_hike_override: Optional[float] = None,
        use_calibrated: bool = True,
    ) -> Dict[str, Any]:
        """
        Evaluates conditional predicted attrition probability under an assumed
        hypothetical feature modification (e.g. mandating overtime or adjusting compensation).
        
        Guarantees:
        - Baseline invariance: Does NOT mutate the input DataFrame.
        - Strictly non-causal epistemic framing: Output represents model-predicted conditional
          probability differences, not evidence of a physical or economic causal treatment effect.
        """
        # 1. Evaluate baseline predictions on unmutated input
        base_preds = self.predict_batch(employees_df, use_calibrated=use_calibrated)
        base_mean_prob = float(base_preds["predicted_attrition_probability"].mean())
        
        # 2. Construct isolated scenario modification
        scenario_df = employees_df.copy()
        scenario_applied = {}
        
        if overtime_override is not None:
            overtime_val = str(overtime_override).strip()
            if overtime_val not in ["Yes", "No"]:
                raise ValueError(f"overtime_override must be 'Yes' or 'No', got '{overtime_override}'")
            scenario_df["OverTime"] = overtime_val
            scenario_applied["overtime_override"] = overtime_val
            
        if salary_hike_override is not None:
            salary_hike_val = float(salary_hike_override)
            scenario_df["PercentSalaryHike"] = salary_hike_val
            scenario_applied["salary_hike_override"] = salary_hike_val
            
        # 3. Evaluate scenario predictions
        scen_preds = self.predict_batch(scenario_df, use_calibrated=use_calibrated)
        scen_mean_prob = float(scen_preds["predicted_attrition_probability"].mean())
        delta_prob = scen_mean_prob - base_mean_prob
        
        return {
            "baseline_mean_probability": round(base_mean_prob, 4),
            "scenario_mean_probability": round(scen_mean_prob, 4),
            "delta_probability": round(delta_prob, 4),
            "scenario_definition": scenario_applied,
            "employees_evaluated": len(employees_df),
            "epistemic_tier": "PREDICTED",
            "interpretation": (
                f"Model-predicted mean attrition probability shifted from {base_mean_prob:.1%} to {scen_mean_prob:.1%} "
                f"({delta_prob:+.1%}) under the assumed feature modification. "
                "The scenario modification represents an assumed change to an input feature. "
                "The resulting probability difference represents the model's conditional response "
                "and is not evidence of a causal effect."
            ),
        }
