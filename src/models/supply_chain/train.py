import os
import json
import time
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.frozen import FrozenEstimator
from sklearn.calibration import CalibratedClassifierCV
import xgboost as xgb

from src.data.dataco_loader import load_dataco_raw
from src.data.dataco_features import (
    create_dataco_features,
    split_chronological_dataco,
    get_feature_columns,
    get_numerical_features,
    get_categorical_features,
    ALL_EXCLUDED_COLUMNS,
)
from src.models.supply_chain.baselines import NaiveMajorityBaseline
from src.models.supply_chain.evaluate import compute_classification_metrics, find_optimal_threshold

MODEL_OUTPUT_DIR = "models/supply_chain"

def build_preprocessor(numerical_cols: list, categorical_cols: list) -> ColumnTransformer:
    """Constructs leakage-free ColumnTransformer for DataCo features."""
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numerical_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_cols),
        ],
        remainder="drop"
    )

def train_supply_chain_pipeline(
    data_dir: str = "data/raw/dataco",
    output_dir: str = MODEL_OUTPUT_DIR,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Executes the complete Supply Chain Delivery Risk modeling pipeline:
    1. Ingestion & integrity validation
    2. Feature engineering with strict anti-leakage exclusion
    3. Chronological time split (Train 24mo / Val 6mo / Test 7mo)
    4. Fit preprocessor strictly on Train
    5. Train Level 0 (Naive Majority / Prevalence)
    6. Train Level 1 (Logistic Regression)
    7. Train Level 2 (XGBoost Classifier)
    8. Fit Sigmoid Calibration on Validation partition via FrozenEstimator
    9. Select optimal decision threshold strictly on Validation F1
    10. Final evaluation once on untouched Test set
    11. Serialization of model bundle and comprehensive experimental artifacts
    """
    os.makedirs(output_dir, exist_ok=True)
    start_time = time.time()

    print("=" * 70)
    print("STEP 1: Ingesting DataCo dataset...")
    print("=" * 70)
    df_raw = load_dataco_raw(data_dir=data_dir)
    print(f"Loaded raw dataset: {len(df_raw):,} records x {len(df_raw.columns)} columns.")

    print("\n" + "=" * 70)
    print("STEP 2: Engineering order-time features (Strict Anti-Leakage)...")
    print("=" * 70)
    df_feat = create_dataco_features(df_raw)
    feature_cols = get_feature_columns()
    num_cols = get_numerical_features()
    cat_cols = get_categorical_features()
    print(f"Feature matrix: {len(df_feat):,} rows x {len(feature_cols)} predictors ({len(num_cols)} num, {len(cat_cols)} cat).")

    # Anti-leakage verification assertion
    for prohibited in ALL_EXCLUDED_COLUMNS:
        assert prohibited not in df_feat.columns, f"LEAKAGE DETECTED: {prohibited}"

    print("\n" + "=" * 70)
    print("STEP 3: Chronological forward time splitting...")
    print("=" * 70)
    train_df, val_df, test_df = split_chronological_dataco(df_feat)
    
    print(f"Train: {len(train_df):,} rows ({train_df['order_dt'].min().strftime('%Y-%m-%d')} to {train_df['order_dt'].max().strftime('%Y-%m-%d')}) | Late: {train_df['late_delivery_risk'].mean():.4%}")
    print(f"Val:   {len(val_df):,} rows ({val_df['order_dt'].min().strftime('%Y-%m-%d')} to {val_df['order_dt'].max().strftime('%Y-%m-%d')}) | Late: {val_df['late_delivery_risk'].mean():.4%}")
    print(f"Test:  {len(test_df):,} rows ({test_df['order_dt'].min().strftime('%Y-%m-%d')} to {test_df['order_dt'].max().strftime('%Y-%m-%d')}) | Late: {test_df['late_delivery_risk'].mean():.4%}")

    X_train, y_train = train_df[feature_cols], train_df["late_delivery_risk"].values
    X_val, y_val = val_df[feature_cols], val_df["late_delivery_risk"].values
    X_test, y_test = test_df[feature_cols], test_df["late_delivery_risk"].values

    print("\n" + "=" * 70)
    print("STEP 4: Fitting Preprocessing Pipeline on Training Data...")
    print("=" * 70)
    preprocessor = build_preprocessor(num_cols, cat_cols)
    X_train_proc = preprocessor.fit_transform(X_train)
    X_val_proc = preprocessor.transform(X_val)
    X_test_proc = preprocessor.transform(X_test)
    print(f"Preprocessed feature dimensionality: {X_train_proc.shape[1]} encoded features.")

    print("\n" + "=" * 70)
    print("STEP 5: Training Level 0 Baseline (Naive Majority & Prevalence)...")
    print("=" * 70)
    level0 = NaiveMajorityBaseline().fit(X_train, y_train)
    p_val_level0 = level0.predict_proba(X_val)[:, 1]
    metrics_val_l0 = compute_classification_metrics(y_val, p_val_level0, threshold=0.5)
    print(f"Level 0 (Val): ROC-AUC={metrics_val_l0['roc_auc']:.4f} | PR-AUC={metrics_val_l0['pr_auc']:.4f} | Brier={metrics_val_l0['brier_score']:.4f} | F1={metrics_val_l0['f1_score']:.4f}")

    print("\n" + "=" * 70)
    print("STEP 6: Training Level 1 Baseline (Logistic Regression)...")
    print("=" * 70)
    level1 = LogisticRegression(max_iter=1000, random_state=random_state, solver="lbfgs")
    level1.fit(X_train_proc, y_train)
    p_val_level1 = level1.predict_proba(X_val_proc)[:, 1]
    metrics_val_l1 = compute_classification_metrics(y_val, p_val_level1, threshold=0.5)
    print(f"Level 1 (Val): ROC-AUC={metrics_val_l1['roc_auc']:.4f} | PR-AUC={metrics_val_l1['pr_auc']:.4f} | Brier={metrics_val_l1['brier_score']:.4f} | F1={metrics_val_l1['f1_score']:.4f}")

    print("\n" + "=" * 70)
    print("STEP 7: Training Level 2 Model (XGBoost Classifier)...")
    print("=" * 70)
    xgb_model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        tree_method="hist",
        eval_metric="logloss",
        random_state=random_state,
        n_jobs=-1,
    )
    xgb_model.fit(
        X_train_proc,
        y_train,
        eval_set=[(X_val_proc, y_val)],
        verbose=50,
    )

    p_val_xgb_raw = xgb_model.predict_proba(X_val_proc)[:, 1]
    metrics_val_xgb_raw = compute_classification_metrics(y_val, p_val_xgb_raw, threshold=0.5)
    print(f"Level 2 Raw (Val): ROC-AUC={metrics_val_xgb_raw['roc_auc']:.4f} | PR-AUC={metrics_val_xgb_raw['pr_auc']:.4f} | Brier={metrics_val_xgb_raw['brier_score']:.4f} | ECE={metrics_val_xgb_raw['expected_calibration_error']:.4f} | F1={metrics_val_xgb_raw['f1_score']:.4f}")

    print("\n" + "=" * 70)
    print("STEP 8: Fitting Sigmoid Calibration strictly on Validation Set...")
    print("=" * 70)
    # Using scikit-learn 1.9 FrozenEstimator API
    frozen_xgb = FrozenEstimator(xgb_model)
    calibrated_xgb = CalibratedClassifierCV(estimator=frozen_xgb, method="sigmoid")
    calibrated_xgb.fit(X_val_proc, y_val)

    p_val_xgb_cal = calibrated_xgb.predict_proba(X_val_proc)[:, 1]
    metrics_val_xgb_cal = compute_classification_metrics(y_val, p_val_xgb_cal, threshold=0.5)
    print(f"Level 2 Calibrated (Val): ROC-AUC={metrics_val_xgb_cal['roc_auc']:.4f} | PR-AUC={metrics_val_xgb_cal['pr_auc']:.4f} | Brier={metrics_val_xgb_cal['brier_score']:.4f} | ECE={metrics_val_xgb_cal['expected_calibration_error']:.4f} | F1={metrics_val_xgb_cal['f1_score']:.4f}")

    # Probability quality comparison on validation
    brier_improvement = metrics_val_xgb_raw["brier_score"] - metrics_val_xgb_cal["brier_score"]
    print(f"Validation Brier score delta: {brier_improvement:+.4f} (positive indicates calibration improvement).")

    print("\n" + "=" * 70)
    print("STEP 9: Selecting Decision Threshold strictly on Validation F1...")
    print("=" * 70)
    optimal_thresh_raw, best_f1_raw = find_optimal_threshold(y_val, p_val_xgb_raw)
    optimal_thresh_cal, best_f1_cal = find_optimal_threshold(y_val, p_val_xgb_cal)
    print(f"Raw Optimal Threshold: {optimal_thresh_raw:.2f} (Val F1 = {best_f1_raw:.4f})")
    print(f"Calibrated Optimal Threshold: {optimal_thresh_cal:.2f} (Val F1 = {best_f1_cal:.4f})")

    # Selected primary production threshold
    selected_threshold = optimal_thresh_cal

    print("\n" + "=" * 70)
    print("STEP 10: Final Single Evaluation on Untouched Test Set...")
    print("=" * 70)
    p_test_l0 = level0.predict_proba(X_test)[:, 1]
    p_test_l1 = level1.predict_proba(X_test_proc)[:, 1]
    p_test_xgb_raw = xgb_model.predict_proba(X_test_proc)[:, 1]
    p_test_xgb_cal = calibrated_xgb.predict_proba(X_test_proc)[:, 1]

    metrics_test_l0 = compute_classification_metrics(y_test, p_test_l0, threshold=0.5)
    metrics_test_l1 = compute_classification_metrics(y_test, p_test_l1, threshold=0.5)
    metrics_test_xgb_raw_05 = compute_classification_metrics(y_test, p_test_xgb_raw, threshold=0.5)
    metrics_test_xgb_cal_05 = compute_classification_metrics(y_test, p_test_xgb_cal, threshold=0.5)
    metrics_test_xgb_cal_opt = compute_classification_metrics(y_test, p_test_xgb_cal, threshold=selected_threshold)

    print("\nFINAL TEST EVALUATION SUMMARY (Strict Chronological Holdout):")
    print(f"  Level 0 (Naive Majority): ROC-AUC={metrics_test_l0['roc_auc']:.4f} | PR-AUC={metrics_test_l0['pr_auc']:.4f} | Brier={metrics_test_l0['brier_score']:.4f} | F1={metrics_test_l0['f1_score']:.4f}")
    print(f"  Level 1 (Logistic Reg):   ROC-AUC={metrics_test_l1['roc_auc']:.4f} | PR-AUC={metrics_test_l1['pr_auc']:.4f} | Brier={metrics_test_l1['brier_score']:.4f} | F1={metrics_test_l1['f1_score']:.4f}")
    print(f"  Level 2 (XGB Raw @0.50):  ROC-AUC={metrics_test_xgb_raw_05['roc_auc']:.4f} | PR-AUC={metrics_test_xgb_raw_05['pr_auc']:.4f} | Brier={metrics_test_xgb_raw_05['brier_score']:.4f} | ECE={metrics_test_xgb_raw_05['expected_calibration_error']:.4f} | F1={metrics_test_xgb_raw_05['f1_score']:.4f}")
    print(f"  Level 2 (XGB Cal @0.50):  ROC-AUC={metrics_test_xgb_cal_05['roc_auc']:.4f} | PR-AUC={metrics_test_xgb_cal_05['pr_auc']:.4f} | Brier={metrics_test_xgb_cal_05['brier_score']:.4f} | ECE={metrics_test_xgb_cal_05['expected_calibration_error']:.4f} | F1={metrics_test_xgb_cal_05['f1_score']:.4f}")
    print(f"  Level 2 (XGB Cal @{selected_threshold:.2f}): ROC-AUC={metrics_test_xgb_cal_opt['roc_auc']:.4f} | PR-AUC={metrics_test_xgb_cal_opt['pr_auc']:.4f} | Brier={metrics_test_xgb_cal_opt['brier_score']:.4f} | F1={metrics_test_xgb_cal_opt['f1_score']:.4f} | Prec={metrics_test_xgb_cal_opt['precision']:.4f} | Rec={metrics_test_xgb_cal_opt['recall']:.4f}")

    print("\n" + "=" * 70)
    print("STEP 11: Serializing Production Artifacts...")
    print("=" * 70)
    
    # 1. Serialized Model Bundle
    model_bundle = {
        "preprocessor": preprocessor,
        "base_model": xgb_model,
        "calibrated_model": calibrated_xgb,
        "decision_threshold": float(selected_threshold),
        "feature_names": feature_cols,
        "numerical_features": num_cols,
        "categorical_features": cat_cols,
        "training_metadata": {
            "dataset": "DataCo Smart Supply Chain",
            "task": "Conditional Late Delivery Risk Classification",
            "target": "Late_delivery_risk",
            "epistemic_tier": "PREDICTED",
            "train_rows": len(train_df),
            "val_rows": len(val_df),
            "test_rows": len(test_df),
            "train_period": f"{train_df['order_dt'].min().strftime('%Y-%m-%d')} to {train_df['order_dt'].max().strftime('%Y-%m-%d')}",
            "val_period": f"{val_df['order_dt'].min().strftime('%Y-%m-%d')} to {val_df['order_dt'].max().strftime('%Y-%m-%d')}",
            "test_period": f"{test_df['order_dt'].min().strftime('%Y-%m-%d')} to {test_df['order_dt'].max().strftime('%Y-%m-%d')}",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "training_duration_seconds": round(time.time() - start_time, 2),
            "random_state": random_state,
        }
    }
    
    model_bundle_path = os.path.join(output_dir, "supply_chain_model.joblib")
    joblib.dump(model_bundle, model_bundle_path, compress=3)
    file_size_mb = os.path.getsize(model_bundle_path) / (1024 * 1024)
    print(f"Serialized model artifact bundle: {model_bundle_path} ({file_size_mb:.2f} MB)")

    # 2. Metrics JSON
    metrics_payload = {
        "dataset": "DataCo Smart Supply Chain",
        "target": "Late_delivery_risk",
        "epistemic_tier": "PREDICTED",
        "partitions": {
            "train": {"rows": len(train_df), "late_rate": round(float(train_df["late_delivery_risk"].mean()), 4)},
            "validation": {"rows": len(val_df), "late_rate": round(float(val_df["late_delivery_risk"].mean()), 4)},
            "test": {"rows": len(test_df), "late_rate": round(float(test_df["late_delivery_risk"].mean()), 4)},
        },
        "validation_evaluation": {
            "level_0_naive": metrics_val_l0,
            "level_1_logistic": metrics_val_l1,
            "level_2_xgb_raw": metrics_val_xgb_raw,
            "level_2_xgb_calibrated": metrics_val_xgb_cal,
        },
        "test_evaluation": {
            "level_0_naive": metrics_test_l0,
            "level_1_logistic": metrics_test_l1,
            "level_2_xgb_raw": metrics_test_xgb_raw_05,
            "level_2_xgb_calibrated_default_threshold": metrics_test_xgb_cal_05,
            "level_2_xgb_calibrated_optimal_threshold": metrics_test_xgb_cal_opt,
        }
    }
    with open(os.path.join(output_dir, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2)

    # 3. Confusion Matrix JSON
    with open(os.path.join(output_dir, "confusion_matrix.json"), "w", encoding="utf-8") as f:
        json.dump({
            "test_level_2_calibrated_optimal": metrics_test_xgb_cal_opt["confusion_matrix"],
            "test_level_1_logistic": metrics_test_l1["confusion_matrix"],
            "test_level_0_naive": metrics_test_l0["confusion_matrix"],
        }, f, indent=2)

    # 4. Calibration JSON
    with open(os.path.join(output_dir, "calibration.json"), "w", encoding="utf-8") as f:
        json.dump({
            "method": "sigmoid",
            "calibration_partition": "validation (strict chronological 2017-01 to 2017-06)",
            "validation_raw_brier": metrics_val_xgb_raw["brier_score"],
            "validation_calibrated_brier": metrics_val_xgb_cal["brier_score"],
            "validation_raw_ece": metrics_val_xgb_raw["expected_calibration_error"],
            "validation_calibrated_ece": metrics_val_xgb_cal["expected_calibration_error"],
            "test_raw_brier": metrics_test_xgb_raw_05["brier_score"],
            "test_calibrated_brier": metrics_test_xgb_cal_05["brier_score"],
            "test_raw_ece": metrics_test_xgb_raw_05["expected_calibration_error"],
            "test_calibrated_ece": metrics_test_xgb_cal_05["expected_calibration_error"],
            "test_calibration_curve_raw": metrics_test_xgb_raw_05["calibration_curve"],
            "test_calibration_curve_calibrated": metrics_test_xgb_cal_05["calibration_curve"],
        }, f, indent=2)

    # 5. Experiment Metadata JSON
    with open(os.path.join(output_dir, "experiment_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(model_bundle["training_metadata"], f, indent=2)

    print(f"Generated evaluation records: metrics.json, confusion_matrix.json, calibration.json, experiment_metadata.json.")
    print(f"Total training pipeline duration: {time.time() - start_time:.2f} seconds.")
    
    return metrics_payload

if __name__ == "__main__":
    train_supply_chain_pipeline()
