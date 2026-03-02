# ARCA Platform - Automated Root Cause Analysis

![ARCA Platform](https://img.shields.io/badge/ARCA-Platform-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![React](https://img.shields.io/badge/React-18+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-red)

## Overview

**ARCA (Automated Root Cause Analysis) Platform** is a comprehensive system designed to automatically detect, analyze, and provide recommendations for deployment errors and system anomalies. The platform uses a combination of threshold-based detection, statistical analysis, and rule-based reasoning to identify root causes and generate actionable recommendations.

## Features

### Core Capabilities

- ✅ **Real-time Anomaly Detection**
  - Log analysis with keyword detection
  - Metric threshold monitoring (CPU, Memory, Disk)
  - Statistical anomaly detection
  - Severity classification (Critical, High, Medium, Low)

- ✅ **Root Cause Analysis**
  - Pattern-based rule matching
  - Event correlation across time windows
  - Causal chain generation
  - Confidence scoring

- ✅ **Intelligent Recommendations**
  - Context-aware fix suggestions
  - Historical fix tracking
  - Priority-based recommendation ranking

- ✅ **Real-time Monitoring Dashboard**
  - System health visualization
  - Anomaly timeline
  - RCA reports
  - Alert management

- ✅ **Alert System**
  - Multi-channel notifications
  - Severity-based filtering
  - Alert acknowledgment

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  Dashboard | System Health | Anomalies | RCA | Alerts   │
└─────────────────────────────────────────────────────────┘
                            ↓ REST API
┌─────────────────────────────────────────────────────────┐
│                  Backend (Flask/Python)                  │
├─────────────────────────────────────────────────────────┤
│  Presentation Layer                                      │
│    - DashboardController (REST API)                      │
│    - AlertSystem                                         │
├─────────────────────────────────────────────────────────┤
│  Business Logic Layer                                    │
│    - RCAEngine (Root Cause Analysis)                     │
│    - RecommendationEngine                                │
│    - EventCorrelator                                     │
├─────────────────────────────────────────────────────────┤
│  Analysis Layer                                          │
│    - AnomalyDetector (Hybrid Detection)                  │
├─────────────────────────────────────────────────────────┤
│  Collection Layer                                        │
│    - LogCollector                                        │
│    - MetricCollector                                     │
│    - SlidingWindow (Data Buffer)                         │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              Data Layer (MongoDB Atlas)                  │
│    Anomalies | RCA Results | Metrics | Alerts           │
└─────────────────────────────────────────────────────────┘
```

## Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: Flask 3.0
- **Database**: MongoDB
- **Key Libraries**:
  - `pymongo` - MongoDB driver
  - `psutil` - System metrics
  - `numpy` - Statistical analysis
  - `flask-cors` - CORS support

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Styling**: CSS3 (Custom)

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- MongoDB (local or Atlas)
- Git

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd arca-platform/backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   # Copy example env file
   cp .env.example .env
   
   # Edit .env with your settings
   # Set MONGODB_URI, SECRET_KEY, etc.
   ```

5. **Start the backend server**:
   ```bash
   python app.py
   ```

   Backend will run on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd arca-platform/frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

   Frontend will run on `http://localhost:3000`

4. **Build for production**:
   ```bash
   npm run build
   ```

## API Documentation

### Health & Status

- `GET /api/health` - Health check
- `GET /api/system-health` - System health overview
- `GET /api/statistics` - Platform statistics

### Anomaly Detection

- `GET /api/anomalies` - Get anomalies (filter by severity)
- `POST /api/detect` - Detect anomalies from logs/metrics

**Example Request**:
```json
POST /api/detect
{
  "logs": [
    {
      "level": "ERROR",
      "message": "Deployment failed",
      "timestamp": "2026-03-02T10:00:00Z"
    }
  ],
  "metrics": {
    "cpu_usage": 95.5,
    "memory_usage": 88.2
  }
}
```

### Root Cause Analysis

- `POST /api/rca/analyze` - Analyze root cause
- `GET /api/rca-reports` - Get RCA reports
- `GET /api/rca-reports/:id` - Get specific report

### Alerts

- `GET /api/alerts` - Get all alerts
- `POST /api/alerts/acknowledge` - Acknowledge alert

### Metrics

- `GET /api/metrics/current` - Current system metrics
- `GET /api/metrics/history` - Historical metrics

## Configuration

### Backend Configuration (`.env`)

```env
# Application Settings
FLASK_ENV=development
API_PORT=5000
DEBUG=True

# MongoDB
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=arca_db

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# CORS
ALLOWED_ORIGINS=http://localhost:3000

# Thresholds
CPU_THRESHOLD=80
MEMORY_THRESHOLD=85
RESPONSE_TIME_THRESHOLD=2000
```

### Frontend Configuration

Create `.env` file in frontend directory:

```env
VITE_API_URL=http://localhost:5000/api
```

## Usage Examples

### 1. Manual Anomaly Detection

```python
from modules.anomaly_detector import AnomalyDetector, Threshold

# Create detector
thresholds = {
    'cpu_usage': Threshold(min_value=0, max_value=80),
    'memory_usage': Threshold(min_value=0, max_value=85)
}
detector = AnomalyDetector(thresholds)

# Detect from metrics
metrics = {'cpu_usage': 95.5, 'memory_usage': 78.0}
anomalies = detector.detect_metric_anomalies(metrics)
```

### 2. Root Cause Analysis

```python
from modules.rca_engine import RCAEngine
from modules.event_correlator import EventCorrelator

# Correlate events
correlator = EventCorrelator(window_size_minutes=5)
correlated = correlator.correlate_anomalies(anomalies)

# Analyze root cause
engine = RCAEngine([])
result = engine.analyze_root_cause(correlated)

print(f"Root Cause: {result.root_cause}")
print(f"Confidence: {result.confidence}")
print(f"Recommendations: {result.recommendations}")
```

## Project Structure

```
arca-platform/
├── backend/
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── anomaly_detector.py
│   │   ├── rca_engine.py
│   │   ├── log_collector.py
│   │   ├── metric_collector.py
│   │   ├── event_correlator.py
│   │   ├── recommendation_engine.py
│   │   ├── alert_system.py
│   │   └── sliding_window.py
│   ├── app.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── Navbar.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Anomalies.jsx
│   │   │   ├── RCAReports.jsx
│   │   │   ├── Alerts.jsx
│   │   │   └── SystemHealth.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Development

### Running Tests

Backend:
```bash
cd backend
python -m pytest
```

Frontend:
```bash
cd frontend
npm test
```

### Code Style

Backend follows PEP 8 guidelines. Frontend uses ESLint.

```bash
# Backend
flake8 backend/

# Frontend
npm run lint
```

## Deployment

### AWS EC2 (Backend)

1. Launch EC2 instance (Ubuntu 22.04)
2. Install dependencies
3. Configure Nginx reverse proxy
4. Setup systemd service
5. Configure security groups

See `Assignment5/deployment-scripts/` for deployment scripts.

### Vercel (Frontend)

1. Connect repository to Vercel
2. Configure build settings:
   - Build Command: `npm run build`
   - Output Directory: `dist`
3. Set environment variables
4. Deploy

## Monitoring

The platform includes built-in monitoring:

- System health dashboard
- Real-time metrics tracking
- Anomaly history
- Alert management
- RCA report archival

## Troubleshooting

### Backend Issues

**MongoDB Connection Error**:
```bash
# Check MongoDB is running
sudo systemctl status mongodb

# Check connection string in .env
MONGODB_URI=mongodb://localhost:27017/
```

**Port Already in Use**:
```bash
# Change port in .env
API_PORT=5001
```

### Frontend Issues

**API Connection Error**:
- Check backend is running
- Verify VITE_API_URL in .env
- Check CORS settings

**Build Errors**:
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

This project is part of academic coursework for CS331 - Software Engineering.

## Acknowledgments

- Based on assignments from CS331 Software Engineering course
- Implements layered architecture pattern
- Uses industry-standard tools and practices

## Contact

For questions or issues, please open an issue on the repository.

---

**Built with ❤️ for automated system reliability**
