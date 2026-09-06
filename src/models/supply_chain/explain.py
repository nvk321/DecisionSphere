import os
import json
import joblib
import numpy as np
import pandas as pd
import shap
from typing import Dict, Any, List, Optional

from src.data.dataco_loader import load_dataco_raw
from src.data.dataco_features import (
    create_dataco_features,
    split_chronological_dataco,
    get_feature_columns,
)

DEFAULT_MODEL_PATH = "models/supply_chain/supply_chain_model.joblib"
DEFAULT_EXPLAIN_OUTPUT_DIR = "models/supply_chain"

def compute_supply_chain_shap(
    model_path: str = DEFAULT_MODEL_PATH,
    output_dir: str = DEFAULT_EXPLAIN_OUTPUT_DIR,
    sample_size: int = 2000,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Computes TreeSHAP feature attribution matrices on a representative holdout test sample.
    Extracts empirical global feature importance and persists feature_importance.json.
    """
    os.makedirs(output_dir, exist_ok=True)
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Trained model bundle not found at {model_path}. Train model first.")
        
    print(f"Loading model bundle from {model_path}...")
    bundle = joblib.load(model_path)
    base_model = bundle["base_model"]
    preprocessor = bundle["preprocessor"]
    feature_cols = bundle["feature_names"]
    
    # 1. Load test data
    print("Loading test data partition for SHAP attribution...")
    df_raw = load_dataco_raw()
    df_feat = create_dataco_features(df_raw)
    _, _, test_df = split_chronological_dataco(df_feat)
    
    # Sample representative holdout
    np.random.seed(random_state)
    if len(test_df) > sample_size:
        sample_indices = np.random.choice(len(test_df), size=sample_size, replace=False)
        test_sample = test_df.iloc[sample_indices].copy().reset_index(drop=True)
    else:
        test_sample = test_df.copy()
        
    X_sample = test_sample[feature_cols]
    X_proc = preprocessor.transform(X_sample)
    encoded_feature_names = preprocessor.get_feature_names_out()
    
    print(f"Computing TreeSHAP values on {len(test_sample):,} test instances ({len(encoded_feature_names)} encoded features)...")
    explainer = shap.TreeExplainer(base_model)
    shap_values = explainer.shap_values(X_proc)
    
    # If binary classification returns list [shap_class_0, shap_class_1] or single array
    if isinstance(shap_values, list):
        shap_vals_class1 = shap_values[1]
    else:
        shap_vals_class1 = shap_values
        
    mean_abs_shap_encoded = np.mean(np.abs(shap_vals_class1), axis=0)
    
    # Sort encoded features
    encoded_ranking = []
    for name, val in zip(encoded_feature_names, mean_abs_shap_encoded):
        encoded_ranking.append({"feature": name, "mean_abs_shap": round(float(val), 6)})
    encoded_ranking.sort(key=lambda x: x["mean_abs_shap"], reverse=True)
    
    # Aggregate back to high-level predictor columns
    agg_importance = {}
    for item in encoded_ranking:
        enc_name = item["feature"]
        val = item["mean_abs_shap"]
        # Strip prefix e.g. "cat__shipping_mode_First Class" -> "shipping_mode"
        clean_name = enc_name.split("__")[-1]
        for base_col in feature_cols:
            if clean_name == base_col or clean_name.startswith(base_col + "_") or clean_name.startswith(base_col):
                agg_importance[base_col] = agg_importance.get(base_col, 0.0) + val
                break
        else:
            agg_importance[clean_name] = agg_importance.get(clean_name, 0.0) + val
            
    sorted_agg_importance = sorted(
        [{"feature": k, "mean_abs_shap": round(v, 6)} for k, v in agg_importance.items()],
        key=lambda x: x["mean_abs_shap"],
        reverse=True
    )
    
    print("\nTop 10 High-Level Predictor Features by TreeSHAP Importance:")
    for i, item in enumerate(sorted_agg_importance[:10], 1):
        print(f"  {i:2d}. {item['feature']:30s} : {item['mean_abs_shap']:.6f}")
        
    print("\nTop 10 Encoded Sub-Features by TreeSHAP Importance:")
    for i, item in enumerate(encoded_ranking[:10], 1):
        print(f"  {i:2d}. {item['feature']:45s} : {item['mean_abs_shap']:.6f}")
        
    # Serialize feature importance artifact
    output_payload = {
        "dataset": "DataCo Smart Supply Chain",
        "method": "TreeSHAP",
        "evaluation_partition": "Test (strict chronological holdout 2017-07 to 2018-01)",
        "sample_size": len(test_sample),
        "epistemic_tier": "PREDICTED",
        "high_level_feature_importance": sorted_agg_importance,
        "top_encoded_features": encoded_ranking[:30],
        "shap_base_value": float(explainer.expected_value) if hasattr(explainer, "expected_value") else 0.0,
    }
    
    importance_path = os.path.join(output_dir, "feature_importance.json")
    with open(importance_path, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2)
        
    print(f"Saved feature importance artifact: {importance_path}")
    return output_payload

def explain_order_instance(
    order_dict: Dict[str, Any],
    model_bundle: Optional[Dict[str, Any]] = None,
    model_path: str = DEFAULT_MODEL_PATH,
    top_k: int = 5
) -> Dict[str, Any]:
    """
    Generates a grounded local TreeSHAP explanation for a single order instance.
    Uses strict non-causal language: 'associated with increased/decreased predicted risk'.
    """
    if model_bundle is None:
        model_bundle = joblib.load(model_path)
        
    base_model = model_bundle["base_model"]
    preprocessor = model_bundle["preprocessor"]
    feature_cols = model_bundle["feature_names"]
    
    # Format input as 1-row DataFrame
    df_instance = pd.DataFrame([order_dict])
    for col in feature_cols:
        if col not in df_instance.columns:
            df_instance[col] = 0.0 if col in model_bundle["numerical_features"] else "Unknown"
            
    df_instance = df_instance[feature_cols]
    X_proc = preprocessor.transform(df_instance)
    encoded_names = preprocessor.get_feature_names_out()
    
    explainer = shap.TreeExplainer(base_model)
    shap_vals = explainer.shap_values(X_proc)
    if isinstance(shap_vals, list):
        shap_vals = shap_vals[1]
    shap_vals = shap_vals[0]
    
    calibrated_model = model_bundle.get("calibrated_model")
    if calibrated_model is not None:
        pred_prob = float(calibrated_model.predict_proba(X_proc)[0, 1])
    else:
        pred_prob = float(base_model.predict_proba(X_proc)[0, 1])
        
    threshold = model_bundle.get("decision_threshold", 0.5)
    pred_class = int(pred_prob >= threshold)
    
    # Sort contributions
    features_with_shap = []
    for name, s_val in zip(encoded_names, shap_vals):
        features_with_shap.append({
            "feature": name,
            "shap_attribution": round(float(s_val), 6),
            "direction": "increases_risk" if s_val > 0 else "decreases_risk"
        })
        
    features_with_shap.sort(key=lambda x: abs(x["shap_attribution"]), reverse=True)
    
    top_increasing = [f for f in features_with_shap if f["direction"] == "increases_risk"][:top_k]
    top_decreasing = [f for f in features_with_shap if f["direction"] == "decreases_risk"][:top_k]
    
    return {
        "predicted_risk_probability": round(pred_prob, 4),
        "predicted_risk_class": pred_class,
        "decision_threshold": round(threshold, 4),
        "epistemic_tier": "PREDICTED",
        "attribution_statement": (
            f"The fitted model estimated a conditional late-delivery risk probability of {pred_prob:.1%}. "
            "Attributions represent learned statistical feature associations, not proved physical causality."
        ),
        "top_risk_increasing_factors": top_increasing,
        "top_risk_decreasing_factors": top_decreasing,
    }

if __name__ == "__main__":
    compute_supply_chain_shap()
