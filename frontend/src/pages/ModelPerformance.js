import React from 'react';
import { CheckCircle, AlertTriangle } from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  ReferenceLine
} from 'recharts';

// Sample data
const aucData = Array.from({ length: 30 }, (_, i) => ({
  date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
  auc: 0.82 + Math.random() * 0.08
}));

const featureImportance = [
  { feature: 'total_sessions', importance: 0.25 },
  { feature: 'pricing_page_visits', importance: 0.22 },
  { feature: 'company_size', importance: 0.18 },
  { feature: 'industry', importance: 0.15 },
  { feature: 'avg_session_duration', importance: 0.12 },
  { feature: 'traffic_source', importance: 0.08 },
];

function ModelPerformance() {
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Model Performance</h1>
        <p className="page-subtitle">Monitor AI model performance and health metrics</p>
      </div>

      {/* Model Info */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-label">Model Version</div>
          <div className="metric-value">v2.1.0</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Last Trained</div>
          <div className="metric-value">2026-03-01</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Training Data Size</div>
          <div className="metric-value">50,000</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Model Status</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '8px' }}>
            <CheckCircle size={20} color="#4caf50" />
            <span style={{ color: '#4caf50', fontWeight: 500 }}>Healthy</span>
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Model Metrics</h3>
        </div>
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-label">AUC Score</div>
            <div className="metric-value">0.872</div>
            <div className="metric-change positive">+0.02 from last week</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Precision</div>
            <div className="metric-value">0.84</div>
            <div className="metric-change positive">+0.01 from last week</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Recall</div>
            <div className="metric-value">0.79</div>
            <div className="metric-change positive">+0.03 from last week</div>
          </div>
          <div className="metric-card">
            <div className="metric-label">F1 Score</div>
            <div className="metric-value">0.81</div>
            <div className="metric-change positive">+0.02 from last week</div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">AUC Over Time</h3>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={aucData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis domain={[0.7, 1]} tick={{ fontSize: 12 }} />
                <Tooltip />
                <ReferenceLine y={0.85} stroke="green" strokeDasharray="5 5" label="Target: 0.85" />
                <Line 
                  type="monotone" 
                  dataKey="auc" 
                  stroke="#1976d2" 
                  strokeWidth={2}
                  dot={false}
                  name="AUC Score"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Feature Importance</h3>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={featureImportance} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" domain={[0, 0.3]} tick={{ fontSize: 12 }} />
                <YAxis dataKey="feature" type="category" width={150} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="importance" fill="#1976d2" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Drift Detection */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Data Drift Detection</h3>
        </div>
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-label">Data Drift Score</div>
            <div className="metric-value">0.03</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '8px', color: '#4caf50' }}>
              <CheckCircle size={16} />
              <span>Within threshold</span>
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Target Drift Score</div>
            <div className="metric-value">0.02</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '8px', color: '#4caf50' }}>
              <CheckCircle size={16} />
              <span>Within threshold</span>
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-label">Prediction Distribution</div>
            <div className="metric-value">Stable</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '8px', color: '#4caf50' }}>
              <CheckCircle size={16} />
              <span>No anomalies detected</span>
            </div>
          </div>
        </div>
      </div>

      {/* Status Message */}
      <div className="card" style={{ borderLeft: '4px solid #4caf50' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <CheckCircle size={24} color="#4caf50" />
          <div>
            <h4 style={{ marginBottom: '4px' }}>Model is Healthy</h4>
            <p style={{ color: '#757575', fontSize: '14px' }}>
              All metrics are within expected parameters. The model is ready for production inference.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ModelPerformance;
