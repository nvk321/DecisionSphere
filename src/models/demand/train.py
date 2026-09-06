import os
import json
import time
import joblib
import pandas as pd
import numpy as np
import xgboost as xgb

from src.data.rossmann_loader import load_rossmann_raw, merge_store_metadata
from src.data.rossmann_features import create_demand_features, get_feature_columns, split_chronological
from src.models.demand.baselines import NaiveSeasonalBaseline, RidgeRegressionBaseline
from src.models.demand.evaluate import compute_forecast_metrics

MODEL_OUTPUT_DIR = "models/demand"

def train_demand_pipeline(data_dir: str = "data/raw/rossmann", output_dir: str = MODEL_OUTPUT_DIR):
    """
    Executes the complete retail demand forecasting training pipeline:
    1. Ingestion & metadata merging
    2. Causally valid feature engineering
    3. Chronological splitting (70% train / 15% val / 15% test)
    4. Training Level 0 (Naive), Level 1 (Ridge), Level 2 (XGBoost)
    5. Comprehensive metric evaluation in Sales units
    6. Serialization of model artifact and evaluation records
    """
    os.makedirs(output_dir, exist_ok=True)
    start_time = time.time()
    
    print("Step 1: Loading raw Rossmann data...")
    df_train_raw, df_store_raw = load_rossmann_raw(data_dir=data_dir)
    print(f"Loaded train: {len(df_train_raw):,} records, store: {len(df_store_raw):,} stores.")
    
    print("Step 2: Merging store metadata and engineering features...")
    df_merged = merge_store_metadata(df_train_raw, df_store_raw)
    df_feat = create_demand_features(df_merged)
    feature_cols = get_feature_columns()
    print(f"Feature matrix assembled: {len(df_feat):,} rows x {len(feature_cols)} predictor features.")
    
    print("Step 3: Performing chronological train/val/test split...")
    train_df, val_df, test_df = split_chronological(
        df_feat,
        train_end_date="2014-10-19",
        val_end_date="2015-03-10"
    )
    print(f"Train split: {len(train_df):,} rows ({train_df['Date'].min().strftime('%Y-%m-%d')} to {train_df['Date'].max().strftime('%Y-%m-%d')})")
    print(f"Val split:   {len(val_df):,} rows ({val_df['Date'].min().strftime('%Y-%m-%d')} to {val_df['Date'].max().strftime('%Y-%m-%d')})")
    print(f"Test split:  {len(test_df):,} rows ({test_df['Date'].min().strftime('%Y-%m-%d')} to {test_df['Date'].max().strftime('%Y-%m-%d')})")
    
    # Filter for open stores during training (as sales are deterministically 0 when closed)
    train_open = train_df[(train_df["Open"] == 1) & (train_df["Sales"] > 0)].copy()
    val_open = val_df[(val_df["Open"] == 1) & (val_df["Sales"] > 0)].copy()
    test_open = test_df[(test_df["Open"] == 1) & (test_df["Sales"] > 0)].copy()
    
    X_train, y_train = train_open[feature_cols], train_open["Sales"]
    X_val, y_val = val_open[feature_cols], val_open["Sales"]
    X_test, y_test = test_open[feature_cols], test_open["Sales"]
    
    metrics_record = {
        "dataset": "Rossmann Store Sales",
        "evaluation_units": "Sales units",
        "split_boundaries": {
            "train": f"{train_df['Date'].min().strftime('%Y-%m-%d')} to {train_df['Date'].max().strftime('%Y-%m-%d')}",
            "val": f"{val_df['Date'].min().strftime('%Y-%m-%d')} to {val_df['Date'].max().strftime('%Y-%m-%d')}",
            "test": f"{test_df['Date'].min().strftime('%Y-%m-%d')} to {test_df['Date'].max().strftime('%Y-%m-%d')}"
        },
        "sample_counts": {
            "train_open": len(X_train),
            "val_open": len(X_val),
            "test_open": len(X_test),
            "test_total": len(test_df)
        },
        "models": {}
    }
    
    # ----------------------------------------------------
    # Level 0: Naive Seasonal Baseline
    # ----------------------------------------------------
    print("\nTraining Level 0: Naive Seasonal Baseline...")
    l0_model = NaiveSeasonalBaseline().fit(train_open)
    l0_test_pred = l0_model.predict(test_open)
    l0_metrics = compute_forecast_metrics(y_test.values, l0_test_pred)
    metrics_record["models"]["Level_0_Naive_Seasonal"] = {
        "description": "7-day seasonal persistence (y_{t-7}) with store-mean fallback",
        "test_metrics": l0_metrics
    }
    print(f"Level 0 Test Results -> MAE: {l0_metrics['mae_sales_units']} Sales units, RMSE: {l0_metrics['rmse_sales_units']}, WAPE: {l0_metrics['wape_pct']}%")
    
    # ----------------------------------------------------
    # Level 1: Regularized Linear Model (Ridge)
    # ----------------------------------------------------
    print("\nTraining Level 1: Regularized Ridge Regression Baseline...")
    l1_model = RidgeRegressionBaseline(alpha=10.0).fit(X_train, y_train, feature_cols)
    l1_test_pred = l1_model.predict(test_open)
    l1_metrics = compute_forecast_metrics(y_test.values, l1_test_pred)
    metrics_record["models"]["Level_1_Ridge_Regression"] = {
        "description": "Ridge regression (L2 regularized) on scaled features",
        "test_metrics": l1_metrics
    }
    print(f"Level 1 Test Results -> MAE: {l1_metrics['mae_sales_units']} Sales units, RMSE: {l1_metrics['rmse_sales_units']}, WAPE: {l1_metrics['wape_pct']}%")
    
    # ----------------------------------------------------
    # Level 2: XGBoost Regressor
    # ----------------------------------------------------
    print("\nTraining Level 2: XGBoost Regressor (Histogram tree method)...")
    xgb_params = {
        "n_estimators": 350,
        "max_depth": 8,
        "learning_rate": 0.08,
        "subsample": 0.85,
        "colsample_bytree": 0.85,
        "tree_method": "hist",
        "random_state": 42,
        "n_jobs": -1,
        "early_stopping_rounds": 30
    }
    
    xgb_model = xgb.XGBRegressor(**xgb_params)
    xgb_model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=50
    )
    
    val_pred = xgb_model.predict(X_val)
    test_pred = xgb_model.predict(X_test)
    
    val_metrics = compute_forecast_metrics(y_val.values, val_pred)
    test_metrics = compute_forecast_metrics(y_test.values, test_pred)
    
    # Also evaluate on full test set including closed stores (applying Open==0 => 0 rule)
    full_test_pred = np.where(test_df["Open"] == 0, 0.0, xgb_model.predict(test_df[feature_cols]))
    full_test_metrics = compute_forecast_metrics(test_df["Sales"].values, full_test_pred)
    
    metrics_record["models"]["Level_2_XGBoost"] = {
        "description": "XGBoost Regressor with early stopping",
        "best_iteration": int(xgb_model.best_iteration),
        "val_metrics": val_metrics,
        "test_metrics_open_stores": test_metrics,
        "test_metrics_all_stores": full_test_metrics
    }
    print(f"Level 2 Test Results (Open) -> MAE: {test_metrics['mae_sales_units']} Sales units, RMSE: {test_metrics['rmse_sales_units']}, WAPE: {test_metrics['wape_pct']}%")
    print(f"Level 2 Test Results (All)  -> MAE: {full_test_metrics['mae_sales_units']} Sales units, RMSE: {full_test_metrics['rmse_sales_units']}, WAPE: {full_test_metrics['wape_pct']}%")
    
    # ----------------------------------------------------
    # Serialization of Artifact Bundle
    # ----------------------------------------------------
    artifact_path = os.path.join(output_dir, "demand_model.joblib")
    artifact_bundle = {
        "model": xgb_model,
        "feature_columns": feature_cols,
        "xgb_params": xgb_params,
        "best_iteration": int(xgb_model.best_iteration),
        "split_boundaries": metrics_record["split_boundaries"],
        "metrics": test_metrics,
        "training_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    joblib.dump(artifact_bundle, artifact_path, compress=3)
    print(f"\nModel artifact successfully saved to: {artifact_path} ({os.path.getsize(artifact_path)/(1024*1024):.2f} MB)")
    
    metrics_path = os.path.join(output_dir, "metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_record, f, indent=2)
    print(f"Evaluation metrics saved to: {metrics_path}")
    
    elapsed = time.time() - start_time
    print(f"Phase 2 Demand Training Pipeline completed in {elapsed:.2f} seconds.")
    return metrics_record

if __name__ == "__main__":
    train_demand_pipeline()
