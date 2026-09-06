import numpy as np
from typing import Dict, Any

def compute_forecast_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
    """
    Computes standard forecasting error metrics in the dataset's native Sales units.
    - MAE: Mean Absolute Error (in Sales units)
    - RMSE: Root Mean Squared Error (in Sales units)
    - WAPE: Weighted Absolute Percentage Error (sum(|y - y_hat|) / sum(y))
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    
    # Clip predictions to non-negative sales
    y_pred = np.maximum(y_pred, 0.0)
    
    abs_errors = np.abs(y_true - y_pred)
    mae = float(np.mean(abs_errors))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    
    sum_actual = float(np.sum(y_true))
    if sum_actual > 0:
        wape = float(np.sum(abs_errors) / sum_actual)
    else:
        wape = float("nan")
        
    return {
        "sample_count": int(len(y_true)),
        "mean_actual_sales": round(float(np.mean(y_true)), 2),
        "mae_sales_units": round(mae, 2),
        "rmse_sales_units": round(rmse, 2),
        "wape_ratio": round(wape, 4),
        "wape_pct": round(wape * 100.0, 2)
    }
