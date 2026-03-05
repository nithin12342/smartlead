import React from 'react';
import { 
  TrendingUp, 
  Users, 
  DollarSign, 
  Target,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';
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
  PieChart,
  Pie,
  Cell
} from 'recharts';

// Sample data for demonstration
const gradeData = [
  { name: 'Grade A', value: 156, color: '#4caf50' },
  { name: 'Grade B', value: 312, color: '#8bc34a' },
  { name: 'Grade C', value: 450, color: '#ffc107' },
  { name: 'Grade D', value: 316, color: '#f44336' },
];

const trendData = Array.from({ length: 30 }, (_, i) => ({
  date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
  conversion: 50 + Math.random() * 15,
  score: 55 + Math.random() * 10
}));

const recentLeads = [
  { id: 'lead-001', email: 'john@tech.com', grade: 'A', probability: 0.85, value: 15000 },
  { id: 'lead-002', email: 'jane@corp.com', grade: 'B', probability: 0.62, value: 8500 },
  { id: 'lead-003', email: 'bob@startup.io', grade: 'C', probability: 0.41, value: 3200 },
  { id: 'lead-004', email: 'alice@enterprise.com', grade: 'A', probability: 0.91, value: 25000 },
  { id: 'lead-005', email: 'mike@smallbiz.com', grade: 'D', probability: 0.18, value: 1000 },
];

function Dashboard() {
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Overview of lead scoring performance and metrics</p>
      </div>

      {/* Metrics Grid */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-label">Total Leads Scored</div>
          <div className="metric-value">1,234</div>
          <div className="metric-change positive">
            <ArrowUpRight size={16} /> +12% from last month
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Average Score</div>
          <div className="metric-value">62.5</div>
          <div className="metric-change positive">
            <ArrowUpRight size={16} /> +5% from last month
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-label">High-Value Leads (A)</div>
          <div className="metric-value">156</div>
          <div className="metric-change positive">
            <ArrowUpRight size={16} /> +8% from last month
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Pipeline Value</div>
          <div className="metric-value">$2.4M</div>
          <div className="metric-change positive">
            <ArrowUpRight size={16} /> +15% from last month
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Leads by Grade</h3>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={gradeData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {gradeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Conversion Trend</h3>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="conversion" 
                  stroke="#1976d2" 
                  strokeWidth={2}
                  dot={false}
                  name="Conversion %"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent Predictions */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Recent Predictions</h3>
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Lead ID</th>
              <th>Email</th>
              <th>Grade</th>
              <th>Probability</th>
              <th>Value</th>
            </tr>
          </thead>
          <tbody>
            {recentLeads.map(lead => (
              <tr key={lead.id}>
                <td>{lead.id}</td>
                <td>{lead.email}</td>
                <td>
                  <span className={`grade-badge grade-${lead.grade}`}>
                    Grade {lead.grade}
                  </span>
                </td>
                <td>{(lead.probability * 100).toFixed(1)}%</td>
                <td>${lead.value.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Dashboard;
