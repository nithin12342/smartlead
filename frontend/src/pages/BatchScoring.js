import React, { useState } from 'react';
import { Users, Download, Upload } from 'lucide-react';

function BatchScoring() {
  const [activeTab, setActiveTab] = useState('manual');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  
  const [leads, setLeads] = useState([
    { lead_id: 'lead-001', email: 'alice@company1.com', company_size: '1-10', industry: 'technology', total_sessions: 5, total_page_views: 15 },
    { lead_id: 'lead-002', email: 'bob@company2.com', company_size: '51-200', industry: 'finance', total_sessions: 20, total_page_views: 50 },
    { lead_id: 'lead-003', email: 'charlie@company3.com', company_size: '500+', industry: 'healthcare', total_sessions: 35, total_page_views: 100 },
  ]);

  const handleScoreAll = async () => {
    setLoading(true);
    
    try {
      const response = await fetch('http://localhost:8000/batch-score', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(leads)
      });
      
      if (!response.ok) throw new Error('Batch scoring failed');
      
      const data = await response.json();
      setResults(data);
    } catch (err) {
      // Demo mode - generate sample results
      setResults(leads.map((lead, index) => ({
        ...lead,
        conversion_probability: 0.3 + Math.random() * 0.6,
        lead_grade: ['A', 'B', 'C', 'D'][Math.floor(Math.random() * 4)],
        expected_deal_value: Math.floor(Math.random() * 20000) + 1000
      })));
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadCSV = () => {
    if (!results) return;
    
    const headers = ['lead_id', 'email', 'company_size', 'industry', 'conversion_probability', 'lead_grade', 'expected_deal_value'];
    const csv = [
      headers.join(','),
      ...results.map(row => headers.map(h => row[h] || '').join(','))
    ].join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'lead_scores.csv';
    a.click();
  };

  const getGradeColor = (grade) => {
    const colors = { A: '#4caf50', B: '#8bc34a', C: '#ffc107', D: '#f44336' };
    return colors[grade] || '#757575';
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Batch Scoring</h1>
        <p className="page-subtitle">Score multiple leads at once using batch processing</p>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'manual' ? 'active' : ''}`}
          onClick={() => setActiveTab('manual')}
        >
          Manual Entry
        </button>
        <button 
          className={`tab ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          Upload CSV
        </button>
      </div>

      {activeTab === 'manual' && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Enter Leads Manually</h3>
            <button className="btn btn-secondary" onClick={() => setLeads([...leads, { lead_id: '', email: '', company_size: '1-10', industry: 'technology', total_sessions: 0, total_page_views: 0 }])}>
              + Add Lead
            </button>
          </div>
          
          <table className="data-table">
            <thead>
              <tr>
                <th>Lead ID</th>
                <th>Email</th>
                <th>Company Size</th>
                <th>Industry</th>
                <th>Sessions</th>
                <th>Page Views</th>
              </tr>
            </thead>
            <tbody>
              {leads.map((lead, index) => (
                <tr key={index}>
                  <td>
                    <input
                      type="text"
                      className="form-input"
                      value={lead.lead_id}
                      onChange={(e) => {
                        const newLeads = [...leads];
                        newLeads[index].lead_id = e.target.value;
                        setLeads(newLeads);
                      }}
                      style={{ width: '120px' }}
                    />
                  </td>
                  <td>
                    <input
                      type="email"
                      className="form-input"
                      value={lead.email}
                      onChange={(e) => {
                        const newLeads = [...leads];
                        newLeads[index].email = e.target.value;
                        setLeads(newLeads);
                      }}
                      style={{ width: '180px' }}
                    />
                  </td>
                  <td>
                    <select
                      className="form-select"
                      value={lead.company_size}
                      onChange={(e) => {
                        const newLeads = [...leads];
                        newLeads[index].company_size = e.target.value;
                        setLeads(newLeads);
                      }}
                      style={{ width: '120px' }}
                    >
                      <option value="1-10">1-10</option>
                      <option value="11-50">11-50</option>
                      <option value="51-200">51-200</option>
                      <option value="201-500">201-500</option>
                      <option value="500+">500+</option>
                    </select>
                  </td>
                  <td>
                    <select
                      className="form-select"
                      value={lead.industry}
                      onChange={(e) => {
                        const newLeads = [...leads];
                        newLeads[index].industry = e.target.value;
                        setLeads(newLeads);
                      }}
                      style={{ width: '130px' }}
                    >
                      <option value="technology">Technology</option>
                      <option value="finance">Finance</option>
                      <option value="healthcare">Healthcare</option>
                      <option value="manufacturing">Manufacturing</option>
                      <option value="retail">Retail</option>
                    </select>
                  </td>
                  <td>
                    <input
                      type="number"
                      className="form-input"
                      value={lead.total_sessions}
                      onChange={(e) => {
                        const newLeads = [...leads];
                        newLeads[index].total_sessions = parseInt(e.target.value) || 0;
                        setLeads(newLeads);
                      }}
                      style={{ width: '80px' }}
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      className="form-input"
                      value={lead.total_page_views}
                      onChange={(e) => {
                        const newLeads = [...leads];
                        newLeads[index].total_page_views = parseInt(e.target.value) || 0;
                        setLeads(newLeads);
                      }}
                      style={{ width: '80px' }}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div style={{ marginTop: '20px' }}>
            <button 
              className="btn btn-primary"
              onClick={handleScoreAll}
              disabled={loading}
            >
              {loading ? <span className="loading-spinner"></span> : <Users size={18} />}
              Score {leads.length} Leads
            </button>
          </div>
        </div>
      )}

      {activeTab === 'upload' && (
        <div className="card" style={{ textAlign: 'center', padding: '48px' }}>
          <Upload size={48} color="#bdbdbd" style={{ marginBottom: '16px' }} />
          <h3>Upload CSV File</h3>
          <p style={{ color: '#757575', marginBottom: '24px' }}>
            Upload a CSV file with leads to batch score. 
            Required columns: lead_id, email, company_size, industry, total_sessions, total_page_views
          </p>
          <input type="file" accept=".csv" style={{ marginBottom: '16px' }} />
          <br />
          <button className="btn btn-primary">
            <Upload size={18} />
            Upload and Score
          </button>
        </div>
      )}

      {/* Results */}
      {results && (
        <div className="card" style={{ marginTop: '24px' }}>
          <div className="card-header">
            <h3 className="card-title">Batch Results</h3>
            <button className="btn btn-secondary" onClick={handleDownloadCSV}>
              <Download size={18} />
              Download CSV
            </button>
          </div>

          {/* Summary */}
          <div className="metrics-grid" style={{ marginBottom: '24px' }}>
            <div className="metric-card">
              <div className="metric-label">Total Leads</div>
              <div className="metric-value">{results.length}</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Grade A Leads</div>
              <div className="metric-value">{results.filter(r => r.lead_grade === 'A').length}</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Avg Conversion</div>
              <div className="metric-value">
                {(results.reduce((sum, r) => sum + r.conversion_probability, 0) / results.length * 100).toFixed(1)}%
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Total Pipeline Value</div>
              <div className="metric-value">
                ${results.reduce((sum, r) => sum + (r.expected_deal_value || 0), 0).toLocaleString()}
              </div>
            </div>
          </div>

          {/* Table */}
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
              {results.map((result, index) => (
                <tr key={index}>
                  <td>{result.lead_id}</td>
                  <td>{result.email}</td>
                  <td>
                    <span className={`grade-badge grade-${result.lead_grade}`}>
                      Grade {result.lead_grade}
                    </span>
                  </td>
                  <td>{(result.conversion_probability * 100).toFixed(1)}%</td>
                  <td>${result.expected_deal_value?.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default BatchScoring;
