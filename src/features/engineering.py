import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class ClinicalFeatureEngineer(BaseEstimator, TransformerMixin):
    """
    Scikit-learn compatible transformer to add engineered clinical features
    without data leakage.
    """
    def __init__(self):
        pass
        
    def fit(self, X, y=None):
        # No fitting required as these are deterministic transformations
        return self
        
    def transform(self, X):
        # Create a copy so we don't modify the original dataframe in place
        X_out = X.copy()
        
        if not isinstance(X_out, pd.DataFrame):
            # If a numpy array is passed, it means we lost column names,
            # this shouldn't happen if we use this before other transformations,
            # but we assume X is a DataFrame
            raise ValueError("ClinicalFeatureEngineer requires a pandas DataFrame with column names.")
            
        # 1. Age group
        if 'age' in X_out.columns:
            X_out['age_group'] = pd.cut(
                X_out['age'],
                bins=[0, 39, 49, 59, 200],
                labels=["<40", "40-49", "50-59", "60+"]
            )
            # 2. Maximum heart-rate ratio
            # Estimated max heart rate formula: 220 - age
            if 'thalch' in X_out.columns:
                X_out['heart_rate_ratio'] = X_out['thalch'] / (220 - X_out['age'])
                
            # 5. Cholesterol-age interaction
            if 'chol' in X_out.columns:
                X_out['chol_age_interaction'] = X_out['chol'] * X_out['age']
                
        # 3. Exercise stress interaction
        if 'exang' in X_out.columns and 'oldpeak' in X_out.columns:
            # exang might be categorical or bool depending on preprocessing, convert to float for multiplication
            # Wait, if exang has missing values, they will be NaN.
            # In our pipeline, missing value imputation happens, so we should apply this after imputation
            # OR we can just fillna(0) for this specific feature if it's done before imputation.
            # Assuming exang is True/False or 1/0
            try:
                X_out['exercise_stress'] = X_out['exang'].astype(float) * X_out['oldpeak']
            except:
                pass
                
        # 4. Blood pressure category
        if 'trestbps' in X_out.columns:
            # Normal <120, Elevated 120-129, High >= 130
            conditions = [
                (X_out['trestbps'] < 120),
                (X_out['trestbps'] >= 120) & (X_out['trestbps'] < 130),
                (X_out['trestbps'] >= 130)
            ]
            choices = ['Normal', 'Elevated', 'High']
            # We use np.select to assign categories, default is missing
            X_out['bp_category'] = np.select(conditions, choices, default=np.nan)
            
        return X_out
