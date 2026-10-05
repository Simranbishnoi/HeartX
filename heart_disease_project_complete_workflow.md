# Heart Disease Prediction System --- Complete Implementation Workflow

## 0. Project Objective

### Project title

**AI-Based Database-Driven Heart Disease Prediction System using
Optimized XGBoost**

### Main objective

Build a DBMS-backed healthcare prediction system that:

1.  Stores patient/clinical information in a normalized relational
    database.
2.  Cleans and preprocesses a public Kaggle/UCI heart-disease dataset.
3.  Converts the original multiclass target into a binary heart-disease
    prediction target.
4.  Trains and evaluates:
    -   Logistic Regression
    -   Random Forest
    -   XGBoost
5.  Evaluates every model using:
    -   Accuracy
    -   Precision
    -   Recall
    -   F1-score
    -   Confusion Matrix
    -   ROC-AUC
6.  Adds a meaningful project novelty:
    -   Clinical/domain-inspired feature engineering
    -   Feature selection
    -   Hyperparameter optimization
    -   Optional decision-threshold optimization
7.  Compares baseline models against the proposed improved model.
8.  Stores patients, clinical measurements, model versions, predictions,
    and audit information in a relational database.
9.  Provides a final interface/API through which a patient record can be
    entered and a prediction can be generated and stored.

### Important project principle

Do **not** promise that accuracy, precision, recall, and F1 will all
increase simultaneously. Machine-learning metrics can trade off against
one another.

The project should instead demonstrate that the proposed method gives a
**better overall and defensible validation/test performance** than the
baseline models.

------------------------------------------------------------------------

# 1. Dataset Information

The uploaded dataset is:

`heart_disease_uci.csv`

Dataset shape:

-   Rows: 920
-   Columns: 16

Columns:

  -------------------------------------------------------------------------
  Column            Type               Meaning            ML Usage
  ----------------- ------------------ ------------------ -----------------
  `id`              integer            Record identifier  Do not use as
                                                          predictive
                                                          feature

  `age`             integer            Age                Feature

  `sex`             categorical        Male/Female        Feature

  `dataset`         categorical        Source dataset     Special handling;
                                                          do not blindly
                                                          use

  `cp`              categorical        Chest pain type    Feature

  `trestbps`        numeric            Resting blood      Feature
                                       pressure           

  `chol`            numeric            Cholesterol        Feature

  `fbs`             categorical/bool   Fasting blood      Feature
                                       sugar              

  `restecg`         categorical        Resting ECG result Feature

  `thalch`          numeric            Maximum heart rate Feature
                                       achieved           

  `exang`           categorical/bool   Exercise-induced   Feature
                                       angina             

  `oldpeak`         numeric            ST depression      Feature

  `slope`           categorical        ST segment slope   Feature

  `ca`              numeric            Number of major    Feature
                                       vessels            

  `thal`            categorical        Thalassemia result Feature

  `num`             integer            Original disease   Convert to binary
                                       target             target
  -------------------------------------------------------------------------

Observed target distribution:

-   `num = 0`: 411
-   `num = 1`: 265
-   `num = 2`: 109
-   `num = 3`: 107
-   `num = 4`: 28

Therefore, for the main binary prediction task:

``` text
num = 0  ->  0 = No Heart Disease
num > 0  -> 1 = Heart Disease
```

Create:

``` python
df["target"] = (df["num"] > 0).astype(int)
```

After creating `target`, do not use `num` as an input feature because it
directly contains the original diagnosis.

------------------------------------------------------------------------

# 2. Important Dataset Missing-Value Situation

The dataset contains missing values.

Observed missing counts:

  Column         Missing
  ------------ ---------
  `trestbps`          59
  `chol`              30
  `fbs`               90
  `restecg`            2
  `thalch`            55
  `exang`             55
  `oldpeak`           62
  `slope`            309
  `ca`               611
  `thal`             486

This is important.

## Do NOT simply run:

``` python
df.dropna()
```

because a large amount of data would be lost, especially because `ca`,
`thal`, and `slope` contain many missing values.

Use a preprocessing pipeline.

------------------------------------------------------------------------

# 3. Complete Project Architecture

``` text
                         ┌──────────────────────┐
                         │ Kaggle/UCI Dataset   │
                         │ 920 × 16             │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Data Validation       │
                         │ Schema / Duplicates   │
                         │ Missing values        │
                         │ Invalid values        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Data Cleaning         │
                         │ Missing-value         │
                         │ imputation            │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Target Transformation│
                         │ num=0 -> 0            │
                         │ num>0 -> 1            │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Train/Test Split      │
                         │ Stratified            │
                         └──────────┬───────────┘
                                    │
                                    ▼
                    ┌────────────────────────────────┐
                    │ Preprocessing Pipeline          │
                    │ Numeric imputation/scaling      │
                    │ Categorical imputation/encoding │
                    └────────────────┬───────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
             ┌────────────┐   ┌────────────┐   ┌────────────┐
             │ Logistic   │   │ Random     │   │ XGBoost    │
             │ Regression │   │ Forest     │   │ Baseline   │
             └─────┬──────┘   └─────┬──────┘   └─────┬──────┘
                   │                │                │
                   └────────────────┼────────────────┘
                                    ▼
                         ┌──────────────────────┐
                         │ Baseline Evaluation │
                         │ Accuracy             │
                         │ Precision            │
                         │ Recall               │
                         │ F1                   │
                         │ Confusion Matrix     │
                         │ ROC-AUC              │
                         └──────────┬───────────┘
                                    │
                                    ▼
              ╔══════════════════════════════════════════╗
              ║              PROPOSED NOVELTY            ║
              ║                                          ║
              ║ Clinical Feature Engineering             ║
              ║              ↓                           ║
              ║ Feature Selection                        ║
              ║              ↓                           ║
              ║ Hyperparameter Optimization              ║
              ║              ↓                           ║
              ║ Optimized XGBoost                        ║
              ║              ↓                           ║
              ║ Optional Threshold Optimization          ║
              ╚════════════════════╤═════════════════════╝
                                   │
                                   ▼
                         ┌──────────────────────┐
                         │ Final Model          │
                         │ Optimized XGBoost    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Final Evaluation     │
                         │ Accuracy             │
                         │ Precision            │
                         │ Recall               │
                         │ F1                   │
                         │ Confusion Matrix     │
                         │ ROC-AUC              │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Prediction API/UI    │
                         │ Disease probability  │
                         │ Risk classification  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ PostgreSQL DB        │
                         │ Patient              │
                         │ Clinical data        │
                         │ Predictions          │
                         │ Model metadata       │
                         │ Audit logs           │
                         └──────────────────────┘
```

