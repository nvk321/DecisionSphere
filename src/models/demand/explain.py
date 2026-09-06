import os
import json
import joblib
import pandas as pd
import numpy as np
import shap

from src.data.rossmann_loader import load_rossmann_raw, merge_store_metadata
from src.data.rossmann_features import create_demand_features, split_chronological

def generate_shap_explanations(
    artifact_path: str = "models/demand/demand_model.joblib",
    output_dir: str = "models/demand",
    sample_size: int = 2000,
    random_state: int = 42
):
    """
    Computes empirical SHAP (TreeExplainer) feature attributions on holdout test observations.
    Does NOT assume or force any preconceived feature rankings.
    Saves empirical global importance ranking to models/demand/feature_importance.json.
    """
    if not os.path.exists(artifact_path):
        raise FileNotFoundError(f"Model artifact not found at {artifact_path}. Run train.py first.")
        
    print("Loading serialized demand model bundle...")
    bundle = joblib.load(artifact_path)
    model = bundle["model"]
    feature_cols = bundle["feature_columns"]
    
    print("Loading test data for empirical SHAP computation...")
    df_train_raw, df_store_raw = load_rossmann_raw()
    df_merged = merge_store_metadata(df_train_raw, df_store_raw)
    df_feat = create_demand_features(df_merged)
    
    _, _, test_df = split_chronological(df_feat)
    test_open = test_df[(test_df["Open"] == 1) & (test_df["Sales"] > 0)].copy()
    
    # Sample a representative subset of test observations for tractable explanation
    if len(test_open) > sample_size:
        sample_df = test_open.sample(n=sample_size, random_state=random_state).reset_index(drop=True)
    else:
        sample_df = test_open.reset_index(drop=True)
        
    X_sample = sample_df[feature_cols]
    
    print(f"Initializing TreeExplainer on {len(X_sample)} sample test observations...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)
    
    # Compute mean absolute SHAP values per feature
    mean_abs_shap = np.mean(np.abs(shap_values), axis=0)
    
    ranking = []
    for col, score in zip(feature_cols, mean_abs_shap):
        ranking.append({
            "feature": col,
            "mean_abs_shap": round(float(score), 4)
        })
        
    # Sort strictly by observed empirical importance descending
    ranking.sort(key=lambda x: x["mean_abs_shap"], reverse=True)
    
    output_data = {
        "explanation_method": "TreeSHAP (shap.TreeExplainer)",
        "sample_size": len(X_sample),
        "base_value": round(float(explainer.expected_value), 2) if hasattr(explainer, "expected_value") else None,
        "feature_ranking": ranking
    }
    
    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, "feature_importance.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
        
    print(f"\nEmpirical SHAP Ranking saved to {out_file}:")
    print("Top 10 Most Influential Features:")
    for i, item in enumerate(ranking[:10], 1):
        print(f"  {i:2d}. {item['feature']:30s} | Mean |SHAP|: {item['mean_abs_shap']:.2f} Sales units")
        
    return output_data

def explain_local_forecast(model, feature_cols: list, feature_vector: pd.DataFrame, top_k: int = 5):
    """
    Computes local feature attributions for an individual forecast or simulated scenario shock.
    Returns the top positive and top negative contributing factors.
    """
    explainer = shap.TreeExplainer(model)
    shap_val = explainer.shap_values(feature_vector[feature_cols])[0]
    
    contributions = []
    for col, val, shap_amt in zip(feature_cols, feature_vector[feature_cols].iloc[0], shap_val):
        contributions.append({
            "feature": col,
            "value": float(val) if isinstance(val, (int, float, np.number)) else str(val),
            "attribution": round(float(shap_amt), 2)
        })
        
    top_pos = sorted([c for c in contributions if c["attribution"] > 0], key=lambda x: x["attribution"], reverse=True)[:top_k]
    top_neg = sorted([c for c in contributions if c["attribution"] < 0], key=lambda x: x["attribution"])[:top_k]
    
    return {
        "base_value": round(float(explainer.expected_value), 2) if hasattr(explainer, "expected_value") else None,
        "top_positive_factors": top_pos,
        "top_negative_factors": top_neg
    }

if __name__ == "__main__":
    generate_shap_explanations()
