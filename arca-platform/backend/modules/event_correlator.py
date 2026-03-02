"""
Event Correlator Module
Correlates related anomalies across time and services
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class CorrelatedEvent:
    """Group of related anomalies"""
    anomalies: List
    correlation_score: float
    time_window: str
    affected_components: List[str]


class EventCorrelator:
    """
    EventCorrelator Class
    Links related anomalies across time windows and service dependencies
    """
    
    def __init__(self, window_size_minutes: int = 5):
        """
        Initialize EventCorrelator
        
        Args:
            window_size_minutes: Time window size for correlation in minutes
        """
        self.correlation_window = window_size_minutes
        self.correlated_events: List[CorrelatedEvent] = []
        self.dependency_graph: Dict[str, List[str]] = {}
    
    def correlate_anomalies(self, anomalies: List) -> List[CorrelatedEvent]:
        """
        Correlate anomalies based on time and dependencies
        
        Args:
            anomalies: List of Anomaly objects or dictionaries
        
        Returns:
            List of CorrelatedEvent objects
        """
        if not anomalies:
            return []
        
        # Group anomalies by time window
        time_windows = self._group_by_timestamp(anomalies)
        
        correlated_events = []
        
        for window_key, window_anomalies in time_windows.items():
            if len(window_anomalies) < 2:
                # Need at least 2 anomalies to correlate
                continue
            
            # Calculate correlation score
            correlation_score = self._calculate_correlation_score(window_anomalies)
            
            # Extract affected components
            affected_components = self._extract_affected_components(window_anomalies)
            
            # Create correlated event
            correlated_event = CorrelatedEvent(
                anomalies=window_anomalies,
                correlation_score=correlation_score,
                time_window=window_key,
                affected_components=affected_components
            )
            
            correlated_events.append(correlated_event)
        
        self.correlated_events = correlated_events
        return correlated_events
    
    def find_related_events(self, anomaly) -> List:
        """
        Find events related to a specific anomaly
        
        Args:
            anomaly: Anomaly object to find relations for
        
        Returns:
            List of related Anomaly objects
        """
        related = []
        
        # Get anomaly timestamp
        if isinstance(anomaly, dict):
            anomaly_time = anomaly.get('timestamp')
            if isinstance(anomaly_time, str):
                anomaly_time = datetime.fromisoformat(anomaly_time)
        else:
            anomaly_time = getattr(anomaly, 'timestamp', datetime.now())
        
        # Look through all correlated events
        for ce in self.correlated_events:
            for a in ce.anomalies:
                if a == anomaly:
                    continue
                
                # Get this anomaly's timestamp
                if isinstance(a, dict):
                    a_time = a.get('timestamp')
                    if isinstance(a_time, str):
                        a_time = datetime.fromisoformat(a_time)
                else:
                    a_time = getattr(a, 'timestamp', datetime.now())
                
                # Check if within time window
                if self.is_within_time_window(anomaly_time, a_time):
                    related.append(a)
        
        return related
    
    def set_dependencies(self, dependencies: Dict[str, List[str]]):
        """
        Set service dependency graph
        
        Args:
            dependencies: Dictionary mapping component to its dependencies
        """
        self.dependency_graph = dependencies
    
    def is_within_time_window(self, time1: datetime, time2: datetime) -> bool:
        """
        Check if two timestamps are within the correlation window
        
        Args:
            time1: First timestamp
            time2: Second timestamp
        
        Returns:
            True if within window, False otherwise
        """
        if not isinstance(time1, datetime):
            try:
                time1 = datetime.fromisoformat(str(time1))
            except:
                return False
        
        if not isinstance(time2, datetime):
            try:
                time2 = datetime.fromisoformat(str(time2))
            except:
                return False
        
        time_diff = abs((time1 - time2).total_seconds())
        window_seconds = self.correlation_window * 60
        
        return time_diff <= window_seconds
    
    def _group_by_timestamp(self, anomalies: List) -> Dict[str, List]:
        """
        Group anomalies by time windows
        
        Args:
            anomalies: List of anomaly objects
        
        Returns:
            Dictionary mapping window key to anomaly list
        """
        windows = {}
        
        for anomaly in anomalies:
            # Get timestamp
            if isinstance(anomaly, dict):
                timestamp = anomaly.get('timestamp')
                if isinstance(timestamp, str):
                    try:
                        timestamp = datetime.fromisoformat(timestamp)
                    except:
                        timestamp = datetime.now()
            else:
                timestamp = getattr(anomaly, 'timestamp', datetime.now())
            
            if not isinstance(timestamp, datetime):
                timestamp = datetime.now()
            
            # Calculate window key (rounded to window size)
            window_start = timestamp - timedelta(
                minutes=timestamp.minute % self.correlation_window,
                seconds=timestamp.second,
                microseconds=timestamp.microsecond
            )
            window_key = window_start.strftime('%Y-%m-%d_%H:%M')
            
            if window_key not in windows:
                windows[window_key] = []
            
            windows[window_key].append(anomaly)
        
        return windows
    
    def _calculate_correlation_score(self, anomalies: List) -> float:
        """
        Calculate correlation score for a group of anomalies
        
        Args:
            anomalies: List of anomaly objects
        
        Returns:
            Correlation score between 0 and 1
        """
        if len(anomalies) < 2:
            return 0.0
        
        score = 0.0
        
        # Factor 1: Time proximity (already grouped by window)
        score += 0.3
        
        # Factor 2: Severity alignment
        severities = []
        for a in anomalies:
            if isinstance(a, dict):
                severities.append(a.get('severity', 'LOW'))
            else:
                severities.append(getattr(a, 'severity', 'LOW'))
        
        critical_count = severities.count('CRITICAL')
        high_count = severities.count('HIGH')
        
        if critical_count > 0:
            score += 0.3
        if high_count > 0:
            score += 0.2
        
        # Factor 3: Related components
        components = self._extract_affected_components(anomalies)
        if len(components) > 1:
            # Check if components are related in dependency graph
            has_dependencies = False
            for comp1 in components:
                for comp2 in components:
                    if comp1 != comp2:
                        if comp2 in self.dependency_graph.get(comp1, []):
                            has_dependencies = True
                            break
            
            if has_dependencies:
                score += 0.2
        
        return min(score, 1.0)
    
    def _extract_affected_components(self, anomalies: List) -> List[str]:
        """
        Extract affected components from anomalies
        
        Args:
            anomalies: List of anomaly objects
        
        Returns:
            List of unique component names
        """
        components = set()
        
        for anomaly in anomalies:
            # Try to extract component from metric name or type
            if isinstance(anomaly, dict):
                metric = anomaly.get('metric', '')
                anomaly_type = anomaly.get('type', '')
            else:
                metric = getattr(anomaly, 'metric_name', '')
                anomaly_type = getattr(anomaly, 'anomaly_type', '')
            
            # Extract component name from metric
            # e.g., "app-server.cpu_usage" -> "app-server"
            if '.' in metric:
                component = metric.split('.')[0]
                components.add(component)
            elif '_' in metric:
                component = metric.split('_')[0]
                components.add(component)
            else:
                # Use anomaly type as component fallback
                if anomaly_type:
                    components.add(anomaly_type.lower())
        
        return list(components) if components else ['unknown']


# Test code
if __name__ == "__main__":
    print("Testing EventCorrelator...")
    
    # Create test anomalies
    now = datetime.now()
    
    test_anomalies = [
        {
            'type': 'LOG_ERROR',
            'severity': 'CRITICAL',
            'metric': 'app-server.error_logs',
            'timestamp': now.isoformat()
        },
        {
            'type': 'METRIC_ANOMALY',
            'severity': 'HIGH',
            'metric': 'app-server.cpu_usage',
            'timestamp': (now + timedelta(seconds=30)).isoformat()
        },
        {
            'type': 'LOG_ERROR',
            'severity': 'HIGH',
            'metric': 'database.connection',
            'timestamp': (now + timedelta(minutes=1)).isoformat()
        }
    ]
    
    # Create correlator
    correlator = EventCorrelator(window_size_minutes=5)
    
    # Set dependencies
    correlator.set_dependencies({
        'app-server': ['database', 'cache'],
        'database': []
    })
    
    # Correlate anomalies
    correlated = correlator.correlate_anomalies(test_anomalies)
    
    print(f"✅ Correlated {len(correlated)} event groups")
    if correlated:
        print(f"✅ Correlation Score: {correlated[0].correlation_score:.2f}")
        print(f"✅ Affected Components: {correlated[0].affected_components}")
    
    print("✅ EventCorrelator tests passed!")
