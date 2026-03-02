import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health & Status
export const getHealth = () => api.get('/health');
export const getSystemHealth = () => api.get('/system-health');
export const getStatistics = () => api.get('/statistics');

// Anomalies
export const getAnomalies = (params) => api.get('/anomalies', { params });
export const detectAnomalies = (data) => api.post('/detect', data);

// RCA Reports
export const getRCAReports = (params) => api.get('/rca-reports', { params });
export const analyzeRootCause = (data) => api.post('/rca/analyze', data);
export const getRCAReportDetail = (reportId) => api.get(`/rca-reports/${reportId}`);

// Alerts
export const getAlerts = () => api.get('/alerts');
export const acknowledgeAlert = (alertId) => api.post('/alerts/acknowledge', { alert_id: alertId });

// Metrics
export const getCurrentMetrics = () => api.get('/metrics/current');
export const getMetricsHistory = (params) => api.get('/metrics/history', { params });

// Logs
export const uploadLogs = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/logs/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export default api;
