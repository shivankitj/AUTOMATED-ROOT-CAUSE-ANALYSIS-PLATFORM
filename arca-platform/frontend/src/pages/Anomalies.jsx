import React, { useState, useEffect } from 'react';
import { getAnomalies } from '../services/api';
import './Anomalies.css';

function Anomalies() {
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAnomaly, setSelectedAnomaly] = useState(null);

  useEffect(() => {
    loadAnomalies();
    const interval = setInterval(loadAnomalies, 30000);
    return () => clearInterval(interval);
  }, [filter]);

  const loadAnomalies = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = filter !== 'ALL' ? { severity: filter } : {};
      const response = await getAnomalies(params);
      setAnomalies(response.data.anomalies || []);
    } catch (err) {
      console.error('Error loading anomalies:', err);
      setError('Failed to load anomalies');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    const colors = {
      CRITICAL: '#f44336',
      HIGH: '#ff9800',
      MEDIUM: '#ffc107',
      LOW: '#4CAF50'
    };
    return colors[severity] || '#666';
  };

  const visibleAnomalies = anomalies.filter((anomaly) => {
    if (!searchTerm.trim()) return true;
    const term = searchTerm.toLowerCase();
    return [anomaly.type, anomaly.metric, anomaly.description, anomaly.severity]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(term));
  });

  return (
    <div className="anomalies-page">
      <div className="page-header page-header-row">
        <div>
          <h1>Anomalies</h1>
          <p>Detected system and deployment anomalies</p>
        </div>
        <div className="page-actions">
          <input
            type="text"
            className="input-control"
            placeholder="Search severity, type, metric..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button type="button" className="btn btn-secondary" onClick={loadAnomalies}>
            Refresh
          </button>
        </div>
      </div>

      <div className="card">
        <div className="filters">
          <button
            className={`filter-btn ${filter === 'ALL' ? 'active' : ''}`}
            onClick={() => setFilter('ALL')}
          >
            All
          </button>
          <button
            className={`filter-btn ${filter === 'CRITICAL' ? 'active' : ''}`}
            onClick={() => setFilter('CRITICAL')}
          >
            Critical
          </button>
          <button
            className={`filter-btn ${filter === 'HIGH' ? 'active' : ''}`}
            onClick={() => setFilter('HIGH')}
          >
            High
          </button>
          <button
            className={`filter-btn ${filter === 'MEDIUM' ? 'active' : ''}`}
            onClick={() => setFilter('MEDIUM')}
          >
            Medium
          </button>
          <button
            className={`filter-btn ${filter === 'LOW' ? 'active' : ''}`}
            onClick={() => setFilter('LOW')}
          >
            Low
          </button>
        </div>

        {loading && anomalies.length === 0 ? (
          <div className="loading">Loading anomalies...</div>
        ) : error ? (
          <div className="error">{error}</div>
        ) : visibleAnomalies.length === 0 ? (
          <div className="empty-state">No anomalies found</div>
        ) : (
          <>
            <div className="results-summary">Showing {visibleAnomalies.length} anomalies</div>
            <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Severity</th>
                  <th>Type</th>
                  <th>Metric</th>
                  <th>Value</th>
                  <th>Description</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {visibleAnomalies.map((anomaly, index) => (
                  <tr key={index} className="clickable-row" onClick={() => setSelectedAnomaly(anomaly)}>
                    <td>
                      <span
                        className="badge"
                        style={{ backgroundColor: getSeverityColor(anomaly.severity) }}
                      >
                        {anomaly.severity}
                      </span>
                    </td>
                    <td>{anomaly.type}</td>
                    <td><code>{anomaly.metric}</code></td>
                    <td>{anomaly.value?.toFixed(2)}</td>
                    <td>{anomaly.description}</td>
                    <td>{new Date(anomaly.timestamp).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            </div>

            {selectedAnomaly && (
              <div className="details-panel">
                <div className="details-header">
                  <h3>Anomaly Details</h3>
                  <button className="btn btn-secondary" onClick={() => setSelectedAnomaly(null)}>
                    Close
                  </button>
                </div>
                <div className="details-grid">
                  <div><strong>Severity:</strong> {selectedAnomaly.severity || 'N/A'}</div>
                  <div><strong>Type:</strong> {selectedAnomaly.type || 'N/A'}</div>
                  <div><strong>Metric:</strong> {selectedAnomaly.metric || 'N/A'}</div>
                  <div><strong>Value:</strong> {selectedAnomaly.value?.toFixed(2) || 'N/A'}</div>
                  <div><strong>Timestamp:</strong> {selectedAnomaly.timestamp ? new Date(selectedAnomaly.timestamp).toLocaleString() : 'N/A'}</div>
                  <div><strong>ID:</strong> {selectedAnomaly.id || selectedAnomaly._id || 'N/A'}</div>
                </div>
                <p className="details-description">{selectedAnomaly.description || 'No description available.'}</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default Anomalies;
