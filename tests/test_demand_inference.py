import pytest
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.models.demand.inference import DemandForecaster

ARTIFACT_PATH = "models/demand/demand_model.joblib"

@pytest.fixture(scope="module")
def forecaster():
    assert os.path.exists(ARTIFACT_PATH), "Model artifact does not exist. Train model first."
    return DemandForecaster(artifact_path=ARTIFACT_PATH)

def test_model_artifact_loads(forecaster):
    """Verify artifact loads correctly and has expected feature columns."""
    assert forecaster.model is not None
    assert len(forecaster.feature_columns) == 23
    assert "Sales_lag_1" in forecaster.feature_columns
    assert "Promo" in forecaster.feature_columns

def test_recursive_multistep_forecasting(forecaster):
    """Verify recursive multi-step forecasting over 14 days without future actual sales."""
    # Create 35 days of dummy history for Store 1
    dates = pd.date_range("2015-06-01", periods=35, freq="D")
    sales = [5000.0 + np.sin(i) * 500 for i in range(35)]
    hist_df = pd.DataFrame({"Date": dates, "Sales": sales})
    
    metadata = {
        "StoreType_Encoded": 0,
        "Assortment_Encoded": 0,
        "LogCompetitionDistance": 8.0,
        "CompetitionOpen": 1,
        "Promo2": 0,
        "Promo2Active": 0,
        "SchoolHoliday": 0,
        "StateHoliday_Encoded": 0
    }
    
    result = forecaster.predict_horizon(
        store_id=1,
        store_metadata=metadata,
        history_series=hist_df,
        start_date="2015-07-06",
        horizon_days=14
    )
    
    assert result["store_id"] == 1
    assert result["horizon_days"] == 14
    assert result["units"] == "Sales units"
    assert result["forecasting_method"] == "recursive_autoregressive_multistep"
    assert len(result["daily_timeline"]) == 14
    assert result["total_projected_sales_units"] > 0
    
    # Check that each day has non-negative sales
    for day in result["daily_timeline"]:
        assert day["predicted_sales"] >= 0.0
        # If open is 0, sales must be 0
        if day["open"] == 0:
            assert day["predicted_sales"] == 0.0

def test_conditional_scenario_simulation(forecaster):
    """Verify conditional scenario simulation comparing baseline (Promo=0) vs simulated (Promo=1)."""
    dates = pd.date_range("2015-06-01", periods=35, freq="D")
    sales = [5000.0 + np.sin(i) * 500 for i in range(35)]
    hist_df = pd.DataFrame({"Date": dates, "Sales": sales})
    
    metadata = {
        "StoreType_Encoded": 0,
        "Assortment_Encoded": 0,
        "LogCompetitionDistance": 8.0,
        "CompetitionOpen": 1,
        "Promo2": 0,
        "Promo2Active": 0,
        "SchoolHoliday": 0,
        "StateHoliday_Encoded": 0
    }
    
    sim = forecaster.simulate_conditional_scenario(
        store_id=1,
        store_metadata=metadata,
        history_series=hist_df,
        start_date="2015-07-06",
        horizon_days=14,
        promo_override_flag=1
    )
    
    assert "baseline_projected_sales" in sim
    assert "simulated_projected_sales" in sim
    assert "sales_delta_units" in sim
    assert "methodological_demarcation" in sim
    assert sim["units"] == "Sales units"
    # Model conditional response with promo=1 should forecast higher volume than promo=0
    assert sim["simulated_projected_sales"] > sim["baseline_projected_sales"]