------------------------------------------------------------------------

# 4. Recommended Project Folder Structure

Use a structure that separates data, ML, backend, database, and
experiments.

``` text
heart-disease-prediction/
│
├── README.md
├── requirements.txt
├── .env
├── .gitignore
│
├── data/
│   ├── raw/
│   │   └── heart_disease_uci.csv
│   └── processed/
│       └── heart_disease_clean.csv
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_baseline_models.ipynb
│   ├── 04_feature_engineering.ipynb
│   ├── 05_feature_selection.ipynb
│   ├── 06_xgboost_tuning.ipynb
│   └── 07_final_evaluation.ipynb
│
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── cleaning.py
│   │   └── preprocessing.py
│   │
│   ├── features/
│   │   ├── engineering.py
│   │   └── selection.py
│   │
│   ├── models/
│   │   ├── logistic.py
│   │   ├── random_forest.py
│   │   ├── xgboost_model.py
│   │   └── tuning.py
│   │
│   ├── evaluation/
│   │   └── metrics.py
│   │
│   └── prediction/
│       └── predict.py
│
├── models/
│   ├── baseline/
│   └── final/
│
├── database/
│   ├── schema.sql
│   ├── views.sql
│   ├── procedures.sql
│   ├── seed.sql
│   └── audit.sql
│
├── backend/
│   ├── main.py
│   ├── routes/
│   │   ├── patients.py
│   │   └── predictions.py
│   ├── models/
│   ├── schemas/
│   └── services/
│
├── reports/
│   ├── figures/
│   ├── model_comparison.csv
│   └── final_results.csv
│
└── tests/
    ├── test_cleaning.py
    ├── test_prediction.py
    └── test_database.py
```

------------------------------------------------------------------------

# 5. Phase 1 --- Environment Setup

## Install required packages

``` bash
pip install pandas numpy scikit-learn xgboost matplotlib seaborn
pip install sqlalchemy psycopg2-binary python-dotenv joblib
pip install fastapi uvicorn
```

Optional:

``` bash
pip install optuna
```

if Optuna is used for hyperparameter optimization.

Freeze dependencies:

``` bash
pip freeze > requirements.txt
```

------------------------------------------------------------------------

# 6. Phase 2 --- Load and Validate Dataset

First load the raw dataset.

``` python
import pandas as pd

df = pd.read_csv("data/raw/heart_disease_uci.csv")

print(df.shape)
print(df.head())
print(df.info())
print(df.isnull().sum())
print(df.describe(include="all"))
```

Expected shape:

``` text
(920, 16)
```

## Validation checklist

Check:

-   Number of rows
-   Number of columns
-   Column names
-   Data types
-   Missing values
-   Duplicate rows
-   Target distribution
-   Unique values in categorical columns
-   Impossible numerical values

Do not modify the raw file.

Always keep:

``` text
data/raw/
```

unchanged.

------------------------------------------------------------------------

# 7. Phase 3 --- Exploratory Data Analysis

Before cleaning, understand the data.

## Check target

``` python
df["num"].value_counts().sort_index()
```

Then binary target:

``` python
df["target"] = (df["num"] > 0).astype(int)

print(df["target"].value_counts())
print(df["target"].value_counts(normalize=True))
```

## Check categorical values

``` python
for col in df.select_dtypes(include="object").columns:
    print(col)
    print(df[col].value_counts(dropna=False))
```

## Check numerical distributions

Plot:

-   age
-   trestbps
-   chol
-   thalch
-   oldpeak
-   ca

## Check class balance

Use a bar chart.

## Check correlations

Only use correlation appropriately for numerical/encoded variables. Do
not treat arbitrary category labels as continuous numerical
measurements.

------------------------------------------------------------------------

# 8. Phase 4 --- Data Cleaning

## 8.1 Remove identifier from ML features

Remove:

``` python
id
```

Do not use an arbitrary record ID as a predictor.

The ID may still be retained in the database for record identification.

------------------------------------------------------------------------

## 8.2 Remove original target from X

After:

``` python
df["target"] = (df["num"] > 0).astype(int)
```

the ML feature matrix must not contain:

``` text
num
```

because that is target leakage.

------------------------------------------------------------------------

## 8.3 Handle missing values correctly

Recommended approach:

### Numerical features

Use median imputation.

``` text
trestbps
chol
thalch
oldpeak
ca
```

### Categorical features

Use most-frequent imputation or an explicit `"Missing"` category.

``` text
fbs
restecg
exang
slope
thal
```

Do this using a scikit-learn Pipeline/ColumnTransformer rather than
calculating statistics manually on the complete dataset.

This prevents train/test leakage.

------------------------------------------------------------------------

# 9. Phase 5 --- Train/Test Split

Use a stratified split.

Recommended:

``` python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)
```

Why stratify?

Because the proportion of:

``` text
No Disease
Disease
```

should remain approximately similar in train and test sets.

## Critical rule

Do not:

``` text
Impute entire dataset
↓
Scale entire dataset
↓
Select features using entire dataset
↓
Split train/test
```

That leaks information from the test set.

Correct:

``` text
Raw data
↓
Split train/test
↓
Fit preprocessing only on training data
↓
Transform train and test
↓
Train model only on train
↓
Evaluate once on test
```

------------------------------------------------------------------------

# 10. Phase 6 --- Preprocessing Pipeline

Categorical columns:

``` text
sex
dataset (if retained)
cp
fbs
restecg
exang
slope
thal
```

Numerical columns:

``` text
age
trestbps
chol
thalch
oldpeak
ca
```

A robust approach:

``` python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer([
    ("num", numeric_pipeline, numeric_features),
    ("cat", categorical_pipeline, categorical_features)
])
```

## Important

Do not scale categorical variables before one-hot encoding.

Do not fit the preprocessor on test data.

------------------------------------------------------------------------

# 11. Phase 7 --- Baseline Model 1: Logistic Regression

Purpose:

