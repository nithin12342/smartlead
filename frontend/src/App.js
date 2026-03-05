import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { 
  Target, 
  LayoutDashboard, 
  Users, 
  Zap, 
  BarChart3
} from 'lucide-react';
import LeadScoring from './pages/LeadScoring';
import BatchScoring from './pages/BatchScoring';
import Dashboard from './pages/Dashboard';
import ModelPerformance from './pages/ModelPerformance';

// API Base URL - can be overridden via environment
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// API Client
const api = {
  async scoreLead(leadData) {
    const response = await fetch(`${API_BASE_URL}/score-lead`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(leadData)
    });
    if (!response.ok) throw new Error('Failed to score lead');
    return response.json();
  },
  
  async batchScore(leads) {
    const response = await fetch(`${API_BASE_URL}/batch-score`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(leads)
    });
    if (!response.ok) throw new Error('Failed to batch score');
    return response.json();
  },
  
  async healthCheck() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`, { 
        signal: AbortSignal.timeout(5000) 
      });
      return response.ok ? { status: 'healthy' } : { status: 'unhealthy' };
    } catch {
      return { status: 'unavailable' };
    }
  }
};

// Navigation Component
function Sidebar({ apiStatus }) {
  const location = useLocation();
  
  const navItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/score', label: 'Lead Scoring', icon: Target },
    { path: '/batch', label: 'Batch Scoring', icon: Users },
    { path: '/performance', label: 'Model Performance', icon: BarChart3 },
  ];
  
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <Zap size={24} />
        </div>
        <span className="sidebar-title">SmartLead</span>
      </div>
      
      <ul className="nav-menu">
        {navItems.map(item => (
          <li key={item.path} className="nav-item">
            <Link 
              to={item.path} 
              className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
            >
              <item.icon size={20} />
              {item.label}
            </Link>
          </li>
        ))}
      </ul>
      
      <div className="status-indicator">
        <span className={`status-dot ${apiStatus === 'healthy' ? 'healthy' : 'unhealthy'}`}></span>
        <span>API: {apiStatus === 'healthy' ? 'Connected' : 'Disconnected'}</span>
      </div>
    </aside>
  );
}

// Main Layout
function Layout() {
  const [apiStatus, setApiStatus] = useState('checking');
  
  useEffect(() => {
    const checkHealth = async () => {
      const status = await api.healthCheck();
      setApiStatus(status.status);
    };
    
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="app-container">
      <Sidebar apiStatus={apiStatus} />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/score" element={<LeadScoring />} />
          <Route path="/batch" element={<BatchScoring />} />
          <Route path="/performance" element={<ModelPerformance />} />
        </Routes>
      </main>
    </div>
  );
}

// App Component
function App() {
  return (
    <Router>
      <Layout />
    </Router>
  );
}

export default App;
