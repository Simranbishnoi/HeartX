
# Heart Disease Prediction System — Complete End-to-End Implementation

## 0. Scope

The ML workflow from the previous project document is already substantially completed. The remaining work is:

1. Final ML analysis:
   - baseline vs novelty comparison
   - percentage improvement
   - ROC curve
   - Precision-Recall curve
   - SHAP explainability
2. PostgreSQL database
3. FastAPI backend
4. ML ↔ backend integration
5. React frontend
6. Prediction history
7. DBMS requirements:
   - ER model
   - normalization
   - SQL
   - transactions
   - views
   - stored functions/procedures
   - access control
   - audit logs
8. End-to-end testing and final demo

> **Educational project:** predictions are model outputs for the project dataset and must not be presented as medical diagnoses.

---

# 1. Final Architecture

```text
                         ┌──────────────────────────┐
                         │       React Frontend     │
                         │ Login / Dashboard        │
                         │ Patient Form             │
                         │ Prediction Result        │
                         │ Prediction History       │
                         └────────────┬─────────────┘
                                      │ REST/JSON
                                      ▼
                         ┌──────────────────────────┐
                         │       FastAPI Backend    │
                         │ Auth / Validation        │
                         │ Patient APIs             │
                         │ Prediction API           │
                         │ DB operations             │
                         │ ML prediction service     │
                         │ Audit logging              │
                         └───────┬──────────┬───────┘
                                 │          │
                         SQLAlchemy          │ loads
                                 │          ▼
                                 │   ┌─────────────────┐
                                 │   │ Saved ML Model  │
                                 │   │ preprocessing   │
                                 │   │ XGBoost         │
                                 │   │ threshold       │
                                 │   └─────────────────┘
                                 ▼
                         ┌──────────────────────────┐
                         │       PostgreSQL         │
                         │ users                    │
                         │ patients                 │
                         │ clinical_records         │
                         │ model_registry            │
                         │ predictions              │
                         │ audit_logs               │
                         └──────────────────────────┘
```

The key separation is:

```text
Kaggle CSV → training/development only
PostgreSQL → runtime application data
Saved pipeline → runtime ML inference
FastAPI → bridge between PostgreSQL, ML and frontend
```

The frontend must never connect directly to PostgreSQL.

---

# 2. Recommended Stack

| Layer | Technology |
|---|---|
| ML | Python, pandas, scikit-learn, XGBoost, SHAP |
| Model persistence | joblib |
| Backend | FastAPI + Uvicorn |
| ORM | SQLAlchemy |
| Database | PostgreSQL |
| Frontend | React + Vite |
| API | REST/JSON |
| Authentication | JWT |
| DB driver | psycopg2-binary |
| Containerization | Docker Compose |

---

# 3. Final Project Structure

```text
heart-disease-project/
│
├── ml/
│   ├── data/
│   │   └── heart_disease_uci.csv
│   ├── notebooks/
│   │   ├── 01_eda_cleaning.ipynb
│   │   ├── 02_baseline_models.ipynb
│   │   ├── 03_novelty.ipynb
│   │   ├── 04_tuning.ipynb
│   │   ├── 05_threshold_analysis.ipynb
│   │   ├── 06_validation.ipynb
│   │   └── 07_final_evaluation.ipynb
│   ├── src/
│   │   ├── preprocessing.py
│   │   ├── feature_engineering.py
│   │   ├── feature_selection.py
│   │   ├── train.py
│   │   └── evaluate.py
│   └── models/
│       ├── heart_pipeline.joblib
│       ├── model_metadata.json
│       └── feature_schema.json
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── database/
│   │   │   └── connection.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── patient.py
│   │   │   ├── clinical.py
│   │   │   ├── model_registry.py
│   │   │   ├── prediction.py
│   │   │   └── audit.py
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── patient.py
│   │   │   └── prediction.py
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── patients.py
│   │   │   ├── predictions.py
│   │   │   └── dashboard.py
│   │   └── services/
│   │       ├── prediction_service.py
│   │       └── audit_service.py
│   ├── requirements.txt
│   └── .env
│
├── database/
│   ├── schema.sql
│   ├── views.sql
│   ├── functions.sql
│   ├── roles.sql
│   └── seed.sql
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── PatientForm.jsx
│   │   │   ├── PredictionResult.jsx
│   │   │   └── PredictionHistory.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── .env
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

# 4. Phase 1 — Freeze the ML Contract

Before connecting the application, freeze the exact input schema expected by the final model.

Typical UCI-style fields are:

```text
age
sex
cp
trestbps
chol
fbs
restecg
thalch
exang
oldpeak
slope
ca
thal
```

Your actual CSV must be checked before finalizing these names.

Create:

`ml/models/feature_schema.json`

```json
{
  "features": [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalch",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal"
  ],
  "target": "heart_disease",
  "threshold": 0.50,
  "model": "optimized_xgboost"
}
```

Replace the threshold and feature list with the values from your actual final pipeline.

## Critical rule

The backend must use the **same preprocessing pipeline used during training**.

Best design:

```text
raw frontend values
      ↓