-   Baseline linear model
-   Easy to interpret
-   Provides a comparison point

Example:

``` python
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

logistic_model = Pipeline([
    ("preprocessor", preprocessor),
    ("model", LogisticRegression(
        max_iter=2000,
        random_state=42
    ))
])

logistic_model.fit(X_train, y_train)

y_pred = logistic_model.predict(X_test)
y_prob = logistic_model.predict_proba(X_test)[:, 1]
```

Evaluate using the common evaluation function.

------------------------------------------------------------------------

# 12. Phase 8 --- Baseline Model 2: Random Forest

``` python
from sklearn.ensemble import RandomForestClassifier

rf_model = Pipeline([
    ("preprocessor", preprocessor),
    ("model", RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced"
    ))
])

rf_model.fit(X_train, y_train)

y_pred_rf = rf_model.predict(X_test)
y_prob_rf = rf_model.predict_proba(X_test)[:, 1]
```

Do not assume these parameters are optimal.

They are baseline parameters only.

------------------------------------------------------------------------

# 13. Phase 9 --- Baseline Model 3: XGBoost

Use XGBoost as a major baseline.

Example:

``` python
from xgboost import XGBClassifier

xgb_model = Pipeline([
    ("preprocessor", preprocessor),
    ("model", XGBClassifier(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="logloss"
    ))
])

xgb_model.fit(X_train, y_train)

y_pred_xgb = xgb_model.predict(X_test)
y_prob_xgb = xgb_model.predict_proba(X_test)[:, 1]
```

Again, these are baseline/tentative parameters.

Final parameters must be selected using validation/CV, not by repeatedly
changing them based on the final test set.

------------------------------------------------------------------------

# 14. Phase 10 --- Evaluation Function

Every model must be evaluated using the exact same metrics.

``` python
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
    results = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_true, y_prob)
    }

    print(results)
    print("Confusion Matrix:")
    print(confusion_matrix(y_true, y_pred))
    print(classification_report(y_true, y_pred, zero_division=0))

    return results
```

------------------------------------------------------------------------

# 15. Phase 11 --- Required Metrics

## Accuracy

Overall percentage of correct predictions.

``` text
(TP + TN) / (TP + TN + FP + FN)
```

## Precision

Of the patients predicted as positive, how many were actually positive?

``` text
TP / (TP + FP)
```

## Recall

Of the patients who actually have disease, how many did the model
detect?

``` text
TP / (TP + FN)
```

## F1-score

Balances precision and recall.

``` text
2 × Precision × Recall / (Precision + Recall)
```

## Confusion Matrix

``` text
                 Predicted
                0       1

Actual 0       TN      FP
Actual 1       FN      TP
```

## ROC-AUC

Measures ranking/discrimination ability across classification
thresholds.

------------------------------------------------------------------------

# 16. Phase 12 --- Save Baseline Results

Create one comparison table.

Example:

  -----------------------------------------------------------------------------
  Model            Accuracy    Precision       Recall           F1      ROC-AUC
  ------------ ------------ ------------ ------------ ------------ ------------
  Logistic           actual       actual       actual       actual       actual
  Regression         result       result       result       result       result

  Random             actual       actual       actual       actual       actual
  Forest             result       result       result       result       result

  XGBoost            actual       actual       actual       actual       actual
                     result       result       result       result       result
  -----------------------------------------------------------------------------

Do not manually type values.

Generate this table programmatically and save:

``` text
reports/model_comparison.csv
```

------------------------------------------------------------------------

# 17. Phase 13 --- Novelty Design

## Proposed novelty

### Hybrid Feature-Engineered and Feature-Selected Optimized XGBoost

The novelty has four stages:

``` text
Raw clinical features
        ↓
Clinical feature engineering
        ↓
Feature selection
        ↓
Hyperparameter optimization
        ↓
Optimized XGBoost
        ↓
Optional threshold optimization
```

The novelty should be tested experimentally.

Do not claim improvement until it is measured.

------------------------------------------------------------------------

# 18. Phase 14 --- Novelty Part 1: Feature Engineering

Create clinically meaningful derived features.

Possible examples:

### 18.1 Age group

``` python
df["age_group"] = pd.cut(
    df["age"],
    bins=[0, 39, 49, 59, 200],
    labels=["<40", "40-49", "50-59", "60+"]
)
```

Do not blindly add every engineered feature. Keep only features that are
justified and validated.

------------------------------------------------------------------------

### 18.2 Maximum heart-rate ratio

Create an age-related expected maximum heart-rate estimate and derive:

``` text
heart_rate_ratio =
observed_max_heart_rate / estimated_max_heart_rate
```

Document the formula used in the report.

This is an engineered modeling feature, not a medical diagnostic rule.

------------------------------------------------------------------------

### 18.3 Exercise stress interaction

``` text
exercise_stress = exang × oldpeak
```

The purpose is to capture an interaction between exercise-induced angina
and ST depression.

------------------------------------------------------------------------

### 18.4 Blood pressure category

Create categories such as:

``` text
Normal
Elevated
High
```

Use a clearly documented clinical convention if this feature is
included.

Do not present the category itself as a medical diagnosis.

------------------------------------------------------------------------

### 18.5 Cholesterol-age interaction

Potential feature:

``` text
chol_age_interaction = chol × age
```

or another justified normalized relationship.

------------------------------------------------------------------------

## Important feature-engineering rule

Do not create dozens of arbitrary features.

Use a small number of explainable features, then test whether they
actually improve cross-validation/test performance.

------------------------------------------------------------------------

# 19. Phase 15 --- Novelty Part 2: Feature Selection

The teacher's requirements explicitly mention feature selection.

Possible methods:

1.  Mutual Information
2.  Chi-Square
3.  Recursive Feature Elimination
4.  Model-based feature importance
5.  PCA
6.  Genetic Algorithm

For this project, a practical primary choice is:

``` text
Mutual Information
        ↓
Select top-k features
        ↓
XGBoost
```

Why?

-   Easy to explain
-   Appropriate for feature-selection experiments
-   Does not require a complicated optimization algorithm
-   Easy to compare with the all-feature model

Optional advanced experiment:

``` text
Genetic Algorithm
        ↓
Feature subset
        ↓
XGBoost
```

Do not add Genetic Algorithm merely to make the project sound advanced.
Use it only if you can implement and evaluate it correctly.

