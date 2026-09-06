import pytest
import os
import numpy as np
import pandas as pd

from src.data.dataco_loader import load_dataco_raw
from src.data.dataco_features import (
    create_dataco_features,
    split_chronological_dataco,
    get_feature_columns,
    get_numerical_features,
    get_categorical_features,
    ALL_EXCLUDED_COLUMNS,
    PROHIBITED_LOOKAHEAD_COLUMNS,
    PROHIBITED_ACCOUNTING_COLUMNS,
    PROHIBITED_PII_SURROGATE_COLUMNS,
)

@pytest.fixture(scope="module")
def sample_dataco_raw():
    """Loads a small sample of DataCo raw data for unit testing."""
    df_raw = load_dataco_raw()
    return df_raw.head(500).copy()

def test_dataco_raw_dimensions_and_schema():
    """Verify raw dataset dimensions and critical column existence."""
    df_raw = load_dataco_raw()
    assert len(df_raw) == 180519, f"Expected 180,519 rows, got {len(df_raw)}"
    assert len(df_raw.columns) == 54, f"Expected 54 columns (53 raw + parsed order_dt), got {len(df_raw.columns)}"
    assert "Late_delivery_risk" in df_raw.columns
    assert set(df_raw["Late_delivery_risk"].unique()) == {0, 1}

def test_feature_creation_strict_anti_leakage(sample_dataco_raw):
    """
    CRITICAL REGRESSION TEST:
    Asserts that prohibited lookahead, post-fulfillment, accounting, PII,
    and surrogate identifier columns are NEVER present in feature matrix X.
    """
    df_feat = create_dataco_features(sample_dataco_raw)
    feature_cols = get_feature_columns()
    
    # 1. Check all prohibited columns are absent
    for col in ALL_EXCLUDED_COLUMNS:
        assert col not in df_feat.columns, f"LEAKAGE VIOLATION: '{col}' found in feature matrix!"
        assert col not in feature_cols, f"LEAKAGE VIOLATION: '{col}' found in feature column list!"

    # 2. Check individual critical lookahead names
    for col in [
        "Days for shipping (real)",
        "Delivery Status",
        "shipping date (DateOrders)",
        "Order Status",
        "Benefit per order",
        "Order Profit Per Order",
        "Order Item Profit Ratio",
        "Sales per customer"
    ]:
        assert col not in df_feat.columns
        assert col not in feature_cols

def test_pii_and_surrogate_identifiers_excluded(sample_dataco_raw):
    """Asserts that customer and order IDs are strictly excluded."""
    df_feat = create_dataco_features(sample_dataco_raw)
    for pii_col in ["Customer Email", "Customer Fname", "Customer Lname", "Customer Password", "Customer Id", "Order Id", "Order Item Id"]:
        assert pii_col not in df_feat.columns

def test_feature_column_consistency(sample_dataco_raw):
    """Verify feature column types and predictor list integrity."""
    df_feat = create_dataco_features(sample_dataco_raw)
    num_cols = get_numerical_features()
    cat_cols = get_categorical_features()
    feature_cols = get_feature_columns()
    
    assert len(feature_cols) == len(num_cols) + len(cat_cols)
    assert set(feature_cols) == set(num_cols).union(set(cat_cols))
    
    for col in num_cols:
        assert np.issubdtype(df_feat[col].dtype, np.number), f"Numerical feature '{col}' is not numeric"
        
    for col in cat_cols:
        assert (
            pd.api.types.is_string_dtype(df_feat[col])
            or pd.api.types.is_object_dtype(df_feat[col])
            or isinstance(df_feat[col].dtype, pd.CategoricalDtype)
        ), f"Categorical feature '{col}' has invalid dtype: {df_feat[col].dtype}"

def test_chronological_split_strict_invariants():
    """
    Asserts strict chronological ordering:
    max(train) < min(val) < min(test) with zero temporal overlap.
    """
    df_raw = load_dataco_raw()
    df_feat = create_dataco_features(df_raw)
    train_df, val_df, test_df = split_chronological_dataco(df_feat)
    
    assert train_df["order_dt"].max() < val_df["order_dt"].min()
    assert val_df["order_dt"].max() < test_df["order_dt"].min()
    assert len(train_df) + len(val_df) + len(test_df) == len(df_raw)
    
    # Check expected partition sizes
    assert len(train_df) == 125200
    assert len(val_df) == 30950
    assert len(test_df) == 24369
    
    # Target prevalence check (assert reasonable operational bounds ~54-55%)
    assert 0.50 <= train_df["late_delivery_risk"].mean() <= 0.60
    assert 0.50 <= val_df["late_delivery_risk"].mean() <= 0.60
    assert 0.50 <= test_df["late_delivery_risk"].mean() <= 0.60
