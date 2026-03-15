# Frontend ↔ Backend ↔ MongoDB Connection Guide

## 🔄 Complete Data Flow: How Database Values Show on Frontend

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA FLOW DIAGRAM                         │
└─────────────────────────────────────────────────────────────┘

MongoDB (Database)
    │
    │ PyMongo Driver
    │ (Read/Write Operations)
    ▼
Flask Backend (Port 5000)
    │
    │ REST API Endpoints
    │ /api/anomalies
    │ /api/rca-reports
    │ /api/statistics
    │ /api/metrics/current
    │
    │ JSON Responses
    │ CORS Headers
    ▼
React Frontend (Port 5173 or 3000)
    │
    │ Axios HTTP Client
    │ api.js Service Layer
    │
    ▼
React Components
    │
    │ useState/useEffect
    │ Data Rendering
    ▼
Browser Display
```

---

## 📋 Step-by-Step Connection Process

### 1. MongoDB Stores Data

MongoDB collections:
```javascript
arca_db
  ├── anomalies       // Detected anomalies
  ├── rca_results     // Root cause analysis reports
  ├── metrics         // System metrics history
  ├── logs            // Application logs
  └── alerts          // Alert notifications
```

### 2. Backend Connects to MongoDB

**File**: `backend/app.py` (Line 33-39)

```python
# MongoDB connection
try:
    mongo_client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
    db = mongo_client[os.getenv('MONGODB_DB_NAME', 'arca_db')]
    print("✅ MongoDB connected successfully")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    db = None
