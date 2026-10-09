import { Routes, Route, Link, useLocation, useNavigate, Navigate } from 'react-router-dom'
import { Activity, LayoutDashboard, UserPlus, History, ShieldAlert } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import PatientForm from './pages/PatientForm'
import PredictionHistory from './pages/PredictionHistory'
import HighRiskCases from './pages/HighRiskCases'
import Login from './pages/Login'

function App() {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <>
      {location.pathname !== '/login' && (
        <nav className="navbar">
          <Link to="/" className="nav-brand">
          <Activity color="#6366f1" size={28} />
          Heart<span>X</span>
        </Link>
        <div className="nav-links">
          <Link to="/" className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}>
            <span style={{display: 'flex', alignItems: 'center', gap: '6px'}}>
              <LayoutDashboard size={18} /> Dashboard
            </span>
          </Link>
          <Link to="/new-patient" className={`nav-link ${location.pathname === '/new-patient' ? 'active' : ''}`}>
            <span style={{display: 'flex', alignItems: 'center', gap: '6px'}}>
              <UserPlus size={18} /> New Patient
            </span>
          </Link>
          <Link to="/history" className={`nav-link ${location.pathname === '/history' ? 'active' : ''}`}>
             <span style={{display: 'flex', alignItems: 'center', gap: '6px'}}>
              <History size={18} /> History
            </span>
          </Link>
          <Link to="/high-risk" className={`nav-link ${location.pathname === '/high-risk' ? 'active' : ''}`}>
             <span style={{display: 'flex', alignItems: 'center', gap: '6px'}}>
              <ShieldAlert size={18} /> High Risk
            </span>
          </Link>
          <button 
            onClick={() => {
              localStorage.removeItem('doctor_id');
              navigate('/login');
            }} 
            className="nav-link" 
            style={{background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--danger-color)', marginLeft: 'auto'}}
          >
             <span style={{display: 'flex', alignItems: 'center', gap: '6px'}}>
               Logout
            </span>
          </button>
        </div>
      </nav>
      )}
      
      <main className="container">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={localStorage.getItem('doctor_id') ? <Dashboard /> : <Navigate to="/login" />} />
          <Route path="/new-patient" element={localStorage.getItem('doctor_id') ? <PatientForm /> : <Navigate to="/login" />} />
          <Route path="/history" element={localStorage.getItem('doctor_id') ? <PredictionHistory /> : <Navigate to="/login" />} />
          <Route path="/high-risk" element={localStorage.getItem('doctor_id') ? <HighRiskCases /> : <Navigate to="/login" />} />
        </Routes>
      </main>
    </>
  )
}

export default App