------------------------------------------------------------------------

# 20. Phase 16 --- Feature Selection Must Avoid Leakage

Wrong:

``` text
Entire dataset
↓
Calculate feature importance
↓
Select features
↓
Train/test split
```

Correct:

``` text
Train/test split
↓
Feature selection fitted on training data
↓
Selected features applied to train/test
↓
Model training
↓
Final test evaluation
```

For rigorous implementation, put feature selection inside a Pipeline/CV
workflow.

------------------------------------------------------------------------

# 21. Phase 17 --- Novelty Part 3: Hyperparameter Optimization

Tune XGBoost instead of using default parameters.

Parameters worth tuning:

``` text
n_estimators
max_depth
learning_rate
subsample
colsample_bytree
min_child_weight
gamma
reg_alpha
reg_lambda
```

Example search space:

``` text
n_estimators: 100–800
max_depth: 2–8
learning_rate: 0.01–0.2
subsample: 0.6–1.0
colsample_bytree: 0.6–1.0
min_child_weight: 1–10
```

Do not blindly search every possible combination.

Use:

-   RandomizedSearchCV
-   GridSearchCV for a small grid
-   Optuna for an advanced implementation

------------------------------------------------------------------------

# 22. Phase 18 --- What Metric Should Optimization Target?

Do not automatically optimize accuracy.

For a healthcare screening-oriented system, consider:

``` text
F1
```

or:

``` text
Recall
```

or:

``` text
ROC-AUC
```

depending on the project objective.

Recommended academic approach:

``` text
Primary tuning objective:
F1 or ROC-AUC

Secondary reported metrics:
Accuracy
Precision
Recall
F1
ROC-AUC
Confusion Matrix
```

Explain the choice.

If minimizing false negatives is the priority, recall deserves special
attention.

------------------------------------------------------------------------

# 23. Phase 19 --- Cross-Validation

Use stratified cross-validation.

Example:

``` python
from sklearn.model_selection import StratifiedKFold

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)
```

Use cross-validation for:

-   hyperparameter selection
-   feature-selection evaluation
-   comparing candidate approaches

The final test set must remain untouched until final evaluation.

------------------------------------------------------------------------

# 24. Phase 20 --- Threshold Optimization

Normally:

``` text
probability >= 0.50
    ↓
Disease
```

But 0.50 is not a law.

You can evaluate thresholds such as:

``` text
0.30
0.35
0.40
0.45
0.50
0.55
0.60
```

Use validation/CV predictions to choose a threshold.

Then freeze that threshold.

Finally evaluate once on the untouched test set.

------------------------------------------------------------------------

# 25. Important Threshold Warning

Do NOT do:

``` text
Try threshold 0.30 on test set
↓
Check metrics
↓
Try 0.35 on test set
↓
Try 0.40 on test set
↓
Choose whichever gives best result
```

This is test-set overfitting.

Correct:

``` text
Training data
↓
Cross-validation
↓
Select threshold
↓
Freeze threshold
↓
Final test evaluation
```

------------------------------------------------------------------------

# 26. Phase 21 --- Final Proposed Model

The final model can be:

``` text
Input
 ↓
Cleaning
 ↓
Preprocessing
 ↓
Clinical Feature Engineering
 ↓
Feature Selection
 ↓
Optimized XGBoost
 ↓
Probability
 ↓
Frozen Classification Threshold
 ↓
Prediction
```

This becomes the project's main contribution.

------------------------------------------------------------------------

# 27. Phase 22 --- Final Model Comparison

Final report table:

  --------------------------------------------------------------------------------------
  Model                     Accuracy    Precision       Recall           F1      ROC-AUC
  --------------------- ------------ ------------ ------------ ------------ ------------
  Logistic Regression         actual       actual       actual       actual       actual

  Random Forest               actual       actual       actual       actual       actual

  Baseline XGBoost            actual       actual       actual       actual       actual

  Proposed                    actual       actual       actual       actual       actual
  Feature-Engineered                                                        
  XGBoost                                                                   

  Proposed Selected +         actual       actual       actual       actual       actual
  Tuned XGBoost                                                             

  Final                       actual       actual       actual       actual       actual
  Threshold-Optimized                                                       
  Model                                                                     
  --------------------------------------------------------------------------------------

This table is one of the most important tables in the project.

------------------------------------------------------------------------

# 28. Phase 23 --- Improvement Calculation

For each metric:

``` text
Improvement =
Final Model Metric - Baseline Model Metric
```

Percentage improvement:

``` text
((Final - Baseline) / Baseline) × 100
```

Example:

If baseline accuracy = 0.87 and final accuracy = 0.90:

``` text
absolute improvement = 0.03 = 3 percentage points
```

Do not confuse:

``` text
3 percentage points
```

with:

``` text
3% relative improvement
```

Report both correctly if needed.

------------------------------------------------------------------------

# 29. Phase 24 --- Expected Performance Range

For this dataset, a reasonable project target is approximately:

``` text
Baseline models:
~84–89% accuracy

Strong tuned/engineered model:
~87–91% accuracy

Recall:
~89–94% may be achievable depending on split,
preprocessing, model, and threshold.

Precision:
~87–92% may be achievable.

F1:
~88–92% may be achievable.

ROC-AUC:
~92–96% may be achievable.
```

These are target ranges, NOT guaranteed results.

The actual values depend on:

-   random split
-   preprocessing
-   feature engineering
-   selected features
-   model parameters
-   threshold
-   cross-validation strategy

Never manufacture results to fit the target range.

------------------------------------------------------------------------

# 30. Phase 25 --- Confusion Matrix Analysis

For the final model, show:

``` text
                 Predicted
                 No   Disease

Actual No        TN     FP
Actual Disease  FN     TP
```

Explain:

### True Negative

Healthy patient correctly predicted as healthy.

### True Positive

Patient with disease correctly detected.

### False Positive

Healthy patient incorrectly predicted as having disease.

### False Negative

Patient with disease incorrectly predicted as healthy.

For a healthcare screening system, false negatives deserve special
attention.

------------------------------------------------------------------------

# 31. Phase 26 --- ROC Curve

Plot ROC curves for:

-   Logistic Regression
-   Random Forest
-   XGBoost
-   Proposed model

Use:

``` text
False Positive Rate
vs
True Positive Rate
```

