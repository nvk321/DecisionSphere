import pytest
import os
import numpy as np
import pandas as pd

from src.models.supply_chain.inference import SupplyChainInferenceService
from src.data.dataco_loader import load_dataco_raw
from src.data.dataco_features import create_dataco_features, split_chronological_dataco

MODEL_PATH = "models/supply_chain/supply_chain_model.joblib"

@pytest.fixture(scope="module")
def inference_service():
    """Initializes the SupplyChainInferenceService once for tests."""
    assert os.path.exists(MODEL_PATH), f"Model bundle {MODEL_PATH} must exist before running inference tests."
    return SupplyChainInferenceService(model_path=MODEL_PATH)

@pytest.fixture(scope="module")
def sample_test_orders():
    """Loads a small sample of test orders for inference tests."""
    df_raw = load_dataco_raw()
    df_feat = create_dataco_features(df_raw)
    _, _, test_df = split_chronological_dataco(df_feat)
    return test_df.head(50).copy()

def test_single_order_prediction_schema_and_bounds(inference_service, sample_test_orders):
    """Verifies single-order prediction output structure, bounds, and epistemic tier."""
    sample_order = sample_test_orders.iloc[0].to_dict()
    res = inference_service.predict_risk(sample_order)
    
    assert "risk_probability" in res
    assert "risk_class" in res
    assert "raw_probability" in res
    assert "epistemic_tier" in res
    
    assert 0.0 <= res["risk_probability"] <= 1.0
    assert 0.0 <= res["raw_probability"] <= 1.0
    assert res["risk_class"] in {0, 1}
    assert res["epistemic_tier"] == "PREDICTED"

def test_deterministic_reproducibility(inference_service, sample_test_orders):
    """Verifies that duplicate calls on identical input produce identical output."""
    sample_order = sample_test_orders.iloc[0].to_dict()
    res1 = inference_service.predict_risk(sample_order)
    res2 = inference_service.predict_risk(sample_order)
    
    assert res1["risk_probability"] == res2["risk_probability"]
    assert res1["risk_class"] == res2["risk_class"]
    assert res1["raw_probability"] == res2["raw_probability"]

def test_batch_prediction_shape_and_ordering(inference_service, sample_test_orders):
    """Verifies batch inference preserves row indexing and returns correct columns."""
    res_batch = inference_service.predict_batch(sample_test_orders)
    
    assert len(res_batch) == len(sample_test_orders)
    assert list(res_batch.index) == list(sample_test_orders.index)
    assert "predicted_late_risk_probability" in res_batch.columns
    assert "predicted_late_risk_class" in res_batch.columns
    assert (res_batch["epistemic_tier"] == "PREDICTED").all()
    assert (res_batch["predicted_late_risk_probability"] >= 0.0).all()
    assert (res_batch["predicted_late_risk_probability"] <= 1.0).all()

def test_scenario_simulation_non_mutation_and_delta(inference_service, sample_test_orders):
    """
    Verifies that simulate_scenario:
    1. Does not mutate the input DataFrame
    2. Correctly computes probability delta = scenario - baseline
    3. Returns epistemic_tier 'PREDICTED'
    """
    original_df = sample_test_orders.copy(deep=True)
    
    res_scen = inference_service.simulate_scenario(
        sample_test_orders,
        shipping_mode_override="First Class",
        scheduled_days_offset=-1
    )
    
    # Assert input was not mutated
    pd.testing.assert_frame_equal(sample_test_orders, original_df)
    
    assert "baseline_mean_probability" in res_scen
    assert "scenario_mean_probability" in res_scen
    assert "delta_probability" in res_scen
    assert res_scen["epistemic_tier"] == "PREDICTED"
    
    expected_delta = round(res_scen["scenario_mean_probability"] - res_scen["baseline_mean_probability"], 4)
    assert abs(res_scen["delta_probability"] - expected_delta) < 1e-4

def test_unseen_category_robustness(inference_service, sample_test_orders):
    """Verifies that unseen categories do not cause exceptions due to OneHotEncoder ignore fallback."""
    unseen_order = sample_test_orders.iloc[0].to_dict()
    unseen_order["shipping_mode"] = "Hyperloop_Ultra_Express"
    unseen_order["customer_state"] = "ZZ"
    unseen_order["market"] = "Antarctica"
    
    res = inference_service.predict_risk(unseen_order)
    assert 0.0 <= res["risk_probability"] <= 1.0
    assert res["risk_class"] in {0, 1}

def test_monotonicity_diagnostic_contract(inference_service, sample_test_orders):
    """Verifies that the monotonicity diagnostic returns a valid contract without failing on non-monotonicity."""
    diag = inference_service.evaluate_monotonicity(sample_test_orders, scheduled_days_sweep=[0, 1, 2, 4])
    
    assert "sweep" in diag
    assert "is_monotonic" in diag
    assert "monotonic_direction" in diag
    assert diag["epistemic_tier"] == "PREDICTED"
    assert isinstance(diag["is_monotonic"], bool)
    assert diag["monotonic_direction"] in {"strictly_decreasing", "strictly_increasing", "non_monotonic"}
