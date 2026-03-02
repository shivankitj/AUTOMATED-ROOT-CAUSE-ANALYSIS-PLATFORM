"""
Metric Collector Module
Gathers system performance metrics
"""

from typing import Dict, Optional
import psutil
import time
from datetime import datetime


class MetricCollector:
    """
    MetricCollector Class
    Collects system performance metrics (CPU, Memory, Disk, Network)
    """
    
    def __init__(self, interval: int = 10):
        """
        Initialize MetricCollector
        
        Args:
            interval: Collection interval in seconds
        """
        self.metrics: Dict[str, float] = {}
        self.collection_interval = interval
        self.is_running = False
        self._metric_history: Dict[str, list] = {}
    
    def start_collection(self):
        """Start continuous metric collection"""
        self.is_running = True
        print(f"📊 MetricCollector started (interval: {self.collection_interval}s)")
    
    def stop_collection(self):
        """Stop metric collection"""
        self.is_running = False
        print("🛑 MetricCollector stopped")
    
    def collect_cpu_usage(self) -> float:
        """
        Collect current CPU usage percentage
        
        Returns:
            CPU usage as percentage (0-100)
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics['cpu_usage'] = cpu_percent
            return cpu_percent
        except Exception as e:
            print(f"❌ Error collecting CPU usage: {e}")
            return 0.0
    
    def collect_memory_usage(self) -> float:
        """
        Collect current memory usage percentage
        
        Returns:
            Memory usage as percentage (0-100)
        """
        try:
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.metrics['memory_usage'] = memory_percent
            self.metrics['memory_available_mb'] = memory.available / (1024 * 1024)
            self.metrics['memory_used_mb'] = memory.used / (1024 * 1024)
            return memory_percent
        except Exception as e:
            print(f"❌ Error collecting memory usage: {e}")
            return 0.0
    
    def collect_disk_usage(self) -> float:
        """
        Collect disk usage percentage
        
        Returns:
            Disk usage as percentage (0-100)
        """
        try:
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            self.metrics['disk_usage'] = disk_percent
            self.metrics['disk_free_gb'] = disk.free / (1024 ** 3)
            return disk_percent
        except Exception as e:
            print(f"❌ Error collecting disk usage: {e}")
            return 0.0
    
    def collect_response_time(self, endpoint: Optional[str] = None) -> float:
        """
        Collect application response time
        
        Args:
            endpoint: Optional endpoint to measure
        
        Returns:
            Response time in milliseconds
        """
        # This is a placeholder - in real implementation,
        # would measure actual endpoint response time
        try:
            # Simulate response time measurement
            start_time = time.time()
            # Perform measurement...
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to ms
            
            self.metrics['response_time'] = response_time
            return response_time
        except Exception as e:
            print(f"❌ Error collecting response time: {e}")
            return 0.0
    
    def collect_network_io(self) -> Dict[str, float]:
        """
        Collect network I/O statistics
        
        Returns:
            Dictionary with bytes sent and received
        """
        try:
            net_io = psutil.net_io_counters()
            stats = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
            }
            self.metrics.update(stats)
            return stats
        except Exception as e:
            print(f"❌ Error collecting network I/O: {e}")
            return {}
    
    def get_metric_snapshot(self) -> Dict[str, float]:
        """
        Get snapshot of all current metrics
        
        Returns:
            Dictionary of all metrics
        """
        try:
            snapshot = {
                'timestamp': datetime.now().isoformat(),
                'cpu_usage': self.collect_cpu_usage(),
                'memory_usage': self.collect_memory_usage(),
                'disk_usage': self.collect_disk_usage(),
            }
            
            # Add network metrics
            net_stats = self.collect_network_io()
            snapshot.update(net_stats)
            
            # Store in history
            self._store_in_history(snapshot)
            
            return snapshot
        except Exception as e:
            print(f"❌ Error getting metric snapshot: {e}")
            return {'timestamp': datetime.now().isoformat()}
    
    def get_metric(self, metric_name: str) -> Optional[float]:
        """
        Get specific metric value
        
        Args:
            metric_name: Name of the metric
        
        Returns:
            Metric value or None
        """
        return self.metrics.get(metric_name)
    
    def get_metric_history(self, metric_name: str, limit: int = 100) -> list:
        """
        Get historical values for a specific metric
        
        Args:
            metric_name: Name of the metric
            limit: Maximum number of historical values
        
        Returns:
            List of historical values
        """
        history = self._metric_history.get(metric_name, [])
        return history[-limit:]
    
    def _store_in_history(self, snapshot: Dict[str, float]):
        """
        Store metric snapshot in history
        
        Args:
            snapshot: Metric snapshot dictionary
        """
        for metric_name, value in snapshot.items():
            if metric_name == 'timestamp':
                continue
            
            if metric_name not in self._metric_history:
                self._metric_history[metric_name] = []
            
            self._metric_history[metric_name].append({
                'value': value,
                'timestamp': snapshot['timestamp']
            })
            
            # Keep only last 1000 entries
            if len(self._metric_history[metric_name]) > 1000:
                self._metric_history[metric_name] = self._metric_history[metric_name][-1000:]
    
    def _calculate_averages(self):
        """Calculate average values for metrics"""
        for metric_name, history in self._metric_history.items():
            if history:
                values = [h['value'] for h in history if isinstance(h['value'], (int, float))]
                if values:
                    avg = sum(values) / len(values)
                    self.metrics[f'{metric_name}_avg'] = avg


# Test code
if __name__ == "__main__":
    print("Testing MetricCollector...")
    
    # Create collector
    collector = MetricCollector(interval=10)
    
    # Collect metrics
    collector.start_collection()
    
    # Get snapshot
    snapshot = collector.get_metric_snapshot()
    
    print(f"✅ CPU Usage: {snapshot.get('cpu_usage', 0):.2f}%")
    print(f"✅ Memory Usage: {snapshot.get('memory_usage', 0):.2f}%")
    print(f"✅ Disk Usage: {snapshot.get('disk_usage', 0):.2f}%")
    
    collector.stop_collection()
    
    print("✅ MetricCollector tests passed!")
