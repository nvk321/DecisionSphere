import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression

from src.data.dataco_features import get_numerical_features, get_categorical_features

class NaiveMajorityBaseline(BaseEstimator, ClassifierMixin):
    """
    Level 0 Naive Baseline.
    - Majority class prediction: Always predicts the training set majority class (1).
    - Prevalence probability prediction: Predicts the constant empirical training prevalence P(y=1).
    Serves as the rigorous baseline anchor for ROC-AUC (0.5), PR-AUC (prevalence), and Brier Score.
    """
    def __init__(self):
        self.majority_class_: int = 1
        self.prevalence_: float = 0.5
        self.classes_ = np.array([0, 1])

    def fit(self, X: Any, y: pd.Series):
        y_arr = np.asarray(y)
        self.prevalence_ = float(np.mean(y_arr))
        self.majority_class_ = int(self.prevalence_ >= 0.5)
        return self

    def predict(self, X: Any) -> np.ndarray:
        n_samples = len(X)
        return np.full(n_samples, self.majority_class_, dtype=int)

    def predict_proba(self, X: Any) -> np.ndarray:
        n_samples = len(X)
        prob_1 = self.prevalence_
        prob_0 = 1.0 - prob_1
        return np.tile([prob_0, prob_1], (n_samples, 1))

def build_logistic_regression_pipeline(
    numerical_cols: List[str] = None,
    categorical_cols: List[str] = None,
    max_iter: int = 1000,
    random_state: int = 42
) -> Pipeline:
    """
    Level 1 Linear Classifier Baseline.
    Constructs a leakage-free Scikit-Learn Pipeline combining:
    - StandardScaler on numerical predictors
    - OneHotEncoder(handle_unknown='ignore') on categorical predictors
    - LogisticRegression with L2 regularization
    """
    if numerical_cols is None:
        numerical_cols = get_numerical_features()
    if categorical_cols is None:
        categorical_cols = get_categorical_features()

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numerical_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_cols),
        ],
        remainder="drop"
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", LogisticRegression(max_iter=max_iter, random_state=random_state, solver="lbfgs"))
        ]
    )

    return pipeline
