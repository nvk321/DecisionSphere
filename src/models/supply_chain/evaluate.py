import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score,
    accuracy_score,
    confusion_matrix,
)
from sklearn.calibration import calibration_curve

def compute_classification_metrics(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float = 0.5,
    n_bins: int = 10
) -> Dict[str, Any]:
    """
    Computes comprehensive discrimination, calibration, and classification metrics
    for late delivery risk prediction.
    
    Parameters:
    -----------
    y_true : 1D array of ground truth binary labels {0, 1}
    y_prob : 1D array of predicted probabilities P(y=1) in [0, 1]
    threshold : Decision cutoff for discrete class predictions (selected on validation set)
    n_bins : Number of probability bins for calibration curve and ECE proxy
    
    Returns:
    --------
    Dictionary containing all evaluated metrics, calibration curve, and confusion matrix.
    """
    y_true = np.asarray(y_true, dtype=int)
    y_prob = np.asarray(y_prob, dtype=float)
    y_prob = np.clip(y_prob, 0.0, 1.0)
    
    y_pred = (y_prob >= threshold).astype(int)
    
    # 1. Discrimination Metrics
    # Handle constant probability edge-case
    if len(np.unique(y_prob)) <= 1 or len(np.unique(y_true)) <= 1:
        roc_auc = 0.5
        pr_auc = float(np.mean(y_true))
    else:
        roc_auc = float(roc_auc_score(y_true, y_prob))
        pr_auc = float(average_precision_score(y_true, y_prob))
        
    # 2. Probability Quality Metrics
    brier = float(brier_score_loss(y_true, y_prob))
    
    # Calibration curve & Expected Calibration Error (ECE proxy)
    prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=n_bins, strategy="uniform")
    
    # ECE calculation: sum |acc(b) - conf(b)| * (|b| / N)
    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    bin_indices = np.digitize(y_prob, bin_edges) - 1
    bin_indices = np.clip(bin_indices, 0, n_bins - 1)
    
    ece = 0.0
    total_n = len(y_prob)
    for b in range(n_bins):
        in_bin = (bin_indices == b)
        n_in_bin = int(np.sum(in_bin))
        if n_in_bin > 0:
            avg_conf = float(np.mean(y_prob[in_bin]))
            avg_acc = float(np.mean(y_true[in_bin]))
            ece += (n_in_bin / total_n) * abs(avg_acc - avg_conf)
            
    # 3. Discrete Classification Metrics (at selected threshold)
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    
    precision = float(precision_score(y_true, y_pred, zero_division=0))
    recall = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    acc = float(accuracy_score(y_true, y_pred))
    specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    
    return {
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "brier_score": round(brier, 4),
        "expected_calibration_error": round(float(ece), 4),
        "decision_threshold": round(float(threshold), 4),
        "f1_score": round(f1, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "specificity": round(specificity, 4),
        "accuracy": round(acc, 4),
        "confusion_matrix": {
            "true_negative": int(tn),
            "false_positive": int(fp),
            "false_negative": int(fn),
            "true_positive": int(tp),
        },
        "calibration_curve": {
            "fraction_of_positives": [round(float(p), 4) for p in prob_true],
            "mean_predicted_value": [round(float(p), 4) for p in prob_pred],
        }
    }

def find_optimal_threshold(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    thresholds: np.ndarray = None
) -> Tuple[float, float]:
    """
    Finds optimal decision threshold on VALIDATION data to maximize F1-score.
    Never uses test data.
    """
    if thresholds is None:
        thresholds = np.linspace(0.10, 0.90, 81)
        
    best_f1 = -1.0
    best_thresh = 0.50
    
    for thresh in thresholds:
        y_pred = (y_prob >= thresh).astype(int)
        score = f1_score(y_true, y_pred, zero_division=0)
        if score > best_f1:
            best_f1 = float(score)
            best_thresh = float(thresh)
            
    return best_thresh, best_f1
