from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

def evaluate_model(y_true, y_pred, y_prob):
    """
    Standardized evaluation function (Phase 10) to be used across all models.
    """
    results = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_true, y_prob)
    }

    print("\n--- Model Metrics ---")
    for metric, value in results.items():
        print(f"{metric.upper()}: {value:.4f}")
        
    print("\n--- Confusion Matrix ---")
    print(confusion_matrix(y_true, y_pred))
    
    print("\n--- Classification Report ---")
    print(classification_report(y_true, y_pred, zero_division=0))

    return results
