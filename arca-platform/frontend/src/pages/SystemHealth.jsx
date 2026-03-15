import React, { useState, useEffect } from 'react';
import { getSystemHealth, getCurrentMetrics } from '../services/api';
import './SystemHealth.css';

function SystemHealth() {
  const [systemHealth, setSystemHealth] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    loadSystemHealth();
    const interval = setInterval(() => {
      if (autoRefresh) {
        loadSystemHealth();
      }
    }, 10000);
    return () => clearInterval(interval);
  }, [autoRefresh]);

  const loadSystemHealth = async (isManual = false) => {
    try {
      if (!systemHealth) {
        setLoading(true);
      }
      if (isManual) {
        setRefreshing(true);
      }
      setError(null);
      
      const [healthRes, metricsRes] = await Promise.all([
        getSystemHealth(),
        getCurrentMetrics()
      ]);

      setSystemHealth(healthRes.data);
      setMetrics(metricsRes.data);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Error loading system health:', err);
      setError('Failed to load system health');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const getStatusColor = (status) => {
    return status === 'ok' || status === 'healthy' ? '#4CAF50' : '#f44336';
  };

  const getMetricStatus = (value, threshold) => {
    if (value >= threshold) return { status: 'Critical', color: '#f44336' };
    if (value >= threshold * 0.8) return { status: 'Warning', color: '#ff9800' };
    return { status: 'Normal', color: '#4CAF50' };
  };

  if (loading && !systemHealth) {
    return <div className="loading">Loading system health...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="system-health-page">
      <div className="page-header page-header-row">
        <div>
          <h1>System Health</h1>
          <p>Real-time system status and performance metrics</p>
          <div className="muted-text">
            Last updated: {lastUpdated ? lastUpdated.toLocaleTimeString() : 'Not yet available'}
          </div>
        </div>
        <div className="page-actions">
          <label htmlFor="auto-refresh-toggle" className="muted-text">Auto-refresh</label>
          <input
            id="auto-refresh-toggle"
            type="checkbox"
            checked={autoRefresh}
            onChange={(e) => setAutoRefresh(e.target.checked)}
          />
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => loadSystemHealth(true)}
            disabled={refreshing}
          >
            {refreshing ? 'Refreshing...' : 'Refresh now'}
          </button>
        </div>
      </div>

      {/* Overall Status */}
      <div className="card status-card">
        <div className="status-indicator">
          <div
            className="status-circle"
            style={{ backgroundColor: getStatusColor(systemHealth?.status) }}
          ></div>
          <div className="status-text">
            <h2>System Status</h2>
            <p className="status-value" style={{ color: getStatusColor(systemHealth?.status) }}>
              {systemHealth?.status?.toUpperCase() || 'UNKNOWN'}
            </p>
          </div>
        </div>
        
        {systemHealth?.statistics && (
          <div className="stats-inline">
            <div className="stat-item">
              <span className="stat-label">Total Anomalies:</span>
              <span className="stat-value">{systemHealth.statistics.total_anomalies}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">RCA Reports:</span>
              <span className="stat-value">{systemHealth.statistics.total_rca_reports}</span>
            </div>
          </div>
        )}
      </div>

      {/* Current Metrics */}
      {metrics && (
        <div className="card">
          <h2>Performance Metrics</h2>
          <div className="metrics-detailed">
            <div className="metric-card">
              <div className="metric-header">
                <h3>CPU Usage</h3>
                <span
                  className="metric-status"
                  style={{ color: getMetricStatus(metrics.cpu_usage, 80).color }}
                >
                  {getMetricStatus(metrics.cpu_usage, 80).status}
                </span>
              </div>
              <div className="metric-value-large">{metrics.cpu_usage?.toFixed(1)}%</div>
              <div className="metric-progress">
                <div
                  className="metric-progress-bar"
                  style={{
                    width: `${metrics.cpu_usage}%`,
                    backgroundColor: getMetricStatus(metrics.cpu_usage, 80).color
                  }}
                ></div>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-header">
                <h3>Memory Usage</h3>
                <span
                  className="metric-status"
                  style={{ color: getMetricStatus(metrics.memory_usage, 85).color }}
                >
                  {getMetricStatus(metrics.memory_usage, 85).status}
                </span>
              </div>
              <div className="metric-value-large">{metrics.memory_usage?.toFixed(1)}%</div>
              <div className="metric-progress">
                <div
                  className="metric-progress-bar"
                  style={{
                    width: `${metrics.memory_usage}%`,
                    backgroundColor: getMetricStatus(metrics.memory_usage, 85).color
                  }}
                ></div>
              </div>
              {metrics.memory_available_mb && (
                <div className="metric-info">
                  Available: {metrics.memory_available_mb.toFixed(0)} MB
                </div>
              )}
            </div>

            <div className="metric-card">
              <div className="metric-header">
                <h3>Disk Usage</h3>
                <span
                  className="metric-status"
                  style={{ color: getMetricStatus(metrics.disk_usage, 90).color }}
                >
                  {getMetricStatus(metrics.disk_usage, 90).status}
                </span>
              </div>
              <div className="metric-value-large">{metrics.disk_usage?.toFixed(1)}%</div>
              <div className="metric-progress">
                <div
                  className="metric-progress-bar"
                  style={{
                    width: `${metrics.disk_usage}%`,
                    backgroundColor: getMetricStatus(metrics.disk_usage, 90).color
                  }}
                ></div>
              </div>
              {metrics.disk_free_gb && (
                <div className="metric-info">
                  Free: {metrics.disk_free_gb.toFixed(1)} GB
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Recent Anomalies */}
      {systemHealth?.recent_anomalies && systemHealth.recent_anomalies.length > 0 && (
        <div className="card">
          <h2>Recent Anomalies</h2>
          <div className="anomalies-summary">
            {systemHealth.recent_anomalies.map((anomaly, index) => (
              <div key={index} className="anomaly-summary-item">
                <span className={`badge badge-${anomaly.severity?.toLowerCase()}`}>
                  {anomaly.severity}
                </span>
                <span className="anomaly-desc">{anomaly.description}</span>
                <span className="anomaly-time">
                  {new Date(anomaly.timestamp).toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default SystemHealth;
