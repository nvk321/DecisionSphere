import numpy as np
from typing import Dict, Any, Tuple, Optional
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


def calculate_expected_calibration_error(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 10,
) -> float:
    """
    Computes Expected Calibration Error (ECE) via uniform probability binning:
    ECE = sum_{b=1}^B (N_b / N) * |acc(B_b) - conf(B_b)|
    """
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    bin_assignments = np.digitize(y_prob, bins) - 1
    bin_assignments = np.clip(bin_assignments, 0, n_bins - 1)
    
    n_total = len(y_true)
    ece = 0.0
    for b in range(n_bins):
        mask = bin_assignments == b
        n_b = np.sum(mask)
        if n_b > 0:
            acc_b = np.mean(y_true[mask])
            conf_b = np.mean(y_prob[mask])
            ece += (n_b / n_total) * abs(acc_b - conf_b)
            
    return float(ece)


def evaluate_workforce_classification(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    decision_threshold: float = 0.5,
    n_bins: int = 10,
) -> Dict[str, Any]:
    """
    Evaluates workforce attrition classification performance across discrimination,
    probability quality, and operational threshold-based classification metrics.
    
    Parameters:
    -----------
    y_true : Ground truth binary array (0 or 1).
    y_prob : Predicted attrition probabilities in [0, 1].
    decision_threshold : Operating classification threshold (default 0.50).
    n_bins : Number of bins for calibration analysis.
    
    Returns:
    --------
    Dict containing ROC-AUC, PR-AUC, Brier score, ECE, F1, Precision, Recall, Specificity,
    Accuracy, Confusion Matrix, and Calibration Curve points.
    """
    y_t = np.asarray(y_true, dtype=int)
    y_p = np.asarray(y_prob, dtype=float)
    
    # Discrimination metrics
    # Handle single-class edge case gracefully if encountered
    if len(np.unique(y_t)) > 1:
        roc_auc = float(roc_auc_score(y_t, y_p))
        pr_auc = float(average_precision_score(y_t, y_p))
    else:
        roc_auc = 0.5
        pr_auc = float(np.mean(y_t))
        
    # Probability quality metrics
    brier = float(brier_score_loss(y_t, y_p))
    ece = calculate_expected_calibration_error(y_t, y_p, n_bins=n_bins)
    
    # Calibration curve
    try:
        prob_true, prob_pred = calibration_curve(y_t, y_p, n_bins=n_bins, strategy="uniform")
        curve_dict = {
            "fraction_of_positives": [round(float(x), 4) for x in prob_true],
            "mean_predicted_value": [round(float(x), 4) for x in prob_pred],
        }
    except Exception:
        curve_dict = {"fraction_of_positives": [], "mean_predicted_value": []}
        
    # Threshold classification metrics
    y_pred = (y_p >= decision_threshold).astype(int)
    f1 = float(f1_score(y_t, y_pred, zero_division=0))
    prec = float(precision_score(y_t, y_pred, zero_division=0))
    rec = float(recall_score(y_t, y_pred, zero_division=0))
    acc = float(accuracy_score(y_t, y_pred))
    
    cm = confusion_matrix(y_t, y_pred)
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
        spec = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    else:
        tn = int(np.sum((y_t == 0) & (y_pred == 0)))
        fp = int(np.sum((y_t == 0) & (y_pred == 1)))
        fn = int(np.sum((y_t == 1) & (y_pred == 0)))
        tp = int(np.sum((y_t == 1) & (y_pred == 1)))
        spec = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
        
    return {
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "brier_score": round(brier, 4),
        "expected_calibration_error": round(ece, 4),
        "decision_threshold": round(float(decision_threshold), 4),
        "f1_score": round(f1, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "specificity": round(spec, 4),
        "accuracy": round(acc, 4),
        "confusion_matrix": {
            "true_negative": int(tn),
            "false_positive": int(fp),
            "false_negative": int(fn),
            "true_positive": int(tp),
        },
        "calibration_curve": curve_dict,
    }


def find_optimal_validation_threshold(
    y_val: np.ndarray,
    y_val_prob: np.ndarray,
    threshold_grid: Optional[np.ndarray] = None,
) -> Tuple[float, float, Dict[str, Any]]:
    """
    Selects the optimal classification decision threshold tau* strictly using Validation:
    tau* = argmax_{tau in T} F_1(y_val, y_val_prob >= tau)
    
    Also computes a separate operational recall-oriented threshold diagnostic
    (e.g., threshold achieving >= 80% recall), but clearly demarcates tau* as the formal F1-optimal threshold.
    
    Returns:
    --------
    Tuple[float, float, Dict[str, Any]]:
        optimal_threshold (tau*),
        best_f1,
        diagnostic_info
    """
    if threshold_grid is None:
        threshold_grid = np.linspace(0.05, 0.95, 91)
        
    best_f1 = -1.0
    optimal_tau = 0.50
    
    threshold_search_history = []
    recall_80_tau = None
    
    for tau in threshold_grid:
        preds = (y_val_prob >= tau).astype(int)
        score = f1_score(y_val, preds, zero_division=0)
        rec = recall_score(y_val, preds, zero_division=0)
        prec = precision_score(y_val, preds, zero_division=0)
        
        threshold_search_history.append({
            "threshold": round(float(tau), 4),
            "f1": round(float(score), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
        })
        
        if score > best_f1:
            best_f1 = score
            optimal_tau = float(tau)
            
        if rec >= 0.80 and recall_80_tau is None:
            # First threshold from top that achieves >=80% recall
            recall_80_tau = float(tau)
            
    diagnostic_info = {
        "criterion": "max_f1",
        "optimal_f1_threshold": round(optimal_tau, 4),
        "validation_f1_at_optimal_threshold": round(best_f1, 4),
        "recall_oriented_diagnostic_threshold_80pct": (
            round(recall_80_tau, 4) if recall_80_tau is not None else None
        ),
    }
    
    return float(optimal_tau), float(best_f1), diagnostic_info