Add AUC values to the legend.

------------------------------------------------------------------------

# 32. Phase 27 --- Precision-Recall Curve

Because the project is about disease prediction, also consider a
Precision-Recall curve.

Plot:

``` text
Precision
vs
Recall
```

This gives another view of the classification trade-off.

------------------------------------------------------------------------

# 33. Phase 28 --- Feature Importance / Explainability

For the final XGBoost model, show important features.

Possible methods:

-   XGBoost feature importance
-   Permutation importance
-   SHAP

Recommended advanced addition:

``` text
SHAP
```

Use it if your implementation remains manageable.

Show:

``` text
Feature
Importance
Direction/effect where appropriate
```

Do not claim that feature importance proves medical causation.

It only shows model behavior/association.

------------------------------------------------------------------------

# 34. Phase 29 --- DBMS Design

The ML model alone is not enough because this is a DBMS project.

Design the relational database.

Recommended entities:

``` text
Patient
ClinicalMeasurements
Symptoms/ClinicalTests
Model
Prediction
User/Doctor
AuditLog
```

------------------------------------------------------------------------

# 35. Phase 30 --- ER Model

Basic relationships:

``` text
PATIENT
   │
   ├───────────────< CLINICAL_MEASUREMENTS
   │
   ├───────────────< CLINICAL_TESTS
   │
   └───────────────< PREDICTIONS
                         │
                         └──── MODEL
```

And:

``` text
USER/DOCTOR
    │
    └───────────────< AUDIT_LOG
```

Document:

-   entities
-   attributes
-   primary keys
-   foreign keys
-   cardinality
-   relationships

------------------------------------------------------------------------

# 36. Phase 31 --- Normalized Database Schema

Example:

## PATIENT

