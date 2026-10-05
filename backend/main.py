from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import joblib
import pandas as pd
import os
import sys

# Ensure src can be imported for unpickling the model
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from .database import engine, Base, get_db
from .models import domain
from .schemas import api

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HeartX Prediction API")

# Phase 41: Load the Model
# We load the entire pipeline once at startup. We DO NOT fit during prediction (Phase 40).
model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'final', 'optimized_xgboost.pkl')
try:
    final_pipeline = joblib.load(model_path)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Warning: Could not load model from {model_path}. Error: {e}")
    final_pipeline = None

# Classification threshold (frozen from validation phase)
CLASSIFICATION_THRESHOLD = 0.50

def determine_risk_level(probability: float) -> str:
    # Phase 43: Risk Classification (Project-defined bands)
    if probability < 0.30:
        return "Low"
    elif probability < 0.70:
        return "Moderate"
    else:
        return "High"

def create_audit_log(db: Session, action: str, table_name: str, record_id: int):
    # Phase 38: Audit Logging
    log = domain.AuditLog(action=action, table_name=table_name, record_id=record_id)
    db.add(log)
    db.commit()

@app.post("/patients", response_model=api.PatientResponse)
def create_patient(patient_data: api.PatientCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Phase 36: Transactions
    # The SQLAlchemy session handles the transaction
    
    # 1. Create Patient
    db_patient = domain.Patient(age=patient_data.age, sex=patient_data.sex)
    db.add(db_patient)
    db.flush() # Get patient_id
    
    # 2. Add Measurements
    db_measurements = domain.ClinicalMeasurements(
        patient_id=db_patient.patient_id,
        trestbps=patient_data.trestbps,
        chol=patient_data.chol,
        thalch=patient_data.thalch,
        oldpeak=patient_data.oldpeak,
        ca=patient_data.ca
    )
    db.add(db_measurements)
    
    # 3. Add Tests
    db_tests = domain.ClinicalTests(
        patient_id=db_patient.patient_id,
        fbs=patient_data.fbs,
        restecg=patient_data.restecg,
        exang=patient_data.exang,
        slope=patient_data.slope,
        thal=patient_data.thal
    )
    db.add(db_tests)
    
    # Commit transaction
    db.commit()
    db.refresh(db_patient)
    
    background_tasks.add_task(create_audit_log, db, "PATIENT_CREATED", "patient", db_patient.patient_id)
    return db_patient

@app.post("/predict/{patient_id}", response_model=api.PredictionResponse)
def predict_heart_disease(patient_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if final_pipeline is None:
        raise HTTPException(status_code=503, detail="Machine learning model is not loaded.")
        
    patient = db.query(domain.Patient).filter(domain.Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    measurements = db.query(domain.ClinicalMeasurements).filter(domain.ClinicalMeasurements.patient_id == patient_id).first()
    tests = db.query(domain.ClinicalTests).filter(domain.ClinicalTests.patient_id == patient_id).first()
    
    # Phase 39: Construct ML input
    # Needs to match the DataFrame format expected by the pipeline
    input_data = pd.DataFrame([{
        "age": patient.age,
        "sex": patient.sex,
        "dataset": "API", # Default or handle missing
        "cp": "API_default", # Need real data for these in a full app
        "trestbps": measurements.trestbps if measurements else None,
        "chol": measurements.chol if measurements else None,
        "fbs": tests.fbs if tests else None,
        "restecg": tests.restecg if tests else None,
        "thalch": measurements.thalch if measurements else None,
        "exang": tests.exang if tests else None,
        "oldpeak": measurements.oldpeak if measurements else None,
        "slope": tests.slope if tests else None,
        "ca": measurements.ca if measurements else None,
        "thal": tests.thal if tests else None
    }])
    
    # Generate probability
    try:
        probability = float(final_pipeline.predict_proba(input_data)[0, 1])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
        
    # Apply frozen threshold
    prediction_class = 1 if probability >= CLASSIFICATION_THRESHOLD else 0
    risk_level = determine_risk_level(probability)
    
    # Store Prediction
    # We use model_id 1 assuming it's the one we seeded
    model = db.query(domain.MLModel).filter(domain.MLModel.model_name == 'Proposed Novelty XGBoost').first()
    model_id = model.model_id if model else 1
    
    db_prediction = domain.Prediction(
        patient_id=patient_id,
        model_id=model_id,
        probability=probability,
        prediction=prediction_class,
        risk_level=risk_level
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    
    background_tasks.add_task(create_audit_log, db, "PREDICTION_CREATED", "predictions", db_prediction.prediction_id)
    return db_prediction

@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": final_pipeline is not None}
