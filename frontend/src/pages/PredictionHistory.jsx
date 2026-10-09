import React, { useState, useEffect, useMemo } from 'react'
import { History, Search, Filter, X } from 'lucide-react'

export default function PredictionHistory() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedLog, setSelectedLog] = useState(null);
  const itemsPerPage = 6;

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:8000/predictions');
        const json = await response.json();
        
        const formatted = json.map(item => ({
          log: `L-${item.prediction_id}`,
          id: `#P-${item.patient_id}`,
          age: item.age,
          sex: item.sex,
          score: `${(item.probability * 100).toFixed(1)}%`,
          level: item.risk_level,
          color: item.risk_level === 'High' ? 'badge-high' : item.risk_level === 'Moderate' ? 'badge-moderate' : 'badge-low',
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

  // Filter Data
  const filteredData = useMemo(() => {
    return data.filter(item => 
      item.id.toLowerCase().includes(searchTerm.toLowerCase()) || 
      item.level.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [data, searchTerm]);

  // Pagination Logic
  const totalPages = Math.ceil(filteredData.length / itemsPerPage);
  const currentData = useMemo(() => {
    const start = (currentPage - 1) * itemsPerPage;
    return filteredData.slice(start, start + itemsPerPage);
  }, [filteredData, currentPage]);

  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  return (
    <div className="history-page">
      <header style={{marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end'}}>
        <div>
          <h1 style={{display: 'flex', alignItems: 'center', gap: '12px'}}>
            <History color="#6366f1" size={32} /> Prediction History
          </h1>
          <p>Comprehensive log of all patient predictions and risk assessments.</p>
        </div>
        <div style={{display: 'flex', gap: '1rem'}}>
          <div style={{position: 'relative'}}>
            <Search size={18} style={{position: 'absolute', left: '12px', top: '14px', color: 'var(--text-secondary)'}} />
            <input 
              type="text" 
              placeholder="Search Patient ID..." 
              value={searchTerm}
              onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }}
              className="form-input" 
              style={{paddingLeft: '36px', width: '250px'}} 
            />
          </div>
        </div>
      </header>

      {/* Modal for View Details */}
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
            <h2 style={{marginTop: 0}}>Log Details</h2>
            <p><strong>Log ID:</strong> {selectedLog.log}</p>
            <p><strong>Patient ID:</strong> {selectedLog.id}</p>
            <p><strong>Risk Score:</strong> {selectedLog.score}</p>
            <hr style={{borderColor: 'var(--panel-border)', margin: '1rem 0'}} />
            <p>{selectedLog.details}</p>
            <button className="btn" style={{marginTop: '1rem', width: '100%'}} onClick={() => setSelectedLog(null)}>Close</button>
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
                <tr><td colSpan="8" style={{textAlign: 'center', padding: '2rem'}}>Loading database records...</td></tr>
              ) : currentData.length > 0 ? currentData.map((row, i) => (
                <tr key={i}>
                  <td style={{color: 'var(--text-secondary)'}}>{row.log}</td>
                  <td style={{fontWeight: '500', color: 'var(--text-primary)'}}>{row.id}</td>
                  <td>{row.age} / {row.sex}</td>
                  <td style={{color: 'var(--text-secondary)'}}>XGBoost API</td>
                  <td style={{fontWeight: '600'}}>{row.score}</td>
                  <td><span className={`badge ${row.color}`}>{row.level}</span></td>
                  <td style={{color: 'var(--text-secondary)'}}>{row.time}</td>
                  <td>
                    <button onClick={() => setSelectedLog(row)} className="btn btn-secondary" style={{padding: '4px 12px', fontSize: '0.8rem'}}>View</button>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan="8" style={{textAlign: 'center', padding: '2rem'}}>No database records found. Submit a patient first!</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1.5rem', paddingTop: '1.5rem', borderTop: '1px solid var(--panel-border)'}}>
          <p style={{color: 'var(--text-secondary)', fontSize: '0.9rem'}}>
            Showing {filteredData.length > 0 ? (currentPage - 1) * itemsPerPage + 1 : 0} to {Math.min(currentPage * itemsPerPage, filteredData.length)} of {filteredData.length} entries
          </p>
          <div style={{display: 'flex', gap: '8px'}}>
            <button 
              className="btn btn-secondary" 
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
              style={{opacity: currentPage === 1 ? 0.5 : 1}}
            >
              Previous
            </button>
            
            {Array.from({ length: totalPages }).map((_, i) => (
              <button 
                key={i}
                onClick={() => handlePageChange(i + 1)}
                className="btn btn-secondary" 
                style={currentPage === i + 1 ? {background: 'rgba(99, 102, 241, 0.2)', color: 'var(--accent-hover)'} : {}}
              >
                {i + 1}
              </button>
            ))}

            <button 
              className="btn btn-secondary" 
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages || totalPages === 0}
              style={{opacity: currentPage === totalPages || totalPages === 0 ? 0.5 : 1}}
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
