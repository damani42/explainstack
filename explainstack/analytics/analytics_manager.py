"""Analytics manager for ExplainStack."""

import logging
from typing import Dict, Any, Optional
from .metrics_collector import MetricsCollector, UserSession, AgentUsage, SystemMetrics

logger = logging.getLogger(__name__)


class AnalyticsManager:
    """Manages analytics and metrics for ExplainStack."""
    
    def __init__(self):
        """Initialize analytics manager."""
        self.metrics_collector = MetricsCollector()
    
    def track_user_session(self, user_id: str, session_id: str) -> None:
        """Track user session start.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
        """
        self.metrics_collector.start_user_session(user_id, session_id)
        logger.info(f"Tracking session for user {user_id}: {session_id}")
    
    def track_agent_usage(self, agent_id: str, user_id: str, tokens_used: int = 0, 
                         cost: float = 0.0, response_time: float = 0.0, success: bool = True) -> None:
        """Track agent usage.
        
        Args:
            agent_id: Agent identifier
            user_id: User identifier
            tokens_used: Number of tokens used
            cost: Cost of the request
            response_time: Response time in seconds
            success: Whether the request was successful
        """
        self.metrics_collector.record_agent_usage(
            agent_id, user_id, tokens_used, cost, response_time, success
        )
        logger.debug(f"Tracked usage: {agent_id} for user {user_id}")
    
    def get_dashboard_data(self, user_id: Optional[str] = None, hours: int = 24) -> Dict[str, Any]:
        """Get dashboard data.
        
        Args:
            user_id: User identifier (optional)
            hours: Number of hours to look back
            
        Returns:
            Dashboard data dictionary
        """
        if user_id:
            # User-specific dashboard
            user_metrics = self.metrics_collector.get_user_metrics(user_id)
            return {
                'type': 'user_dashboard',
                'user_id': user_id,
                'metrics': user_metrics
            }
        else:
            # System-wide dashboard
            system_metrics = self.metrics_collector.get_system_metrics(hours)
            return {
                'type': 'system_dashboard',
                'metrics': system_metrics
            }
    
    def get_agent_performance(self, agent_id: str, hours: int = 24) -> Dict[str, Any]:
        """Get agent performance metrics.
        
        Args:
            agent_id: Agent identifier
            hours: Number of hours to look back
            
        Returns:
            Agent performance metrics
        """
        return self.metrics_collector.get_agent_performance(agent_id, hours)
    
    def get_usage_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get usage summary.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Usage summary dictionary
        """
        system_metrics = self.metrics_collector.get_system_metrics(hours)
        
        # Get agent performance for all agents
        agents = ['code_expert', 'patch_reviewer', 'import_cleaner', 'commit_writer', 'security_expert', 'performance_expert']
        agent_performance = {}
        
        for agent_id in agents:
            agent_performance[agent_id] = self.metrics_collector.get_agent_performance(agent_id, hours)
        
        return {
            'system_metrics': system_metrics,
            'agent_performance': agent_performance,
            'top_agents': sorted(
                agent_performance.items(),
                key=lambda x: x[1]['total_requests'],
                reverse=True
            )[:3]
        }
    
    def generate_analytics_report(self, hours: int = 24) -> str:
        """Generate analytics report.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Analytics report string
        """
        usage_summary = self.get_usage_summary(hours)
        system_metrics = usage_summary['system_metrics']
        agent_performance = usage_summary['agent_performance']
        
        report = f"""📊 **ExplainStack Analytics Report** ({hours}h)

**System Overview:**
- **Total Users**: {system_metrics['total_users']}
- **Active Sessions**: {system_metrics['active_sessions']}
- **Total Requests**: {system_metrics['total_requests']}
- **Total Tokens**: {system_metrics['total_tokens']:,}
- **Total Cost**: ${system_metrics['total_cost']:.2f}
- **Error Rate**: {system_metrics['error_rate']:.1f}%
- **Avg Response Time**: {system_metrics['average_response_time']:.2f}s
- **Uptime**: {system_metrics['uptime_hours']:.1f}h

**Agent Performance:**
"""
        
        for agent_id, metrics in agent_performance.items():
            if metrics['total_requests'] > 0:
                report += f"- **{agent_id.replace('_', ' ').title()}**: {metrics['total_requests']} requests, {metrics['success_rate']:.1f}% success, {metrics['average_response_time']:.2f}s avg\n"
        
        # Top agents
        top_agents = usage_summary['top_agents']
        if top_agents:
            report += f"\n**Top Agents:**\n"
            for i, (agent_id, metrics) in enumerate(top_agents, 1):
                if metrics['total_requests'] > 0:
                    report += f"{i}. **{agent_id.replace('_', ' ').title()}**: {metrics['total_requests']} requests\n"
        
        return report
    
    def cleanup_old_data(self, days: int = 30) -> None:
        """Clean up old analytics data.
        
        Args:
            days: Number of days to keep data
        """
        self.metrics_collector.cleanup_old_data(days)
        logger.info(f"Cleaned up analytics data older than {days} days")
    
    def export_analytics(self, format: str = 'json') -> str:
        """Export analytics data.
        
        Args:
            format: Export format ('json' or 'csv')
            
        Returns:
            Exported data string
        """
        return self.metrics_collector.export_metrics(format)
