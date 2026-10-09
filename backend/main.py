from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import joblib
import pandas as pd
import os
import sys

# Ensure src can be imported for unpickling the model
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import engine, Base, get_db, SessionLocal
from models import domain
from schemas import api

# Create tables
Base.metadata.create_all(bind=engine)

# Seed Doctors
db_session = SessionLocal()
try:
    if db_session.query(domain.Doctor).count() == 0:
        print("Seeding 15 doctors...")
        import random
        for i in range(1, 16):
            if i == 1:
                gmail = "simran21@gmail.com"
            else:
                domains = ["gmail.com"]
                gmail = f"doctor{i}_{random.randint(10,99)}@gmail.com"
            
            prefix = gmail.split("@")[0]
            password = prefix[::-1] # Reverse of email prefix
            doc = domain.Doctor(doctor_id=i, gmail=gmail, password=password)
            db_session.add(doc)
        db_session.commit()
except Exception as e:
    print(f"Failed to seed doctors: {e}")
finally:
    db_session.close()

app = FastAPI(title="HeartX Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    elif probability < 0.50:
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
        cp=patient_data.cp,
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

@app.put("/patients/{patient_id}", response_model=api.PatientResponse)
def update_patient(patient_id: int, patient_data: api.PatientCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_patient = db.query(domain.Patient).filter(domain.Patient.patient_id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    db_patient.age = patient_data.age
    db_patient.sex = patient_data.sex
    
    measurements = db.query(domain.ClinicalMeasurements).filter(domain.ClinicalMeasurements.patient_id == patient_id).first()
    if measurements:
        measurements.trestbps = patient_data.trestbps
        measurements.chol = patient_data.chol
        measurements.thalch = patient_data.thalch
        measurements.oldpeak = patient_data.oldpeak
        measurements.ca = patient_data.ca
        
    tests = db.query(domain.ClinicalTests).filter(domain.ClinicalTests.patient_id == patient_id).first()
    if tests:
        tests.cp = patient_data.cp
        tests.fbs = patient_data.fbs
        tests.restecg = patient_data.restecg
        tests.exang = patient_data.exang
        tests.slope = patient_data.slope
        tests.thal = patient_data.thal
        
    db.commit()
    db.refresh(db_patient)
    
    background_tasks.add_task(create_audit_log, db, "PATIENT_UPDATED", "patient", db_patient.patient_id)
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
    input_data = pd.DataFrame([{
        "age": patient.age,
        "sex": patient.sex,
        "dataset": "Cleveland", # Most common dataset from UCI
        "cp": tests.cp if hasattr(tests, 'cp') else 0, # Pass actual chest pain type
        "trestbps": measurements.trestbps if measurements else 120,
        "chol": measurements.chol if measurements else 200,
        "fbs": tests.fbs if tests else 0,
        "restecg": tests.restecg if tests else 0,
        "thalch": measurements.thalch if measurements else 150,
        "exang": tests.exang if tests else 0,
        "oldpeak": measurements.oldpeak if measurements else 0.0,
        "slope": tests.slope if tests else 1,
        "ca": measurements.ca if measurements else 0,
        "thal": tests.thal if tests else 2
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

@app.get("/predictions")
def get_prediction_history(db: Session = Depends(get_db)):
    predictions = db.query(domain.Prediction).order_by(domain.Prediction.prediction_time.desc()).all()
    results = []
    for p in predictions:
        patient = db.query(domain.Patient).filter(domain.Patient.patient_id == p.patient_id).first()
        results.append({
            "prediction_id": p.prediction_id,
            "patient_id": p.patient_id,
            "age": patient.age if patient else 'N/A',
            "sex": patient.sex if patient else 'N/A',
            "probability": p.probability,
            "risk_level": p.risk_level,
            "prediction_time": p.prediction_time
        })
    return results

@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": final_pipeline is not None}

@app.post("/login", response_model=api.DoctorResponse)
def login_doctor(credentials: api.DoctorLogin, db: Session = Depends(get_db)):
    doctor = db.query(domain.Doctor).filter(domain.Doctor.doctor_id == credentials.doctor_id).first()
    if not doctor or doctor.password != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid Doctor ID or password")
    
    return {"doctor_id": doctor.doctor_id, "message": "Login successful"}
