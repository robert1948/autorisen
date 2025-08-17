"""
Analytics Service for Performance Analytics Dashboard
Handles system metrics, user behavior tracking, and performance analysis.
"""
import asyncio
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from app.models.analytics import AnalyticsEvent, SystemMetrics, UserSession, APIUsageStats
from app.models import User
from app.database import get_db
import logging
import json
import uuid

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for collecting and analyzing performance and user data"""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.request_count = 0
        self.active_sessions = {}
        
    async def record_system_metrics(self, db: Session) -> Dict[str, float]:
        """Record current system performance metrics"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics = {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_usage': disk.percent,
                'disk_free_gb': disk.free / (1024**3)
            }
            
            # Record metrics in database
            for metric_type, value in metrics.items():
                metric_record = SystemMetrics(
                    metric_type=metric_type,
                    metric_value=value,
                    metric_unit='percent' if 'usage' in metric_type else 'gb',
                    source='localhost'
                )
                db.add(metric_record)
            
            db.commit()
            logger.info(f"System metrics recorded: CPU {cpu_percent}%, Memory {memory.percent}%")
            return metrics
            
        except Exception as e:
            logger.error(f"Error recording system metrics: {e}")
            return {}
    
    async def record_user_event(self, db: Session, user_id: Optional[str], event_type: str, 
                               event_category: str, event_data: Optional[Dict] = None,
                               endpoint: Optional[str] = None, method: Optional[str] = None,
                               status_code: Optional[int] = None, duration_ms: Optional[float] = None,
                               ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """Record a user interaction event"""
        try:
            event = AnalyticsEvent(
                user_id=user_id,
                event_type=event_type,
                event_category=event_category,
                event_data=event_data,
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                duration_ms=duration_ms,
                ip_address=ip_address,
                user_agent=user_agent
            )
            db.add(event)
            db.commit()
            
            logger.debug(f"User event recorded: {event_type} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error recording user event: {e}")
    
    async def get_dashboard_data(self, db: Session, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive dashboard data for the specified time period"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # System Performance Metrics
            recent_metrics = db.query(SystemMetrics).filter(
                SystemMetrics.recorded_at >= cutoff_time
            ).order_by(desc(SystemMetrics.recorded_at)).limit(100).all()
            
            # User Activity Metrics
            user_events = db.query(AnalyticsEvent).filter(
                AnalyticsEvent.created_at >= cutoff_time
            ).count()
            
            unique_users = db.query(AnalyticsEvent.user_id).filter(
                and_(
                    AnalyticsEvent.created_at >= cutoff_time,
                    AnalyticsEvent.user_id.isnot(None)
                )
            ).distinct().count()
            
            # API Usage Statistics
            api_calls = db.query(AnalyticsEvent).filter(
                and_(
                    AnalyticsEvent.created_at >= cutoff_time,
                    AnalyticsEvent.event_category == 'api'
                )
            ).count()
            
            # Average response time
            avg_response_time = db.query(func.avg(AnalyticsEvent.duration_ms)).filter(
                and_(
                    AnalyticsEvent.created_at >= cutoff_time,
                    AnalyticsEvent.duration_ms.isnot(None)
                )
            ).scalar() or 0
            
            # Error rate
            error_count = db.query(AnalyticsEvent).filter(
                and_(
                    AnalyticsEvent.created_at >= cutoff_time,
                    AnalyticsEvent.status_code >= 400
                )
            ).count()
            
            # Active sessions
            active_sessions = db.query(UserSession).filter(
                UserSession.is_active == True
            ).count()
            
            # Top endpoints
            top_endpoints = db.query(
                AnalyticsEvent.endpoint,
                func.count(AnalyticsEvent.id).label('count'),
                func.avg(AnalyticsEvent.duration_ms).label('avg_duration')
            ).filter(
                and_(
                    AnalyticsEvent.created_at >= cutoff_time,
                    AnalyticsEvent.endpoint.isnot(None)
                )
            ).group_by(AnalyticsEvent.endpoint).order_by(desc('count')).limit(10).all()
            
            # Performance trends (hourly data for the last 24 hours)
            performance_trends = []
            for i in range(24):
                hour_start = datetime.utcnow() - timedelta(hours=i+1)
                hour_end = datetime.utcnow() - timedelta(hours=i)
                
                hour_metrics = db.query(SystemMetrics).filter(
                    and_(
                        SystemMetrics.recorded_at >= hour_start,
                        SystemMetrics.recorded_at < hour_end,
                        SystemMetrics.metric_type.in_(['cpu_usage', 'memory_usage'])
                    )
                ).all()
                
                if hour_metrics:
                    cpu_values = [m.metric_value for m in hour_metrics if m.metric_type == 'cpu_usage']
                    memory_values = [m.metric_value for m in hour_metrics if m.metric_type == 'memory_usage']
                    
                    performance_trends.append({
                        'hour': hour_start.strftime('%H:00'),
                        'cpu_avg': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                        'memory_avg': sum(memory_values) / len(memory_values) if memory_values else 0,
                        'timestamp': hour_start.isoformat()
                    })
            
            performance_trends.reverse()  # Show chronological order
            
            return {
                'system_metrics': {
                    'cpu_usage': recent_metrics[0].metric_value if recent_metrics and recent_metrics[0].metric_type == 'cpu_usage' else 0,
                    'memory_usage': next((m.metric_value for m in recent_metrics if m.metric_type == 'memory_usage'), 0),
                    'disk_usage': next((m.metric_value for m in recent_metrics if m.metric_type == 'disk_usage'), 0),
                    'uptime_hours': (datetime.utcnow() - self.start_time).total_seconds() / 3600
                },
                'user_activity': {
                    'total_events': user_events,
                    'unique_users': unique_users,
                    'active_sessions': active_sessions,
                    'events_per_user': user_events / max(unique_users, 1)
                },
                'api_metrics': {
                    'total_calls': api_calls,
                    'avg_response_time_ms': round(avg_response_time, 2),
                    'error_count': error_count,
                    'error_rate': round((error_count / max(api_calls, 1)) * 100, 2),
                    'success_rate': round(((api_calls - error_count) / max(api_calls, 1)) * 100, 2)
                },
                'top_endpoints': [
                    {
                        'endpoint': endpoint,
                        'calls': count,
                        'avg_duration_ms': round(avg_duration or 0, 2)
                    }
                    for endpoint, count, avg_duration in top_endpoints
                ],
                'performance_trends': performance_trends,
                'period_hours': hours,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {
                'error': str(e),
                'system_metrics': {},
                'user_activity': {},
                'api_metrics': {},
                'top_endpoints': [],
                'performance_trends': [],
                'period_hours': hours,
                'last_updated': datetime.utcnow().isoformat()
            }
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time system metrics without database storage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            # Get recent request count (mock data for now)
            current_requests_per_minute = self.request_count
            
            return {
                'cpu_usage': round(cpu_percent, 1),
                'memory_usage': round(memory.percent, 1),
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'requests_per_minute': current_requests_per_minute,
                'uptime_seconds': int((datetime.utcnow() - self.start_time).total_seconds()),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time metrics: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def increment_request_count(self):
        """Increment the request counter for rate tracking"""
        self.request_count += 1
    
    async def start_metrics_collection(self, db_session_factory, interval_seconds: int = 60):
        """Start background metrics collection"""
        logger.info(f"Starting metrics collection with {interval_seconds}s interval")
        
        while True:
            try:
                db = next(db_session_factory())
                await self.record_system_metrics(db)
                db.close()
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                await asyncio.sleep(interval_seconds)

# Global analytics service instance
analytics_service = AnalyticsService()
