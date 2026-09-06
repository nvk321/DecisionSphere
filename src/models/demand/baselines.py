import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from typing import List

class NaiveSeasonalBaseline:
    """
    Level 0 Forecasting Baseline:
    Predicts sales using the 7-day seasonal persistence lag (y_{t-7}).
    Falls back to historical store mean sales when lag is unavailable.
    """
    def __init__(self):
        self.store_means = {}
        self.global_mean = 0.0

    def fit(self, df_train: pd.DataFrame):
        self.global_mean = float(df_train["Sales"].mean())
        self.store_means = df_train.groupby("Store")["Sales"].mean().to_dict()
        return self

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        # Use Sales_lag_7 if present, else fallback to store mean
        if "Sales_lag_7" in df.columns:
            preds = df["Sales_lag_7"].copy()
            # Fill missing with store mean
            fallback = df["Store"].map(self.store_means).fillna(self.global_mean)
            preds = preds.fillna(fallback).values
        else:
            preds = df["Store"].map(self.store_means).fillna(self.global_mean).values
            
        # Closed stores predict 0
        if "Open" in df.columns:
            preds = np.where(df["Open"] == 0, 0.0, preds)
            
        return np.maximum(preds, 0.0)


class RidgeRegressionBaseline:
    """
    Level 1 Forecasting Baseline:
    Linear model with L2 regularization (Ridge) fitted on standardized numerical
    and one-hot / encoded categorical attributes.
    """
    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha
        self.scaler = StandardScaler()
        self.model = Ridge(alpha=self.alpha, random_state=42)
        self.feature_columns: List[str] = []

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series, feature_columns: List[str]):
        self.feature_columns = feature_columns
        X_mat = X_train[self.feature_columns].values
        X_scaled = self.scaler.fit_transform(X_mat)
        self.model.fit(X_scaled, y_train.values)
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        X_mat = X[self.feature_columns].values
        X_scaled = self.scaler.transform(X_mat)
        preds = self.model.predict(X_scaled)
        
        # Closed store constraint
        if "Open" in X.columns:
            preds = np.where(X["Open"] == 0, 0.0, preds)
            
        return np.maximum(preds, 0.0)
