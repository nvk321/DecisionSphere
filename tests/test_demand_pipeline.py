import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.data.rossmann_features import create_demand_features, get_feature_columns, split_chronological
from src.models.demand.evaluate import compute_forecast_metrics

def create_synthetic_store_data():
    """Generates a small multi-store dataframe to verify feature logic and leakage controls."""
    dates = pd.date_range("2014-01-01", periods=60, freq="D")
    records = []
    
    # Store 1 has predictable linear sales: 100, 110, 120...
    for i, d in enumerate(dates):
        records.append({
            "Store": 1,
            "Date": d,
            "Sales": float(100 + i * 10),
            "Open": 1,
            "Promo": 1 if i % 7 == 0 else 0,
            "StateHoliday": "0",
            "SchoolHoliday": 0,
            "StoreType": "a",
            "Assortment": "a",
            "CompetitionDistance": 500.0,
            "CompetitionOpenSinceMonth": 1.0,
            "CompetitionOpenSinceYear": 2013.0,
            "Promo2": 0,
            "Promo2SinceWeek": np.nan,
            "Promo2SinceYear": np.nan,
            "PromoInterval": np.nan
        })
        
    # Store 2 has distinct constant sales: 5000, 5000...
    for i, d in enumerate(dates):
        records.append({
            "Store": 2,
            "Date": d,
            "Sales": 5000.0,
            "Open": 1 if i % 7 != 6 else 0, # Closed on Sundays
            "Promo": 0,
            "StateHoliday": "0",
            "SchoolHoliday": 0,
            "StoreType": "c",
            "Assortment": "c",
            "CompetitionDistance": 2000.0,
            "CompetitionOpenSinceMonth": np.nan,
            "CompetitionOpenSinceYear": np.nan,
            "Promo2": 1,
            "Promo2SinceWeek": 1.0,
            "Promo2SinceYear": 2013.0,
            "PromoInterval": "Jan,Apr,Jul,Oct"
        })
        
    df = pd.DataFrame(records)
    # Intentionally shuffle to test that sorting is handled correctly
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    return df

def test_store_isolation_in_lags():
    """Verify that lag features for Store 2 NEVER inherit sales from Store 1."""
    df_raw = create_synthetic_store_data()
    df_feat = create_demand_features(df_raw)
    
    # Check Store 2 first rows
    s2 = df_feat[df_feat["Store"] == 2].sort_values("Date").reset_index(drop=True)
    
    # Store 2 sales are always 5000. Lag_1 for Store 2 must be 5000.0
    for val in s2["Sales_lag_1"]:
        assert val == 5000.0, f"Cross-store leakage detected! Found {val} in Store 2 lag."

def test_anti_leakage_in_rolling_statistics():
    """Verify that rolling mean never uses current day target y_t."""
    df_raw = create_synthetic_store_data()
    df_feat = create_demand_features(df_raw)
    
    s1 = df_feat[df_feat["Store"] == 1].sort_values("Date").reset_index(drop=True)
    
    # On day index 10:
    # Sales values for days 0..10 are: 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200
    # Day 10 Sales is 200.
    # The 7-day rolling mean at day 10 must use days 3..9 (130, 140, 150, 160, 170, 180, 190) -> mean = 160.0
    expected_mean_day_10 = np.mean([130, 140, 150, 160, 170, 180, 190])
    actual_mean_day_10 = s1.loc[10, "Sales_rolling_mean_7"]
    assert actual_mean_day_10 == pytest.approx(expected_mean_day_10), (
        f"Rolling mean leakage detected! Expected {expected_mean_day_10}, got {actual_mean_day_10}"
    )

def test_chronological_splitting():
    """Verify that train, validation, and test splits have strictly non-overlapping dates in ascending sequence."""
    df_raw = create_synthetic_store_data()
    train_df, val_df, test_df = split_chronological(
        df_raw,
        train_end_date="2014-01-31",
        val_end_date="2014-02-15"
    )
    
    assert train_df["Date"].max() < val_df["Date"].min()
    assert val_df["Date"].max() < test_df["Date"].min()
    assert len(train_df) + len(val_df) + len(test_df) == len(df_raw)

def test_feature_columns_exist():
    """Verify that all feature columns produced are non-empty and numerical."""
    df_raw = create_synthetic_store_data()
    df_feat = create_demand_features(df_raw)
    cols = get_feature_columns()
    
    for c in cols:
        assert c in df_feat.columns, f"Missing feature column: {c}"
        assert not df_feat[c].isnull().any(), f"Feature column {c} contains null values!"
        assert np.issubdtype(df_feat[c].dtype, np.number), f"Feature column {c} is not numeric!"

def test_forecast_metrics_units():
    """Verify that compute_forecast_metrics computes MAE, RMSE, and WAPE correctly in Sales units."""
    y_true = np.array([1000.0, 2000.0, 3000.0])
    y_pred = np.array([1100.0, 1900.0, 3200.0])
    # Absolute errors: 100, 100, 200 -> MAE = 400 / 3 = 133.33
    # Squared errors: 10000, 10000, 40000 -> MSE = 60000 / 3 = 20000 -> RMSE = sqrt(20000) = 141.42
    # Sum actual = 6000 -> WAPE = 400 / 6000 = 0.0667 (6.67%)
    metrics = compute_forecast_metrics(y_true, y_pred)
    assert metrics["mae_sales_units"] == pytest.approx(133.33, abs=0.01)
    assert metrics["rmse_sales_units"] == pytest.approx(141.42, abs=0.01)
    assert metrics["wape_pct"] == pytest.approx(6.67, abs=0.01)
