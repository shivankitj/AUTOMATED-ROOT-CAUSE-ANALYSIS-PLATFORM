"""
MongoDB Seed Script for ARCA Platform
Populates the database with initial dummy data for testing and demonstration
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'arca_db')

# Connect to MongoDB with timeout settings
try:
    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=5000,  # 5 second timeout
        connectTimeoutMS=5000
    )
    db = client[MONGODB_DB_NAME]
    
    # Actually test the connection
    client.admin.command('ping')
    print(f"✅ Connected to MongoDB: {MONGODB_DB_NAME}")
except Exception as e:
    print(f"❌ Failed to connect to MongoDB: {e}")
    print("\n💡 Troubleshooting tips:")
    print("   1. Make sure MongoDB is running: net start MongoDB")
    print("   2. Check if MongoDB is listening on port 27017")
    print("   3. Try: docker run -d -p 27017:27017 mongo:latest")
    exit(1)


def clear_collections():
    """Clear existing collections"""
    collections = ['anomalies', 'rca_results', 'metrics', 'logs', 'alerts']
    try:
        for collection in collections:
            result = db[collection].delete_many({})
            print(f"🧹 Cleared collection: {collection} ({result.deleted_count} documents)")
    except Exception as e:
        print(f"❌ Error clearing collections: {e}")
        print("   MongoDB connection may have been lost.")
        exit(1)


def seed_anomalies():
    """Seed anomalies collection with dummy data"""
    print("\n📊 Seeding anomalies...")
    
    anomalies = []
    base_time = datetime.now() - timedelta(hours=24)
    
    # CPU Usage Anomalies
    for i in range(5):
        timestamp = base_time + timedelta(hours=i*4, minutes=random.randint(0, 59))
        severity = random.choice(['MEDIUM', 'HIGH', 'CRITICAL'])
        value = random.uniform(85.0, 99.9)
        
        anomalies.append({
            'id': f"cpu_usage_{timestamp.strftime('%Y%m%d_%H%M%S')}",
            'type': 'threshold_breach',
            'severity': severity,
            'value': value,
            'metric': 'cpu_usage',
            'timestamp': timestamp,
            'description': f"CPU usage exceeded threshold: {value:.2f}%"
        })
    
    # Memory Usage Anomalies
    for i in range(4):
        timestamp = base_time + timedelta(hours=i*5, minutes=random.randint(0, 59))
        severity = random.choice(['MEDIUM', 'HIGH'])
        value = random.uniform(87.0, 96.5)
        
        anomalies.append({
            'id': f"memory_usage_{timestamp.strftime('%Y%m%d_%H%M%S')}",
            'type': 'threshold_breach',
            'severity': severity,
            'value': value,
            'metric': 'memory_usage',
            'timestamp': timestamp,
            'description': f"Memory usage exceeded threshold: {value:.2f}%"
        })
    
    # Response Time Anomalies
    for i in range(6):
        timestamp = base_time + timedelta(hours=i*3, minutes=random.randint(0, 59))
        severity = random.choice(['LOW', 'MEDIUM', 'HIGH'])
        value = random.uniform(2100.0, 5500.0)
        
        anomalies.append({
            'id': f"response_time_{timestamp.strftime('%Y%m%d_%H%M%S')}",
            'type': 'threshold_breach',
            'severity': severity,
            'value': value,
            'metric': 'response_time',
            'timestamp': timestamp,
            'description': f"Response time exceeded threshold: {value:.2f}ms"
        })
    
    # Error Rate Anomalies
    for i in range(4):
        timestamp = base_time + timedelta(hours=i*6, minutes=random.randint(0, 59))
        severity = random.choice(['HIGH', 'CRITICAL'])
        value = random.uniform(6.0, 15.5)
        
        anomalies.append({
            'id': f"error_rate_{timestamp.strftime('%Y%m%d_%H%M%S')}",
            'type': 'threshold_breach',
            'severity': severity,
            'value': value,
            'metric': 'error_rate',
            'timestamp': timestamp,
            'description': f"Error rate exceeded threshold: {value:.2f}%"
        })
    
    # Log-based Anomalies
    log_anomalies = [
        {
            'type': 'log_pattern',
            'severity': 'CRITICAL',
            'metric': 'deployment_error',
            'description': 'Multiple deployment failures detected in logs',
            'patterns': ['deployment failed', 'rollback initiated']
        },
        {
            'type': 'log_pattern',
            'severity': 'HIGH',
            'metric': 'connection_error',
            'description': 'Database connection refused errors detected',
            'patterns': ['connection refused', 'timeout']
        },
        {
            'type': 'log_pattern',
            'severity': 'CRITICAL',
            'metric': 'memory_error',
            'description': 'Out of memory errors detected',
            'patterns': ['out of memory', 'OOM killer']
        },
        {
            'type': 'log_pattern',
            'severity': 'MEDIUM',
            'metric': 'authentication_error',
            'description': 'Multiple authentication failures',
            'patterns': ['authentication failed', 'invalid credentials']
        }
    ]
    
    for i, log_anomaly in enumerate(log_anomalies):
        timestamp = base_time + timedelta(hours=i*5, minutes=random.randint(10, 50))
        anomaly = {
            'id': f"{log_anomaly['metric']}_{timestamp.strftime('%Y%m%d_%H%M%S')}",
            'type': log_anomaly['type'],
            'severity': log_anomaly['severity'],
            'value': random.randint(3, 10),
            'metric': log_anomaly['metric'],
            'timestamp': timestamp,
            'description': log_anomaly['description']
        }
        if 'patterns' in log_anomaly:
            anomaly['patterns'] = log_anomaly['patterns']
        anomalies.append(anomaly)
    
    # Insert all anomalies
    if anomalies:
        result = db.anomalies.insert_many(anomalies)
        print(f"✅ Inserted {len(result.inserted_ids)} anomalies")


def seed_rca_results():
    """Seed RCA results collection with root cause analysis reports"""
    print("\n🔍 Seeding RCA results...")
    
    rca_results = []
    base_time = datetime.now() - timedelta(hours=24)
    
    # RCA Result 1: Resource Exhaustion
    rca_results.append({
        'root_cause': 'RESOURCE_EXHAUSTION',
        'confidence': 0.92,
        'affected_components': ['web-server', 'application', 'database'],
        'causal_chain': [
            'Spike in user traffic',
            'CPU usage exceeded 95%',
            'Memory allocation increased',
            'Response time degraded',
            'Connection pool exhausted'
        ],
        'evidence': [
            {'metric': 'cpu_usage', 'value': 96.5, 'severity': 'CRITICAL'},
            {'metric': 'memory_usage', 'value': 94.2, 'severity': 'HIGH'},
            {'metric': 'response_time', 'value': 4500.0, 'severity': 'HIGH'}
        ],
        'recommendations': [
            'Scale up server resources (CPU and Memory)',
            'Implement auto-scaling policies',
            'Optimize database queries',
            'Add caching layer to reduce load'
        ],
        'timestamp': base_time + timedelta(hours=2),
        'analysis_duration_ms': 1250
    })
    
    # RCA Result 2: Deployment Failure
    rca_results.append({
        'root_cause': 'DEPLOYMENT_CONFIGURATION_ERROR',
        'confidence': 0.88,
        'affected_components': ['deployment-pipeline', 'web-server', 'configuration-manager'],
        'causal_chain': [
            'Deployment initiated',
            'Configuration validation failed',
            'Missing environment variables',
            'Service failed to start',
            'Health check failures',
            'Automatic rollback triggered'
        ],
        'evidence': [
            {'type': 'log', 'message': 'deployment failed: missing DATABASE_URL', 'severity': 'CRITICAL'},
            {'type': 'log', 'message': 'health check failed: connection refused', 'severity': 'CRITICAL'},
            {'metric': 'error_rate', 'value': 12.5, 'severity': 'CRITICAL'}
        ],
        'recommendations': [
            'Validate all environment variables before deployment',
            'Implement configuration drift detection',
            'Add pre-deployment validation checks',
            'Review deployment checklist and procedures'
        ],
        'timestamp': base_time + timedelta(hours=8),
        'analysis_duration_ms': 980
    })
    
    # RCA Result 3: Database Connection Issues
    rca_results.append({
        'root_cause': 'DATABASE_CONNECTION_POOL_EXHAUSTION',
        'confidence': 0.85,
        'affected_components': ['database', 'connection-pool', 'api-gateway'],
        'causal_chain': [
            'Increased API request rate',
            'Connection pool reached maximum capacity',
            'New connections timing out',
            'Response time increased significantly',
            'Service degradation'
        ],
        'evidence': [
            {'type': 'log', 'message': 'connection refused by database', 'severity': 'HIGH'},
            {'type': 'log', 'message': 'connection timeout after 5000ms', 'severity': 'HIGH'},
            {'metric': 'response_time', 'value': 5200.0, 'severity': 'HIGH'},
            {'metric': 'error_rate', 'value': 8.3, 'severity': 'HIGH'}
        ],
        'recommendations': [
            'Increase database connection pool size',
            'Implement connection pooling with proper timeout settings',
            'Add connection retry logic with exponential backoff',
            'Monitor database performance metrics'
        ],
        'timestamp': base_time + timedelta(hours=14),
        'analysis_duration_ms': 1100
    })
    
    # RCA Result 4: Memory Leak
    rca_results.append({
        'root_cause': 'MEMORY_LEAK',
        'confidence': 0.79,
        'affected_components': ['application', 'cache-service'],
        'causal_chain': [
            'Application uptime exceeds 48 hours',
            'Memory usage gradually increasing',
            'Garbage collection frequency increased',
            'Out of memory errors',
            'Service restart required'
        ],
        'evidence': [
            {'metric': 'memory_usage', 'value': 97.8, 'severity': 'CRITICAL'},
            {'type': 'log', 'message': 'out of memory: heap exhausted', 'severity': 'CRITICAL'},
            {'type': 'pattern', 'description': 'Memory usage increasing 2% per hour'}
        ],
        'recommendations': [
            'Perform heap dump analysis to identify memory leak source',
            'Review cache implementation for unbounded growth',
            'Implement memory monitoring and alerting',
            'Schedule periodic application restarts as temporary mitigation'
        ],
        'timestamp': base_time + timedelta(hours=18),
        'analysis_duration_ms': 1580
    })
    
    # RCA Result 5: Network Latency
    rca_results.append({
        'root_cause': 'NETWORK_LATENCY',
        'confidence': 0.73,
        'affected_components': ['load-balancer', 'network', 'api-gateway'],
        'causal_chain': [
            'Network congestion detected',
            'Packet loss increased',
            'Latency spike to external services',
            'API response times degraded',
            'Timeout errors increased'
        ],
        'evidence': [
            {'metric': 'response_time', 'value': 3800.0, 'severity': 'MEDIUM'},
            {'type': 'network', 'description': 'Average latency: 450ms', 'severity': 'MEDIUM'},
            {'type': 'log', 'message': 'connection timeout to external API', 'severity': 'MEDIUM'}
        ],
        'recommendations': [
            'Investigate network path to external dependencies',
            'Implement circuit breaker pattern for external calls',
            'Add request/response caching where appropriate',
            'Consider CDN for static content delivery'
        ],
        'timestamp': base_time + timedelta(hours=22),
        'analysis_duration_ms': 920
    })
    
    # Insert all RCA results
    if rca_results:
        result = db.rca_results.insert_many(rca_results)
        print(f"✅ Inserted {len(result.inserted_ids)} RCA reports")


def seed_metrics():
    """Seed metrics collection with historical performance data"""
    print("\n📈 Seeding metrics...")
    
    metrics = []
    base_time = datetime.now() - timedelta(hours=24)
    
    # Generate metrics for last 24 hours (every 5 minutes)
    for i in range(288):  # 24 hours * 12 (5-min intervals)
        timestamp = base_time + timedelta(minutes=i*5)
        
        # Simulate normal patterns with occasional spikes
        is_spike = random.random() < 0.05  # 5% chance of spike
        
        cpu_base = 45.0 if not is_spike else 85.0
        cpu_usage = cpu_base + random.uniform(-10, 15)
        
        memory_base = 60.0 if not is_spike else 88.0
        memory_usage = memory_base + random.uniform(-8, 12)
        
        response_time_base = 250.0 if not is_spike else 2500.0
        response_time = response_time_base + random.uniform(-50, 200)
        
        error_rate_base = 0.5 if not is_spike else 6.0
        error_rate = max(0, error_rate_base + random.uniform(-0.3, 2.0))
        
        metrics.append({
            'timestamp': timestamp,
            'cpu_usage': round(min(100, max(0, cpu_usage)), 2),
            'memory_usage': round(min(100, max(0, memory_usage)), 2),
            'disk_usage': round(random.uniform(45, 75), 2),
            'response_time': round(max(50, response_time), 2),
            'error_rate': round(error_rate, 2),
            'request_count': random.randint(100, 1000),
            'active_connections': random.randint(10, 150)
        })
    
    # Insert all metrics
    if metrics:
        result = db.metrics.insert_many(metrics)
        print(f"✅ Inserted {len(result.inserted_ids)} metric records")


def seed_logs():
    """Seed logs collection with sample log entries"""
    print("\n📝 Seeding logs...")
    
    logs = []
    base_time = datetime.now() - timedelta(hours=24)
    
    log_templates = [
        {'level': 'INFO', 'message': 'Application started successfully', 'source': 'app-server'},
        {'level': 'INFO', 'message': 'User authentication successful', 'source': 'auth-service'},
        {'level': 'INFO', 'message': 'Database connection established', 'source': 'database'},
        {'level': 'INFO', 'message': 'API request processed successfully', 'source': 'api-gateway'},
        {'level': 'WARN', 'message': 'Slow query detected: execution time 2.3s', 'source': 'database'},
        {'level': 'WARN', 'message': 'Cache miss rate above threshold: 15%', 'source': 'cache-service'},
        {'level': 'WARN', 'message': 'Connection pool utilization: 85%', 'source': 'database'},
        {'level': 'ERROR', 'message': 'Failed to connect to external API: timeout', 'source': 'api-gateway'},
        {'level': 'ERROR', 'message': 'Database query failed: connection refused', 'source': 'database'},
        {'level': 'ERROR', 'message': 'Authentication failed: invalid credentials', 'source': 'auth-service'},
        {'level': 'ERROR', 'message': 'Request rate limit exceeded', 'source': 'api-gateway'},
        {'level': 'CRITICAL', 'message': 'Out of memory: heap space exhausted', 'source': 'app-server'},
        {'level': 'CRITICAL', 'message': 'Deployment failed: missing environment variable DATABASE_URL', 'source': 'deployment'},
        {'level': 'CRITICAL', 'message': 'Health check failed: service not responding', 'source': 'monitoring'},
        {'level': 'CRITICAL', 'message': 'Automatic rollback initiated', 'source': 'deployment'}
    ]
    
    # Generate logs over 24 hours
    for i in range(500):
        template = random.choice(log_templates)
        timestamp = base_time + timedelta(minutes=random.randint(0, 1440))
        
        logs.append({
            'timestamp': timestamp,
            'level': template['level'],
            'message': template['message'],
            'source': template['source'],
            'host': f"server-{random.randint(1, 5)}",
            'process_id': random.randint(1000, 9999)
        })
    
    # Sort by timestamp
    logs.sort(key=lambda x: x['timestamp'])
    
    # Insert all logs
    if logs:
        result = db.logs.insert_many(logs)
        print(f"✅ Inserted {len(result.inserted_ids)} log entries")


def seed_alerts():
    """Seed alerts collection with alert history"""
    print("\n🚨 Seeding alerts...")
    
    alerts = []
    base_time = datetime.now() - timedelta(hours=24)
    
    alert_configs = [
        {
            'type': 'CRITICAL_ANOMALY',
            'severity': 'CRITICAL',
            'title': 'Multiple Critical Anomalies Detected',
            'message': 'System has detected 3 critical anomalies in the last 5 minutes',
            'root_cause': 'RESOURCE_EXHAUSTION',
            'affected_components': ['web-server', 'database']
        },
        {
            'type': 'THRESHOLD_BREACH',
            'severity': 'HIGH',
            'title': 'CPU Usage Threshold Exceeded',
            'message': 'CPU usage has exceeded 90% for more than 5 minutes',
            'metric': 'cpu_usage',
            'value': 94.5
        },
        {
            'type': 'DEPLOYMENT_FAILURE',
            'severity': 'CRITICAL',
            'title': 'Deployment Failed',
            'message': 'Deployment to production environment failed',
            'root_cause': 'DEPLOYMENT_CONFIGURATION_ERROR',
            'affected_components': ['deployment-pipeline']
        },
        {
            'type': 'SERVICE_DOWN',
            'severity': 'CRITICAL',
            'title': 'Service Health Check Failed',
            'message': 'Health check endpoint not responding',
            'affected_components': ['api-gateway'],
            'downtime_minutes': 8
        },
        {
            'type': 'HIGH_ERROR_RATE',
            'severity': 'HIGH',
            'title': 'Error Rate Spike Detected',
            'message': 'Error rate has increased to 12.5% (normal: 0.5%)',
            'metric': 'error_rate',
            'value': 12.5
        },
        {
            'type': 'MEMORY_WARNING',
            'severity': 'MEDIUM',
            'title': 'Memory Usage Warning',
            'message': 'Memory usage approaching threshold at 82%',
            'metric': 'memory_usage',
            'value': 82.3
        }
    ]
    
    for i, alert_config in enumerate(alert_configs):
        timestamp = base_time + timedelta(hours=i*3.5, minutes=random.randint(0, 30))
        
        alert = {
            'alert_id': f"alert_{timestamp.strftime('%Y%m%d_%H%M%S')}_{i}",
            'timestamp': timestamp,
            'type': alert_config['type'],
            'severity': alert_config['severity'],
            'title': alert_config['title'],
            'message': alert_config['message'],
            'status': random.choice(['open', 'acknowledged', 'resolved']),
            'acknowledged_at': timestamp + timedelta(minutes=random.randint(5, 30)) if random.random() > 0.3 else None,
            'resolved_at': timestamp + timedelta(hours=random.randint(1, 4)) if random.random() > 0.5 else None
        }
        
        # Add optional fields
        if 'root_cause' in alert_config:
            alert['root_cause'] = alert_config['root_cause']
        if 'affected_components' in alert_config:
            alert['affected_components'] = alert_config['affected_components']
        if 'metric' in alert_config:
            alert['metric'] = alert_config['metric']
            alert['value'] = alert_config['value']
        if 'downtime_minutes' in alert_config:
            alert['downtime_minutes'] = alert_config['downtime_minutes']
        
        alerts.append(alert)
    
    # Insert all alerts
    if alerts:
        result = db.alerts.insert_many(alerts)
        print(f"✅ Inserted {len(result.inserted_ids)} alerts")


def create_indexes():
    """Create indexes for better query performance"""
    print("\n🔧 Creating indexes...")
    
    # Anomalies indexes
    db.anomalies.create_index([('timestamp', -1)])
    db.anomalies.create_index([('severity', 1)])
    db.anomalies.create_index([('metric', 1)])
    
    # RCA results indexes
    db.rca_results.create_index([('timestamp', -1)])
    db.rca_results.create_index([('root_cause', 1)])
    db.rca_results.create_index([('confidence', -1)])
    
    # Metrics indexes
    db.metrics.create_index([('timestamp', -1)])
    
    # Logs indexes
    db.logs.create_index([('timestamp', -1)])
    db.logs.create_index([('level', 1)])
    db.logs.create_index([('source', 1)])
    
    # Alerts indexes
    db.alerts.create_index([('timestamp', -1)])
    db.alerts.create_index([('status', 1)])
    db.alerts.create_index([('severity', 1)])
    
    print("✅ Indexes created successfully")


def print_summary():
    """Print summary of seeded data"""
    print("\n" + "="*60)
    print("📊 SEED SUMMARY")
    print("="*60)
    
    print(f"Anomalies:    {db.anomalies.count_documents({})}")
    print(f"RCA Reports:  {db.rca_results.count_documents({})}")
    print(f"Metrics:      {db.metrics.count_documents({})}")
    print(f"Logs:         {db.logs.count_documents({})}")
    print(f"Alerts:       {db.alerts.count_documents({})}")
    
    print("\n" + "="*60)
    print("✅ Database seeding completed successfully!")
    print("="*60)


def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("🌱 ARCA Platform - MongoDB Seed Script")
    print("="*60)
    
    # Confirm before proceeding
    response = input("\n⚠️  This will clear all existing data. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Seeding cancelled")
        return
    
    # Clear existing data
    clear_collections()
    
    # Seed all collections
    seed_anomalies()
    seed_rca_results()
    seed_metrics()
    seed_logs()
    seed_alerts()
    
    # Create indexes
    create_indexes()
    
    # Print summary
    print_summary()
    
    # Close connection
    client.close()


if __name__ == "__main__":
    main()
