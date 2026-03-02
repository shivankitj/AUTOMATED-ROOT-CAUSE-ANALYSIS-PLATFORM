import React, { useState, useEffect } from 'react';
import { getAlerts, acknowledgeAlert } from '../services/api';
import './Alerts.css';

function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAlerts();
    const interval = setInterval(loadAlerts, 15000);
    return () => clearInterval(interval);
  }, []);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getAlerts();
      setAlerts(response.data.alerts || []);
    } catch (err) {
      console.error('Error loading alerts:', err);
      setError('Failed to load alerts');
    } finally {
      setLoading(false);
    }
  };

  const handleAcknowledge = async (alertId) => {
    try {
      await acknowledgeAlert(alertId);
      loadAlerts();
    } catch (err) {
      console.error('Error acknowledging alert:', err);
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

  const unacknowledgedAlerts = alerts.filter(a => !a.acknowledged);
  const acknowledgedAlerts = alerts.filter(a => a.acknowledged);

  return (
    <div className="alerts-page">
      <div className="page-header">
        <h1>Alerts</h1>
        <p>System alerts and notifications</p>
      </div>

      <div className="stats-row">
        <div className="stat-box">
          <div className="stat-value">{unacknowledgedAlerts.length}</div>
          <div className="stat-label">Unacknowledged</div>
        </div>
        <div className="stat-box">
          <div className="stat-value">{acknowledgedAlerts.length}</div>
          <div className="stat-label">Acknowledged</div>
        </div>
        <div className="stat-box">
          <div className="stat-value">{alerts.length}</div>
          <div className="stat-label">Total</div>
        </div>
      </div>

      {loading && alerts.length === 0 ? (
        <div className="loading">Loading alerts...</div>
      ) : error ? (
        <div className="error">{error}</div>
      ) : (
        <>
          {unacknowledgedAlerts.length > 0 && (
            <div className="card">
              <h2>Unacknowledged Alerts</h2>
              <div className="alerts-container">
                {unacknowledgedAlerts.map((alert, index) => (
                  <div key={index} className="alert-card unacknowledged">
                    <div className="alert-header">
                      <span
                        className="severity-badge"
                        style={{ backgroundColor: getSeverityColor(alert.severity) }}
                      >
                        {alert.severity}
                      </span>
                      <span className="alert-type">{alert.type}</span>
                      <span className="alert-time">
                        {new Date(alert.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <div className="alert-message">{alert.message}</div>
                    <button
                      className="btn btn-primary"
                      onClick={() => handleAcknowledge(alert.id)}
                    >
                      Acknowledge
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {acknowledgedAlerts.length > 0 && (
            <div className="card">
              <h2>Acknowledged Alerts</h2>
              <div className="alerts-container">
                {acknowledgedAlerts.map((alert, index) => (
                  <div key={index} className="alert-card acknowledged">
                    <div className="alert-header">
                      <span
                        className="severity-badge"
                        style={{ backgroundColor: getSeverityColor(alert.severity) }}
                      >
                        {alert.severity}
                      </span>
                      <span className="alert-type">{alert.type}</span>
                      <span className="alert-time">
                        {new Date(alert.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <div className="alert-message">{alert.message}</div>
                    <div className="acknowledged-info">
                      ✓ Acknowledged at {new Date(alert.acknowledged_at).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {alerts.length === 0 && (
            <div className="card">
              <div className="empty-state">No alerts to display</div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Alerts;
