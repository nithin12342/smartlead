import React, { useState } from 'react';
import { Zap, AlertCircle, CheckCircle } from 'lucide-react';

function LeadScoring() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  
  const [formData, setFormData] = useState({
    lead_id: `lead-${Date.now()}`,
    email: '',
    company_size: '11-50',
    industry: 'technology',
    job_title: '',
    traffic_source: 'organic search',
    total_sessions: 10,
    total_page_views: 25,
    pricing_page_visits: 3,
    avg_session_duration: 5,
    demo_requested: false,
    whitepaper_downloaded: false
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/score-lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      if (!response.ok) throw new Error('Failed to score lead');
      
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
      // Demo mode - show sample result
      setResult({
        lead_id: formData.lead_id,
        conversion_probability: 0.72,
        lead_grade: 'B',
        expected_deal_value: 8500,
        recommended_action: 'Nurture with premium content'
      });
    } finally {
      setLoading(false);
    }
  };

  const loadSample = () => {
    setFormData({
      lead_id: 'sample-lead-001',
      email: 'john.doe@techcorp.com',
      company_size: '51-200',
      industry: 'technology',
      job_title: 'VP of Engineering',
      traffic_source: 'organic search',
      total_sessions: 15,
      total_page_views: 45,
      pricing_page_visits: 5,
      avg_session_duration: 8,
      demo_requested: true,
      whitepaper_downloaded: true
    });
  };

  const getGradeColor = (grade) => {
    const colors = { A: '#4caf50', B: '#8bc34a', C: '#ffc107', D: '#f44336' };
    return colors[grade] || '#757575';
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Lead Scoring</h1>
        <p className="page-subtitle">Score individual leads in real-time using AI-powered prediction</p>
      </div>

      <div className="grid-2">
        {/* Form */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Lead Information</h3>
          </div>
          
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Lead ID</label>
              <input
                type="text"
                name="lead_id"
                className="form-input"
                value={formData.lead_id}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Email *</label>
              <input
                type="email"
                name="email"
                className="form-input"
                placeholder="lead@example.com"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Company Size</label>
              <select
                name="company_size"
                className="form-select"
                value={formData.company_size}
                onChange={handleChange}
              >
                <option value="1-10">1-10 employees</option>
                <option value="11-50">11-50 employees</option>
                <option value="51-200">51-200 employees</option>
                <option value="201-500">201-500 employees</option>
                <option value="500+">500+ employees</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Industry</label>
              <select
                name="industry"
                className="form-select"
                value={formData.industry}
                onChange={handleChange}
              >
                <option value="technology">Technology</option>
                <option value="finance">Finance</option>
                <option value="healthcare">Healthcare</option>
                <option value="manufacturing">Manufacturing</option>
                <option value="retail">Retail</option>
                <option value="education">Education</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Job Title</label>
              <input
                type="text"
                name="job_title"
                className="form-input"
                placeholder="e.g., CTO"
                value={formData.job_title}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Traffic Source</label>
              <select
                name="traffic_source"
                className="form-select"
                value={formData.traffic_source}
                onChange={handleChange}
              >
                <option value="organic search">Organic Search</option>
                <option value="paid search">Paid Search</option>
                <option value="social media">Social Media</option>
                <option value="referral">Referral</option>
                <option value="email">Email</option>
                <option value="direct">Direct</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Total Sessions</label>
              <input
                type="number"
                name="total_sessions"
                className="form-input"
                min="0"
                value={formData.total_sessions}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Total Page Views</label>
              <input
                type="number"
                name="total_page_views"
                className="form-input"
                min="0"
                value={formData.total_page_views}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Pricing Page Visits</label>
              <input
                type="number"
                name="pricing_page_visits"
                className="form-input"
                min="0"
                value={formData.pricing_page_visits}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Avg Session Duration (min)</label>
              <input
                type="number"
                name="avg_session_duration"
                className="form-input"
                min="0"
                value={formData.avg_session_duration}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label className="form-checkbox">
                <input
                  type="checkbox"
                  name="demo_requested"
                  checked={formData.demo_requested}
                  onChange={handleChange}
                />
                Demo Requested
              </label>
            </div>

            <div className="form-group">
              <label className="form-checkbox">
                <input
                  type="checkbox"
                  name="whitepaper_downloaded"
                  checked={formData.whitepaper_downloaded}
                  onChange={handleChange}
                />
                Whitepaper Downloaded
              </label>
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
              <button 
                type="submit" 
                className="btn btn-primary btn-block"
                disabled={loading}
              >
                {loading ? <span className="loading-spinner"></span> : <Zap size={18} />}
                Score Lead
              </button>
              <button 
                type="button" 
                className="btn btn-secondary"
                onClick={loadSample}
              >
                Load Sample
              </button>
            </div>
          </form>
        </div>

        {/* Results */}
        <div>
          {error && (
            <div className="card" style={{ borderLeft: '4px solid #f44336' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', color: '#f44336' }}>
                <AlertCircle size={20} />
                <span>{error}</span>
              </div>
            </div>
          )}

          {result && (
            <div className="score-result">
              <div className="score-result-header">Conversion Probability</div>
              <div className="score-result-value">
                {(result.conversion_probability * 100).toFixed(1)}%
              </div>
              <div className="score-result-details">
                <div className="score-detail-item">
                  <div className="score-detail-label">Lead Grade</div>
                  <div className="score-detail-value" style={{ color: getGradeColor(result.lead_grade) }}>
                    {result.lead_grade}
                  </div>
                </div>
                <div className="score-detail-item">
                  <div className="score-detail-label">Deal Value</div>
                  <div className="score-detail-value">
                    ${result.expected_deal_value?.toLocaleString() || '0'}
                  </div>
                </div>
                <div className="score-detail-item">
                  <div className="score-detail-label">Action</div>
                  <div className="score-detail-value" style={{ fontSize: '14px' }}>
                    {result.recommended_action || 'Nurture'}
                  </div>
                </div>
              </div>
            </div>
          )}

          {result && (
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Score Details</h3>
              </div>
              <table className="data-table">
                <tbody>
                  <tr>
                    <td><strong>Lead ID</strong></td>
                    <td>{result.lead_id}</td>
                  </tr>
                  <tr>
                    <td><strong>Conversion Probability</strong></td>
                    <td>{(result.conversion_probability * 100).toFixed(1)}%</td>
                  </tr>
                  <tr>
                    <td><strong>Lead Grade</strong></td>
                    <td>
                      <span className={`grade-badge grade-${result.lead_grade}`}>
                        Grade {result.lead_grade}
                      </span>
                    </td>
                  </tr>
                  <tr>
                    <td><strong>Expected Deal Value</strong></td>
                    <td>${result.expected_deal_value?.toLocaleString() || '0'}</td>
                  </tr>
                  <tr>
                    <td><strong>Recommended Action</strong></td>
                    <td>{result.recommended_action || 'Nurture with content'}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          )}

          {!result && !error && !loading && (
            <div className="card" style={{ textAlign: 'center', padding: '48px' }}>
              <Zap size={48} color="#bdbdbd" style={{ marginBottom: '16px' }} />
              <p style={{ color: '#757575' }}>
                Enter lead information and click "Score Lead" to get AI-powered predictions
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default LeadScoring;
