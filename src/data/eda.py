import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_eda(filepath="data/raw/heart_disease_uci.csv", output_dir="reports/figures"):
    print("Running Exploratory Data Analysis...")
    df = pd.read_csv(filepath)
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n--- Target Distribution (Original) ---")
    print(df["num"].value_counts().sort_index())
    
    df["target"] = (df["num"] > 0).astype(int)
    print("\n--- Target Distribution (Binary) ---")
    print(df["target"].value_counts())
    print("\n--- Target Distribution (Normalized) ---")
    print(df["target"].value_counts(normalize=True))
    
    print("\n--- Categorical Values ---")
    for col in df.select_dtypes(include=["object", "category"]).columns:
        print(f"\nColumn: {col}")
        print(df[col].value_counts(dropna=False))
       
    print(f"\nGenerating and saving plots to {output_dir}/ ...")
    numeric_cols = ["age", "trestbps", "chol", "thalch", "oldpeak", "ca"]
    
    for col in numeric_cols:
        if col in df.columns:
            plt.figure(figsize=(8, 4))
            sns.histplot(df[col].dropna(), kde=True, bins=30)
            plt.title(f"Distribution of {col}")
            plt.savefig(os.path.join(output_dir, f"dist_{col}.png"))
            plt.close()
            
    plt.figure(figsize=(6, 4))
    sns.countplot(data=df, x="target")
    plt.title("Class Balance (Binary Target)")
    plt.savefig(os.path.join(output_dir, "class_balance.png"))
    plt.close()
    
    print("\n--- Correlation Matrix with Target ---")
    num_df = df.select_dtypes(include=['int64', 'float64'])
    corr = num_df.corr()
    print(corr["target"].sort_values(ascending=False))
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", cbar=True)
    plt.title("Correlation Matrix")
    plt.savefig(os.path.join(output_dir, "correlation_matrix.png"))
    plt.close()
    
    print("\nEDA complete. Plots have been saved successfully.")

if __name__ == "__main__":
    run_eda()