``` sql
CREATE TABLE patient (
    patient_id SERIAL PRIMARY KEY,
    age INT NOT NULL,
    sex VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## CLINICAL_MEASUREMENTS

``` sql
CREATE TABLE clinical_measurements (
    measurement_id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patient(patient_id),
    trestbps NUMERIC,
    chol NUMERIC,
    thalch NUMERIC,
    oldpeak NUMERIC,
    ca NUMERIC
);
```

## CLINICAL_TESTS

``` sql
CREATE TABLE clinical_tests (
    test_id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patient(patient_id),
    fbs BOOLEAN,
    restecg VARCHAR(50),
    exang BOOLEAN,
    slope VARCHAR(50),
    thal VARCHAR(50)
);
```

## PREDICTIONS

``` sql
CREATE TABLE predictions (
    prediction_id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patient(patient_id),
    model_id INT NOT NULL,
    probability NUMERIC,
    prediction INT,
    risk_level VARCHAR(30),
    prediction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## MODEL

``` sql
CREATE TABLE model (
    model_id SERIAL PRIMARY KEY,
    model_name VARCHAR(100),
    version VARCHAR(50),
    accuracy NUMERIC,
    precision_score NUMERIC,
    recall_score NUMERIC,
    f1_score NUMERIC,
    roc_auc NUMERIC,
    trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## AUDIT_LOG

``` sql
CREATE TABLE audit_log (
    log_id SERIAL PRIMARY KEY,
    user_id INT,
    action VARCHAR(100),
    table_name VARCHAR(100),
    record_id INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Adapt types and constraints to your final design.

------------------------------------------------------------------------

# 37. Phase 32 --- Why Normalization Is Needed

Avoid storing:

``` text
patient_id
age
sex
blood_pressure
cholesterol
prediction
doctor_name
doctor_phone
model_accuracy
```

all in one giant table.

Instead separate entities.

Target at least:

``` text
1NF
2NF
3NF
```

Explain:

-   1NF: atomic values
-   2NF: no partial dependency on part of a composite key
-   3NF: no transitive dependency

If your teacher expects BCNF, discuss whether each relation satisfies
BCNF and identify candidate keys/dependencies where appropriate.

------------------------------------------------------------------------

# 38. Phase 33 --- SQL Requirements

Demonstrate:

### INSERT

Store a patient.

### SELECT

Retrieve patient history.

### UPDATE

Update clinical information.

### DELETE

Remove a test record where appropriate.

### JOIN

Join patient + clinical data + predictions.

### GROUP BY

Example:

``` sql
SELECT risk_level, COUNT(*)
FROM predictions
GROUP BY risk_level;
```

### ORDER BY

Show highest-risk patients.

### WHERE

Filter patients.

### Aggregate functions

Use:

``` text
COUNT
AVG
MIN
MAX
```

------------------------------------------------------------------------

# 39. Phase 34 --- Database Views

Create useful views.

Example:

``` sql
CREATE VIEW patient_prediction_view AS
SELECT
    p.patient_id,
    p.age,
    p.sex,
    pr.prediction,
    pr.probability,
    pr.risk_level,
    pr.prediction_time
FROM patient p
JOIN predictions pr
    ON p.patient_id = pr.patient_id;
```

Use this view in the application/reporting layer.

------------------------------------------------------------------------

# 40. Phase 35 --- Stored Procedure / Function

Create a database function for an appropriate DBMS task.

For example:

``` text
Register patient
Retrieve latest prediction
Generate patient summary
```

Keep ML inference in the application/ML layer unless there is a specific
reason to move it into the database.

The database should store and manage structured data; Python should
execute the ML model.

------------------------------------------------------------------------

# 41. Phase 36 --- Transactions

Show a transaction for prediction storage.

Conceptually:

``` text
BEGIN
    Insert/update patient data
    Insert clinical measurements
    Insert prediction
    Insert audit log
COMMIT
```

If something fails:

``` text
ROLLBACK
```

This demonstrates a real DBMS transaction rather than simply storing
data independently.

------------------------------------------------------------------------

# 42. Phase 37 --- Access Control

Create roles such as:

``` text
admin
doctor
analyst
```

Example permissions:

``` text
admin:
    full database access

doctor:
    read patient data
    create predictions
    read prediction history

analyst:
    access anonymized/statistical data
```

Do not expose unnecessary patient information to every role.

------------------------------------------------------------------------

# 43. Phase 38 --- Audit Logging

Record actions such as:

``` text
LOGIN
PATIENT_CREATED
PATIENT_UPDATED
PREDICTION_CREATED
PREDICTION_VIEWED
```

Store:

``` text
user
action
table
record
timestamp
```

This directly satisfies the teacher's audit-log requirement.

------------------------------------------------------------------------

# 44. Phase 39 --- ML + Database Integration

Final application flow:

``` text
User enters patient information
             ↓
Backend validates input
             ↓
Store patient information
             ↓
Retrieve required ML features
             ↓
Apply same preprocessing pipeline
             ↓
Feature engineering
             ↓
Feature selection
             ↓
Load trained model
             ↓
Generate probability
             ↓
Apply frozen threshold
             ↓
Generate prediction/risk level
             ↓
Store prediction in PostgreSQL
             ↓
Create audit log
             ↓
Return result to UI
```

------------------------------------------------------------------------

# 45. Phase 40 --- Never Refit During Prediction

This is a critical implementation rule.

When the application receives a new patient:

``` text
DO NOT:
fit imputer
fit scaler
fit encoder
fit feature selector
fit model
```

during prediction.

Instead:

``` text
Training:
fit everything
↓
save complete pipeline/model

Prediction:
load saved pipeline/model
↓
transform new patient
↓
predict
```

------------------------------------------------------------------------

# 46. Phase 41 --- Save the Model

Use `joblib` for a scikit-learn-compatible pipeline.

Example:

``` python
import joblib

joblib.dump(final_pipeline, "models/final/heart_model.joblib")
```

If threshold is separate:

``` python
joblib.dump(
    {
        "model": final_pipeline,
        "threshold": selected_threshold
    },
    "models/final/heart_model_bundle.joblib"
)
```

Also save:

-   model version
-   training date
-   preprocessing configuration
-   selected features
-   metrics

------------------------------------------------------------------------

# 47. Phase 42 --- Backend/API

Recommended endpoints:

``` text
POST /patients
GET  /patients/{patient_id}

POST /predict/{patient_id}
GET  /predictions/{patient_id}

GET /models
GET /health
```

Example:

``` text
POST /predict/{patient_id}
```

Flow:

``` text
patient_id
   ↓
fetch patient data
   ↓
construct ML input
   ↓
load model
   ↓
predict
   ↓
store result
   ↓
return prediction
```

------------------------------------------------------------------------

# 48. Phase 43 --- Risk Classification

The ML model should first produce a probability.

Example:

``` text
P(heart disease) = 0.82
```

Then apply the frozen classification threshold.

For example, if threshold = 0.50:

``` text
0.82 >= 0.50
       ↓
Disease predicted
```

If you implement multiple risk levels, define them explicitly and make
clear that these are **project-defined model output categories**, not
clinical diagnoses.

For example:

``` text
Low
Moderate
High
```

based on probability bands selected for the project.

Do not present these categories as medically validated clinical risk
scores.

------------------------------------------------------------------------

# 49. Phase 44 --- Frontend/UI

The UI should contain:

## Patient input

``` text
Age
Sex
Chest Pain
Resting BP
Cholesterol
Fasting Blood Sugar
Resting ECG
Maximum Heart Rate
Exercise Angina
Oldpeak
Slope
CA
Thal
```

## Prediction result

``` text
Patient ID: P102

Probability: 82%

Prediction:
Heart Disease Detected

Risk Category:
High
```

## Historical results

Show:

``` text
Date
Model
Probability
Prediction
Risk
```

------------------------------------------------------------------------

# 50. Phase 45 --- Testing

Testing should be divided into four levels.

## A. Data tests

Check:

``` text
No unexpected columns
No impossible target values
Missing values handled
Correct target transformation
```

## B. ML tests

Check:

``` text
Prediction is 0/1
Probability is between 0 and 1
Same input gives consistent prediction
Model file loads
```

## C. Database tests

Check:

``` text
Foreign keys
Primary keys
Constraints
Transactions
Rollback
Views
Queries
```

## D. API tests

Test:

``` text
Valid patient
Missing field
Invalid field
Unknown patient ID
Prediction endpoint
Database failure
```

------------------------------------------------------------------------

# 51. Phase 46 --- Leakage Checklist

Before finalizing results, verify all of these:

-   `num` is not in X.
-   `target` is not in X.
-   `id` is not used as a feature.
-   Imputation is fitted only on training data.
-   Scaling is fitted only on training data.
-   Encoding is fitted only on training data.
-   Feature selection is fitted only on training data.
-   Hyperparameter tuning does not use the final test set.
-   Threshold selection does not use the final test set.
-   Oversampling, if used, happens only inside training/CV folds.
-   Test set is evaluated only after the complete pipeline is frozen.

------------------------------------------------------------------------

# 52. Phase 47 --- Handling Class Imbalance

The binary target is not perfectly balanced.

Options:

### Option A

Use:

``` text
class_weight="balanced"
```

for models that support it.

### Option B

Use SMOTE.

But if SMOTE is used:

``` text
SMOTE must happen only on training data
```

or inside an imbalanced-learn Pipeline during cross-validation.

Never:

``` text
SMOTE entire dataset
↓
train/test split
```

because this can cause leakage.

For this dataset, first establish a clean baseline without SMOTE. Add
SMOTE only as an experimental comparison if it provides a justified
improvement.

------------------------------------------------------------------------

# 53. Phase 48 --- Reproducibility

Set random seeds.

Example:

``` python
RANDOM_STATE = 42
```

Use it consistently for:

-   train/test split
-   Random Forest
-   XGBoost
-   CV
-   random search

Record:

``` text
dataset version
random seed
test size
CV folds
model parameters
feature list
threshold
metrics
```

This allows the same experiment to be reproduced.

------------------------------------------------------------------------

# 54. Phase 49 --- Recommended Experiment Table

Keep an experiment log.

  ---------------------------------------------------------------------------------------------------------------------
  Experiment   Features     Selection   Model      Tuning   Threshold     Accuracy   Precision   Recall      F1     AUC
  ------------ ------------ ----------- ---------- -------- ----------- ---------- ----------- -------- ------- -------
  E1           Raw          No          Logistic   No       0.5                                                 

  E2           Raw          No          RF         No       0.5                                                 

  E3           Raw          No          XGB        No       0.5                                                 

  E4           Engineered   No          XGB        No       0.5                                                 

  E5           Engineered   Yes         XGB        No       0.5                                                 

  E6           Engineered   Yes         XGB        Yes      0.5                                                 

  E7           Engineered   Yes         XGB        Yes      optimized                                           
  ---------------------------------------------------------------------------------------------------------------------

This table proves that your novelty was experimentally evaluated rather
than added only for presentation.

------------------------------------------------------------------------

# 55. Phase 50 --- Final Research Question

Use a clear research question:

> **Can clinically informed feature engineering, feature selection, and
> hyperparameter optimization improve heart-disease prediction
> performance over conventional Logistic Regression, Random Forest, and
> baseline XGBoost models while maintaining a database-driven and
> reproducible prediction workflow?**

This is much stronger than:

> "Can we get high accuracy?"

------------------------------------------------------------------------

# 56. Phase 51 --- Final Project Workflow

The complete implementation is:

``` text
PHASE 1
Environment Setup
        ↓
PHASE 2
Dataset Loading + Validation
        ↓
PHASE 3
Exploratory Data Analysis
        ↓
PHASE 4
Data Cleaning
        ↓
PHASE 5
Target Transformation
        ↓
PHASE 6
Train/Test Split
        ↓
PHASE 7
Preprocessing Pipeline
        ↓
PHASE 8
Logistic Regression
        ↓
PHASE 9
Random Forest
        ↓
PHASE 10
Baseline XGBoost
        ↓
PHASE 11
Baseline Evaluation
        ↓
PHASE 12
Clinical Feature Engineering
        ↓
PHASE 13
Feature Selection
        ↓
PHASE 14
Hyperparameter Optimization
        ↓
PHASE 15
Cross-Validation
        ↓
PHASE 16
Threshold Optimization
        ↓
PHASE 17
Final Optimized XGBoost
        ↓
PHASE 18
Final Evaluation
        ↓
PHASE 19
Explainability
        ↓
PHASE 20
PostgreSQL Database Design
        ↓
PHASE 21
ER Model + Normalization
        ↓
PHASE 22
SQL + Views
        ↓
PHASE 23
Stored Procedures/Functions
        ↓
PHASE 24
Transactions
        ↓
PHASE 25
Access Control
        ↓
PHASE 26
Audit Logging
        ↓
PHASE 27
ML + Database Integration
        ↓
PHASE 28
Backend/API
        ↓
PHASE 29
Frontend/UI
        ↓
PHASE 30
Testing
        ↓
PHASE 31
Final Report + Presentation
```

------------------------------------------------------------------------

# 57. Phase 52 --- Final Deliverables

Your final repository should contain:

``` text
1. Raw dataset
2. Cleaned dataset
3. EDA notebook
4. Cleaning/preprocessing code
5. Logistic Regression model
6. Random Forest model
7. XGBoost baseline
8. Feature-engineering implementation
9. Feature-selection implementation
10. Hyperparameter tuning implementation
11. Final optimized model
12. Saved model pipeline
13. Evaluation metrics
14. Confusion matrices
15. ROC curves
16. Precision-Recall curve
17. Feature importance/SHAP plots
18. Model comparison table
19. ER diagram
20. Relational schema
21. SQL scripts
22. Views
23. Stored procedures/functions
24. Transaction demonstration
25. Access-control design
26. Audit-log implementation
27. Backend/API
28. Frontend
29. Unit/API/database tests
30. README
31. Final project report
32. Presentation
```

------------------------------------------------------------------------

# 58. Phase 53 --- Recommended Report Chapter Structure

## Chapter 1 --- Introduction

-   Problem statement
-   Motivation
-   Objectives
-   Scope

## Chapter 2 --- Dataset

-   Dataset source
-   Features
-   Target
-   Missing values
-   Dataset statistics

## Chapter 3 --- DBMS Design

-   ER model
-   Relational schema
-   Normalization
-   Keys
-   Relationships

## Chapter 4 --- Data Preprocessing

-   Missing values
-   Encoding
-   Scaling
-   Target transformation
-   Train/test split

## Chapter 5 --- Machine Learning Models

-   Logistic Regression
-   Random Forest
-   XGBoost

## Chapter 6 --- Proposed Novelty

-   Feature engineering
-   Feature selection
-   Hyperparameter optimization
-   Threshold optimization

## Chapter 7 --- Evaluation

-   Accuracy
-   Precision
-   Recall
-   F1
-   Confusion Matrix
-   ROC-AUC
-   PR-AUC if included

## Chapter 8 --- Database Integration

-   SQL
-   Views
-   Transactions
-   Stored procedures/functions
-   Access control
-   Audit logs

## Chapter 9 --- System Implementation

-   Backend
-   API
-   Frontend
-   Prediction workflow

## Chapter 10 --- Results

-   Baseline comparison
-   Proposed model comparison
-   Improvement analysis
-   Explainability

## Chapter 11 --- Limitations

Mention:

-   Public dataset
-   Relatively small dataset
-   Dataset-source differences
-   Missing clinical information
-   Not clinically validated
-   Not a replacement for professional diagnosis

## Chapter 12 --- Future Work

Possible extensions:

-   Larger multi-center datasets
-   External validation
-   Calibration
-   Explainable AI
-   Continuous monitoring
-   More diseases
-   Doctor dashboard
-   Model drift monitoring

------------------------------------------------------------------------

# 59. Critical Errors to Avoid

## Error 1 --- Target leakage

Never use:

``` text
num
```

as an input feature after creating:

``` text
target = num > 0
```

------------------------------------------------------------------------

## Error 2 --- Data leakage during preprocessing

Never fit:

``` text
imputer
scaler
encoder
feature selector
```

on the complete dataset before splitting.

------------------------------------------------------------------------

## Error 3 --- Test-set tuning

Never repeatedly tune the model using test-set performance.

------------------------------------------------------------------------

## Error 4 --- SMOTE leakage

Never apply SMOTE before train/test splitting.

------------------------------------------------------------------------

## Error 5 --- ID as a feature

Do not use `id`.

------------------------------------------------------------------------

## Error 6 --- Blindly dropping missing rows

Do not use:

``` python
df.dropna()
```

as the main strategy.

------------------------------------------------------------------------

## Error 7 --- Claiming guaranteed metric improvement

Do not write:

> "Our novelty increases accuracy, precision, and recall."

until the experiment proves it.

Write:

> "The proposed approach was evaluated against the baseline models to
> determine whether it improves predictive performance."

------------------------------------------------------------------------

## Error 8 --- Treating model probability as a clinical diagnosis

The output is a machine-learning prediction based on a public dataset.

It is not a medically validated diagnosis.

------------------------------------------------------------------------

## Error 9 --- Different preprocessing for different models

Keep preprocessing consistent when comparing models unless the model
specifically requires a different treatment.

Otherwise the comparison becomes difficult to interpret.

------------------------------------------------------------------------

## Error 10 --- Re-training during API prediction

The API should load the already-trained model.

It must not train the model every time a patient submits the form.

------------------------------------------------------------------------

# 60. Final One-Line Architecture for Presentation

Use this on your PPT:

``` text
Kaggle Heart Dataset
→ Data Cleaning
→ Preprocessing
→ Stratified Split
→ Logistic Regression / Random Forest / XGBoost
→ Baseline Evaluation
→ Feature Engineering
→ Feature Selection
→ Hyperparameter Optimization
→ Optimized XGBoost
→ Threshold Optimization
→ Final Evaluation
→ PostgreSQL Storage
→ API
→ Heart Disease Risk Prediction
```

------------------------------------------------------------------------

# 61. Final Project Architecture

``` text
                    ┌───────────────────────────┐
                    │      PUBLIC DATASET       │
                    │      Heart Disease        │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │      DATA PIPELINE        │
                    │ Validation                 │
                    │ Cleaning                   │
                    │ Imputation                 │
                    │ Encoding                  │
                    │ Scaling                   │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │       BASE MODELS         │
                    │ Logistic Regression       │
                    │ Random Forest             │
                    │ XGBoost                   │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │     MODEL EVALUATION      │
                    │ Accuracy                  │
                    │ Precision                 │
                    │ Recall                    │
                    │ F1                        │
                    │ Confusion Matrix          │
                    │ ROC-AUC                   │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ╔═══════════════════════════╗
                    ║      PROJECT NOVELTY      ║
                    ║                           ║
                    ║ Feature Engineering       ║
                    ║ Feature Selection         ║
                    ║ Hyperparameter Tuning     ║
                    ║ Threshold Optimization    ║
                    ╚═════════════╤═════════════╝
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │     FINAL XGBOOST         │
                    │      MODEL PIPELINE       │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │      PREDICTION API       │
                    │ Probability + Risk        │
                    └─────────────┬─────────────┘
                                  │
                     ┌────────────┴────────────┐
                     ▼                         ▼
          ┌─────────────────────┐   ┌─────────────────────┐
          │    POSTGRESQL DB    │   │    FRONTEND/UI      │
          │                     │   │                     │
          │ Patients            │   │ Patient Input       │
          │ Clinical Data       │   │ Prediction           │
          │ Models              │   │ Probability          │
          │ Predictions         │   │ History              │
          │ Audit Logs          │   │ Dashboard            │
          └─────────────────────┘   └─────────────────────┘
```

------------------------------------------------------------------------

# 62. Final Success Criteria

The project is complete when all of the following are true:

### ML

-   [ ] Dataset cleaned
-   [ ] Missing values handled
-   [ ] Target converted correctly
-   [ ] No target leakage
-   [ ] Stratified train/test split
-   [ ] Preprocessing pipeline implemented
-   [ ] Logistic Regression trained
-   [ ] Random Forest trained
-   [ ] XGBoost trained
-   [ ] Accuracy calculated
-   [ ] Precision calculated
-   [ ] Recall calculated
-   [ ] F1 calculated
-   [ ] Confusion matrices generated
-   [ ] ROC-AUC calculated
-   [ ] Baseline comparison completed
-   [ ] Feature engineering implemented
-   [ ] Feature selection implemented
-   [ ] Hyperparameter tuning implemented
-   [ ] Cross-validation performed
-   [ ] Final model selected using validation/CV
-   [ ] Threshold selected without using final test labels
-   [ ] Final test evaluation performed
-   [ ] Feature importance/explainability generated

### DBMS

-   [ ] ER diagram
-   [ ] Relational schema
-   [ ] Primary keys
-   [ ] Foreign keys
-   [ ] 1NF/2NF/3NF discussion
-   [ ] SQL CRUD
-   [ ] Joins
-   [ ] Aggregations
-   [ ] Views
-   [ ] Stored procedure/function
-   [ ] Transactions
-   [ ] Rollback demonstration
-   [ ] Access control
-   [ ] Audit logs

### Application

-   [ ] Saved ML model
-   [ ] Backend/API
-   [ ] Patient registration/input
-   [ ] Prediction endpoint
-   [ ] Prediction stored in database
-   [ ] Prediction history
-   [ ] Frontend/dashboard
-   [ ] Error handling
-   [ ] Unit tests
-   [ ] API tests
-   [ ] Database tests

### Documentation

-   [ ] README
-   [ ] Architecture diagram
-   [ ] ER diagram
-   [ ] Model comparison table
-   [ ] Confusion matrices
-   [ ] ROC curves
-   [ ] Feature importance
-   [ ] Novelty explanation
-   [ ] Limitations
-   [ ] Future work
-   [ ] Final report
-   [ ] Presentation

------------------------------------------------------------------------

# 63. The Most Important Implementation Order

Do not start by building the frontend or database.

Follow this exact order:

``` text
1. Inspect CSV
        ↓
2. Clean + validate data
        ↓
3. Create binary target
        ↓
4. Build leakage-safe preprocessing
        ↓
5. Train Logistic Regression
        ↓
6. Train Random Forest
        ↓
7. Train baseline XGBoost
        ↓
8. Generate all baseline metrics
        ↓
9. Build feature engineering
        ↓
10. Add feature selection
        ↓
11. Tune XGBoost using CV
        ↓
12. Select threshold using validation/CV
        ↓
13. Freeze final pipeline
        ↓
14. Evaluate once on test set
        ↓
15. Save model + metrics
        ↓
16. Design ER model
        ↓
17. Create normalized PostgreSQL schema
        ↓
18. Add SQL/views/procedures/transactions/audit
        ↓
19. Integrate ML with database
        ↓
20. Build API
        ↓
21. Build UI
        ↓
22. Test complete system
        ↓
23. Prepare report + PPT
```

**This order prevents the most common mistakes and keeps the ML
experiment scientifically valid while also satisfying the DBMS
requirements.**
