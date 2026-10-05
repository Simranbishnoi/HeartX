import pandas as pd

def validate_dataset(filepath="data/raw/heart_disease_uci.csv"):
    print("Loading dataset...")
    df = pd.read_csv(filepath)
    
    print("\n--- Dataset Shape ---")
    print(df.shape)
    
    print("\n--- First 5 Rows ---")
    print(df.head())
    
    print("\n--- Dataset Info ---")
    df.info()
    
    print("\n--- Missing Values ---")
    print(df.isnull().sum())
    
    print("\n--- Summary Statistics ---")
    print(df.describe(include="all"))
    
    print("\n--- Duplicate Rows ---")
    print("Duplicates:", df.duplicated().sum())
    
    print("\n--- Target Distribution (num) ---")
    if 'num' in df.columns:
        print(df['num'].value_counts(dropna=False))
    
    print("\nValidation complete.")

if __name__ == "__main__":
    validate_dataset()
