import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any
from datetime import datetime
import sklearn
import xgboost
import shap

from sklearn.frozen import FrozenEstimator
from sklearn.calibration import CalibratedClassifierCV

from src.data.ibm_hr_loader import load_ibm_hr_raw
from src.data.ibm_hr_features import (
    create_ibm_hr_features,
    split_stratified_ibm_hr,
    build_workforce_preprocessor,
    ALL_PREDICTOR_FEATURES,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    ALL_EXCLUDED_COLUMNS,
)
from src.models.workforce.baselines import (
    MajorityClassWorkforceBaseline,
    PrevalenceProbabilityWorkforceBaseline,
    create_logistic_regression_workforce_baseline,
)
from src.models.workforce.evaluate import (
    evaluate_workforce_classification,
    find_optimal_validation_threshold,
)

MODELS_DIR = "models/workforce"


def train_and_evaluate_workforce_pipeline(
    output_dir: str = MODELS_DIR,
    random_state: int = 42,
) -> Dict[str, Any]:
    """
    Executes the multi-level training, validation calibration, threshold tuning,
    and untouched test evaluation for the Phase 4 Workforce Attrition Pipeline.
    
    Guarantees:
    - Preprocessing is fitted strictly on Train.
    - Base XGBoost is fitted strictly on Train.
    - Sigmoid calibration mapping is fitted strictly on Validation using FrozenEstimator.
    - Decision threshold tau* is selected strictly on Validation F1.
    - Test holdout is evaluated exactly once at the final step.
    - Both raw and calibrated probability quality metrics are reported honestly.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Ingest raw dataset
    df_raw = load_ibm_hr_raw()
    
    # 2. Construct feature matrix (30 predictors + target)
    df_feat = create_ibm_hr_features(df_raw)
    
    # 3. Stratified Train / Val / Test splitting
    train_df, val_df, test_df = split_stratified_ibm_hr(
        df_feat,
        train_ratio=0.70,
        val_ratio=0.15,
        test_ratio=0.15,
        random_state=random_state,
    )
    
    # 4. Extract ground truth labels
    y_train = train_df["target_attrition"].values.astype(int)
    y_val = val_df["target_attrition"].values.astype(int)
    y_test = test_df["target_attrition"].values.astype(int)
    
    # Record exact split counts and class prevalences
    train_pos = int(np.sum(y_train == 1))
    train_neg = int(np.sum(y_train == 0))
    val_pos = int(np.sum(y_val == 1))
    val_neg = int(np.sum(y_val == 0))
    test_pos = int(np.sum(y_test == 1))
    test_neg = int(np.sum(y_test == 0))
    
    scale_pos_weight = float(train_neg / train_pos)
    
    partition_metadata = {
        "train": {
            "rows": len(train_df),
            "positive_attrition": train_pos,
            "negative_attrition": train_neg,
            "prevalence": round(float(train_pos / len(train_df)), 4),
        },
        "validation": {
            "rows": len(val_df),
            "positive_attrition": val_pos,
            "negative_attrition": val_neg,
            "prevalence": round(float(val_pos / len(val_df)), 4),
        },
        "test": {
            "rows": len(test_df),
            "positive_attrition": test_pos,
            "negative_attrition": test_neg,
            "prevalence": round(float(test_pos / len(test_df)), 4),
        },
        "scale_pos_weight": round(scale_pos_weight, 4),
    }
    
    # 5. Fit preprocessor strictly on Train
    preprocessor = build_workforce_preprocessor(NUMERICAL_FEATURES, CATEGORICAL_FEATURES)
    X_train_proc = preprocessor.fit_transform(train_df[ALL_PREDICTOR_FEATURES])
    X_val_proc = preprocessor.transform(val_df[ALL_PREDICTOR_FEATURES])
    X_test_proc = preprocessor.transform(test_df[ALL_PREDICTOR_FEATURES])
    
    # 6. Fit Level 0a & 0b Baselines
    level_0a = MajorityClassWorkforceBaseline().fit(X_train_proc, y_train)
    level_0b = PrevalenceProbabilityWorkforceBaseline().fit(X_train_proc, y_train)
    
    # 7. Fit Level 1 Baseline (Balanced Logistic Regression)
    level_1_lr = create_logistic_regression_workforce_baseline(
        class_weight="balanced", random_state=random_state
    )
    level_1_lr.fit(X_train_proc, y_train)
    
    # 8. Fit Level 2 Model (Weighted XGBoost)
    base_xgb = xgboost.XGBClassifier(
        n_estimators=100,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        eval_metric="logloss",
        random_state=random_state,
        tree_method="hist",
    )
    base_xgb.fit(X_train_proc, y_train)
    
    # 9. Fit Sigmoid Calibration Mapping strictly on Validation using FrozenEstimator
    calibrator = CalibratedClassifierCV(
        estimator=FrozenEstimator(base_xgb),
        method="sigmoid",
    )
    calibrator.fit(X_val_proc, y_val)
    
    # 10. Predict on Validation
    p_val_0b = level_0b.predict_proba(X_val_proc)[:, 1]
    p_val_lr = level_1_lr.predict_proba(X_val_proc)[:, 1]
    p_val_xgb_raw = base_xgb.predict_proba(X_val_proc)[:, 1]
    p_val_xgb_cal = calibrator.predict_proba(X_val_proc)[:, 1]
    
    # 11. Select decision threshold tau* strictly on Validation calibrated probabilities
    optimal_tau, val_f1, tau_diag = find_optimal_validation_threshold(
        y_val=y_val,
        y_val_prob=p_val_xgb_cal,
    )
    
    # Evaluate validation performances
    val_eval = {
        "level_0_naive_prevalence": evaluate_workforce_classification(y_val, p_val_0b, decision_threshold=0.5),
        "level_1_logistic": evaluate_workforce_classification(y_val, p_val_lr, decision_threshold=0.5),
        "level_2_xgb_raw": evaluate_workforce_classification(y_val, p_val_xgb_raw, decision_threshold=0.5),
        "level_2_xgb_calibrated": evaluate_workforce_classification(y_val, p_val_xgb_cal, decision_threshold=0.5),
        "threshold_selection": tau_diag,
    }
    
    # 12. Evaluate on Untouched Test Holdout (Executed exactly ONCE)
    p_test_0b = level_0b.predict_proba(X_test_proc)[:, 1]
    p_test_lr = level_1_lr.predict_proba(X_test_proc)[:, 1]
    p_test_xgb_raw = base_xgb.predict_proba(X_test_proc)[:, 1]
    p_test_xgb_cal = calibrator.predict_proba(X_test_proc)[:, 1]
    
    test_eval = {
        "level_0_naive_prevalence": evaluate_workforce_classification(
            y_test, p_test_0b, decision_threshold=0.5
        ),
        "level_1_logistic": evaluate_workforce_classification(
            y_test, p_test_lr, decision_threshold=0.5
        ),
        "level_2_xgb_raw_default_threshold": evaluate_workforce_classification(
            y_test, p_test_xgb_raw, decision_threshold=0.5
        ),
        "level_2_xgb_calibrated_default_threshold": evaluate_workforce_classification(
            y_test, p_test_xgb_cal, decision_threshold=0.5
        ),
        "level_2_xgb_calibrated_optimal_threshold": evaluate_workforce_classification(
            y_test, p_test_xgb_cal, decision_threshold=optimal_tau
        ),
    }
    
    # 13. Assemble complete metrics bundle
    full_metrics = {
        "dataset": "IBM HR Analytics Employee Attrition",
        "target": "Attrition (1=Yes, 0=No)",
        "epistemic_tier": "PREDICTED",
        "partitions": partition_metadata,
        "validation_evaluation": val_eval,
        "test_evaluation": test_eval,
    }
    
    # Write metrics.json
    metrics_path = os.path.join(output_dir, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(full_metrics, f, indent=2)
        
    # Write confusion_matrix.json
    cm_path = os.path.join(output_dir, "confusion_matrix.json")
    cm_bundle = {
        "validation": {
            k: v["confusion_matrix"]
            for k, v in val_eval.items()
            if "confusion_matrix" in v
        },
        "test": {
            k: v["confusion_matrix"]
            for k, v in test_eval.items()
            if "confusion_matrix" in v
        },
    }
    with open(cm_path, "w") as f:
        json.dump(cm_bundle, f, indent=2)
        
    # Write calibration.json
    cal_path = os.path.join(output_dir, "calibration.json")
    cal_bundle = {
        "validation": {
            k: v["calibration_curve"]
            for k, v in val_eval.items()
            if "calibration_curve" in v
        },
        "test": {
            k: v["calibration_curve"]
            for k, v in test_eval.items()
            if "calibration_curve" in v
        },
    }
    with open(cal_path, "w") as f:
        json.dump(cal_bundle, f, indent=2)
        
    # Write experiment_metadata.json
    exp_metadata = {
        "dataset": "IBM HR Analytics Employee Attrition & Performance",
        "dataset_rows": len(df_raw),
        "dataset_cols": df_raw.shape[1],
        "excluded_columns": ALL_EXCLUDED_COLUMNS,
        "modeling_features_count": len(ALL_PREDICTOR_FEATURES),
        "modeling_features": ALL_PREDICTOR_FEATURES,
        "numerical_features": NUMERICAL_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "random_state": random_state,
        "split_counts": partition_metadata,
        "scale_pos_weight": round(scale_pos_weight, 4),
        "train_positive_count": train_pos,
        "train_negative_count": train_neg,
        "optimal_threshold_tau_star": round(optimal_tau, 4),
        "validation_f1_at_tau_star": round(val_f1, 4),
        "threshold_criterion": "Validation F1 maximization",
        "calibration_method": "FrozenEstimator Sigmoid on Validation",
        "scikit_learn_version": sklearn.__version__,
        "xgboost_version": xgboost.__version__,
        "shap_version": shap.__version__,
        "training_timestamp": datetime.now().isoformat(),
        "epistemic_tier": "PREDICTED",
    }
    meta_path = os.path.join(output_dir, "experiment_metadata.json")
    with open(meta_path, "w") as f:
        json.dump(exp_metadata, f, indent=2)
        
    # 14. Serialize Model Artifact Bundle
    model_bundle = {
        "preprocessor": preprocessor,
        "base_model": base_xgb,
        "calibrated_model": calibrator,
        "logistic_baseline": level_1_lr,
        "decision_threshold": optimal_tau,
        "feature_names": ALL_PREDICTOR_FEATURES,
        "numerical_features": NUMERICAL_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "scale_pos_weight": scale_pos_weight,
        "training_metadata": exp_metadata,
    }
    bundle_path = os.path.join(output_dir, "workforce_model.joblib")
    joblib.dump(model_bundle, bundle_path)
    
    print(f"Phase 4 Workforce Model successfully serialized to {bundle_path}")
    print(f"Optimal threshold tau*: {optimal_tau:.4f} (Validation F1: {val_f1:.4f})")
    print(f"Test PR-AUC: {test_eval['level_2_xgb_raw_default_threshold']['pr_auc']:.4f} (Raw) vs {test_eval['level_2_xgb_calibrated_default_threshold']['pr_auc']:.4f} (Calibrated)")
    print(f"Test ROC-AUC: {test_eval['level_2_xgb_raw_default_threshold']['roc_auc']:.4f} (Raw) vs {test_eval['level_2_xgb_calibrated_default_threshold']['roc_auc']:.4f} (Calibrated)")
    print(f"Test Brier: {test_eval['level_2_xgb_raw_default_threshold']['brier_score']:.4f} (Raw) vs {test_eval['level_2_xgb_calibrated_default_threshold']['brier_score']:.4f} (Calibrated)")
    
    return full_metrics


if __name__ == "__main__":
    train_and_evaluate_workforce_pipeline()
