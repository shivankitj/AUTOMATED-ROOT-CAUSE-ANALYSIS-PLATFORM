import React, { useState, useEffect } from 'react';
import { getAlerts, acknowledgeAlert } from '../services/api';
import './Alerts.css';

function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dismissedAlertIds, setDismissedAlertIds] = useState([]);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [actionMessage, setActionMessage] = useState(null);
  const [processingAlertId, setProcessingAlertId] = useState(null);

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
      setProcessingAlertId(alertId);
      await acknowledgeAlert(alertId);
      setActionMessage({ type: 'success', text: 'Alert acknowledged successfully.' });
      await loadAlerts();
    } catch (err) {
      console.error('Error acknowledging alert:', err);
      setActionMessage({ type: 'error', text: 'Unable to acknowledge alert.' });
    } finally {
      setProcessingAlertId(null);
    }
  };

  const handleDismiss = (alertId) => {
    setDismissedAlertIds((prev) => [...new Set([...prev, alertId])]);
    if (selectedAlert && (selectedAlert.id === alertId || selectedAlert._id === alertId)) {
      setSelectedAlert(null);
    }
    setActionMessage({ type: 'success', text: 'Alert dismissed from current view.' });
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

  const visibleAlerts = alerts.filter((alert) => {
    const alertId = alert.id || alert._id;
    return !dismissedAlertIds.includes(alertId);
  });

  const unacknowledgedAlerts = visibleAlerts.filter(a => !a.acknowledged);
  const acknowledgedAlerts = visibleAlerts.filter(a => a.acknowledged);

  return (
    <div className="alerts-page">
      <div className="page-header page-header-row">
        <div>
          <h1>Alerts</h1>
          <p>System alerts and notifications</p>
        </div>
        <div className="page-actions">
          <button type="button" className="btn btn-secondary" onClick={loadAlerts}>
            Refresh
          </button>
        </div>
      </div>

      {actionMessage && (
        <div className={`status-banner ${actionMessage.type}`}>
          {actionMessage.text}
        </div>
      )}

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
                    <div className="alert-actions">
                      <button
                        className="btn btn-primary"
                        onClick={() => handleAcknowledge(alert.id)}
                        disabled={processingAlertId === alert.id}
                      >
                        {processingAlertId === alert.id ? 'Acknowledging...' : 'Acknowledge'}
                      </button>
                      <button
                        className="btn btn-secondary"
                        onClick={() => setSelectedAlert(alert)}
                      >
                        View Details
                      </button>
                      <button
                        className="btn btn-danger"
                        onClick={() => handleDismiss(alert.id || alert._id)}
                      >
                        Dismiss
                      </button>
                    </div>
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
                    <div className="alert-actions">
                      <button
                        className="btn btn-secondary"
                        onClick={() => setSelectedAlert(alert)}
                      >
                        View Details
                      </button>
                      <button
                        className="btn btn-danger"
                        onClick={() => handleDismiss(alert.id || alert._id)}
                      >
                        Dismiss
                      </button>
                    </div>
                    <div className="acknowledged-info">
                      ✓ Acknowledged at {new Date(alert.acknowledged_at).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {visibleAlerts.length === 0 && (
            <div className="card">
              <div className="empty-state">No alerts to display</div>
            </div>
          )}

          {selectedAlert && (
            <div className="card details-card">
              <div className="details-header">
                <h2>Alert Details</h2>
                <button className="btn btn-secondary" onClick={() => setSelectedAlert(null)}>
                  Close
                </button>
              </div>
              <div className="details-grid">
                <div><strong>ID:</strong> {selectedAlert.id || selectedAlert._id || 'N/A'}</div>
                <div><strong>Type:</strong> {selectedAlert.type || 'N/A'}</div>
                <div><strong>Severity:</strong> {selectedAlert.severity || 'N/A'}</div>
                <div><strong>Timestamp:</strong> {selectedAlert.timestamp ? new Date(selectedAlert.timestamp).toLocaleString() : 'N/A'}</div>
              </div>
              <div className="details-message">
                <strong>Message:</strong> {selectedAlert.message || 'No message available'}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Alerts;
