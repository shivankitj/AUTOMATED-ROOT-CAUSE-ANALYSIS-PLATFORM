"""
Sliding Window Module
Manages recent data buffer with circular buffer pattern
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from collections import deque


class SlidingWindow:
    """
    SlidingWindow Class
    Maintains a fixed-size buffer of recent data using circular buffer pattern
    Automatically evicts old data when buffer is full
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize SlidingWindow
        
        Args:
            max_size: Maximum number of items to keep in buffer
        """
        if max_size <= 0:
            raise ValueError("max_size must be positive")
        
        self.max_size = max_size
        self._buffer = deque(maxlen=max_size)
        self._metadata = {
            'total_items_added': 0,
            'current_size': 0,
            'items_evicted': 0
        }
    
    def add(self, item: Any):
        """
        Add item to the sliding window
        
        Args:
            item: Item to add to buffer
        """
        # Check if buffer is full (will evict oldest item)
        if len(self._buffer) >= self.max_size:
            self._metadata['items_evicted'] += 1
        
        self._buffer.append(item)
        self._metadata['total_items_added'] += 1
        self._metadata['current_size'] = len(self._buffer)
    
    def get_all(self) -> List[Any]:
        """
        Get all items in the window
        
        Returns:
            List of all items in buffer
        """
        return list(self._buffer)
    
    def get_recent(self, n: int) -> List[Any]:
        """
        Get the n most recent items
        
        Args:
            n: Number of recent items to retrieve
        
        Returns:
            List of n most recent items
        """
        if n <= 0:
            return []
        
        if n >= len(self._buffer):
            return list(self._buffer)
        
        # Get last n items
        return list(self._buffer)[-n:]
    
    def get_oldest(self, n: int) -> List[Any]:
        """
        Get the n oldest items
        
        Args:
            n: Number of oldest items to retrieve
        
        Returns:
            List of n oldest items
        """
        if n <= 0:
            return []
        
        if n >= len(self._buffer):
            return list(self._buffer)
        
        # Get first n items
        return list(self._buffer)[:n]
    
    def clear(self):
        """Clear all items from the window"""
        self._buffer.clear()
        self._metadata['current_size'] = 0
        # Don't reset total_items_added and items_evicted to maintain history
    
    def is_full(self) -> bool:
        """
        Check if window is full
        
        Returns:
            True if full, False otherwise
        """
        return len(self._buffer) >= self.max_size
    
    def is_empty(self) -> bool:
        """
        Check if window is empty
        
        Returns:
            True if empty, False otherwise
        """
        return len(self._buffer) == 0
    
    def size(self) -> int:
        """
        Get current number of items in window
        
        Returns:
            Number of items currently in buffer
        """
        return len(self._buffer)
    
    def get_metadata(self) -> Dict[str, int]:
        """
        Get window metadata
        
        Returns:
            Dictionary with metadata information
        """
        return self._metadata.copy()
    
    def filter(self, condition) -> List[Any]:
        """
        Filter items in window by condition
        
        Args:
            condition: Function that takes an item and returns True/False
        
        Returns:
            List of items that match the condition
        """
        return [item for item in self._buffer if condition(item)]
    
    def get_by_time_range(self, start_time: datetime, end_time: datetime) -> List[Any]:
        """
        Get items within a time range
        Assumes items have a 'timestamp' attribute or key
        
        Args:
            start_time: Start of time range
            end_time: End of time range
        
        Returns:
            List of items within time range
        """
        results = []
        
        for item in self._buffer:
            # Try to get timestamp from item
            timestamp = None
            
            if isinstance(item, dict):
                timestamp = item.get('timestamp')
            elif hasattr(item, 'timestamp'):
                timestamp = getattr(item, 'timestamp')
            
            if timestamp:
                # Convert string timestamps to datetime if needed
                if isinstance(timestamp, str):
                    try:
                        timestamp = datetime.fromisoformat(timestamp)
                    except:
                        continue
                
                # Check if within range
                if start_time <= timestamp <= end_time:
                    results.append(item)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistical information about the window
        
        Returns:
            Dictionary with statistics
        """
        return {
            'current_size': len(self._buffer),
            'max_size': self.max_size,
            'utilization': (len(self._buffer) / self.max_size) * 100,
            'total_items_added': self._metadata['total_items_added'],
            'items_evicted': self._metadata['items_evicted'],
            'is_full': self.is_full(),
            'is_empty': self.is_empty()
        }
    
    def __len__(self) -> int:
        """Return the number of items in the window"""
        return len(self._buffer)
    
    def __iter__(self):
        """Make the window iterable"""
        return iter(self._buffer)
    
    def __repr__(self) -> str:
        """String representation"""
        return f"SlidingWindow(size={len(self._buffer)}/{self.max_size})"


# Test code
if __name__ == "__main__":
    print("Testing SlidingWindow...")
    
    # Create sliding window with small size for testing
    window = SlidingWindow(max_size=5)
    
    # Add items
    for i in range(10):
        window.add({
            'id': i,
            'value': i * 10,
            'timestamp': datetime.now()
        })
    
    # Test size
    print(f"✅ Window size: {window.size()}/5")
    
    # Test retrieval
    all_items = window.get_all()
    print(f"✅ All items: {len(all_items)}")
    
    recent = window.get_recent(3)
    print(f"✅ Recent 3 items: {[item['id'] for item in recent]}")
    
    # Test metadata
    metadata = window.get_metadata()
    print(f"✅ Total added: {metadata['total_items_added']}")
    print(f"✅ Items evicted: {metadata['items_evicted']}")
    
    # Test statistics
    stats = window.get_statistics()
    print(f"✅ Utilization: {stats['utilization']:.1f}%")
    
    print("✅ SlidingWindow tests passed!")
