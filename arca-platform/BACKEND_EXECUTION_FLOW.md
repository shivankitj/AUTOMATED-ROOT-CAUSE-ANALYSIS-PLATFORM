# ARCA Platform - Backend Execution Flow & Dependencies

## 📋 Table of Contents
1. [Application Startup Flow](#application-startup-flow)
2. [Module Dependencies](#module-dependencies)
3. [API Request Flow](#api-request-flow)
4. [Data Processing Pipeline](#data-processing-pipeline)
5. [Module Interaction Diagram](#module-interaction-diagram)

---

## 🚀 Application Startup Flow

### Entry Point: `backend/app.py`

```
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION STARTUP                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────┐
    │  1. Import Dependencies                   │
    │     - Flask, CORS, PyMongo                │
    │     - dotenv for environment variables    │
    │     - All ARCA modules                    │
    └───────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────┐
    │  2. Load Environment Variables            │
    │     - MONGODB_URI                         │
    │     - MONGODB_DB_NAME                     │
    │     - ALLOWED_ORIGINS                     │
    │     - Threshold values (CPU, Memory, etc) │
    └───────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────┐
    │  3. Initialize Flask App                  │
    │     - Configure CORS                      │
    │     - Connect to MongoDB                  │
    └───────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────┐
    │  4. Initialize ARCA Components            │
    │     ✓ AnomalyDetector (with thresholds)   │
    │     ✓ RCAEngine (with rules)              │
    │     ✓ EventCorrelator (5-min window)      │
    │     ✓ RecommendationEngine (with rules)   │
    │     ✓ AlertSystem                         │
    └───────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────┐
    │  5. Register API Routes                   │
    │     - Health endpoints                    │
    │     - Anomaly detection endpoints         │
    │     - RCA endpoints                       │
    │     - Metrics endpoints                   │
    │     - Log endpoints                       │
    └───────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────┐
    │  6. Start Flask Server                    │
    │     - Default: localhost:5000             │
    │     - Production: Gunicorn WSGI           │
    └───────────────────────────────────────────┘
```

---

## 🔗 Module Dependencies

### 1. **app.py** (Main Application)
**Dependencies:**
- Flask (web framework)
- flask-cors (CORS handling)
- pymongo (MongoDB client)
- python-dotenv (environment variables)

**Module Imports:**
- `anomaly_detector.py` → AnomalyDetector, Threshold
- `rca_engine.py` → RCAEngine
- `log_collector.py` → LogCollector
- `metric_collector.py` → MetricCollector
- `event_correlator.py` → EventCorrelator
- `recommendation_engine.py` → RecommendationEngine
- `alert_system.py` → AlertSystem

**Initialization Order:**
```python
1. thresholds (dict) → defines limits for metrics
2. anomaly_detector → uses thresholds
3. rca_engine → uses empty rules list (loads defaults)
4. event_correlator → uses 5-minute time window
5. recommendation_engine → uses empty rules (loads defaults)
6. alert_system → no dependencies
```

---

### 2. **anomaly_detector.py** (Anomaly Detection)
**External Dependencies:**
- `statistics` (std deviation calculations)
- `datetime` (timestamp handling)

**Internal Dependencies:** None

**Classes:**
- `Anomaly` - Data class for anomaly representation
- `Threshold` - Configuration for detection limits
- `AnomalyDetector` - Main detection engine

**Key Methods:**
```python
detect_log_anomalies(logs: List[Dict]) → List[Anomaly]
  ├─ Analyzes log entries for error patterns
  ├─ Counts ERROR/CRITICAL levels
  └─ Returns list of detected anomalies

detect_metric_anomalies(metrics: Dict) → List[Anomaly]
  ├─ Compares metrics against thresholds
  ├─ Calculates severity based on deviation
  └─ Returns list of metric anomalies

detect_statistical_anomalies(data: List[float]) → List[Anomaly]
  ├─ Uses Z-score algorithm (mean ± std_dev)
  ├─ Detects outliers beyond threshold
  └─ Returns statistical anomalies
```

---

### 3. **rca_engine.py** (Root Cause Analysis)
**External Dependencies:**
- `datetime`, `timedelta` (time calculations)
- `dataclasses` (data structures)

**Internal Dependencies:**
- Receives `CorrelatedEvent` from EventCorrelator

**Classes:**
- `CorrelatedEvent` - Group of related anomalies
- `Rule` - RCA pattern matching rule
- `RCAResult` - Analysis result with recommendations

**Key Methods:**
```python
analyze_root_cause(correlated_events) → RCAResult
  ├─ apply_rule() - Matches events to rules
  ├─ _calculate_confidence() - Determines certainty
  ├─ build_causal_chain() - Creates event sequence
  └─ Returns RCAResult with root cause

apply_rule(rule, events) → bool
  ├─ Checks pattern matching
  ├─ Validates conditions
  └─ Returns match status
```

**Default Rules:**
- RESOURCE_EXHAUSTION (CPU + Memory + Response Time)
- DEPLOYMENT_CONFIGURATION_ERROR (Deployment failures)
- DATABASE_CONNECTION_POOL_EXHAUSTION (Connection errors)
- MEMORY_LEAK (Gradual memory increase)
- NETWORK_LATENCY (High response times)

---

### 4. **event_correlator.py** (Event Correlation)
**External Dependencies:**
- `datetime`, `timedelta` (time window management)
- `dataclasses` (data structures)

**Internal Dependencies:**
- Receives `Anomaly` objects from AnomalyDetector

**Classes:**
- `CorrelatedEvent` - Grouped anomalies
- `EventCorrelator` - Correlation engine

**Key Methods:**
```python
correlate_anomalies(anomalies: List) → List[CorrelatedEvent]
  ├─ _group_by_timestamp() - Time window grouping
  ├─ _calculate_correlation_score() - Similarity scoring
  ├─ _extract_affected_components() - Component mapping
  └─ Returns correlated event groups

_group_by_timestamp(anomalies) → Dict
  ├─ Groups by time windows (5-min default)
  └─ Returns time-bucketed anomalies
```

---

### 5. **recommendation_engine.py** (Recommendations)
**External Dependencies:**
- `datetime` (timestamp handling)

**Internal Dependencies:**
- Receives `RCAResult` from RCAEngine

**Classes:**
- `Recommendation` - Action recommendation
- `Fix` - Historical fix record
- `RecommendationEngine` - Recommendation generator

**Key Methods:**
```python
generate_recommendations(rca_result) → List[Dict]
  ├─ _match_cause_to_action() - Maps cause to fixes
  ├─ get_historical_fixes() - Retrieves past solutions
  ├─ prioritize_recommendations() - Sorts by impact
  └─ Returns prioritized recommendations

_match_cause_to_action(root_cause) → List[Dict]
  ├─ Looks up predefined recommendations
  └─ Returns applicable actions
```

**Default Recommendation Rules:**
- RESOURCE_EXHAUSTION → Scale resources, optimize queries
- DEPLOYMENT_ERROR → Validate config, rollback
- DATABASE_ISSUES → Increase pool, add retries
- MEMORY_LEAK → Analyze heap, review caching
- NETWORK_LATENCY → Check network, add circuit breaker

---

### 6. **alert_system.py** (Alerting)
**External Dependencies:**
- `datetime` (timestamps)
- `dataclasses` (data structures)

**Internal Dependencies:** None

**Classes:**
- `Alert` - Alert data structure
- `AlertSystem` - Alert manager

**Key Methods:**
```python
send_alert(alert_data: Dict) → None
  ├─ _format_alert_message() - Formats message
  ├─ _send_notification() - Sends to channels
  └─ Adds to alert queue

acknowledge_alert(alert_id: str) → bool
  ├─ Marks alert as acknowledged
  └─ Removes from queue
```

---

### 7. **log_collector.py** (Log Collection)
**External Dependencies:**
- `datetime` (timestamps)
- `os`, `time` (file operations)

**Internal Dependencies:** None

**Classes:**
- `LogEntry` - Single log entry
- `LogCollector` - Log file monitor

**Key Methods:**
```python
read_new_logs() → List[LogEntry]
  ├─ Reads log file from last position
  ├─ Parses log format
  └─ Returns new entries

start_collection() → None
  ├─ Begins continuous monitoring
  └─ Reads at specified interval
```

---

### 8. **metric_collector.py** (Metrics Collection)
**External Dependencies:**
- `psutil` (system metrics)
- `datetime`, `time` (timing)

**Internal Dependencies:** None

**Classes:**
- `MetricCollector` - System metrics gatherer

**Key Methods:**
```python
collect_cpu_usage() → float
  └─ Uses psutil.cpu_percent()

collect_memory_usage() → float
  └─ Uses psutil.virtual_memory()

collect_disk_usage() → float
  └─ Uses psutil.disk_usage()

get_metric_snapshot() → Dict
  ├─ Collects all metrics at once
  └─ Returns complete snapshot
```

---

## 🔄 API Request Flow

### Example: Anomaly Detection Request

```
┌─────────────────────────────────────────────────────────────┐
│              POST /api/detect                                │
│   Body: { "logs": [...], "metrics": {...} }                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────┐
    │  1. Flask Route Handler                   │
    │     @app.route('/api/detect', POST)       │
    └───────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────┐
    │  2. Extract Request Data                  │
    │     logs = data.get('logs', [])           │
    │     metrics = data.get('metrics', {})     │
    └───────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────┐
    │  3. AnomalyDetector.detect_log_anomalies()│
    │     - Parses log entries                  │
    │     - Identifies error patterns           │
    │     - Returns log anomalies               │
    └───────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────┐
    │  4. AnomalyDetector.detect_metric_anomalies()│
    │     - Compares against thresholds         │
    │     - Calculates severity                 │
    │     - Returns metric anomalies            │
    └───────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────┐
    │  5. Store Anomalies in MongoDB            │
    │     db.anomalies.insert_one()             │
    └───────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────┐
    │  6. Check for Critical Anomalies          │
    │     Filter severity == 'CRITICAL'         │
    └───────────────────────────────────────────┘
                            │
                            ▼ (if critical)
    ┌───────────────────────────────────────────┐
    │  7. EventCorrelator.correlate_anomalies() │
    │     - Groups by time window               │
    │     - Calculates correlation              │
    │     - Returns correlated events           │
    └───────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────┐
    │  8. RCAEngine.analyze_root_cause()        │
    │     - Applies rules to events             │
    │     - Builds causal chain                 │
    │     - Returns RCA result                  │
    └───────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────┐
    │  9. Store RCA Result in MongoDB           │
    │     db.rca_results.insert_one()           │
    └───────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────┐
    │  10. AlertSystem.send_alert()             │
    │     - Creates alert                       │
    │     - Sends notifications                 │
    └───────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────┐
    │  11. Return JSON Response                 │
    │     {                                     │
    │       "detected_anomalies": count,        │
    │       "log_anomalies": [...],             │
    │       "metric_anomalies": [...],          │
    │       "critical_count": count             │
    │     }                                     │
    └───────────────────────────────────────────┘
```

---

## 🔀 Data Processing Pipeline

### Complete Flow: From Data Input to Recommendations

```
┌─────────────┐
│   INPUT     │
│  Logs +     │
│  Metrics    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│   ANOMALY DETECTION             │
│   (anomaly_detector.py)         │
│                                 │
│  • detect_log_anomalies()       │
│  • detect_metric_anomalies()    │
│  • detect_statistical_anomalies()│
└───────────┬─────────────────────┘
            │
            │ List[Anomaly]
            ▼
┌─────────────────────────────────┐
│   EVENT CORRELATION             │
│   (event_correlator.py)         │
│                                 │
│  • correlate_anomalies()        │
│  • Group by time window         │
│  • Calculate correlation score  │
└───────────┬─────────────────────┘
            │
            │ List[CorrelatedEvent]
            ▼
┌─────────────────────────────────┐
│   ROOT CAUSE ANALYSIS           │
│   (rca_engine.py)               │
│                                 │
│  • analyze_root_cause()         │
│  • Apply rules                  │
│  • Build causal chain           │
└───────────┬─────────────────────┘
            │
            │ RCAResult
            ├──────────────────────┐
            │                      │
            ▼                      ▼
┌───────────────────────┐  ┌──────────────────────┐
│  RECOMMENDATIONS      │  │   ALERT SYSTEM       │
│  (recommendation_     │  │   (alert_system.py)  │
│   engine.py)          │  │                      │
│                       │  │  • send_alert()      │
│  • generate_          │  │  • Notify channels   │
│    recommendations()  │  │                      │
│  • Prioritize actions │  └──────────────────────┘
└───────────────────────┘
            │
            │ List[Recommendation]
            ▼
┌─────────────────────────────────┐
│   STORAGE                       │
│   (MongoDB)                     │
│                                 │
│  • anomalies collection         │
│  • rca_results collection       │
│  • alerts collection            │
└─────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│   OUTPUT                        │
│   (API Response / Dashboard)    │
│                                 │
│  • Anomaly list                 │
│  • Root cause                   │
│  • Recommendations              │
│  • Alerts                       │
└─────────────────────────────────┘
```

---

## 📊 Module Interaction Diagram

```
                    ┌──────────────────────┐
                    │      app.py          │
                    │   (Main Flask App)   │
                    └──────────┬───────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
            ▼                  ▼                  ▼
    ┌──────────────┐   ┌──────────────┐  ┌──────────────┐
    │ LogCollector │   │MetricCollector│  │ MongoDB      │
    │              │   │              │  │ Client       │
    └──────┬───────┘   └──────┬───────┘  └──────┬───────┘
           │                  │                  │
           │ LogEntry         │ Dict             │ Store/Retrieve
           │                  │                  │
           └──────────┬───────┴──────────┬───────┘
                      │                  │
                      ▼                  ▼
              ┌─────────────────────────────┐
              │    AnomalyDetector          │
              │  • detect_log_anomalies()   │
              │  • detect_metric_anomalies()│
              └───────────┬─────────────────┘
                          │
                          │ List[Anomaly]
                          ▼
              ┌─────────────────────────────┐
              │    EventCorrelator          │
              │  • correlate_anomalies()    │
              └───────────┬─────────────────┘
                          │
                          │ List[CorrelatedEvent]
                          ▼
              ┌─────────────────────────────┐
              │      RCAEngine              │
              │  • analyze_root_cause()     │
              └───────────┬─────────────────┘
                          │
                          │ RCAResult
                          │
            ┌─────────────┴─────────────┐
            │                           │
            ▼                           ▼
┌────────────────────────┐   ┌─────────────────────┐
│  RecommendationEngine  │   │   AlertSystem       │
│ • generate_            │   │  • send_alert()     │
│   recommendations()    │   │  • acknowledge()    │
└────────────────────────┘   └─────────────────────┘
```

---

## 🗄️ Database Collections

### MongoDB Collections Used:

1. **anomalies**
   - Stores detected anomalies
   - Fields: id, type, severity, value, metric, timestamp, description

2. **rca_results**
   - Stores root cause analysis results
   - Fields: root_cause, confidence, affected_components, causal_chain, recommendations, timestamp

3. **metrics**
   - Stores historical system metrics
   - Fields: timestamp, cpu_usage, memory_usage, disk_usage, response_time, error_rate

4. **logs**
   - Stores log entries
   - Fields: timestamp, level, message, source, host, process_id

5. **alerts**
   - Stores alert history
   - Fields: alert_id, timestamp, type, severity, status, acknowledged_at

---

## 🔑 Key Environment Variables

```bash
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=arca_db

# CORS Configuration
ALLOWED_ORIGINS=*

# Detection Thresholds
CPU_THRESHOLD=80
MEMORY_THRESHOLD=85
RESPONSE_TIME_THRESHOLD=2000
ERROR_RATE_THRESHOLD=5
```

---

## 🚦 API Endpoints Summary

### Health & Status
- `GET /api/health` - Health check
- `GET /api/system-health` - Overall system health

### Anomaly Detection
- `GET /api/anomalies` - List all anomalies
- `POST /api/detect` - Detect anomalies from logs/metrics

### Root Cause Analysis
- `POST /api/rca/analyze` - Analyze root cause
- `GET /api/rca-reports` - List RCA reports
- `GET /api/rca-reports/<id>` - Get specific report

### Logs & Metrics
- `POST /api/logs/upload` - Upload log files
- `GET /api/metrics/current` - Current system metrics
- `GET /api/metrics/history` - Historical metrics

---

## 📝 Execution Order Example

**Scenario: Detecting a CPU spike**

1. **MetricCollector** gathers system metrics
   ```python
   metrics = {
       'cpu_usage': 95.3,
       'memory_usage': 78.2,
       'response_time': 1200
   }
   ```

2. **POST /api/detect** receives metrics

3. **AnomalyDetector** detects CPU threshold breach
   ```python
   anomaly = Anomaly(
       type='threshold_breach',
       severity='CRITICAL',
       metric='cpu_usage',
       value=95.3
   )
   ```

4. **EventCorrelator** groups with other recent anomalies

5. **RCAEngine** identifies root cause
   ```python
   rca_result = RCAResult(
       root_cause='RESOURCE_EXHAUSTION',
       confidence=0.92
   )
   ```

6. **RecommendationEngine** generates actions
   ```python
   recommendations = [
       'Scale up server resources',
       'Optimize database queries'
   ]
   ```

7. **AlertSystem** sends critical alert

8. **MongoDB** stores all data for dashboard display

---

## 🔧 How to Run

```bash
# From arca-platform/backend directory

# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment variables (create .env file)
echo "MONGODB_URI=mongodb://localhost:27017/" > .env
echo "MONGODB_DB_NAME=arca_db" >> .env

# 3. Run the application
python app.py

# OR for production
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 📚 Dependency Tree

```
ARCA Backend
│
├─ Flask (Web Framework)
│  └─ Werkzeug (WSGI utilities)
│
├─ PyMongo (MongoDB Driver)
│  └─ MongoDB (Database)
│
├─ psutil (System Monitoring)
│  └─ Native OS APIs
│
├─ numpy (Numerical Computing)
│  └─ Statistical anomaly detection
│
├─ pandas (Data Analysis)
│  └─ Metric trend analysis
│
└─ Modules (Internal)
   ├─ anomaly_detector.py (standalone)
   ├─ event_correlator.py (receives Anomaly)
   ├─ rca_engine.py (receives CorrelatedEvent)
   ├─ recommendation_engine.py (receives RCAResult)
   ├─ alert_system.py (standalone)
   ├─ log_collector.py (standalone)
   └─ metric_collector.py (uses psutil)
```

---

**Last Updated:** March 10, 2026  
**Python Version:** 3.12  
**Framework:** Flask 3.0.3
