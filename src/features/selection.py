import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_selection import mutual_info_classif, SelectKBest

class MutualInfoFeatureSelector(BaseEstimator, TransformerMixin):
    """
    Selects top K features based on Mutual Information.
    Designed to work within a scikit-learn Pipeline.
    """
    def __init__(self, k=10):
        self.k = k
        self.selector = SelectKBest(score_func=mutual_info_classif, k=self.k)
        
    def fit(self, X, y):
        # We need to ensure X is numerical here since mutual_info_classif requires it.
        # This transformer should be placed AFTER categorical encoding in the pipeline.
        
        # If X is a DataFrame, we might want to keep track of feature names
        self.feature_names_in_ = None
        if hasattr(X, 'columns'):
            self.feature_names_in_ = X.columns
            
        self.selector.fit(X, y)
        return self
        
    def transform(self, X):
        X_selected = self.selector.transform(X)
        
        # Try to return a DataFrame if we have feature names, to keep things interpreitable
        if self.feature_names_in_ is not None and hasattr(self.selector, 'get_support'):
            selected_features = self.feature_names_in_[self.selector.get_support()]
            return pd.DataFrame(X_selected, columns=selected_features, index=X.index if hasattr(X, 'index') else None)
            
        return X_selected
