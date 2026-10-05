import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import joblib
import os

def load_and_split(filepath="data/processed/heart_disease_clean.csv"):
    print(f"Loading cleaned data from {filepath}...")
    df = pd.read_csv(filepath)
    X = df.drop("target", axis=1)
    y = df["target"]
    
    # Phase 5: Train/Test Split (Stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"Train set: {X_train.shape}, Test set: {X_test.shape}")
    return X_train, X_test, y_train, y_test

def build_preprocessor():
    # Phase 6: Preprocessing Pipeline Setup
    # Notice `dataset` is included in categorical if it wasn't dropped.
    numeric_features = ["age", "trestbps", "chol", "thalch", "oldpeak", "ca"]
    categorical_features = ["sex", "dataset", "cp", "fbs", "restecg", "exang", "slope", "thal"]
    
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
        remainder='drop' # Drops any column not explicitly defined here
    )
    
    return preprocessor

if __name__ == "__main__":
    print("--- Executing Phase 5: Train/Test Split ---")
    X_train, X_test, y_train, y_test = load_and_split()
    
    print("\n--- Executing Phase 6: Preprocessing Pipeline ---")
    preprocessor = build_preprocessor()
    
    # Fit the preprocessor ONLY on the training data (prevents data leakage)
    print("Fitting preprocessor on training data...")
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)
    
    print(f"Processed Train set shape: {X_train_processed.shape}")
    print(f"Processed Test set shape: {X_test_processed.shape}")
    
    # Save the fitted preprocessor for future model use
    os.makedirs("models/baseline", exist_ok=True)
    joblib.dump(preprocessor, "models/baseline/preprocessor.pkl")
    print("Fitted preprocessor successfully saved to models/baseline/preprocessor.pkl")
