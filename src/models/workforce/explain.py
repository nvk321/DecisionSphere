import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List
import shap

from src.data.ibm_hr_loader import load_ibm_hr_raw
from src.data.ibm_hr_features import (
    create_ibm_hr_features,
    split_stratified_ibm_hr,
    ALL_PREDICTOR_FEATURES,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
)

MODELS_DIR = "models/workforce"
MODEL_PATH = os.path.join(MODELS_DIR, "workforce_model.joblib")
FEATURE_IMPORTANCE_PATH = os.path.join(MODELS_DIR, "feature_importance.json")


def compute_and_serialize_workforce_shap(
    model_path: str = MODEL_PATH,
    output_path: str = FEATURE_IMPORTANCE_PATH,
    random_state: int = 42,
) -> Dict[str, Any]:
    """
    Computes empirical TreeSHAP feature attributions on the untouched Test holdout.
    Aggregates encoded categorical columns back to high-level domain features.
    Conducts a ranking stability check across sub-partitions.
    Serializes results to models/workforce/feature_importance.json.
    """
    bundle = joblib.load(model_path)
    base_xgb = bundle["base_model"]
    preprocessor = bundle["preprocessor"]
    
    # Ingest raw and build test holdout
    df_raw = load_ibm_hr_raw()
    df_feat = create_ibm_hr_features(df_raw)
    _, _, test_df = split_stratified_ibm_hr(df_feat, random_state=random_state)
    
    X_test_raw = test_df[ALL_PREDICTOR_FEATURES]
    X_test_proc = preprocessor.transform(X_test_raw)
    
    # ColumnTransformer feature names
    encoded_feature_names = preprocessor.get_feature_names_out()
    
    # Initialize TreeSHAP Explainer
    explainer = shap.TreeExplainer(base_xgb)
    shap_values = explainer.shap_values(X_test_proc)
    
    # Map encoded features back to high-level features
    high_level_shap = {feat: 0.0 for feat in ALL_PREDICTOR_FEATURES}
    detailed_shap = []
    
    for idx, enc_name in enumerate(encoded_feature_names):
        mean_abs_val = float(np.mean(np.abs(shap_values[:, idx])))
        detailed_shap.append({
            "encoded_feature": str(enc_name),
            "mean_abs_shap": round(mean_abs_val, 6),
        })
        
        # Map back to high-level name
        matched_hl = None
        for hl in ALL_PREDICTOR_FEATURES:
            if enc_name.startswith(f"num__{hl}") or enc_name.startswith(f"cat__{hl}"):
                matched_hl = hl
                break
        if matched_hl:
            high_level_shap[matched_hl] += mean_abs_val
        else:
            high_level_shap[enc_name] = mean_abs_val
            
    # Sort high-level features
    sorted_hl = sorted(high_level_shap.items(), key=lambda x: x[1], reverse=True)
    sorted_detailed = sorted(detailed_shap, key=lambda x: x["mean_abs_shap"], reverse=True)
    
    # Stability check across two deterministic test halves (N1, N2)
    half_n = len(X_test_proc) // 2
    shap_half1 = explainer.shap_values(X_test_proc[:half_n])
    shap_half2 = explainer.shap_values(X_test_proc[half_n:])
    
    hl_half1 = {feat: 0.0 for feat in ALL_PREDICTOR_FEATURES}
    hl_half2 = {feat: 0.0 for feat in ALL_PREDICTOR_FEATURES}
    for idx, enc_name in enumerate(encoded_feature_names):
        val1 = float(np.mean(np.abs(shap_half1[:, idx])))
        val2 = float(np.mean(np.abs(shap_half2[:, idx])))
        for hl in ALL_PREDICTOR_FEATURES:
            if enc_name.startswith(f"num__{hl}") or enc_name.startswith(f"cat__{hl}"):
                hl_half1[hl] += val1
                hl_half2[hl] += val2
                break
                
    rank_h1 = [k for k, _ in sorted(hl_half1.items(), key=lambda x: x[1], reverse=True)[:5]]
    rank_h2 = [k for k, _ in sorted(hl_half2.items(), key=lambda x: x[1], reverse=True)[:5]]
    top5_overlap = len(set(rank_h1).intersection(set(rank_h2)))
    
    result_bundle = {
        "dataset": "IBM HR Analytics Employee Attrition",
        "method": "TreeSHAP",
        "evaluation_partition": "Test Holdout (N=221, random_state=42)",
        "sample_size": len(test_df),
        "epistemic_tier": "PREDICTED",
        "high_level_feature_importance": [
            {"feature": k, "mean_abs_shap": round(v, 6)} for k, v in sorted_hl
        ],
        "top_encoded_features": sorted_detailed[:20],
        "stability_analysis": {
            "top5_split1": rank_h1,
            "top5_split2": rank_h2,
            "top5_concordance": f"{top5_overlap}/5",
            "interpretation": (
                "Feature rankings reflect empirical TreeSHAP attribution magnitude on the holdout test set. "
                "Rankings represent statistical associations conditioned on the model architecture."
            ),
        },
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(result_bundle, f, indent=2)
        
    print(f"Workforce TreeSHAP importance serialized to {output_path}")
    print("Top 5 High-Level Features by TreeSHAP:")
    for rank, (feat, score) in enumerate(sorted_hl[:5], 1):
        print(f"  {rank}. {feat}: {score:.4f}")
        
    return result_bundle


class WorkforceExplainerService:
    """
    Provides local explanation for a single employee record using TreeSHAP.
    """
    def __init__(self, model_path: str = MODEL_PATH):
        bundle = joblib.load(model_path)
        self.preprocessor = bundle["preprocessor"]
        self.base_model = bundle["base_model"]
        self.explainer = shap.TreeExplainer(self.base_model)
        self.feature_names = bundle["feature_names"]
        self.encoded_feature_names = self.preprocessor.get_feature_names_out()

    def explain_employee(self, employee_dict: Dict[str, Any], top_k: int = 5) -> Dict[str, Any]:
        """
        Generates local TreeSHAP attribution for an individual employee record.
        Strictly non-causal language.
        """
        df_inst = pd.DataFrame([employee_dict])
        for col in self.feature_names:
            if col not in df_inst.columns:
                df_inst[col] = 0.0 if col in NUMERICAL_FEATURES else "Unknown"
        df_inst = df_inst[self.feature_names]
        X_proc = self.preprocessor.transform(df_inst)
        
        shap_vals = self.explainer.shap_values(X_proc)[0]
        
        attributions = []
        for idx, enc_name in enumerate(self.encoded_feature_names):
            attributions.append({
                "feature": str(enc_name),
                "shap_value": round(float(shap_vals[idx]), 4),
            })
            
        # Sort by absolute impact
        attributions.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
        
        return {
            "top_attributions": attributions[:top_k],
            "epistemic_tier": "PREDICTED",
            "statement": (
                "Local attributions quantify the model's log-odds contribution for each feature state. "
                "These values reflect statistical associations, not physical or causal drivers of turnover."
            ),
        }


if __name__ == "__main__":
    compute_and_serialize_workforce_shap()
