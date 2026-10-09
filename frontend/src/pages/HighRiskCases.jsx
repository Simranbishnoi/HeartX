import React, { useState, useEffect, useMemo } from 'react'
import { ShieldAlert, Search, X } from 'lucide-react'

export default function HighRiskCases() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedLog, setSelectedLog] = useState(null);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:8000/predictions');
        const json = await response.json();
        
        // Filter only High Risk cases
        const highRisk = json.filter(item => item.risk_level === 'High');
        
        const formatted = highRisk.map(item => ({
          log: `L-${item.prediction_id}`,
          id: `#P-${item.patient_id}`,
          age: item.age,
          sex: item.sex,
          score: `${(item.probability * 100).toFixed(1)}%`,
          level: item.risk_level,
          color: 'badge-high',
          time: item.prediction_time ? new Date(item.prediction_time.endsWith('Z') ? item.prediction_time : item.prediction_time + 'Z').toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }) : 'N/A',
          details: `Prediction Probability: ${item.probability}`
        }));
        
        setData(formatted);
      } catch (err) {
        console.error('Failed to fetch predictions', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  const filteredData = useMemo(() => {
    return data.filter(item => 
      item.id.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [data, searchTerm]);

  return (
    <div className="history-page">
      <header style={{marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end'}}>
        <div>
          <h1 style={{display: 'flex', alignItems: 'center', gap: '12px'}}>
            <ShieldAlert color="#ef4444" size={32} /> High Risk Cases
          </h1>
          <p>Monitoring critical patients who require immediate attention.</p>
        </div>
        <div style={{display: 'flex', gap: '1rem'}}>
          <div style={{position: 'relative'}}>
            <Search size={18} style={{position: 'absolute', left: '12px', top: '14px', color: 'var(--text-secondary)'}} />
            <input 
              type="text" 
              placeholder="Search Patient ID..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="form-input" 
              style={{paddingLeft: '36px', width: '250px'}} 
            />
          </div>
        </div>
      </header>

      {selectedLog && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, 
          background: 'rgba(0,0,0,0.7)', zIndex: 1000, 
          display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
          <div className="glass-panel" style={{width: '400px', position: 'relative'}}>
            <button onClick={() => setSelectedLog(null)} style={{
              position: 'absolute', right: '16px', top: '16px', 
              background: 'transparent', border: 'none', color: 'white', cursor: 'pointer'
            }}>
              <X size={24} />
            </button>
            <h2 style={{marginTop: 0}}>Critical Patient Details</h2>
            <p><strong>Log ID:</strong> {selectedLog.log}</p>
            <p><strong>Patient ID:</strong> {selectedLog.id}</p>
            <p><strong>Risk Score:</strong> {selectedLog.score}</p>
            <hr style={{borderColor: 'var(--panel-border)', margin: '1rem 0'}} />
            <p>{selectedLog.details}</p>
            <button className="btn" style={{marginTop: '1rem', width: '100%', background: '#ef4444'}} onClick={() => setSelectedLog(null)}>Close</button>
          </div>
        </div>
      )}

      <div className="glass-panel">
        <div style={{overflowX: 'auto', minHeight: '400px'}}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Log ID</th>
                <th>Patient ID</th>
                <th>Age / Sex</th>
                <th>Model</th>
                <th>Risk Score</th>
                <th>Risk Level</th>
                <th>Timestamp</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="8" style={{textAlign: 'center', padding: '2rem'}}>Loading critical cases...</td></tr>
              ) : filteredData.length > 0 ? filteredData.map((row, i) => (
                <tr key={i}>
                  <td style={{color: 'var(--text-secondary)'}}>{row.log}</td>
                  <td style={{fontWeight: '500', color: 'var(--text-primary)'}}>{row.id}</td>
                  <td>{row.age} / {row.sex}</td>
                  <td style={{color: 'var(--text-secondary)'}}>XGBoost API</td>
                  <td style={{fontWeight: '600', color: '#ef4444'}}>{row.score}</td>
                  <td><span className={`badge ${row.color}`}>{row.level}</span></td>
                  <td style={{color: 'var(--text-secondary)'}}>{row.time}</td>
                  <td>
                    <button onClick={() => setSelectedLog(row)} className="btn btn-secondary" style={{padding: '4px 12px', fontSize: '0.8rem'}}>View</button>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan="8" style={{textAlign: 'center', padding: '2rem'}}>No high risk cases found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
