import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

class DemandForecaster:
    """
    Production inference interface for DecisionSphere demand forecasting.
    Loads serialized offline model artifact and executes single-step and recursive
    multi-step forecasts without assuming knowledge of future actual sales.
    """
    def __init__(self, artifact_path: str = "models/demand/demand_model.joblib"):
        if not os.path.exists(artifact_path):
            raise FileNotFoundError(f"Trained model artifact not found at {artifact_path}. Run train.py first.")
            
        self.bundle = joblib.load(artifact_path)
        self.model = self.bundle["model"]
        self.feature_columns = self.bundle["feature_columns"]
        self.xgb_params = self.bundle.get("xgb_params", {})
        self.best_iteration = self.bundle.get("best_iteration", None)

    def predict_step(self, X: pd.DataFrame) -> np.ndarray:
        """
        Executes a 1-step ahead prediction on pre-computed feature vectors.
        Enforces closed store rule (Open == 0 -> 0 sales).
        """
        X_mat = X[self.feature_columns]
        preds = self.model.predict(X_mat)
        if "Open" in X.columns:
            preds = np.where(X["Open"] == 0, 0.0, preds)
        return np.maximum(preds, 0.0)

    def predict_horizon(
        self,
        store_id: int,
        store_metadata: Dict[str, Any],
        history_series: pd.DataFrame,
        start_date: str,
        horizon_days: int = 14,
        promo_schedule: Optional[List[int]] = None,
        open_schedule: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Executes a recursive autoregressive multi-step forecast over horizon_days.
        Does NOT assume future actual Sales are available.
        Predictions for day t are appended to the historical buffer to compute lags for day t+1.
        
        Parameters:
        - store_id: Target store identifier.
        - store_metadata: Dictionary with StoreType_Encoded, Assortment_Encoded, LogCompetitionDistance, etc.
        - history_series: DataFrame containing at least 28 days of prior records with Date and Sales.
        - start_date: Starting date of forecast horizon (YYYY-MM-DD).
        - horizon_days: Forecast horizon (e.g. 7, 14, 28 days).
        - promo_schedule: Optional list of binary promo flags for each horizon day.
        - open_schedule: Optional list of binary open flags for each horizon day.
        """
        start_dt = pd.to_datetime(start_date)
        
        # Ensure history is sorted ascending and contains Date and Sales
        hist = history_series.copy().sort_values("Date").reset_index(drop=True)
        if len(hist) < 28:
            raise ValueError(f"History buffer must contain at least 28 days of prior sales for store {store_id}. Found {len(hist)}.")
            
        sales_buffer = hist["Sales"].tolist()
        dates_buffer = hist["Date"].tolist()
        
        daily_timeline = []
        projected_sales_sum = 0.0
        
        for step in range(horizon_days):
            current_dt = start_dt + timedelta(days=step)
            
            # Determine open status
            if open_schedule is not None and step < len(open_schedule):
                is_open = int(open_schedule[step])
            else:
                # Default: Closed on Sundays (dayofweek 6 in Python 0-indexed)
                is_open = 0 if current_dt.dayofweek == 6 else 1
                
            # Determine promo status
            if promo_schedule is not None and step < len(promo_schedule):
                promo = int(promo_schedule[step])
            else:
                promo = 0
                
            # Compute lags from current buffer (which includes recursively predicted prior steps)
            lag_1 = sales_buffer[-1]
            lag_7 = sales_buffer[-7]
            lag_14 = sales_buffer[-14]
            lag_28 = sales_buffer[-28]
            
            rolling_7 = float(np.mean(sales_buffer[-7:]))
            rolling_14 = float(np.mean(sales_buffer[-14:]))
            rolling_std_7 = float(np.std(sales_buffer[-7:])) if len(sales_buffer) >= 7 else 0.0
            
            # Assemble feature vector for current step
            row_features = {
                "DayOfWeek": current_dt.dayofweek + 1,
                "Month": current_dt.month,
                "Day": current_dt.day,
                "WeekOfYear": int(current_dt.isocalendar().week),
                "IsWeekend": 1 if current_dt.dayofweek in [5, 6] else 0,
                "IsMonthStart": 1 if current_dt.is_month_start else 0,
                "IsMonthEnd": 1 if current_dt.is_month_end else 0,
                "Promo": promo,
                "Promo2": store_metadata.get("Promo2", 0),
                "Promo2Active": store_metadata.get("Promo2Active", 0),
                "SchoolHoliday": store_metadata.get("SchoolHoliday", 0),
                "LogCompetitionDistance": store_metadata.get("LogCompetitionDistance", 8.0),
                "CompetitionOpen": store_metadata.get("CompetitionOpen", 1),
                "StoreType_Encoded": store_metadata.get("StoreType_Encoded", 0),
                "Assortment_Encoded": store_metadata.get("Assortment_Encoded", 0),
                "StateHoliday_Encoded": store_metadata.get("StateHoliday_Encoded", 0),
                "Sales_lag_1": lag_1,
                "Sales_lag_7": lag_7,
                "Sales_lag_14": lag_14,
                "Sales_lag_28": lag_28,
                "Sales_rolling_mean_7": rolling_7,
                "Sales_rolling_mean_14": rolling_14,
                "Sales_rolling_std_7": rolling_std_7,
                "Open": is_open
            }
            
            df_row = pd.DataFrame([row_features])
            
            if is_open == 0:
                y_hat = 0.0
            else:
                pred = self.model.predict(df_row[self.feature_columns])[0]
                y_hat = max(0.0, float(pred))
                
            # Append recursive prediction to buffer for subsequent steps
            sales_buffer.append(y_hat)
            dates_buffer.append(current_dt)
            projected_sales_sum += y_hat
            
            daily_timeline.append({
                "step": step + 1,
                "date": current_dt.strftime("%Y-%m-%d"),
                "predicted_sales": round(y_hat, 2),
                "promo": promo,
                "open": is_open
            })
            
        return {
            "store_id": store_id,
            "horizon_days": horizon_days,
            "start_date": start_date,
            "end_date": (start_dt + timedelta(days=horizon_days - 1)).strftime("%Y-%m-%d"),
            "total_projected_sales_units": round(projected_sales_sum, 2),
            "forecasting_method": "recursive_autoregressive_multistep",
            "units": "Sales units",
            "daily_timeline": daily_timeline
        }

    def simulate_conditional_scenario(
        self,
        store_id: int,
        store_metadata: Dict[str, Any],
        history_series: pd.DataFrame,
        start_date: str,
        horizon_days: int = 14,
        promo_override_flag: int = 1
    ) -> Dict[str, Any]:
        """
        Simulates the model's conditional response to a hypothetical promotional configuration.
        Compares baseline (promo=0) vs simulated (promo=1 on open weekdays).
        Clearly demarcates predictive simulation from causal claims.
        """
        # Baseline schedule: no promo
        base_promo = [0] * horizon_days
        # Scenario schedule: promo active on open days
        sim_promo = [promo_override_flag] * horizon_days
        
        baseline_res = self.predict_horizon(
            store_id=store_id,
            store_metadata=store_metadata,
            history_series=history_series,
            start_date=start_date,
            horizon_days=horizon_days,
            promo_schedule=base_promo
        )
        
        simulated_res = self.predict_horizon(
            store_id=store_id,
            store_metadata=store_metadata,
            history_series=history_series,
            start_date=start_date,
            horizon_days=horizon_days,
            promo_schedule=sim_promo
        )
        
        base_tot = baseline_res["total_projected_sales_units"]
        sim_tot = simulated_res["total_projected_sales_units"]
        delta_units = round(sim_tot - base_tot, 2)
        delta_pct = round((delta_units / base_tot * 100.0) if base_tot > 0 else 0.0, 2)
        
        return {
            "store_id": store_id,
            "horizon_days": horizon_days,
            "start_date": start_date,
            "units": "Sales units",
            "baseline_projected_sales": base_tot,
            "simulated_projected_sales": sim_tot,
            "sales_delta_units": delta_units,
            "sales_delta_percentage": delta_pct,
            "baseline_timeline": baseline_res["daily_timeline"],
            "simulated_timeline": simulated_res["daily_timeline"],
            "methodological_demarcation": (
                "Notice: This simulation represents the model's predictive response conditioned on hypothetical "
                "input parameters (Promo active). It reflects learned historical associations and should not be "
                "interpreted as an unverified causal proof."
            )
        }
