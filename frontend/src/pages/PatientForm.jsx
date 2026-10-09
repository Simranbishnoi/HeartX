import React, { useState } from 'react'
import { Stethoscope } from 'lucide-react'

export default function PatientForm() {
  const [formData, setFormData] = useState({
    patient_id: '',
    age: '', sex: '1', cp: '0', trestbps: '', chol: '', 
    fbs: '0', restecg: '0', thalch: '', exang: '0', 
    oldpeak: '', slope: '1', ca: '0', thal: '2'
  });
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleChange = (e) => {
    setFormData({...formData, [e.target.name]: e.target.value});
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // 1. Create or Update Patient
      const url = formData.patient_id ? `http://localhost:8000/patients/${formData.patient_id}` : 'http://localhost:8000/patients';
      const method = formData.patient_id ? 'PUT' : 'POST';
      
      const patientResponse = await fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          age: parseInt(formData.age),
          sex: formData.sex === '1' ? 'M' : 'F',
          cp: formData.cp,
          trestbps: parseFloat(formData.trestbps),
          chol: parseFloat(formData.chol),
          fbs: formData.fbs === '1',
          restecg: formData.restecg,
          thalch: parseFloat(formData.thalch),
          exang: formData.exang === '1',
          oldpeak: parseFloat(formData.oldpeak),
          slope: formData.slope,
          ca: parseInt(formData.ca),
          thal: formData.thal
        })
      });
      
      if (!patientResponse.ok) {
          throw new Error('Failed to save patient. Please check Patient ID.');
      }
      
      const patientData = await patientResponse.json();
      
      // 2. Predict Risk
      const predictResponse = await fetch(`http://localhost:8000/predict/${patientData.patient_id}`, {
        method: 'POST'
      });
      
      const predictData = await predictResponse.json();
      setResult({
        probability: predictData.probability,
        level: predictData.risk_level
      });
    } catch (err) {
      console.error(err);
      alert(err.message || 'Error predicting risk. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid-2">
      <div className="glass-panel">
        <h2 style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
          <Stethoscope color="#6366f1" /> Clinical Assessment
        </h2>
        <p style={{marginBottom: '2rem'}}>Enter patient demographics and clinical measurements to run the prediction pipeline.</p>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group" style={{marginBottom: '1rem'}}>
            <label className="form-label">Patient ID (Optional - For Updating)</label>
            <input type="number" name="patient_id" value={formData.patient_id} onChange={handleChange} className="form-input" placeholder="Leave blank for new patient" />
          </div>
          
          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Age</label>
              <input type="number" name="age" value={formData.age} onChange={handleChange} className="form-input" required />
            </div>
            <div className="form-group">
              <label className="form-label">Sex</label>
              <select name="sex" value={formData.sex} onChange={handleChange} className="form-select">
                <option value="1">Male</option>
                <option value="0">Female</option>
              </select>
            </div>
          </div>
          
          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Resting BP (mm Hg)</label>
              <input type="number" name="trestbps" value={formData.trestbps} onChange={handleChange} className="form-input" required />
            </div>
            <div className="form-group">
              <label className="form-label">Cholesterol (mg/dl)</label>
              <input type="number" name="chol" value={formData.chol} onChange={handleChange} className="form-input" required />
            </div>
          </div>

          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Max Heart Rate</label>
              <input type="number" name="thalch" value={formData.thalch} onChange={handleChange} className="form-input" required />
            </div>
            <div className="form-group">
              <label className="form-label">Chest Pain Type</label>
              <select name="cp" value={formData.cp} onChange={handleChange} className="form-select">
                <option value="0">Typical Angina</option>
                <option value="1">Atypical Angina</option>
                <option value="2">Non-anginal Pain</option>
                <option value="3">Asymptomatic</option>
              </select>
            </div>
          </div>
          
          <div style={{marginTop: '1.5rem'}}>
            <button type="submit" className="btn" style={{width: '100%'}} disabled={loading}>
              {loading ? 'Running ML Model...' : 'Predict Risk Level'}
            </button>
          </div>
        </form>
      </div>
      
      <div>
        {result ? (
          <div className="glass-panel" style={{textAlign: 'center', padding: '3rem 2rem'}}>
            <h3 style={{marginBottom: '1rem'}}>Prediction Result</h3>
            <div style={{
              width: '150px', height: '150px', 
              borderRadius: '50%', 
              border: `8px solid ${result.level === 'High' ? 'var(--danger-color)' : result.level === 'Moderate' ? 'var(--warning-color)' : 'var(--success-color)'}`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              margin: '0 auto 2rem',
              fontSize: '2rem', fontWeight: 'bold'
            }}>
              {(result.probability * 100).toFixed(1)}%
            </div>
            <h2 style={{
              color: result.level === 'High' ? 'var(--danger-color)' : result.level === 'Moderate' ? 'var(--warning-color)' : 'var(--success-color)'
            }}>
              {result.level} Risk
            </h2>
            <p style={{marginTop: '1rem'}}>Model used: <strong>Optimized XGBoost v1.0</strong></p>
          </div>
        ) : (
          <div className="glass-panel" style={{height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: 0.5}}>
            <p>Fill out the form and submit to see prediction results.</p>
          </div>
        )}
      </div>
    </div>
  )
}