```

**Environment Variable**: `backend/.env`
```env
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=arca_db
```

### 3. Backend Exposes REST API Endpoints

**Example**: Get anomalies endpoint

**File**: `backend/app.py` (Lines ~117-135)

```python
@app.route('/api/anomalies', methods=['GET'])
def get_anomalies():
    """Get all anomalies with optional filtering"""
    try:
        severity = request.args.get('severity')
        limit = int(request.args.get('limit', 50))
        
        query = {}
        if severity:
            query['severity'] = severity.upper()
        
        if db:
            # Query MongoDB
            anomalies = list(db.anomalies.find(query).sort('timestamp', -1).limit(limit))
            for anomaly in anomalies:
                anomaly['_id'] = str(anomaly['_id'])
        else:
            anomalies = []
        
        # Return JSON response
        return jsonify({
            'total': len(anomalies),
            'anomalies': anomalies
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

**Available Endpoints**:
- `GET /api/anomalies` → Returns anomaly list
- `GET /api/rca-reports` → Returns RCA reports
- `GET /api/statistics` → Returns platform statistics
- `GET /api/metrics/current` → Returns current system metrics
- `GET /api/system-health` → Returns system health overview
- `GET /api/alerts` → Returns alerts

### 4. Backend Enables CORS

**File**: `backend/app.py` (Line 30)

```python
# Configure CORS to allow frontend requests
CORS(app, origins=os.getenv('ALLOWED_ORIGINS', '*').split(','))
```

**Environment Variable**: `backend/.env`
```env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 5. Frontend Configures API Client

**File**: `frontend/src/services/api.js` (Lines 1-10)

```javascript
import axios from 'axios';

// Read backend URL from environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

**Environment Variable**: `frontend/.env`
```env
VITE_API_URL=http://localhost:5000/api
```

### 6. Frontend Defines API Functions

**File**: `frontend/src/services/api.js`

```javascript
// API function to get anomalies
export const getAnomalies = (params) => api.get('/anomalies', { params });

// API function to get statistics
export const getStatistics = () => api.get('/statistics');

// API function to get RCA reports
export const getRCAReports = (params) => api.get('/rca-reports', { params });

// API function to get current metrics
export const getCurrentMetrics = () => api.get('/metrics/current');
```

### 7. React Components Fetch Data

**File**: `frontend/src/pages/Dashboard.jsx` (Lines 16-31)

```javascript
const loadDashboardData = async () => {
  try {
    setLoading(true);
    setError(null);

    // Call multiple API endpoints in parallel
    const [statsRes, anomaliesRes, reportsRes, metricsRes] = await Promise.all([
      getStatistics(),           // GET /api/statistics
      getAnomalies({ limit: 5 }), // GET /api/anomalies?limit=5
      getRCAReports({ limit: 5 }),// GET /api/rca-reports?limit=5
      getCurrentMetrics()         // GET /api/metrics/current
    ]);

    // Update component state with fetched data
    setStats(statsRes.data);
    setRecentAnomalies(anomaliesRes.data.anomalies || []);
    setRecentReports(reportsRes.data.reports || []);
    setCurrentMetrics(metricsRes.data);
  } catch (err) {
    console.error('Error loading dashboard:', err);
    setError('Failed to load dashboard data');
  } finally {
    setLoading(false);
  }
};
```

### 8. React Components Render Data

**File**: `frontend/src/pages/Dashboard.jsx`

```javascript
return (
  <div className="dashboard">
    {/* Display statistics from MongoDB */}
    <div className="stats-section">
      <div className="stat-card">
        <h3>Total Anomalies</h3>
        <p>{stats?.total_anomalies || 0}</p>
      </div>
      <div className="stat-card">
        <h3>RCA Reports</h3>
        <p>{stats?.total_rca_reports || 0}</p>
      </div>
    </div>
    
    {/* Display recent anomalies from MongoDB */}
    <div className="anomalies-section">
      <h2>Recent Anomalies</h2>
      {recentAnomalies.map(anomaly => (
        <div key={anomaly.id} className="anomaly-item">
          <span>{anomaly.metric}</span>
          <span>{anomaly.severity}</span>
          <span>{anomaly.description}</span>
        </div>
      ))}
    </div>
  </div>
);
```

---

## 🐛 Why Your Frontend Isn't Showing Database Values

### Issue Checklist:

- [ ] **MongoDB Not Running**
  ```powershell
  # Check if MongoDB is running
  Get-Service -Name MongoDB*
  
  # Start MongoDB
  net start MongoDB
  ```

- [ ] **No .env Files**
  - ❌ `backend/.env` was missing
  - ❌ `frontend/.env` was missing
  - ✅ **Now created both files**

- [ ] **MongoDB Has No Data**
  ```powershell
  # Run seed script to populate database
  cd arca-platform
  python seed.py
  ```

- [ ] **Backend Not Running**
  ```powershell
  cd backend
  python app.py
  ```

- [ ] **Frontend Not Running**
  ```powershell
  cd frontend
  npm run dev
  ```

- [ ] **CORS Issues**
  - Check browser console for CORS errors
  - Verify `ALLOWED_ORIGINS` in backend/.env

- [ ] **Wrong API URL**
  - Check `VITE_API_URL` in frontend/.env
  - Should match backend port (default: 5000)

---

## ✅ Complete Setup Steps

### Step 1: Start MongoDB

```powershell
# Option 1: Windows Service
net start MongoDB

# Option 2: Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Verify MongoDB is running
netstat -an | findstr "27017"
```

### Step 2: Populate Database

```powershell
cd C:\Users\Shivankit Jaiswal\OneDrive\Desktop\LAB_Software\arca-platform
python seed.py
```

**Expected Output**:
```
✅ Connected to MongoDB: arca_db
🧹 Cleared collection: anomalies (0 documents)
📊 Seeding anomalies...
✅ Inserted 23 anomalies
🔍 Seeding RCA results...
✅ Inserted 5 RCA reports
...
✅ Database seeding completed successfully!
```

### Step 3: Start Backend

```powershell
cd backend
python app.py
```

**Expected Output**:
```
✅ MongoDB connected successfully
==================================================
🚀 ARCA Platform Backend Starting...
📡 Port: 5000
🐛 Debug: True
🗄️  Database: arca_db
==================================================
 * Running on http://0.0.0.0:5000
```

**Test Backend**:
```powershell
# In another terminal
curl http://localhost:5000/api/health
# Should return: {"status":"healthy",...}

curl http://localhost:5000/api/statistics
# Should return: {"total_anomalies":23,...}
```

### Step 4: Start Frontend

```powershell
cd frontend
npm run dev
```

**Expected Output**:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Step 5: Open Browser

Navigate to: `http://localhost:5173` (or port shown)

**What You Should See**:
- Dashboard with statistics (total anomalies, RCA reports, alerts)
- Recent anomalies list
- System health metrics
- Charts and visualizations

---

## 🔍 Troubleshooting

### Problem: "Failed to load dashboard data"

**Check Browser Console** (F12):
```javascript
// Look for errors like:
// "Network Error" → Backend not running
// "CORS Error" → Check ALLOWED_ORIGINS
// "404 Not Found" → Wrong API URL
```

**Verify Backend Response**:
```powershell
# Test each endpoint
curl http://localhost:5000/api/statistics
curl http://localhost:5000/api/anomalies
curl http://localhost:5000/api/rca-reports
```

### Problem: Backend returns empty arrays

**Check MongoDB Data**:
```powershell
# Connect to MongoDB
mongosh

# Use database
use arca_db

# Check collections
db.anomalies.countDocuments()
db.rca_results.countDocuments()

# If 0, run seed.py again
```

### Problem: CORS Error

**Error**: `Access to XMLHttpRequest blocked by CORS policy`

**Solution**: Check `backend/.env`
```env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

Restart backend after changing .env file.

### Problem: Connection Refused

**Error**: `ERR_CONNECTION_REFUSED`

**Check**:
1. Backend is running: `netstat -an | findstr "5000"`
2. Correct port in frontend/.env: `VITE_API_URL=http://localhost:5000/api`
3. No firewall blocking

---

## 📊 Data Flow Example: Loading Dashboard

```
1. User opens http://localhost:5173/
   │
2. Dashboard.jsx component mounts
   │
3. useEffect() hook triggers
   │
4. loadDashboardData() function runs
   │
5. axios calls:
   ├─ GET http://localhost:5000/api/statistics
   ├─ GET http://localhost:5000/api/anomalies?limit=5
   ├─ GET http://localhost:5000/api/rca-reports?limit=5
   └─ GET http://localhost:5000/api/metrics/current
   │
6. Backend receives requests
   │
7. Backend queries MongoDB:
   ├─ db.anomalies.count_documents({})
   ├─ db.anomalies.find().sort().limit(5)
   ├─ db.rca_results.find().sort().limit(5)
   └─ MetricCollector.get_metric_snapshot()
   │
8. Backend returns JSON:
   {
     "total_anomalies": 23,
     "anomalies": [{...}, {...}],
     "reports": [{...}, {...}],
     "metrics": {...}
   }
   │
9. Frontend receives data
   │
10. React state updates:
    ├─ setStats({...})
    ├─ setRecentAnomalies([...])
    ├─ setRecentReports([...])
    └─ setCurrentMetrics({...})
    │
11. Component re-renders
    │
12. Data displayed in browser! 🎉
```

---

## 🚀 Quick Start Commands

Run these in order:

```powershell
# Terminal 1: Start MongoDB
net start MongoDB

# Terminal 2: Seed Database
cd C:\Users\Shivankit Jaiswal\OneDrive\Desktop\LAB_Software\arca-platform
python seed.py

# Terminal 3: Start Backend
cd backend
python app.py

# Terminal 4: Start Frontend
cd frontend
npm run dev

# Open browser: http://localhost:5173
```

---

## 📝 Environment Variables Summary

### Backend (.env)
```env
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=arca_db
API_PORT=5000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:5000/api
```

---

## ✅ Verification Checklist

After setup, verify:

- [ ] MongoDB service running
- [ ] Collections have data (run seed.py)
- [ ] Backend running on port 5000
- [ ] Backend responds to: `http://localhost:5000/api/health`
- [ ] Frontend running on port 5173
- [ ] Browser shows dashboard with data
- [ ] No errors in browser console (F12)
- [ ] No CORS errors


Done by
Lohith Aditya Tadikonda
---

**Last Updated**: March 10, 2026  
**Issue**: Frontend not showing database values  
**Solution**: Missing .env files, MongoDB not running, or no seeded data
