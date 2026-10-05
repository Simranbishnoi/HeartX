from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PatientCreate(BaseModel):
    age: int = Field(..., gt=0, lt=150)
    sex: str
    
    # Clinical measurements
    trestbps: Optional[float] = None
    chol: Optional[float] = None
    thalch: Optional[float] = None
    oldpeak: Optional[float] = None
    ca: Optional[float] = None
    
    # Clinical tests
    fbs: Optional[bool] = None
    restecg: Optional[str] = None
    exang: Optional[bool] = None
    slope: Optional[str] = None
    thal: Optional[str] = None

class PatientResponse(BaseModel):
    patient_id: int
    age: int
    sex: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class PredictionResponse(BaseModel):
    prediction_id: int
    patient_id: int
    probability: float
    prediction: int
    risk_level: str
    prediction_time: datetime
    
    class Config:
        from_attributes = True
