import React, { useState, useEffect } from 'react';
import { getRCAReports } from '../services/api';
import './RCAReports.css';

function RCAReports() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedReport, setSelectedReport] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [confidenceFilter, setConfidenceFilter] = useState('ALL');

  useEffect(() => {
    loadReports();
    const interval = setInterval(loadReports, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadReports = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getRCAReports({ limit: 50 });
      setReports(response.data.reports || []);
    } catch (err) {
      console.error('Error loading RCA reports:', err);
      setError('Failed to load RCA reports');
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return '#4CAF50';
    if (confidence >= 0.6) return '#ff9800';
    return '#f44336';
  };

  const visibleReports = reports
    .filter((report) => {
      if (confidenceFilter === 'HIGH') return (report.confidence || 0) >= 0.8;
      if (confidenceFilter === 'MEDIUM') return (report.confidence || 0) >= 0.6 && (report.confidence || 0) < 0.8;
      if (confidenceFilter === 'LOW') return (report.confidence || 0) < 0.6;
      return true;
    })
    .filter((report) => {
      if (!searchTerm.trim()) return true;
      const term = searchTerm.toLowerCase();
      const components = (report.affected_components || []).join(' ').toLowerCase();
      return `${report.root_cause || ''} ${components}`.toLowerCase().includes(term);
    });

  return (
    <div className="rca-reports-page">
      <div className="page-header page-header-row">
        <div>
          <h1>RCA Reports</h1>
          <p>Root cause analysis results and recommendations</p>
        </div>
        <div className="page-actions">
          <select
            className="input-control"
            value={confidenceFilter}
            onChange={(e) => setConfidenceFilter(e.target.value)}
          >
            <option value="ALL">All confidence</option>
            <option value="HIGH">High (&gt;= 80%)</option>
            <option value="MEDIUM">Medium (60-79%)</option>
            <option value="LOW">Low (&lt; 60%)</option>
          </select>
          <input
            type="text"
            className="input-control"
            placeholder="Search root cause or component"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button type="button" className="btn btn-secondary" onClick={loadReports}>
            Refresh
          </button>
        </div>
      </div>

      <div className="card">
        {loading && reports.length === 0 ? (
          <div className="loading">Loading RCA reports...</div>
        ) : error ? (
          <div className="error">{error}</div>
        ) : visibleReports.length === 0 ? (
          <div className="empty-state">No RCA reports available</div>
        ) : (
          <>
            <div className="results-summary">Showing {visibleReports.length} reports</div>
            <div className="reports-container">
            {visibleReports.map((report, index) => (
              <div key={index} className="report-card">
                <div className="report-summary">
                  <div className="report-main">
                    <h3>{report.root_cause}</h3>
                    <div className="report-meta">
                      <span
                        className="confidence-badge"
                        style={{ backgroundColor: getConfidenceColor(report.confidence) }}
                      >
                        {((report.confidence || 0) * 100).toFixed(0)}% Confidence
                      </span>
                      <span className="report-date">
                        {new Date(report.timestamp).toLocaleString()}
                      </span>
                    </div>
                  </div>
                  <button className="expand-btn" onClick={() => setSelectedReport(report)}>
                    View Details
                  </button>
                </div>
              </div>
            ))}
            </div>

            {selectedReport && (
              <div className="report-details">
                <div className="details-header">
                  <h2>Selected RCA Report</h2>
                  <button className="btn btn-secondary" onClick={() => setSelectedReport(null)}>
                    Close
                  </button>
                </div>
                {selectedReport.affected_components && selectedReport.affected_components.length > 0 && (
                      <div className="detail-section">
                        <h4>Affected Components</h4>
                        <div className="component-list">
                          {selectedReport.affected_components.map((comp, i) => (
                            <span key={i} className="component-tag">{comp}</span>
                          ))}
                        </div>
                      </div>
                    )}

                {selectedReport.causal_chain && selectedReport.causal_chain.length > 0 && (
                      <div className="detail-section">
                        <h4>Causal Chain</h4>
                        <ol className="causal-chain">
                          {selectedReport.causal_chain.map((step, i) => (
                            <li key={i}>{step}</li>
                          ))}
                        </ol>
                      </div>
                    )}

                {selectedReport.recommendations && selectedReport.recommendations.length > 0 && (
                      <div className="detail-section">
                        <h4>Recommendations</h4>
                        <ul className="recommendations">
                          {selectedReport.recommendations.map((rec, i) => (
                            <li key={i}>
                              <span className="rec-icon">💡</span>
                              {rec}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default RCAReports;
