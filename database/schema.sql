-- 1. Patients Table
CREATE TABLE IF NOT EXISTS patient (
    patient_id SERIAL PRIMARY KEY,
    age INT NOT NULL CHECK (age > 0 AND age < 150),
    sex VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Clinical Measurements Table
CREATE TABLE IF NOT EXISTS clinical_measurements (
    measurement_id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patient(patient_id) ON DELETE CASCADE,
    trestbps NUMERIC,
    chol NUMERIC,
    thalch NUMERIC,
    oldpeak NUMERIC,
    ca NUMERIC,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Clinical Tests Table
CREATE TABLE IF NOT EXISTS clinical_tests (
    test_id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patient(patient_id) ON DELETE CASCADE,
    fbs BOOLEAN,
    restecg VARCHAR(50),
    exang BOOLEAN,
    slope VARCHAR(50),
    thal VARCHAR(50),
    tested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Model Metadata Table
CREATE TABLE IF NOT EXISTS model (
    model_id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    version VARCHAR(50),
    accuracy NUMERIC,
    precision_score NUMERIC,
    recall_score NUMERIC,
    f1_score NUMERIC,
    roc_auc NUMERIC,
    trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Predictions Table
CREATE TABLE IF NOT EXISTS predictions (
    prediction_id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patient(patient_id) ON DELETE CASCADE,
    model_id INT NOT NULL REFERENCES model(model_id),
    probability NUMERIC CHECK (probability >= 0 AND probability <= 1),
    prediction INT CHECK (prediction IN (0, 1)),
    risk_level VARCHAR(30),
    prediction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Audit Log Table
CREATE TABLE IF NOT EXISTS audit_log (
    log_id SERIAL PRIMARY KEY,
    user_id INT, -- Can reference a User/Doctor table in future
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    record_id INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed data for the current model we just trained
INSERT INTO model (model_name, version, accuracy, precision_score, recall_score, f1_score, roc_auc) 
VALUES ('Proposed Novelty XGBoost', '1.0', 0.8043, 0.8000, 0.8627, 0.8302, 0.9104);
