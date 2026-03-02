"""
Recommendation Engine Module
Generates actionable fix recommendations based on root cause analysis
"""

from typing import List, Dict, Optional
from datetime import datetime


class Recommendation:
    """Represents a recommendation"""
    def __init__(self, action: str, priority: str, description: str, 
                 estimated_time: str = "Unknown"):
        self.action = action
        self.priority = priority  # "HIGH", "MEDIUM", "LOW"
        self.description = description
        self.estimated_time = estimated_time
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'action': self.action,
            'priority': self.priority,
            'description': self.description,
            'estimated_time': self.estimated_time
        }


class Fix:
    """Historical fix record"""
    def __init__(self, root_cause: str, action_taken: str, 
                 success: bool, timestamp: datetime):
        self.root_cause = root_cause
        self.action_taken = action_taken
        self.success = success
        self.timestamp = timestamp


class RecommendationEngine:
    """
    RecommendationEngine Class
    Generates actionable recommendations based on root cause analysis
    """
    
    def __init__(self, recommendation_rules: Dict[str, List[Dict]]):
        """
        Initialize RecommendationEngine
        
        Args:
            recommendation_rules: Dictionary mapping root causes to recommendations
        """
        self.recommendation_rules = recommendation_rules if recommendation_rules else self._get_default_rules()
        self.historical_fixes: List[Fix] = []
    
    def generate_recommendations(self, rca_result) -> List[Dict]:
        """
        Generate recommendations based on RCA result
        
        Args:
            rca_result: RCAResult object
        
        Returns:
            List of Recommendation dictionaries
        """
        root_cause = rca_result.root_cause
        confidence = rca_result.confidence
        
        # Get recommendations for this root cause
        recommendations = self._match_cause_to_action(root_cause)
        
        # Adjust priorities based on confidence
        for rec in recommendations:
            if confidence > 0.8:
                if rec['priority'] == 'MEDIUM':
                    rec['priority'] = 'HIGH'
            elif confidence < 0.5:
                if rec['priority'] == 'HIGH':
                    rec['priority'] = 'MEDIUM'
        
        # Add historical fixes
        historical = self.get_historical_fixes(root_cause)
        if historical:
            for fix in historical[:3]:  # Top 3 historical fixes
                if fix.success:
                    recommendations.append({
                        'action': fix.action_taken,
                        'priority': 'MEDIUM',
                        'description': 'Previously successful fix',
                        'estimated_time': 'Variable'
                    })
        
        # Prioritize recommendations
        return self.prioritize_recommendations(recommendations)
    
    def prioritize_recommendations(self, recommendations: List[Dict]) -> List[Dict]:
        """
        Prioritize recommendations by impact and effort
        
        Args:
            recommendations: List of recommendation dictionaries
        
        Returns:
            Sorted list of recommendations
        """
        priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        
        sorted_recs = sorted(
            recommendations,
            key=lambda x: priority_order.get(x['priority'], 3)
        )
        
        return sorted_recs
    
    def get_historical_fixes(self, root_cause: str) -> List[Fix]:
        """
        Get historical fixes for a root cause
        
        Args:
            root_cause: Root cause identifier
        
        Returns:
            List of Fix objects
        """
        matching_fixes = [
            fix for fix in self.historical_fixes
            if fix.root_cause == root_cause
        ]
        
        # Sort by timestamp (most recent first)
        matching_fixes.sort(key=lambda x: x.timestamp, reverse=True)
        
        return matching_fixes
    
    def add_new_rule(self, root_cause: str, recommendation: Dict):
        """
        Add a new recommendation rule
        
        Args:
            root_cause: Root cause identifier
            recommendation: Recommendation dictionary
        """
        if root_cause not in self.recommendation_rules:
            self.recommendation_rules[root_cause] = []
        
        self.recommendation_rules[root_cause].append(recommendation)
    
    def record_fix(self, root_cause: str, action_taken: str, success: bool):
        """
        Record a fix attempt
        
        Args:
            root_cause: Root cause that was addressed
            action_taken: Action that was taken
            success: Whether the fix was successful
        """
        fix = Fix(
            root_cause=root_cause,
            action_taken=action_taken,
            success=success,
            timestamp=datetime.now()
        )
        
        self.historical_fixes.append(fix)
    
    def _match_cause_to_action(self, root_cause: str) -> List[Dict]:
        """
        Match root cause to recommended actions
        
        Args:
            root_cause: Root cause identifier
        
        Returns:
            List of recommendation dictionaries
        """
        recommendations = self.recommendation_rules.get(root_cause, [])
        
        if not recommendations:
            # Provide generic recommendations
            recommendations = [
                {
                    'action': 'Review system logs for more details',
                    'priority': 'HIGH',
                    'description': 'Investigate the issue by examining system logs',
                    'estimated_time': '15-30 minutes'
                },
                {
                    'action': 'Check recent configuration changes',
                    'priority': 'MEDIUM',
                    'description': 'Review recent changes that might have caused the issue',
                    'estimated_time': '30 minutes'
                },
                {
                    'action': 'Contact system administrator',
                    'priority': 'LOW',
                    'description': 'Escalate to administrator if issue persists',
                    'estimated_time': 'Variable'
                }
            ]
        
        return recommendations.copy()
    
    def _get_default_rules(self) -> Dict[str, List[Dict]]:
        """
        Get default recommendation rules
        
        Returns:
            Dictionary of recommendation rules
        """
        return {
            'DEPLOYMENT_CONFIGURATION_ERROR': [
                {
                    'action': 'Review deployment configuration files',
                    'priority': 'HIGH',
                    'description': 'Check all configuration files for syntax errors and missing values',
                    'estimated_time': '15-30 minutes'
                },
                {
                    'action': 'Validate environment variables',
                    'priority': 'HIGH',
                    'description': 'Ensure all required environment variables are set correctly',
                    'estimated_time': '10 minutes'
                },
                {
                    'action': 'Verify application dependencies',
                    'priority': 'MEDIUM',
                    'description': 'Check that all required dependencies are available and correct versions',
                    'estimated_time': '20 minutes'
                },
                {
                    'action': 'Rollback to previous stable configuration',
                    'priority': 'HIGH',
                    'description': 'If issue started after recent deployment, rollback to last known good state',
                    'estimated_time': '10-15 minutes'
                }
            ],
            'RESOURCE_EXHAUSTION': [
                {
                    'action': 'Scale up resources immediately',
                    'priority': 'HIGH',
                    'description': 'Increase CPU/Memory allocation to handle current load',
                    'estimated_time': '5-10 minutes'
                },
                {
                    'action': 'Implement resource limits',
                    'priority': 'MEDIUM',
                    'description': 'Set proper resource limits to prevent exhaustion',
                    'estimated_time': '30 minutes'
                },
                {
                    'action': 'Enable auto-scaling',
                    'priority': 'MEDIUM',
                    'description': 'Configure auto-scaling to handle variable load',
                    'estimated_time': '1-2 hours'
                },
                {
                    'action': 'Optimize resource-intensive operations',
                    'priority': 'LOW',
                    'description': 'Review and optimize code that uses excessive resources',
                    'estimated_time': '2-4 hours'
                }
            ],
            'NETWORK_CONNECTIVITY_ISSUE': [
                {
                    'action': 'Check network configuration',
                    'priority': 'HIGH',
                    'description': 'Verify network settings and firewall rules',
                    'estimated_time': '15 minutes'
                },
                {
                    'action': 'Verify DNS resolution',
                    'priority': 'HIGH',
                    'description': 'Test DNS resolution for all service endpoints',
                    'estimated_time': '10 minutes'
                },
                {
                    'action': 'Test connectivity to dependent services',
                    'priority': 'MEDIUM',
                    'description': 'Run connectivity tests to all required services',
                    'estimated_time': '20 minutes'
                },
                {
                    'action': 'Review load balancer settings',
                    'priority': 'MEDIUM',
                    'description': 'Check load balancer configuration and health checks',
                    'estimated_time': '15 minutes'
                }
            ],
            'DATABASE_CONNECTION_FAILURE': [
                {
                    'action': 'Verify database credentials',
                    'priority': 'HIGH',
                    'description': 'Check that database username and password are correct',
                    'estimated_time': '5 minutes'
                },
                {
                    'action': 'Check database server status',
                    'priority': 'HIGH',
                    'description': 'Verify database server is running and accessible',
                    'estimated_time': '10 minutes'
                },
                {
                    'action': 'Review connection pool settings',
                    'priority': 'MEDIUM',
                    'description': 'Check connection pool size and timeout settings',
                    'estimated_time': '15 minutes'
                },
                {
                    'action': 'Increase connection timeout',
                    'priority': 'LOW',
                    'description': 'Adjust timeout values if connections are timing out',
                    'estimated_time': '10 minutes'
                }
            ],
            'MEMORY_LEAK': [
                {
                    'action': 'Restart affected services',
                    'priority': 'HIGH',
                    'description': 'Immediate mitigation by restarting services to free memory',
                    'estimated_time': '5 minutes'
                },
                {
                    'action': 'Profile memory usage',
                    'priority': 'HIGH',
                    'description': 'Use profiling tools to identify memory leak source',
                    'estimated_time': '1-2 hours'
                },
                {
                    'action': 'Review recent code changes',
                    'priority': 'MEDIUM',
                    'description': 'Examine recent changes that might have introduced the leak',
                    'estimated_time': '30-60 minutes'
                },
                {
                    'action': 'Implement memory limits',
                    'priority': 'MEDIUM',
                    'description': 'Set memory limits to prevent complete exhaustion',
                    'estimated_time': '15 minutes'
                }
            ]
        }


# Test code
if __name__ == "__main__":
    print("Testing RecommendationEngine...")
    
    # Create mock RCA result
    class MockRCAResult:
        def __init__(self):
            self.root_cause = "DEPLOYMENT_CONFIGURATION_ERROR"
            self.confidence = 0.85
            self.affected_components = ["app-server"]
    
    # Create engine
    engine = RecommendationEngine({})
    
    # Generate recommendations
    rca_result = MockRCAResult()
    recommendations = engine.generate_recommendations(rca_result)
    
    print(f"✅ Generated {len(recommendations)} recommendations")
    print(f"✅ Top recommendation: {recommendations[0]['action']}")
    
    # Test adding historical fix
    engine.record_fix("DEPLOYMENT_CONFIGURATION_ERROR", "Rollback deployment", True)
    
    historical = engine.get_historical_fixes("DEPLOYMENT_CONFIGURATION_ERROR")
    print(f"✅ Historical fixes: {len(historical)}")
    
    print("✅ RecommendationEngine tests passed!")
