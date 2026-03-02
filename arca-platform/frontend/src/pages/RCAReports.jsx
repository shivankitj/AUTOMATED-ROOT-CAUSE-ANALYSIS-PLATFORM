import React, { useState, useEffect } from 'react';
import { getRCAReports } from '../services/api';
import './RCAReports.css';

function RCAReports() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedReport, setExpandedReport] = useState(null);

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

  const toggleReport = (index) => {
    setExpandedReport(expandedReport === index ? null : index);
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return '#4CAF50';
    if (confidence >= 0.6) return '#ff9800';
    return '#f44336';
  };

  return (
    <div className="rca-reports-page">
      <div className="page-header">
        <h1>RCA Reports</h1>
        <p>Root cause analysis results and recommendations</p>
      </div>

      <div className="card">
        {loading && reports.length === 0 ? (
          <div className="loading">Loading RCA reports...</div>
        ) : error ? (
          <div className="error">{error}</div>
        ) : reports.length === 0 ? (
          <div className="empty-state">No RCA reports available</div>
        ) : (
          <div className="reports-container">
            {reports.map((report, index) => (
              <div key={index} className="report-card">
                <div
                  className="report-summary"
                  onClick={() => toggleReport(index)}
                >
                  <div className="report-main">
                    <h3>{report.root_cause}</h3>
                    <div className="report-meta">
                      <span
                        className="confidence-badge"
                        style={{ backgroundColor: getConfidenceColor(report.confidence) }}
                      >
                        {(report.confidence * 100).toFixed(0)}% Confidence
                      </span>
                      <span className="report-date">
                        {new Date(report.timestamp).toLocaleString()}
                      </span>
                    </div>
                  </div>
                  <button className="expand-btn">
                    {expandedReport === index ? '▲' : '▼'}
                  </button>
                </div>

                {expandedReport === index && (
                  <div className="report-details">
                    {report.affected_components && report.affected_components.length > 0 && (
                      <div className="detail-section">
                        <h4>Affected Components</h4>
                        <div className="component-list">
                          {report.affected_components.map((comp, i) => (
                            <span key={i} className="component-tag">{comp}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    {report.causal_chain && report.causal_chain.length > 0 && (
                      <div className="detail-section">
                        <h4>Causal Chain</h4>
                        <ol className="causal-chain">
                          {report.causal_chain.map((step, i) => (
                            <li key={i}>{step}</li>
                          ))}
                        </ol>
                      </div>
                    )}

                    {report.recommendations && report.recommendations.length > 0 && (
                      <div className="detail-section">
                        <h4>Recommendations</h4>
                        <ul className="recommendations">
                          {report.recommendations.map((rec, i) => (
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
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default RCAReports;
