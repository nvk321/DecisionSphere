import pytest
import numpy as np
import pandas as pd

from src.data.ibm_hr_loader import (
    load_ibm_hr_raw,
    EXPECTED_ROWS,
    EXPECTED_COLS,
    EXPECTED_ATTRITION_YES,
    EXPECTED_ATTRITION_NO,
)
from src.data.ibm_hr_features import (
    create_ibm_hr_features,
    split_stratified_ibm_hr,
    build_workforce_preprocessor,
    ALL_PREDICTOR_FEATURES,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    ALL_EXCLUDED_COLUMNS,
    EXCLUDED_INVARIANT_COLUMNS,
    EXCLUDED_SURROGATE_COLUMNS,
    TARGET_COLUMN,
)


def test_ibm_hr_raw_dimensions_and_schema():
    """Verifies dataset raw integrity assertions (1,470 rows, 35 columns, 0 nulls)."""
    df_raw = load_ibm_hr_raw()
    assert df_raw.shape == (EXPECTED_ROWS, EXPECTED_COLS)
    assert df_raw.isnull().sum().sum() == 0
    
    counts = df_raw["Attrition"].value_counts().to_dict()
    assert counts.get("Yes") == EXPECTED_ATTRITION_YES
    assert counts.get("No") == EXPECTED_ATTRITION_NO


def test_feature_exclusion_matrix_exactness():
    """
    Rigorously verifies the 30-feature modeling matrix:
    - Exactly 30 predictors.
    - All invariant zero-variance columns (EmployeeCount, StandardHours, Over18) are ABSENT.
    - Surrogate key (EmployeeNumber) is ABSENT.
    - Target (Attrition) is ABSENT from input predictors.
    """
    df_raw = load_ibm_hr_raw()
    df_feat = create_ibm_hr_features(df_raw)
    
    # 30 predictors + 1 binary target
    assert df_feat.shape[1] == 31
    assert "target_attrition" in df_feat.columns
    
    # Invariant exclusions
    for inv in EXCLUDED_INVARIANT_COLUMNS:
        assert inv not in df_feat.columns, f"Invariant column '{inv}' must not be present in features!"
        
    # Surrogate exclusion
    for surr in EXCLUDED_SURROGATE_COLUMNS:
        assert surr not in df_feat.columns, f"Surrogate column '{surr}' must not be present in features!"
        
    # Target exclusion
    assert TARGET_COLUMN not in df_feat.columns, f"Raw target '{TARGET_COLUMN}' must not be in feature columns!"
    
    # Predictor count verification
    predictor_cols = [c for c in df_feat.columns if c != "target_attrition"]
    assert len(predictor_cols) == 30, f"Expected exactly 30 predictors, got {len(predictor_cols)}"
    assert set(predictor_cols) == set(ALL_PREDICTOR_FEATURES)


def test_no_zero_variance_features():
    """Verifies that every retained modeling predictor has non-zero variance."""
    df_raw = load_ibm_hr_raw()
    df_feat = create_ibm_hr_features(df_raw)
    
    for num_col in NUMERICAL_FEATURES:
        assert df_feat[num_col].std() > 0.0, f"Feature '{num_col}' has zero standard deviation!"
        
    for cat_col in CATEGORICAL_FEATURES:
        assert df_feat[cat_col].nunique() > 1, f"Feature '{cat_col}' has fewer than 2 categories!"


def test_stratified_split_invariants():
    """
    Verifies stratified split properties:
    - 70% Train (1029), 15% Val (220), 15% Test (221).
    - Zero index overlap between partitions.
    - Attrition prevalence stability (~16%) across partitions.
    """
    df_raw = load_ibm_hr_raw()
    df_feat = create_ibm_hr_features(df_raw)
    train_df, val_df, test_df = split_stratified_ibm_hr(df_feat, random_state=42)
    
    # Dimensions
    assert len(train_df) == 1029
    assert len(val_df) == 220
    assert len(test_df) == 221
    assert len(train_df) + len(val_df) + len(test_df) == 1470
    
    # Zero overlap
    train_idx = set(train_df.index)
    val_idx = set(val_df.index)
    test_idx = set(test_df.index)
    assert len(train_idx.intersection(val_idx)) == 0
    assert len(train_idx.intersection(test_idx)) == 0
    assert len(val_idx.intersection(test_idx)) == 0
    
    # Target prevalence check (all within [0.15, 0.17])
    p_train = train_df["target_attrition"].mean()
    p_val = val_df["target_attrition"].mean()
    p_test = test_df["target_attrition"].mean()
    
    assert 0.15 <= p_train <= 0.17
    assert 0.15 <= p_val <= 0.17
    assert 0.15 <= p_test <= 0.17


def test_holdout_isolation_and_no_leakage():
    """Verifies that preprocessing is fitted strictly on Train and transforms unseen data cleanly."""
    df_raw = load_ibm_hr_raw()
    df_feat = create_ibm_hr_features(df_raw)
    train_df, val_df, test_df = split_stratified_ibm_hr(df_feat, random_state=42)
    
    preprocessor = build_workforce_preprocessor(NUMERICAL_FEATURES, CATEGORICAL_FEATURES)
    X_train_proc = preprocessor.fit_transform(train_df[ALL_PREDICTOR_FEATURES])
    X_test_proc = preprocessor.transform(test_df[ALL_PREDICTOR_FEATURES])
    
    assert X_train_proc.shape[0] == 1029
    assert X_test_proc.shape[0] == 221
    assert X_train_proc.shape[1] == X_test_proc.shape[1]
    
    # Check that test target is NOT in X_test_proc
    assert "target_attrition" not in preprocessor.get_feature_names_out()
