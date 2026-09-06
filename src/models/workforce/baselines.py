import numpy as np
import pandas as pd
from typing import Dict, Any
from sklearn.linear_model import LogisticRegression


class MajorityClassWorkforceBaseline:
    """
    Level 0a Baseline: Predicts constant majority class (0 = No Attrition).
    Useful as the benchmark for classification accuracy and F1.
    """
    def __init__(self):
        self.majority_class_ = 0

    def fit(self, X: np.ndarray, y: np.ndarray):
        counts = np.bincount(y)
        self.majority_class_ = int(np.argmax(counts))
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.full(shape=(len(X),), fill_value=self.majority_class_, dtype=int)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        # Binary probability: [P(y=0), P(y=1)]
        p1 = float(self.majority_class_)
        probs = np.zeros((len(X), 2))
        probs[:, 1] = p1
        probs[:, 0] = 1.0 - p1
        return probs


class PrevalenceProbabilityWorkforceBaseline:
    """
    Level 0b Baseline: Predicts constant training prevalence probability P(y=1) = y_train.mean().
    This is the proper statistical baseline for Brier Score, PR-AUC, and ROC-AUC.
    """
    def __init__(self):
        self.prevalence_ = 0.1613

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.prevalence_ = float(np.mean(y))
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        p1 = self.prevalence_
        probs = np.zeros((len(X), 2))
        probs[:, 1] = p1
        probs[:, 0] = 1.0 - p1
        return probs

    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        return (self.predict_proba(X)[:, 1] >= threshold).astype(int)


def create_logistic_regression_workforce_baseline(
    class_weight: str = "balanced",
    random_state: int = 42,
    max_iter: int = 1000,
) -> LogisticRegression:
    """
    Level 1 Baseline: Linear Logistic Regression with balanced class weighting.
    Provides a standardized linear decision boundary for tabular comparison.
    """
    return LogisticRegression(
        class_weight=class_weight,
        random_state=random_state,
        max_iter=max_iter,
        solver="lbfgs",
    )
