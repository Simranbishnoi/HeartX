from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Patient(Base):
    __tablename__ = "patient"
    patient_id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer, nullable=False)
    sex = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    measurements = relationship("ClinicalMeasurements", back_populates="patient", uselist=False)
    tests = relationship("ClinicalTests", back_populates="patient", uselist=False)
    predictions = relationship("Prediction", back_populates="patient")

class ClinicalMeasurements(Base):
    __tablename__ = "clinical_measurements"
    measurement_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient.patient_id", ondelete="CASCADE"))
    trestbps = Column(Float)
    chol = Column(Float)
    thalch = Column(Float)
    oldpeak = Column(Float)
    ca = Column(Float)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    patient = relationship("Patient", back_populates="measurements")

class ClinicalTests(Base):
    __tablename__ = "clinical_tests"
    test_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient.patient_id", ondelete="CASCADE"))
    cp = Column(String(50))
    fbs = Column(Boolean)
    restecg = Column(String(50))
    exang = Column(Boolean)
    slope = Column(String(50))
    thal = Column(String(50))
    tested_at = Column(DateTime(timezone=True), server_default=func.now())
    
    patient = relationship("Patient", back_populates="tests")

class MLModel(Base):
    __tablename__ = "model"
    model_id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    version = Column(String(50))
    accuracy = Column(Float)
    precision_score = Column(Float)
    recall_score = Column(Float)
    f1_score = Column(Float)
    roc_auc = Column(Float)
    trained_at = Column(DateTime(timezone=True), server_default=func.now())
    
    predictions = relationship("Prediction", back_populates="model")

class Prediction(Base):
    __tablename__ = "predictions"
    prediction_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient.patient_id", ondelete="CASCADE"))
    model_id = Column(Integer, ForeignKey("model.model_id"))
    probability = Column(Float)
    prediction = Column(Integer)
    risk_level = Column(String(30))
    prediction_time = Column(DateTime(timezone=True), server_default=func.now())
    
    patient = relationship("Patient", back_populates="predictions")
    model = relationship("MLModel", back_populates="predictions")

class AuditLog(Base):
    __tablename__ = "audit_log"
    log_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    action = Column(String(100), nullable=False)
    table_name = Column(String(100), nullable=False)
    record_id = Column(Integer)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class Doctor(Base):
    __tablename__ = "doctor"
    doctor_id = Column(Integer, primary_key=True, index=True)
    gmail = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
