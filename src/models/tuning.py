import pandas as pd
import numpy as np
import optuna
import joblib
import os
import sys

# Ensure src can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import StratifiedKFold
from xgboost import XGBClassifier
from sklearn.metrics import f1_score

from src.data.preprocessing import load_and_split
from src.features.engineering import ClinicalFeatureEngineer
from src.features.selection import MutualInfoFeatureSelector
from src.evaluation.metrics import evaluate_model

def build_novelty_pipeline(xgb_params=None, k_features=10):
    """
    Builds the full pipeline including Feature Engineering, Preprocessing,
    Feature Selection, and XGBoost.
    """
    # 1. Base numeric and categorical features
    numeric_features = ["age", "trestbps", "chol", "thalch", "oldpeak", "ca"]
    categorical_features = ["sex", "dataset", "cp", "fbs", "restecg", "exang", "slope", "thal"]
    
    # 2. Add engineered features
    numeric_features.extend(["heart_rate_ratio", "chol_age_interaction", "exercise_stress"])
    categorical_features.extend(["age_group", "bp_category"])
    
    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_features),
            ("cat", categorical_pipeline, categorical_features)
        ],
        remainder='drop'
    )
    
    if xgb_params is None:
        xgb_params = {
            "n_estimators": 300,
            "max_depth": 4,
            "learning_rate": 0.05,
            "random_state": 42,
            "eval_metric": "logloss"
        }
    else:
        xgb_params["random_state"] = 42
        xgb_params["eval_metric"] = "logloss"
        
    model = XGBClassifier(**xgb_params)
    
    pipeline = Pipeline([
        ("feature_engineering", ClinicalFeatureEngineer()),
        ("preprocessing", preprocessor),
        ("feature_selection", MutualInfoFeatureSelector(k=k_features)),
        ("model", model)
    ])
    
    return pipeline

def objective(trial, X_train, y_train):
    """Optuna objective function for hyperparameter tuning."""
    # Hyperparameter search space
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 800),
        "max_depth": trial.suggest_int("max_depth", 2, 8),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
    }
    
    # We also tune the number of features to select
    k_features = trial.suggest_int("k_features", 5, 25)
    
    pipeline = build_novelty_pipeline(xgb_params=params, k_features=k_features)
    
    # Phase 19: Cross-Validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = []
    
    for train_idx, val_idx in cv.split(X_train, y_train):
        # We need to use iloc for safe indexing
        X_tr, y_tr = X_train.iloc[train_idx], y_train.iloc[train_idx]
        X_va, y_va = X_train.iloc[val_idx], y_train.iloc[val_idx]
        
        pipeline.fit(X_tr, y_tr)
        preds = pipeline.predict(X_va)
        
        # Phase 18: Metric Optimization Target is F1 Score
        score = f1_score(y_va, preds, zero_division=0)
        scores.append(score)
        
    return np.mean(scores)

def main():
    print("Loading data...")
    X_train, X_test, y_train, y_test = load_and_split()
    
    print("Starting hyperparameter tuning with Optuna (targeting F1 Score)...")
    study = optuna.create_study(direction="maximize")
    
    # Optimize using a lambda to pass X_train and y_train
    # Increased trials to find a more accurate model
    study.optimize(lambda trial: objective(trial, X_train, y_train), n_trials=50)
    
    print("\nBest hyperparameters found:")
    best_params = study.best_params
    print(best_params)
    
    # Extract k_features
    best_k = best_params.pop("k_features")
    
    print(f"\nTraining final proposed model with top {best_k} features...")
    final_pipeline = build_novelty_pipeline(xgb_params=best_params, k_features=best_k)
    final_pipeline.fit(X_train, y_train)
    
    # Phase 21: Evaluate Final Model
    y_pred = final_pipeline.predict(X_test)
    y_prob = final_pipeline.predict_proba(X_test)[:, 1]
    
    print("\n--- Final Model Evaluation ---")
    metrics = evaluate_model(y_test, y_pred, y_prob)
    metrics["Model"] = "Proposed Novelty"
    
    # Phase 22: Model Comparison
    os.makedirs("reports", exist_ok=True)
    baseline_path = "reports/model_comparison.csv"
    if os.path.exists(baseline_path):
        results_df = pd.read_csv(baseline_path, index_col=0)
        results_df.loc["Proposed Novelty"] = metrics
        results_df.to_csv(baseline_path)
        print("\nUpdated model_comparison.csv with Proposed Novelty results.")
        print(results_df)
    
    # Save the final model
    os.makedirs("models/final", exist_ok=True)
    joblib.dump(final_pipeline, "models/final/optimized_xgboost.pkl")
    print("Final model saved to models/final/optimized_xgboost.pkl")

if __name__ == "__main__":
    main()
