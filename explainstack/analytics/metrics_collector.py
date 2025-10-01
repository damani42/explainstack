"""Metrics collector for ExplainStack analytics."""

import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class UserSession:
    """User session data."""
    user_id: str
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    agent_usage: Dict[str, int] = None
    total_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    
    def __post_init__(self):
        if self.agent_usage is None:
            self.agent_usage = {}


@dataclass
class AgentUsage:
    """Agent usage data."""
    agent_id: str
    user_id: str
    timestamp: datetime
    request_count: int = 1
    tokens_used: int = 0
    cost: float = 0.0
    response_time: float = 0.0
    success: bool = True


@dataclass
class SystemMetrics:
    """System metrics data."""
    timestamp: datetime
    total_users: int
    active_sessions: int
    total_requests: int
    total_tokens: int
    total_cost: float
    agent_usage: Dict[str, int]
    error_count: int
    average_response_time: float


class MetricsCollector:
    """Collects and stores metrics for ExplainStack."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self.sessions: Dict[str, UserSession] = {}
        self.agent_usage: List[AgentUsage] = []
        self.system_metrics: List[SystemMetrics] = []
        self.start_time = datetime.now()
    
    def start_user_session(self, user_id: str, session_id: str) -> None:
        """Start tracking a user session.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
        """
        session = UserSession(
            user_id=user_id,
            session_id=session_id,
            start_time=datetime.now()
        )
        self.sessions[session_id] = session
        logger.info(f"Started session for user {user_id}: {session_id}")
    
    def end_user_session(self, session_id: str) -> None:
        """End tracking a user session.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self.sessions:
            self.sessions[session_id].end_time = datetime.now()
            logger.info(f"Ended session: {session_id}")
    
    def record_agent_usage(self, agent_id: str, user_id: str, tokens_used: int = 0, 
                          cost: float = 0.0, response_time: float = 0.0, success: bool = True) -> None:
        """Record agent usage.
        
        Args:
            agent_id: Agent identifier
            user_id: User identifier
            tokens_used: Number of tokens used
            cost: Cost of the request
            response_time: Response time in seconds
            success: Whether the request was successful
        """
        usage = AgentUsage(
            agent_id=agent_id,
            user_id=user_id,
            timestamp=datetime.now(),
            tokens_used=tokens_used,
            cost=cost,
            response_time=response_time,
            success=success
        )
        
        self.agent_usage.append(usage)
        
        # Update session data
        for session in self.sessions.values():
            if session.user_id == user_id and session.end_time is None:
                session.total_requests += 1
                session.total_tokens += tokens_used
                session.total_cost += cost
                session.agent_usage[agent_id] = session.agent_usage.get(agent_id, 0) + 1
                break
        
        logger.debug(f"Recorded agent usage: {agent_id} for user {user_id}")
    
    def get_user_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get metrics for a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            User metrics dictionary
        """
        user_sessions = [s for s in self.sessions.values() if s.user_id == user_id]
        user_usage = [u for u in self.agent_usage if u.user_id == user_id]
        
        total_sessions = len(user_sessions)
        total_requests = sum(s.total_requests for s in user_sessions)
        total_tokens = sum(s.total_tokens for s in user_sessions)
        total_cost = sum(s.total_cost for s in user_sessions)
        
        # Agent usage breakdown
        agent_usage = {}
        for usage in user_usage:
            agent_id = usage.agent_id
            if agent_id not in agent_usage:
                agent_usage[agent_id] = {
                    'count': 0,
                    'tokens': 0,
                    'cost': 0.0,
                    'avg_response_time': 0.0
                }
            
            agent_usage[agent_id]['count'] += 1
            agent_usage[agent_id]['tokens'] += usage.tokens_used
            agent_usage[agent_id]['cost'] += usage.cost
            agent_usage[agent_id]['avg_response_time'] = (
                (agent_usage[agent_id]['avg_response_time'] * (agent_usage[agent_id]['count'] - 1) + 
                 usage.response_time) / agent_usage[agent_id]['count']
            )
        
        return {
            'user_id': user_id,
            'total_sessions': total_sessions,
            'total_requests': total_requests,
            'total_tokens': total_tokens,
            'total_cost': total_cost,
            'agent_usage': agent_usage,
            'first_session': min(s.start_time for s in user_sessions) if user_sessions else None,
            'last_session': max(s.start_time for s in user_sessions) if user_sessions else None
        }
    
    def get_system_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Get system metrics for the last N hours.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            System metrics dictionary
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter data by time
        recent_usage = [u for u in self.agent_usage if u.timestamp >= cutoff_time]
        active_sessions = [s for s in self.sessions.values() if s.end_time is None or s.end_time >= cutoff_time]
        
        # Calculate metrics
        total_requests = len(recent_usage)
        total_tokens = sum(u.tokens_used for u in recent_usage)
        total_cost = sum(u.cost for u in recent_usage)
        error_count = sum(1 for u in recent_usage if not u.success)
        
        # Agent usage breakdown
        agent_usage = {}
        for usage in recent_usage:
            agent_id = usage.agent_id
            agent_usage[agent_id] = agent_usage.get(agent_id, 0) + 1
        
        # Average response time
        avg_response_time = (
            sum(u.response_time for u in recent_usage) / len(recent_usage)
            if recent_usage else 0.0
        )
        
        # Unique users
        unique_users = len(set(u.user_id for u in recent_usage))
        
        return {
            'period_hours': hours,
            'total_users': unique_users,
            'active_sessions': len(active_sessions),
            'total_requests': total_requests,
            'total_tokens': total_tokens,
            'total_cost': total_cost,
            'error_count': error_count,
            'error_rate': (error_count / total_requests * 100) if total_requests > 0 else 0.0,
            'average_response_time': avg_response_time,
            'agent_usage': agent_usage,
            'uptime_hours': (datetime.now() - self.start_time).total_seconds() / 3600
        }
    
    def get_agent_performance(self, agent_id: str, hours: int = 24) -> Dict[str, Any]:
        """Get performance metrics for a specific agent.
        
        Args:
            agent_id: Agent identifier
            hours: Number of hours to look back
            
        Returns:
            Agent performance metrics
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        agent_usage = [u for u in self.agent_usage if u.agent_id == agent_id and u.timestamp >= cutoff_time]
        
        if not agent_usage:
            return {
                'agent_id': agent_id,
                'total_requests': 0,
                'success_rate': 0.0,
                'average_response_time': 0.0,
                'total_tokens': 0,
                'total_cost': 0.0
            }
        
        total_requests = len(agent_usage)
        successful_requests = sum(1 for u in agent_usage if u.success)
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0.0
        
        avg_response_time = sum(u.response_time for u in agent_usage) / total_requests
        total_tokens = sum(u.tokens_used for u in agent_usage)
        total_cost = sum(u.cost for u in agent_usage)
        
        return {
            'agent_id': agent_id,
            'total_requests': total_requests,
            'success_rate': success_rate,
            'average_response_time': avg_response_time,
            'total_tokens': total_tokens,
            'total_cost': total_cost,
            'requests_per_hour': total_requests / hours if hours > 0 else 0
        }
    
    def cleanup_old_data(self, days: int = 30) -> None:
        """Clean up old metrics data.
        
        Args:
            days: Number of days to keep data
        """
        cutoff_time = datetime.now() - timedelta(days=days)
        
        # Remove old agent usage data
        self.agent_usage = [u for u in self.agent_usage if u.timestamp >= cutoff_time]
        
        # Remove old system metrics
        self.system_metrics = [m for m in self.system_metrics if m.timestamp >= cutoff_time]
        
        # Remove old sessions
        old_sessions = [sid for sid, session in self.sessions.items() 
                       if session.end_time and session.end_time < cutoff_time]
        for session_id in old_sessions:
            del self.sessions[session_id]
        
        logger.info(f"Cleaned up data older than {days} days")
    
    def export_metrics(self, format: str = 'json') -> str:
        """Export metrics data.
        
        Args:
            format: Export format ('json' or 'csv')
            
        Returns:
            Exported data string
        """
        if format == 'json':
            import json
            data = {
                'sessions': [asdict(s) for s in self.sessions.values()],
                'agent_usage': [asdict(u) for u in self.agent_usage],
                'system_metrics': [asdict(m) for m in self.system_metrics]
            }
            return json.dumps(data, default=str, indent=2)
        
        elif format == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            
            # Export agent usage
            if self.agent_usage:
                writer = csv.writer(output)
                writer.writerow(['timestamp', 'agent_id', 'user_id', 'tokens_used', 'cost', 'response_time', 'success'])
                for usage in self.agent_usage:
                    writer.writerow([
                        usage.timestamp.isoformat(),
                        usage.agent_id,
                        usage.user_id,
                        usage.tokens_used,
                        usage.cost,
                        usage.response_time,
                        usage.success
                    ])
            
            return output.getvalue()
        
        else:
            raise ValueError(f"Unsupported format: {format}")