saved preprocessing + encoder/scaler
      ↓
saved XGBoost
      ↓
probability
```

Do not manually reproduce encoding/scaling in FastAPI if the training pipeline already contains those transformations.

---

# 5. Phase 2 — Final ML Analysis

Create:

`ml/notebooks/07_final_evaluation.ipynb`

## 5.1 Final comparison

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | ... | ... | ... | ... | ... |
| Random Forest | ... | ... | ... | ... | ... |
| XGBoost | ... | ... | ... | ... | ... |
| Novel/Optimized XGBoost | ... | ... | ... | ... | ... |

Use the same held-out test set and evaluation protocol.

## 5.2 Percentage improvement

```python
def improvement(baseline, novel):
    return ((novel - baseline) / baseline) * 100
```

Calculate separately for:

```text
accuracy
precision
recall
F1
ROC-AUC
```

Do not claim improvement unless the measured value actually improved.

## 5.3 ROC curve

```python
from sklearn.metrics import roc_curve, roc_auc_score
import matplotlib.pyplot as plt

probabilities = model.predict_proba(X_test)[:, 1]

fpr, tpr, _ = roc_curve(y_test, probabilities)
auc = roc_auc_score(y_test, probabilities)

plt.figure(figsize=(7, 5))
plt.plot(fpr, tpr, label=f"ROC-AUC={auc:.3f}")
plt.plot([0, 1], [0, 1], linestyle="--")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve")
plt.legend()
plt.show()
```

## 5.4 Precision-Recall curve

```python
from sklearn.metrics import precision_recall_curve, average_precision_score

precision, recall, _ = precision_recall_curve(
    y_test,
    probabilities
)

ap = average_precision_score(y_test, probabilities)

plt.figure(figsize=(7, 5))
plt.plot(recall, precision, label=f"AP={ap:.3f}")
plt.xlabel("Recall")
plt.ylabel("Precision")
plt.title("Precision-Recall Curve")
plt.legend()
plt.show()
```

## 5.5 SHAP

```python
import shap

explainer = shap.TreeExplainer(final_model)
shap_values = explainer.shap_values(X_test)

shap.summary_plot(shap_values, X_test)
```

Interpret the result as model contribution, not medical causation.

Good wording:

> Age contributed strongly to the model's predictions in this dataset.

Avoid:

> Age causes heart disease.

---

# 6. Phase 3 — Database Design

## Entities

```text
USER
PATIENT
CLINICAL_RECORD
MODEL_REGISTRY
PREDICTION
AUDIT_LOG
```

## Relationships

```text
USER 1 ─────── N PATIENT
PATIENT 1 ──── N CLINICAL_RECORD
PATIENT 1 ──── N PREDICTION
MODEL 1 ─────── N PREDICTION
USER 1 ──────── N AUDIT_LOG
PATIENT 1 ───── N AUDIT_LOG
```

## Why prediction is a separate table

A patient can have multiple predictions over time:

```text
P001
 ├── Prediction 1
 ├── Prediction 2
 └── Prediction 3
