import pandas as pd
import joblib
import os
import sys

# Ensure src can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.pipeline import Pipeline

from src.evaluation.metrics import evaluate_model
from src.data.preprocessing import load_and_split, build_preprocessor

def train_and_evaluate_baselines():
    print("Loading data for baselines...")
    X_train, X_test, y_train, y_test = load_and_split()
    
    # We retrieve the preprocessor from the previous step.
    # Creating pipelines ensures the preprocessor is fitted with the model cross-validation cleanly.
    preprocessor = build_preprocessor()
    
    # Define models as described in Phases 7, 8, and 9
    models = {
        "Logistic Regression": LogisticRegression(max_iter=2000, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=300, random_state=42, class_weight="balanced"),
        "XGBoost": XGBClassifier(n_estimators=300, max_depth=4, learning_rate=0.05, 
                                 subsample=0.8, colsample_bytree=0.8, random_state=42, 
                                 eval_metric="logloss")
    }
    
    results = []
    os.makedirs("models/baseline", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    for name, model in models.items():
        print(f"\n{'='*50}")
        print(f"Training Baseline: {name}")
        print(f"{'='*50}")
        
        # Build the full scikit-learn Pipeline
        clf = Pipeline([
            ("preprocessor", preprocessor),
            ("model", model)
        ])
        
        # Fit on training data
        clf.fit(X_train, y_train)
        
        # Predict on test data
        y_pred = clf.predict(X_test)
        y_prob = clf.predict_proba(X_test)[:, 1]
        
        # Evaluate model using standard evaluation function
        metrics = evaluate_model(y_test, y_pred, y_prob)
        metrics["Model"] = name
        results.append(metrics)
        
        # Save pipeline model
        filename = f"models/baseline/{name.lower().replace(' ', '_')}.pkl"
        joblib.dump(clf, filename)
        print(f"\n[*] Model Pipeline saved to {filename}")
        
    print("\n--- Summary of Baseline Models ---")
    results_df = pd.DataFrame(results).set_index("Model")
    print(results_df)
    
    # Save results
    results_df.to_csv("reports/model_comparison.csv")
    print("\n[*] Baseline metrics successfully saved to reports/model_comparison.csv")

if __name__ == "__main__":
    train_and_evaluate_baselines()
