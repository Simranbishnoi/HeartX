import pandas as pd

def clean_data(filepath="data/raw/heart_disease_uci.csv", output_path="data/processed/heart_disease_clean.csv"):
    """
    Loads raw data, creates a binary target, and removes non-predictive 
    or leaky columns according to Phase 4 rules.
    """
    print(f"Loading raw data from {filepath}...")
    df = pd.read_csv(filepath)
    
    df["target"] = (df["num"] > 0).astype(int)
    
    cols_to_drop = []
    if "id" in df.columns:
        cols_to_drop.append("id")
    if "num" in df.columns:
        cols_to_drop.append("num")
        
    df_cleaned = df.drop(columns=cols_to_drop)
    
    print(f"Dropped columns: {cols_to_drop}")
    print(f"Cleaned dataset shape: {df_cleaned.shape}")

    df_cleaned.to_csv(output_path, index=False)
    print(f"Cleaned dataset successfully saved to: {output_path}")
    
    return df_cleaned

if __name__ == "__main__":
    clean_data()