```

This gives you prediction history.

---

# 7. Phase 4 — PostgreSQL Schema

Create:

`database/schema.sql`

```sql
CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role VARCHAR(30) NOT NULL
        CHECK (role IN ('ADMIN', 'DOCTOR', 'ANALYST')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE patients (
    patient_id BIGSERIAL PRIMARY KEY,
    patient_code VARCHAR(30) NOT NULL UNIQUE,
    age INTEGER NOT NULL CHECK (age >= 0 AND age <= 120),
    sex VARCHAR(20) NOT NULL,
    created_by BIGINT REFERENCES users(user_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE clinical_records (
    clinical_id BIGSERIAL PRIMARY KEY,
    patient_id BIGINT NOT NULL REFERENCES patients(patient_id)
        ON DELETE CASCADE,

    cp VARCHAR(50),
    trestbps NUMERIC(6,2),
    chol NUMERIC(7,2),
    fbs BOOLEAN,
    restecg VARCHAR(50),
    thalch NUMERIC(6,2),
    exang BOOLEAN,
    oldpeak NUMERIC(6,3),
    slope VARCHAR(30),
    ca INTEGER,
    thal VARCHAR(50),

    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE model_registry (
    model_id BIGSERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    accuracy NUMERIC(6,5),
    precision_score NUMERIC(6,5),
    recall_score NUMERIC(6,5),
    f1_score NUMERIC(6,5),
    roc_auc NUMERIC(6,5),
    threshold NUMERIC(6,5),
    model_path TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(model_name, version)
);

CREATE TABLE predictions (
    prediction_id BIGSERIAL PRIMARY KEY,
    patient_id BIGINT NOT NULL REFERENCES patients(patient_id)
        ON DELETE CASCADE,
    clinical_id BIGINT REFERENCES clinical_records(clinical_id),
    model_id BIGINT REFERENCES model_registry(model_id),

    probability NUMERIC(8,6) NOT NULL
        CHECK (probability >= 0 AND probability <= 1),

    predicted_class INTEGER NOT NULL
        CHECK (predicted_class IN (0, 1)),

    risk_level VARCHAR(30) NOT NULL
        CHECK (risk_level IN ('LOW', 'MODERATE', 'HIGH')),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit_logs (
    audit_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    patient_id BIGINT REFERENCES patients(patient_id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100),
    entity_id BIGINT,
    details JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_predictions_patient
ON predictions(patient_id);

CREATE INDEX idx_predictions_created
ON predictions(created_at);

CREATE INDEX idx_clinical_patient
ON clinical_records(patient_id);

CREATE INDEX idx_audit_patient
ON audit_logs(patient_id);
```

---

# 8. Phase 5 — Normalization

## 1NF

Fields are atomic.

Do not store:

```text
"140/90"
```

as one field if the application needs separate blood-pressure components.

## 2NF

Non-key attributes depend on the complete key.

## 3NF

Non-key attributes should not depend on another non-key attribute.

For example, model metrics belong in `model_registry`, not repeated in every prediction.

The final separation:

```text
patients
clinical_records
model_registry
predictions
users
audit_logs
```

is much better than one giant table.

---

# 9. Phase 6 — Database Views

Create:

`database/views.sql`

```sql
CREATE OR REPLACE VIEW patient_prediction_history AS
SELECT
    p.patient_code,
    p.age,
    p.sex,
    pr.prediction_id,
    pr.probability,
    pr.predicted_class,
    pr.risk_level,
    mr.model_name,
    mr.version,
    pr.created_at
FROM patients p
JOIN predictions pr
    ON p.patient_id = pr.patient_id
LEFT JOIN model_registry mr
    ON pr.model_id = mr.model_id;
```

Dashboard summary:

```sql
CREATE OR REPLACE VIEW prediction_summary AS
SELECT
    risk_level,
    COUNT(*) AS prediction_count,
    AVG(probability) AS average_probability
FROM predictions
GROUP BY risk_level;
```

This directly demonstrates the DBMS **Views** requirement.

---

# 10. Phase 7 — Stored Function

Create:

`database/functions.sql`

```sql
CREATE OR REPLACE FUNCTION get_patient_prediction_history(
    p_patient_id BIGINT
)
RETURNS TABLE (
    prediction_id BIGINT,
    probability NUMERIC,
    predicted_class INTEGER,
    risk_level VARCHAR,
    created_at TIMESTAMPTZ
)
LANGUAGE SQL
AS $$
    SELECT
        prediction_id,
        probability,
        predicted_class,
        risk_level,
        created_at
    FROM predictions
    WHERE patient_id = p_patient_id
    ORDER BY created_at DESC;
$$;
```

This demonstrates a stored database function.

---

# 11. Phase 8 — Database Access Control

Create:

`database/roles.sql`

```sql
CREATE ROLE heart_app LOGIN PASSWORD 'CHANGE_THIS_PASSWORD';

GRANT CONNECT ON DATABASE heartdb TO heart_app;
GRANT USAGE ON SCHEMA public TO heart_app;

GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA public
TO heart_app;

GRANT USAGE, SELECT
ON ALL SEQUENCES IN SCHEMA public
TO heart_app;
```

Use a real password in local configuration, but never commit it.

Application-level roles:

```text
ADMIN
DOCTOR
ANALYST
```

can then be enforced by FastAPI.

---

# 12. Phase 9 — Backend Setup

```bash
cd backend

python -m venv venv

# Windows CMD
venv\Scripts\activate

pip install fastapi uvicorn sqlalchemy psycopg2-binary \
pydantic-settings python-dotenv python-jose[cryptography] \
passlib[bcrypt] python-multipart joblib pandas numpy \
scikit-learn xgboost
```

If SHAP is only used in notebooks, it does not have to be a runtime backend dependency.

---

# 13. Phase 10 — Backend Environment

`backend/.env`

```env
DATABASE_URL=postgresql+psycopg2://heart_app:YOUR_PASSWORD@localhost:5432/heartdb

SECRET_KEY=CHANGE_TO_A_LONG_RANDOM_SECRET
ALGORITHM=HS256

MODEL_PATH=../ml/models/heart_pipeline.joblib
MODEL_METADATA_PATH=../ml/models/model_metadata.json
```

Never commit `.env`.

`.gitignore`:

```text
.env
venv/
__pycache__/
*.pyc
node_modules/
```

---

# 14. Phase 11 — FastAPI Configuration

`backend/app/core/config.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    MODEL_PATH: str
    MODEL_METADATA_PATH: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
```

---

# 15. Phase 12 — Database Connection

`backend/app/database/connection.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

# 16. Phase 13 — SQLAlchemy Models

Create ORM models corresponding exactly to:

```text
users
patients
clinical_records
model_registry
predictions
audit_logs
```

Example:

`backend/app/models/patient.py`

```python
from datetime import datetime

from sqlalchemy import BigInteger, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class Patient(Base):
    __tablename__ = "patients"

    patient_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    patient_code: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False
    )

    age: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    sex: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.user_id")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )

    clinical_records = relationship(
        "ClinicalRecord",
        back_populates="patient"
    )

    predictions = relationship(
        "Prediction",
        back_populates="patient"
    )
```

Repeat the same pattern for the other tables.

---

# 17. Phase 14 — Pydantic Schemas

`backend/app/schemas/patient.py`

```python
from pydantic import BaseModel, Field


class ClinicalDataCreate(BaseModel):
    cp: str | None = None
    trestbps: float | None = Field(default=None, ge=0)
    chol: float | None = Field(default=None, ge=0)
    fbs: bool | None = None
    restecg: str | None = None
    thalch: float | None = Field(default=None, ge=0)
    exang: bool | None = None
    oldpeak: float | None = None
    slope: str | None = None
    ca: int | None = Field(default=None, ge=0)
    thal: str | None = None


class PatientCreate(BaseModel):
    patient_code: str
    age: int = Field(ge=0, le=120)
    sex: str
    clinical: ClinicalDataCreate
```

Use schemas to validate input before database/model operations.

---

# 18. Phase 15 — ML Prediction Service

`backend/app/services/prediction_service.py`

```python
import json
import joblib
import pandas as pd

from app.core.config import settings


model = joblib.load(settings.MODEL_PATH)

with open(settings.MODEL_METADATA_PATH, "r") as f:
    metadata = json.load(f)

THRESHOLD = metadata["threshold"]
FEATURES = metadata["features"]


def predict(clinical_data: dict):

    row = {
        feature: clinical_data.get(feature)
        for feature in FEATURES
    }

    X = pd.DataFrame([row])

    probability = float(
        model.predict_proba(X)[0][1]
    )

    predicted_class = int(
        probability >= THRESHOLD
    )

    if probability < 0.40:
        risk_level = "LOW"
    elif probability < 0.70:
        risk_level = "MODERATE"
    else:
        risk_level = "HIGH"

    return {
        "probability": probability,
        "predicted_class": predicted_class,
        "risk_level": risk_level
    }
```

### Important

The probability/risk thresholds are project-defined output categories, not clinical standards. Use thresholds justified by your validation work.

---

# 19. Phase 16 — Patient API

`backend/app/routes/patients.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.patient import PatientCreate
from app.models.patient import Patient
from app.models.clinical import ClinicalRecord

router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


@router.post("")
def create_patient(
    payload: PatientCreate,
    db: Session = Depends(get_db)
):

    patient = Patient(
        patient_code=payload.patient_code,
        age=payload.age,
        sex=payload.sex
    )

    db.add(patient)
    db.flush()

    clinical = ClinicalRecord(
        patient_id=patient.patient_id,
        **payload.clinical.model_dump()
    )

    db.add(clinical)

    try:
        db.commit()
        db.refresh(patient)
    except Exception:
        db.rollback()
        raise

    return {
        "patient_id": patient.patient_id,
        "patient_code": patient.patient_code
    }
```

---

# 20. Phase 17 — Prediction Endpoint

The prediction workflow is:

```text
patient_id
   ↓
query PostgreSQL
   ↓
get patient + latest clinical record
   ↓
construct model input
   ↓
saved preprocessing/model
   ↓
probability
   ↓
class + risk
   ↓
insert prediction
   ↓
insert audit
   ↓
commit
   ↓
JSON response
```

Core implementation:

```python
@router.post("/patients/{patient_id}/predict")
def create_prediction(
    patient_id: int,
    db: Session = Depends(get_db)
):

    patient = (
        db.query(Patient)
        .filter(Patient.patient_id == patient_id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    clinical = (
        db.query(ClinicalRecord)
        .filter(
            ClinicalRecord.patient_id == patient_id
        )
        .order_by(ClinicalRecord.recorded_at.desc())
        .first()
    )

    if not clinical:
        raise HTTPException(
            status_code=400,
            detail="No clinical data found"
        )

    clinical_data = {
        "age": patient.age,
        "sex": patient.sex,
        "cp": clinical.cp,
        "trestbps": clinical.trestbps,
        "chol": clinical.chol,
        "fbs": clinical.fbs,
        "restecg": clinical.restecg,
        "thalch": clinical.thalch,
        "exang": clinical.exang,
        "oldpeak": clinical.oldpeak,
        "slope": clinical.slope,
        "ca": clinical.ca,
        "thal": clinical.thal
    }

    result = predict(clinical_data)

    # Get active model from model_registry in the real implementation.
    prediction = Prediction(
        patient_id=patient_id,
        clinical_id=clinical.clinical_id,
        model_id=active_model_id,
        probability=result["probability"],
        predicted_class=result["predicted_class"],
        risk_level=result["risk_level"]
    )

    db.add(prediction)

    try:
        db.commit()
        db.refresh(prediction)
    except Exception:
        db.rollback()
        raise

    return {
        "patient_id": patient_id,
        **result,
        "prediction_id": prediction.prediction_id
    }
```

The actual code must import the required models and retrieve `active_model_id` from the database rather than hard-code it.

---

# 21. Phase 18 — Model Registry

After final training, insert the final model's actual metrics.

```sql
INSERT INTO model_registry (
    model_name,
    version,
    accuracy,
    precision_score,
    recall_score,
    f1_score,
    roc_auc,
    threshold,
    model_path,
    is_active
)
VALUES (
    'Optimized XGBoost',
    '1.0',
    0.00000,
    0.00000,
    0.00000,
    0.00000,
    0.00000,
    0.50000,
    '../ml/models/heart_pipeline.joblib',
    TRUE
);
```

Replace every `0.00000` with your actual final values.

The prediction table records which model produced each prediction.

---

# 22. Phase 19 — Audit Logging

Important events:

```text
PATIENT_CREATED
CLINICAL_RECORD_CREATED
PREDICTION_CREATED
PATIENT_UPDATED
LOGIN
```

Example:

```python
audit = AuditLog(
    user_id=current_user.user_id,
    patient_id=patient_id,
    action="PREDICTION_CREATED",
    entity_type="prediction",
    entity_id=prediction.prediction_id,
    details={
        "risk_level": result["risk_level"],
        "probability": result["probability"]
    }
)

db.add(audit)
```

Do not create duplicate audit records by simultaneously using application logging and a database trigger for the same event unless that is intentional.

---

# 23. Phase 20 — FastAPI Main App

`backend/app/main.py`

```python
from fastapi import FastAPI

from app.routes import patients, predictions

app = FastAPI(
    title="Heart Disease Prediction API",
    version="1.0.0"
)

app.include_router(patients.router)
app.include_router(predictions.router)


@app.get("/")
def root():
    return {
        "message": "Heart Disease Prediction Backend is running"
    }
```

Run:

```bash
cd backend
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Test the backend with Swagger **before** building the frontend.

---

# 24. Phase 21 — API Contract

The frontend communicates only with FastAPI.

```text
POST   /auth/login

POST   /patients
GET    /patients
GET    /patients/{id}
PUT    /patients/{id}

POST   /patients/{id}/clinical
GET    /patients/{id}/clinical

POST   /patients/{id}/predict
GET    /patients/{id}/predictions

GET    /dashboard/summary

GET    /models
GET    /models/active
```

Keep the API focused; you do not need dozens of endpoints.

---

# 25. Phase 22 — React Frontend

Create:

```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm run dev
```

Pages:

```text
Login
Dashboard
Patient Form
Prediction Result
Prediction History
```

---

# 26. Phase 23 — Frontend API Client

`frontend/src/services/api.js`

```javascript
const API_BASE = "http://127.0.0.1:8000";

export async function createPatient(patientData) {
    const response = await fetch(`${API_BASE}/patients`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(patientData)
    });

    if (!response.ok) {
        throw new Error("Failed to create patient");
    }

    return response.json();
}


export async function predictPatient(patientId) {
    const response = await fetch(
        `${API_BASE}/patients/${patientId}/predict`,
        {
            method: "POST"
        }
    );

    if (!response.ok) {
        const error = await response.json();
        throw new Error(
            error.detail || "Prediction failed"
        );
    }

    return response.json();
}


export async function getPredictionHistory(patientId) {
    const response = await fetch(
        `${API_BASE}/patients/${patientId}/predictions`
    );

    if (!response.ok) {
        throw new Error("Failed to load prediction history");
    }

    return response.json();
}
```

Later, when JWT is implemented, add the authorization header to every protected request.

---

# 27. Phase 24 — Patient Form

The form must map exactly to the backend schema.

Example:

```jsx
import { useState } from "react";
import { createPatient } from "../services/api";

function PatientForm() {

    const [form, setForm] = useState({
        patient_code: "",
        age: "",
        sex: "",
        clinical: {
            cp: "",
            trestbps: "",
            chol: "",
            fbs: false,
            restecg: "",
            thalch: "",
            exang: false,
            oldpeak: "",
            slope: "",
            ca: "",
            thal: ""
        }
    });

    const submit = async (e) => {
        e.preventDefault();

        try {
            const result = await createPatient(form);
            console.log(result);
            alert("Patient created successfully");
        } catch (error) {
            alert(error.message);
        }
    };

    return (
        <form onSubmit={submit}>
            <input
                placeholder="Patient Code"
                value={form.patient_code}
                onChange={e =>
                    setForm({
                        ...form,
                        patient_code: e.target.value
                    })
                }
            />

            <input
                type="number"
                placeholder="Age"
                value={form.age}
                onChange={e =>
                    setForm({
                        ...form,
                        age: Number(e.target.value)
                    })
                }
            />

            {/* Add the remaining fields */}

            <button type="submit">
                Save Patient
            </button>
        </form>
    );
}

export default PatientForm;
```

For the final UI, use dropdowns for categorical variables so users cannot accidentally submit invalid category strings.

---

# 28. Phase 25 — Prediction UI

Flow:

```text
Create patient
     ↓
patient_id returned
     ↓
Show Run Prediction
     ↓
POST /patients/{id}/predict
     ↓
Display result
```

Example:

```jsx
const runPrediction = async () => {
    setLoading(true);

    try {
        const result = await predictPatient(patientId);
        setPrediction(result);
    } catch (error) {
        setError(error.message);
    } finally {
        setLoading(false);
    }
};
```

Display:

```text
Patient: P102

Heart Disease Probability
87.4%

Risk Level
HIGH

Model
Optimized XGBoost v1.0

[ View History ]
```

---

# 29. Phase 26 — Prediction History

Call:

```text
GET /patients/{patient_id}/predictions
```

Display:

| Date | Model | Probability | Risk |
|---|---|---:|---|
| 05 Oct | XGBoost 1.0 | 87% | HIGH |
| 20 Oct | XGBoost 1.0 | 72% | HIGH |
| 15 Nov | XGBoost 1.1 | 64% | MODERATE |

This proves that predictions are persisted in PostgreSQL.

---

# 30. Phase 27 — Dashboard

Display:

```text
Total Patients
Total Predictions
High Risk Predictions
Moderate Risk Predictions
Low Risk Predictions
Active Model
```

Example:

```text
┌─────────────┐ ┌──────────────┐ ┌──────────────┐
│ Patients    │ │ Predictions  │ │ High Risk    │
│     128     │ │     204      │ │      41      │
└─────────────┘ └──────────────┘ └──────────────┘
```

Example SQL:

```sql
SELECT COUNT(*) FROM patients;

SELECT COUNT(*) FROM predictions;

SELECT COUNT(*)
FROM predictions
WHERE risk_level = 'HIGH';
```

---

# 31. Phase 28 — Authentication and Authorization

Roles:

```text
ADMIN
DOCTOR
ANALYST
```

Example:

| Action | Admin | Doctor | Analyst |
|---|---:|---:|---:|
| Create patient | ✓ | ✓ | ✗ |
| View patient | ✓ | ✓ | ✓ |
| Run prediction | ✓ | ✓ | ✓ |
| View history | ✓ | ✓ | ✓ |
| Manage users | ✓ | ✗ | ✗ |
| View audit logs | ✓ | limited | ✗ |

JWT flow:

```text
Login
 ↓
FastAPI validates credentials
 ↓
JWT generated
 ↓
Frontend sends Authorization header
 ↓
Protected endpoint
 ↓
Role checked
```

Never store plaintext passwords.

---

# 32. Phase 29 — Transactions

Treat prediction generation as one logical operation:

```text
BEGIN

1. Create/update clinical record
2. Read latest patient data
3. Run ML prediction
4. Insert prediction
5. Insert audit log

COMMIT
```

If a database operation fails:

```text
ROLLBACK
```

This demonstrates transaction atomicity.

---

# 33. Phase 30 — Optional Database Audit Trigger

If you want a strong DBMS demonstration, you can implement a PostgreSQL trigger.

```sql
CREATE OR REPLACE FUNCTION log_prediction_insert()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO audit_logs(
        action,
        entity_type,
        entity_id,
        patient_id,
        details
    )
    VALUES (
        'PREDICTION_CREATED',
        'prediction',
        NEW.prediction_id,
        NEW.patient_id,
        jsonb_build_object(
            'risk_level', NEW.risk_level,
            'probability', NEW.probability
        )
    );

    RETURN NEW;
END;
$$;
```

Then:

```sql
CREATE TRIGGER prediction_audit_trigger
AFTER INSERT ON predictions
FOR EACH ROW
EXECUTE FUNCTION log_prediction_insert();
```

Choose either application-level or trigger-level logging for a particular event to avoid duplicate entries.

---

# 34. Phase 31 — Docker

Example `docker-compose.yml`:

```yaml
services:

  postgres:
    image: postgres:16
    container_name: heart_postgres
    environment:
      POSTGRES_DB: heartdb
      POSTGRES_USER: heart_app
      POSTGRES_PASSWORD: change_this
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    container_name: heart_backend
    environment:
      DATABASE_URL: postgresql+psycopg2://heart_app:change_this@postgres:5432/heartdb
    ports:
      - "8000:8000"
    depends_on:
      - postgres

volumes:
  postgres_data:
```

For initial development, it is easier to use:

```text
PostgreSQL → Docker
FastAPI → local
React → local
```

Then containerize the entire stack after everything works.

---

# 35. Phase 32 — Complete Runtime Connection

```text
                    USER
                     │
                     ▼
              React Frontend
                     │
                     │ JSON
                     ▼
              FastAPI Backend
                     │
           ┌─────────┴──────────┐
           │                    │
           ▼                    ▼
      PostgreSQL             ML Model
           │                    │
           │                 Probability
           │                    │
           └─────────┬──────────┘
                     ▼
                  Prediction
                     │
                     ▼
                PostgreSQL
                     │
              ┌──────┴───────┐
              ▼              ▼
          Audit Log       History
              │              │
              └──────┬───────┘
                     ▼
                  FastAPI
                     │
                     ▼
                  React
```

---

# 36. Exact User Journey

## Step 1 — Login

Doctor logs in.

## Step 2 — Add patient

Example:

```text
Patient ID: P102
Age: 52
Sex: Male
...
```

Click:

```text
Save Patient
```

Database writes:

```text
patients
clinical_records
```

## Step 3 — Predict

Click:

```text
Predict Heart Disease Risk
```

Backend:

```text
PostgreSQL
 ↓
clinical data
 ↓
saved preprocessing
 ↓
Optimized XGBoost
 ↓
probability
 ↓
risk
```

## Step 4 — Save

```text
predictions
```

receives the result.

## Step 5 — Audit

```text
audit_logs
```

records:

```text
PREDICTION_CREATED
```

## Step 6 — Display

Frontend:

```text
Probability: 87%
Risk: HIGH
Model: Optimized XGBoost
```

## Step 7 — History

Frontend requests:

```text
GET /patients/P102/predictions
```

PostgreSQL returns previous predictions.

---

# 37. Error Handling

Handle these cases:

```text
404 → Patient not found
400 → Missing clinical data
422 → Validation error
503 → ML model unavailable
500 → Database/internal error
```

Never expose raw SQL exceptions or stack traces to users.

---

# 38. Phase 33 — ML/DB Consistency Checklist

Before declaring the system complete:

### Check 1
Frontend field names match backend schema.

### Check 2
Backend fields match database columns.

### Check 3
Database values map to the ML feature schema.

### Check 4
The saved model contains the same preprocessing used during training.

### Check 5
The inference threshold equals the validated threshold.

### Check 6
Every prediction records the model version.

### Check 7
The model's categorical mappings are exactly the training mappings.

### Check 8
Missing-value handling is the same in training and inference.

This prevents the dangerous situation:

```text
Training preprocessing
        ≠
API preprocessing
```

---

# 39. Phase 34 — Final Testing

## Database

```sql
SELECT * FROM users;
SELECT * FROM patients;
SELECT * FROM clinical_records;
SELECT * FROM model_registry;
SELECT * FROM predictions;
SELECT * FROM audit_logs;
```

## Backend

Test:

```text
GET /
POST /patients
GET /patients/{id}
POST /patients/{id}/predict
GET /patients/{id}/predictions
GET /dashboard/summary
```

## Frontend

Test:

```text
Login
 ↓
Patient form
 ↓
Save
 ↓
Predict
 ↓
Result
 ↓
History
```

## Failure tests

Try:

```text
invalid patient ID
missing clinical value
invalid age
invalid category
database unavailable
model unavailable
```

---

# 40. Phase 35 — Recommended Novelty

A defensible project novelty can be:

```text
Feature Selection
       +
Optimized XGBoost
       +
Threshold Optimization
       +
SHAP Explainability
```

Architecture:

```text
Raw Features
     ↓
Cleaning
     ↓
Feature Engineering
     ↓
Feature Selection
     ↓
XGBoost Hyperparameter Optimization
     ↓
Threshold Selection
     ↓
Final Prediction
     ↓
SHAP Explanation
```

Do not artificially alter predictions to increase metrics.

If one metric improves and another falls, report the trade-off honestly.

---

# 41. Phase 36 — SHAP in the Application

Keep full SHAP analysis in:

```text
07_final_evaluation.ipynb
```

Optionally expose top contributors in the frontend:

```text
Prediction explanation

Age                  ██████████
Exercise Angina      ████████
Chest Pain Type      ███████
Maximum Heart Rate   █████
Cholesterol          ███
```

This is an explanation of the model's behavior, not a medical causal explanation.

---

# 42. Phase 37 — Security and Privacy

Because this is healthcare-themed:

- use only public/synthetic educational data
- do not put real patient data in Git
- never commit passwords
- never commit JWT secrets
- validate all inputs
- use SQLAlchemy/parameterized queries
- keep audit records
- do not expose database credentials to React
- document that the result is a model prediction, not a diagnosis

---

# 43. Phase 38 — Layer Responsibilities

## Frontend

```text
UI
Forms
Validation feedback
Results
History
API calls
```

Never:

```text
connect directly to PostgreSQL
run XGBoost
store database passwords
```

## Backend

```text
Authentication
Authorization
Validation
Database operations
ML invocation
Transactions
Audit logging
API responses
```

## Database

```text
Persistence
Relationships
Constraints
Transactions
Views
Stored functions
Indexes
Audit data
Access permissions
```

## ML

```text
Preprocessing
Feature engineering
Feature selection
Prediction
Evaluation
Explainability
```

---

# 44. Final Complete Workflow

```text
                    OFFLINE TRAINING
                         │
                         ▼
                Kaggle Heart Dataset
                         │
                         ▼
                    Data Cleaning
                         │
                         ▼
                 Feature Engineering
                         │
                         ▼
                  Feature Selection
                         │
                         ▼
              ┌─────────────────────┐
              │ Logistic Regression │
              │ Random Forest       │
              │ XGBoost             │
              └──────────┬──────────┘
                         │
                         ▼
                  Novel Improvement
                         │
                         ▼
                Hyperparameter Tune
                         │
                         ▼
                  Threshold Analysis
                         │
                         ▼
                 Final XGBoost Model
                         │
                         ├── ROC
                         ├── PR Curve
                         ├── Confusion Matrix
                         └── SHAP
                         │
                         ▼
                   Save Pipeline
                         │
                         ▼
              heart_pipeline.joblib
                         │
                         │
               APPLICATION RUNTIME
                         │
                         ▼
                    React UI
                         │
                         ▼
                   FastAPI API
                         │
              ┌──────────┴───────────┐
              │                      │
              ▼                      ▼
         PostgreSQL             ML Pipeline
              │                      │
              │                  Probability
              │                      │
              └──────────┬───────────┘
                         ▼
                    Prediction
                         │
                         ▼
                    PostgreSQL
                         │
               ┌─────────┴─────────┐
               ▼                   ▼
          Audit Log            History
               │                   │
               └─────────┬─────────┘
                         ▼
                    FastAPI
                         │
                         ▼
                    React UI
                         │
                         ▼
                  Result + History
```

---

# 45. Exact Implementation Order

Do not build everything simultaneously.

```text
STEP 1
Finish final ML evaluation
        ↓
STEP 2
Save final preprocessing + model pipeline
        ↓
STEP 3
Create feature_schema.json + model_metadata.json
        ↓
STEP 4
Design ER diagram
        ↓
STEP 5
Normalize schema
        ↓
STEP 6
Create PostgreSQL database
        ↓
STEP 7
Create tables + constraints
        ↓
STEP 8
Insert model_registry metadata
        ↓
STEP 9
Create views
        ↓
STEP 10
Create stored functions
        ↓
STEP 11
Create DB roles/access control
        ↓
STEP 12
Create FastAPI project
        ↓
STEP 13
Connect SQLAlchemy → PostgreSQL
        ↓
STEP 14
Test database APIs in Swagger
        ↓
STEP 15
Connect saved ML pipeline
        ↓
STEP 16
Test prediction endpoint
        ↓
STEP 17
Store prediction in PostgreSQL
        ↓
STEP 18
Add transactions + audit logging
        ↓
STEP 19
Build React frontend
        ↓
STEP 20
Connect React → FastAPI
        ↓
STEP 21
Build prediction history
        ↓
STEP 22
Build dashboard
        ↓
STEP 23
Add authentication/authorization
        ↓
STEP 24
End-to-end testing
        ↓
STEP 25
Dockerize
        ↓
STEP 26
Prepare report/PPT/demo
```

---

# 46. Final Teacher Demonstration

## 1. ER diagram

Explain:

```text
Patient → Clinical Record → Prediction
                    ↓
                ML Model
```

## 2. Normalization

Explain why data is separated.

## 3. PostgreSQL

Run:

```sql
SELECT * FROM patients;
SELECT * FROM predictions;
SELECT * FROM audit_logs;
```

## 4. FastAPI

Open:

```text
/docs
```

## 5. Frontend

Login → Add patient.

## 6. Prediction

Click:

```text
Predict
```

## 7. Explain connection

```text
React
 ↓
FastAPI
 ↓
PostgreSQL
 ↓
ML model
 ↓
Prediction
 ↓
PostgreSQL
 ↓
React
```

## 8. Show history

Prove predictions are persisted.

## 9. Show DBMS features

Demonstrate:

```text
SQL
View
Stored Function
Transaction
Audit Log
Access Control
```

## 10. Show ML novelty

```text
Baseline
     ↓
Novel method
     ↓
Accuracy
Precision
Recall
F1
ROC-AUC
     ↓
Improvement
     ↓
SHAP explanation
```

This makes the project a **database-driven AI application**, not merely an ML notebook with a database attached.
