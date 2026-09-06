import pytest
import os
import numpy as np
import pandas as pd
import joblib

from src.models.workforce.inference import WorkforceInferenceService, DEFAULT_WORKFORCE_MODEL_PATH
from src.data.ibm_hr_loader import load_ibm_hr_raw
from src.data.ibm_hr_features import create_ibm_hr_features, split_stratified_ibm_hr


@pytest.fixture(scope="module")
def inference_service():
    """Initializes the WorkforceInferenceService once for tests."""
    assert os.path.exists(DEFAULT_WORKFORCE_MODEL_PATH), (
        f"Model bundle '{DEFAULT_WORKFORCE_MODEL_PATH}' must exist before running inference tests."
    )
    return WorkforceInferenceService(model_path=DEFAULT_WORKFORCE_MODEL_PATH)


@pytest.fixture(scope="module")
def sample_test_employees():
    """Loads a small sample of test employees for inference tests."""
    df_raw = load_ibm_hr_raw()
    df_feat = create_ibm_hr_features(df_raw)
    _, _, test_df = split_stratified_ibm_hr(df_feat, random_state=42)
    return test_df.head(25).copy()


def test_workforce_artifact_loads():
    """Verifies that the serialized workforce model artifact loads independently."""
    assert os.path.exists(DEFAULT_WORKFORCE_MODEL_PATH)
    bundle = joblib.load(DEFAULT_WORKFORCE_MODEL_PATH)
    expected_keys = {
        "preprocessor",
        "base_model",
        "calibrated_model",
        "decision_threshold",
        "feature_names",
        "numerical_features",
        "categorical_features",
        "training_metadata",
    }
    for k in expected_keys:
        assert k in bundle, f"Missing key '{k}' in workforce model bundle"


def test_single_employee_prediction_schema_and_bounds(inference_service, sample_test_employees):
    """Verifies single-employee prediction output structure, bounds, and epistemic tier."""
    sample_emp = sample_test_employees.iloc[0].to_dict()
    res = inference_service.predict_attrition(sample_emp)
    
    assert "attrition_probability" in res
    assert "raw_probability" in res
    assert "attrition_class" in res
    assert "decision_threshold" in res
    assert "epistemic_tier" in res
    
    assert 0.0 <= res["attrition_probability"] <= 1.0
    assert 0.0 <= res["raw_probability"] <= 1.0
    assert res["attrition_class"] in {0, 1}
    assert res["epistemic_tier"] == "PREDICTED"


def test_deterministic_reproducibility(inference_service, sample_test_employees):
    """Verifies that duplicate calls on identical input produce identical output."""
    sample_emp = sample_test_employees.iloc[0].to_dict()
    res1 = inference_service.predict_attrition(sample_emp)
    res2 = inference_service.predict_attrition(sample_emp)
    
    assert res1["attrition_probability"] == res2["attrition_probability"]
    assert res1["raw_probability"] == res2["raw_probability"]
    assert res1["attrition_class"] == res2["attrition_class"]


def test_batch_prediction_shape_and_ordering(inference_service, sample_test_employees):
    """Verifies batch inference preserves row indexing and returns correct columns."""
    res_batch = inference_service.predict_batch(sample_test_employees)
    
    assert len(res_batch) == len(sample_test_employees)
    assert list(res_batch.index) == list(sample_test_employees.index)
    assert "predicted_attrition_probability" in res_batch.columns
    assert "predicted_attrition_raw_probability" in res_batch.columns
    assert "predicted_attrition_class" in res_batch.columns
    assert (res_batch["epistemic_tier"] == "PREDICTED").all()
    assert (res_batch["predicted_attrition_probability"] >= 0.0).all()
    assert (res_batch["predicted_attrition_probability"] <= 1.0).all()


def test_scenario_simulation_non_mutation(inference_service, sample_test_employees):
    """Verifies that simulate_scenario does NOT mutate the original DataFrame."""
    original_overtimes = sample_test_employees["OverTime"].tolist()
    original_copy = sample_test_employees.copy(deep=True)
    
    _ = inference_service.simulate_scenario(sample_test_employees, overtime_override="Yes")
    
    # Assert input dataframe remains completely untouched
    pd.testing.assert_frame_equal(sample_test_employees, original_copy)
    assert sample_test_employees["OverTime"].tolist() == original_overtimes


def test_scenario_simulation_delta_calculation(inference_service, sample_test_employees):
    """Verifies delta probability equals scenario minus baseline within numerical tolerance."""
    res = inference_service.simulate_scenario(sample_test_employees, overtime_override="Yes")
    
    expected_delta = res["scenario_mean_probability"] - res["baseline_mean_probability"]
    assert np.isclose(res["delta_probability"], expected_delta, atol=1e-4)
    assert res["epistemic_tier"] == "PREDICTED"
    assert "interpretation" in res


def test_scenario_override_behavior(inference_service, sample_test_employees):
    """Verifies that setting overtime_override modifies model predictions."""
    res_yes = inference_service.simulate_scenario(sample_test_employees, overtime_override="Yes")
    res_no = inference_service.simulate_scenario(sample_test_employees, overtime_override="No")
    
    assert res_yes["scenario_definition"]["overtime_override"] == "Yes"
    assert res_no["scenario_definition"]["overtime_override"] == "No"
    
    # The scenario probabilities under Yes vs No should differ
    assert res_yes["scenario_mean_probability"] != res_no["scenario_mean_probability"]


def test_scenario_salary_hike_override(inference_service, sample_test_employees):
    """Verifies salary hike override operates cleanly and preserves non-mutation."""
    res = inference_service.simulate_scenario(sample_test_employees, salary_hike_override=25.0)
    assert res["scenario_definition"]["salary_hike_override"] == 25.0
    assert "delta_probability" in res


def test_unseen_category_robustness(inference_service, sample_test_employees):
    """Verifies that unseen categorical levels are safely ignored without crashing."""
    emp = sample_test_employees.iloc[0].to_dict()
    emp["Department"] = "NON_EXISTENT_DEPARTMENT_999"
    emp["JobRole"] = "CHIEF_IMAGINATION_OFFICER"
    emp["BusinessTravel"] = "SPACE_TRAVEL"
    
    res = inference_service.predict_attrition(emp)
    assert 0.0 <= res["attrition_probability"] <= 1.0
    assert res["attrition_class"] in {0, 1}
