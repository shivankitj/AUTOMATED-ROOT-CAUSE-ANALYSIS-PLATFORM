import React, { useState, useEffect } from 'react';
import { getStatistics, getAnomalies, getRCAReports, getCurrentMetrics } from '../services/api';
import './Dashboard.css';

function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState(null);
  const [recentAnomalies, setRecentAnomalies] = useState([]);
  const [recentReports, setRecentReports] = useState([]);
  const [currentMetrics, setCurrentMetrics] = useState(null);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [recentLimit, setRecentLimit] = useState(5);

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(() => loadDashboardData(), 30000);
    return () => clearInterval(interval);
  }, [recentLimit]);

  const loadDashboardData = async (isManual = false) => {
    try {
      if (!stats) {
        setLoading(true);
      }
      if (isManual) {
        setRefreshing(true);
      }
      setError(null);

      const [statsRes, anomaliesRes, reportsRes, metricsRes] = await Promise.all([
        getStatistics(),
        getAnomalies({ limit: recentLimit }),
        getRCAReports({ limit: recentLimit }),
        getCurrentMetrics()
      ]);

      setStats(statsRes.data);
      setRecentAnomalies(anomaliesRes.data.anomalies || []);
      setRecentReports(reportsRes.data.reports || []);
      setCurrentMetrics(metricsRes.data);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Error loading dashboard:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  if (loading && !stats) {
    return <div className="loading">Loading dashboard...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="dashboard">
      <div className="page-header page-header-row">
        <div>
          <h1>Dashboard</h1>
          <p>Real-time monitoring and root cause analysis</p>
          <div className="muted-text">
            Last updated: {lastUpdated ? lastUpdated.toLocaleTimeString() : 'Not yet available'}
          </div>
        </div>
        <div className="page-actions">
          <label htmlFor="dashboard-limit" className="muted-text">List size</label>
          <select
            id="dashboard-limit"
            className="input-control"
            value={recentLimit}
            onChange={(e) => setRecentLimit(Number(e.target.value))}
          >
            <option value={5}>5</option>
            <option value={10}>10</option>
            <option value={20}>20</option>
          </select>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => loadDashboardData(true)}
            disabled={refreshing}
          >
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-title">Total Anomalies</span>
            <span className="stat-card-icon">🔴</span>
          </div>
          <div className="stat-card-value">{stats?.total_anomalies || 0}</div>
        </div>

        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-title">Critical Anomalies</span>
            <span className="stat-card-icon">⚠️</span>
          </div>
          <div className="stat-card-value">{stats?.critical_anomalies || 0}</div>
        </div>

        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-title">RCA Reports</span>
            <span className="stat-card-icon">📊</span>
          </div>
          <div className="stat-card-value">{stats?.total_rca_reports || 0}</div>
        </div>

        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-title">Total Alerts</span>
            <span className="stat-card-icon">🔔</span>
          </div>
          <div className="stat-card-value">{stats?.total_alerts || 0}</div>
        </div>
      </div>

      {/* Current System Metrics */}
      {currentMetrics && (
        <div className="card">
          <h2>Current System Metrics</h2>
          <div className="metrics-grid">
            <div className="metric-item">
              <div className="metric-label">CPU Usage</div>
              <div className="metric-value">{currentMetrics.cpu_usage?.toFixed(1) || 0}%</div>
              <div className={`metric-bar ${getMetricStatus(currentMetrics.cpu_usage, 80)}`}>
                <div className="metric-fill" style={{ width: `${currentMetrics.cpu_usage || 0}%` }}></div>
              </div>
            </div>
            <div className="metric-item">
              <div className="metric-label">Memory Usage</div>
              <div className="metric-value">{currentMetrics.memory_usage?.toFixed(1) || 0}%</div>
              <div className={`metric-bar ${getMetricStatus(currentMetrics.memory_usage, 85)}`}>
                <div className="metric-fill" style={{ width: `${currentMetrics.memory_usage || 0}%` }}></div>
              </div>
            </div>
            <div className="metric-item">
              <div className="metric-label">Disk Usage</div>
              <div className="metric-value">{currentMetrics.disk_usage?.toFixed(1) || 0}%</div>
              <div className={`metric-bar ${getMetricStatus(currentMetrics.disk_usage, 90)}`}>
                <div className="metric-fill" style={{ width: `${currentMetrics.disk_usage || 0}%` }}></div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-2">
        {/* Recent Anomalies */}
        <div className="card">
          <h2>Recent Anomalies</h2>
          {recentAnomalies.length === 0 ? (
            <p className="empty-state">No recent anomalies</p>
          ) : (
            <div className="anomaly-list">
              {recentAnomalies.map((anomaly, index) => (
                <div key={index} className="anomaly-item">
                  <div className="anomaly-header">
                    <span className={`badge badge-${anomaly.severity?.toLowerCase()}`}>
                      {anomaly.severity}
                    </span>
                    <span className="anomaly-time">
                      {formatTime(anomaly.timestamp)}
                    </span>
                  </div>
                  <div className="anomaly-description">{anomaly.description}</div>
                  <div className="anomaly-metric">{anomaly.metric}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent RCA Reports */}
        <div className="card">
          <h2>Recent RCA Reports</h2>
          {recentReports.length === 0 ? (
            <p className="empty-state">No recent reports</p>
          ) : (
            <div className="report-list">
              {recentReports.map((report, index) => (
                <div key={index} className="report-item">
                  <div className="report-header">
                    <span className="report-cause">{report.root_cause}</span>
                    <span className="report-confidence">
                      {((report.confidence || 0) * 100).toFixed(0)}% confidence
                    </span>
                  </div>
                  <div className="report-time">{formatTime(report.timestamp)}</div>
                  {report.recommendations && report.recommendations.length > 0 && (
                    <div className="report-rec">
                      {report.recommendations[0]}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function getMetricStatus(value, threshold) {
  if (value >= threshold) return 'critical';
  if (value >= threshold * 0.8) return 'warning';
  return 'normal';
}

function formatTime(timestamp) {
  if (!timestamp) return 'N/A';
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now - date;
  
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  
  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  return `${days}d ago`;
}

export default Dashboard;
