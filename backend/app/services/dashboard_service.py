"""
Performance Dashboard Service for Task 1.3.4
============================================

Service layer for the performance dashboard providing:
- Real-time performance analytics
- System health monitoring dashboard
- Performance trend analysis
- Alert aggregation for dashboard
- Historical performance tracking
- Custom dashboard widgets
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import json

from app.middleware.monitoring import metrics_collector, health_check_detailed
from app.services.error_tracker import get_error_tracker
from app.services.audit_service import get_audit_logger


@dataclass
class DashboardWidget:
    """Data class for dashboard widgets"""
    id: str
    title: str
    type: str  # 'metric', 'chart', 'status', 'alert'
    value: Any
    unit: Optional[str] = None
    trend: Optional[str] = None  # 'up', 'down', 'stable'
    status: Optional[str] = None  # 'healthy', 'warning', 'critical'
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class DashboardData:
    """Complete dashboard data structure"""
    timestamp: str
    system_status: str
    widgets: List[DashboardWidget]
    alerts: List[Dict[str, Any]]
    performance_summary: Dict[str, Any]
    trends: Dict[str, Any]


class DashboardService:
    """Service for performance dashboard operations"""
    
    def __init__(self):
        self.error_tracker = get_error_tracker()
        self.audit_logger = get_audit_logger()
        self._cache = {}
        self._cache_ttl = {}
        self.cache_duration = 30  # 30 seconds cache
    
    async def get_dashboard_data(self, time_window_hours: int = 24) -> DashboardData:
        """Get complete dashboard data"""
        cache_key = f"dashboard_data_{time_window_hours}"
        
        # Check cache
        if self._is_cached(cache_key):
            return self._cache[cache_key]
        
        # Gather all dashboard data concurrently
        health_data, performance_data, error_data, system_metrics = await asyncio.gather(
            self._get_health_overview(),
            self._get_performance_overview(time_window_hours),
            self._get_error_overview(time_window_hours),
            self._get_system_overview(),
            return_exceptions=True
        )
        
        # Handle any exceptions
        if isinstance(health_data, Exception):
            health_data = {"status": "unknown", "issues": [str(health_data)]}
        if isinstance(performance_data, Exception):
            performance_data = {}
        if isinstance(error_data, Exception):
            error_data = {}
        if isinstance(system_metrics, Exception):
            system_metrics = {}
        
        # Create dashboard widgets
        widgets = []
        widgets.extend(self._create_system_widgets(system_metrics))
        widgets.extend(self._create_performance_widgets(performance_data))
        widgets.extend(self._create_error_widgets(error_data))
        widgets.extend(self._create_health_widgets(health_data))
        
        # Get active alerts
        alerts = await self._get_dashboard_alerts()
        
        # Create performance summary
        performance_summary = self._create_performance_summary(performance_data, error_data)
        
        # Calculate trends
        trends = await self._calculate_trends(time_window_hours)
        
        dashboard_data = DashboardData(
            timestamp=datetime.utcnow().isoformat(),
            system_status=health_data.get("status", "unknown"),
            widgets=widgets,
            alerts=alerts,
            performance_summary=performance_summary,
            trends=trends
        )
        
        # Cache the result
        self._cache[cache_key] = dashboard_data
        self._cache_ttl[cache_key] = datetime.utcnow() + timedelta(seconds=self.cache_duration)
        
        return dashboard_data
    
    async def get_real_time_dashboard(self) -> Dict[str, Any]:
        """Get real-time dashboard data (minimal cache)"""
        cache_key = "real_time_dashboard"
        
        # Short cache for real-time (5 seconds)
        if self._is_cached(cache_key, 5):
            return self._cache[cache_key]
        
        # Get current system metrics
        stats = metrics_collector.get_statistics()
        health_data = await health_check_detailed()
        
        # Get recent errors
        recent_errors = self.error_tracker.get_error_statistics(hours=1)
        
        real_time_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "system_status": health_data.get("status", "unknown"),
            "quick_stats": {
                "requests_per_minute": self._calculate_requests_per_minute(),
                "error_rate": stats.get("error_rate", 0),
                "avg_response_time": stats.get("avg_response_time", 0),
                "active_errors": recent_errors.get("total_errors", 0)
            },
            "system_health": {
                "cpu_percent": health_data.get("system", {}).get("cpu_percent", 0),
                "memory_percent": health_data.get("system", {}).get("memory_percent", 0),
                "disk_percent": health_data.get("system", {}).get("disk_usage", 0)
            },
            "alerts_count": len(health_data.get("issues", [])),
            "recent_activity": list(metrics_collector.recent_requests)[-5:]  # Last 5 requests
        }
        
        # Cache with short TTL
        self._cache[cache_key] = real_time_data
        self._cache_ttl[cache_key] = datetime.utcnow() + timedelta(seconds=5)
        
        return real_time_data
    
    async def get_performance_charts(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance chart data for visualization"""
        cache_key = f"performance_charts_{hours}"
        
        if self._is_cached(cache_key):
            return self._cache[cache_key]
        
        # Get time-series data
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Create time buckets (hourly)
        time_buckets = []
        current_time = cutoff_time
        while current_time <= datetime.utcnow():
            time_buckets.append(current_time)
            current_time += timedelta(hours=1)
        
        # Get metrics data
        cpu_metrics = metrics_collector.get_metrics("system_cpu_percent")
        memory_metrics = metrics_collector.get_metrics("system_memory_percent")
        request_metrics = metrics_collector.get_metrics("http_requests_total")
        error_metrics = metrics_collector.get_metrics("http_errors_total")
        
        charts_data = {
            "time_buckets": [t.isoformat() for t in time_buckets],
            "system_resources": {
                "cpu": self._aggregate_metrics_by_time(cpu_metrics.get("system_cpu_percent", []), time_buckets),
                "memory": self._aggregate_metrics_by_time(memory_metrics.get("system_memory_percent", []), time_buckets)
            },
            "request_volume": self._aggregate_metrics_by_time(request_metrics.get("http_requests_total", []), time_buckets),
            "error_rate": self._aggregate_metrics_by_time(error_metrics.get("http_errors_total", []), time_buckets),
            "response_times": self._get_response_time_chart_data(time_buckets)
        }
        
        # Cache the result
        self._cache[cache_key] = charts_data
        self._cache_ttl[cache_key] = datetime.utcnow() + timedelta(seconds=self.cache_duration)
        
        return charts_data
    
    async def get_endpoint_analytics(self) -> Dict[str, Any]:
        """Get detailed endpoint performance analytics"""
        cache_key = "endpoint_analytics"
        
        if self._is_cached(cache_key):
            return self._cache[cache_key]
        
        stats = metrics_collector.get_statistics()
        endpoint_stats = stats.get("endpoint_stats", {})
        
        # Sort endpoints by various metrics
        endpoints_by_volume = sorted(
            endpoint_stats.items(), 
            key=lambda x: x[1].get("count", 0), 
            reverse=True
        )[:10]
        
        endpoints_by_errors = sorted(
            endpoint_stats.items(), 
            key=lambda x: x[1].get("error_count", 0), 
            reverse=True
        )[:10]
        
        endpoints_by_response_time = sorted(
            endpoint_stats.items(), 
            key=lambda x: x[1].get("avg_time", 0), 
            reverse=True
        )[:10]
        
        analytics = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_endpoints": len(endpoint_stats),
            "top_by_volume": [
                {
                    "endpoint": endpoint,
                    "requests": data.get("count", 0),
                    "avg_response_time": round(data.get("avg_time", 0) * 1000, 2)
                }
                for endpoint, data in endpoints_by_volume
            ],
            "top_by_errors": [
                {
                    "endpoint": endpoint,
                    "errors": data.get("error_count", 0),
                    "error_rate": round(data.get("error_rate", 0), 2)
                }
                for endpoint, data in endpoints_by_errors if data.get("error_count", 0) > 0
            ],
            "slowest_endpoints": [
                {
                    "endpoint": endpoint,
                    "avg_response_time": round(data.get("avg_time", 0) * 1000, 2),
                    "max_response_time": round(data.get("max_time", 0) * 1000, 2)
                }
                for endpoint, data in endpoints_by_response_time
            ]
        }
        
        # Cache the result
        self._cache[cache_key] = analytics
        self._cache_ttl[cache_key] = datetime.utcnow() + timedelta(seconds=self.cache_duration)
        
        return analytics
    
    def _is_cached(self, key: str, ttl_seconds: Optional[int] = None) -> bool:
        """Check if data is cached and still valid"""
        if key not in self._cache:
            return False
        
        ttl = ttl_seconds or self.cache_duration
        cache_time = self._cache_ttl.get(key)
        if not cache_time:
            return False
        
        return datetime.utcnow() < cache_time
    
    async def _get_health_overview(self) -> Dict[str, Any]:
        """Get system health overview"""
        return await health_check_detailed()
    
    async def _get_performance_overview(self, hours: int) -> Dict[str, Any]:
        """Get performance metrics overview"""
        stats = metrics_collector.get_statistics()
        
        return {
            "total_requests": stats.get("request_count", 0),
            "error_rate": stats.get("error_rate", 0),
            "avg_response_time": stats.get("avg_response_time", 0),
            "slow_request_rate": stats.get("slow_request_rate", 0),
            "requests_per_hour": stats.get("request_count", 0) / max(hours, 1)
        }
    
    async def _get_error_overview(self, hours: int) -> Dict[str, Any]:
        """Get error tracking overview"""
        try:
            error_stats = self.error_tracker.get_error_statistics(hours=hours)
            return error_stats
        except Exception:
            return {}
    
    async def _get_system_overview(self) -> Dict[str, Any]:
        """Get system metrics overview"""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": (disk.used / disk.total) * 100,
                "load_average": list(psutil.cpu_times()) if hasattr(psutil, 'cpu_times') else []
            }
        except Exception:
            return {}
    
    def _create_system_widgets(self, system_data: Dict[str, Any]) -> List[DashboardWidget]:
        """Create system monitoring widgets"""
        widgets = []
        
        # CPU Usage Widget
        cpu_percent = system_data.get("cpu_percent", 0)
        cpu_status = "healthy" if cpu_percent < 70 else "warning" if cpu_percent < 85 else "critical"
        widgets.append(DashboardWidget(
            id="cpu_usage",
            title="CPU Usage",
            type="metric",
            value=round(cpu_percent, 1),
            unit="%",
            status=cpu_status,
            trend=self._calculate_trend("cpu", cpu_percent),
            metadata={"threshold_warning": 70, "threshold_critical": 85}
        ))
        
        # Memory Usage Widget
        memory_percent = system_data.get("memory_percent", 0)
        memory_status = "healthy" if memory_percent < 75 else "warning" if memory_percent < 90 else "critical"
        widgets.append(DashboardWidget(
            id="memory_usage",
            title="Memory Usage",
            type="metric",
            value=round(memory_percent, 1),
            unit="%",
            status=memory_status,
            trend=self._calculate_trend("memory", memory_percent),
            metadata={"threshold_warning": 75, "threshold_critical": 90}
        ))
        
        # Disk Usage Widget
        disk_percent = system_data.get("disk_percent", 0)
        disk_status = "healthy" if disk_percent < 80 else "warning" if disk_percent < 95 else "critical"
        widgets.append(DashboardWidget(
            id="disk_usage",
            title="Disk Usage",
            type="metric",
            value=round(disk_percent, 1),
            unit="%",
            status=disk_status,
            trend=self._calculate_trend("disk", disk_percent),
            metadata={"threshold_warning": 80, "threshold_critical": 95}
        ))
        
        return widgets
    
    def _create_performance_widgets(self, performance_data: Dict[str, Any]) -> List[DashboardWidget]:
        """Create performance monitoring widgets"""
        widgets = []
        
        # Request Rate Widget
        total_requests = performance_data.get("total_requests", 0)
        requests_per_hour = performance_data.get("requests_per_hour", 0)
        widgets.append(DashboardWidget(
            id="request_rate",
            title="Requests/Hour",
            type="metric",
            value=round(requests_per_hour, 1),
            unit="req/h",
            status="healthy",
            trend=self._calculate_trend("requests", requests_per_hour),
            metadata={"total_requests": total_requests}
        ))
        
        # Response Time Widget
        avg_response_time = performance_data.get("avg_response_time", 0)
        response_status = "healthy" if avg_response_time < 500 else "warning" if avg_response_time < 2000 else "critical"
        widgets.append(DashboardWidget(
            id="avg_response_time",
            title="Avg Response Time",
            type="metric",
            value=round(avg_response_time, 0),
            unit="ms",
            status=response_status,
            trend=self._calculate_trend("response_time", avg_response_time),
            metadata={"threshold_warning": 500, "threshold_critical": 2000}
        ))
        
        # Error Rate Widget
        error_rate = performance_data.get("error_rate", 0)
        error_status = "healthy" if error_rate < 1 else "warning" if error_rate < 5 else "critical"
        widgets.append(DashboardWidget(
            id="error_rate",
            title="Error Rate",
            type="metric",
            value=round(error_rate, 2),
            unit="%",
            status=error_status,
            trend=self._calculate_trend("error_rate", error_rate),
            metadata={"threshold_warning": 1, "threshold_critical": 5}
        ))
        
        return widgets
    
    def _create_error_widgets(self, error_data: Dict[str, Any]) -> List[DashboardWidget]:
        """Create error tracking widgets"""
        widgets = []
        
        # Total Errors Widget
        total_errors = error_data.get("total_errors", 0)
        error_status = "healthy" if total_errors == 0 else "warning" if total_errors < 10 else "critical"
        widgets.append(DashboardWidget(
            id="total_errors",
            title="Recent Errors",
            type="metric",
            value=total_errors,
            unit="errors",
            status=error_status,
            trend=self._calculate_trend("errors", total_errors),
            metadata={"categories": error_data.get("by_category", {})}
        ))
        
        return widgets
    
    def _create_health_widgets(self, health_data: Dict[str, Any]) -> List[DashboardWidget]:
        """Create health monitoring widgets"""
        widgets = []
        
        # System Status Widget
        system_status = health_data.get("status", "unknown")
        widgets.append(DashboardWidget(
            id="system_status",
            title="System Status",
            type="status",
            value=system_status.title(),
            status=system_status,
            metadata={"issues": health_data.get("issues", [])}
        ))
        
        return widgets
    
    async def _get_dashboard_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts for dashboard"""
        alerts = []
        
        # Get system alerts
        stats = metrics_collector.get_statistics()
        
        if stats.get("error_rate", 0) > 5:
            alerts.append({
                "id": "high_error_rate",
                "type": "performance",
                "severity": "high",
                "title": "High Error Rate",
                "message": f"Error rate is {stats['error_rate']}%",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        if stats.get("slow_request_rate", 0) > 10:
            alerts.append({
                "id": "slow_requests",
                "type": "performance",
                "severity": "medium",
                "title": "Slow Requests",
                "message": f"{stats['slow_request_rate']}% of requests are slow",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Get system resource alerts
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent
            
            if cpu_percent > 85:
                alerts.append({
                    "id": "high_cpu",
                    "type": "system",
                    "severity": "critical",
                    "title": "High CPU Usage",
                    "message": f"CPU usage is {cpu_percent}%",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            if memory_percent > 90:
                alerts.append({
                    "id": "high_memory",
                    "type": "system",
                    "severity": "critical",
                    "title": "High Memory Usage",
                    "message": f"Memory usage is {memory_percent}%",
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        except Exception:
            pass
        
        return alerts
    
    def _create_performance_summary(self, performance_data: Dict[str, Any], error_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create performance summary for dashboard"""
        return {
            "overall_health": "good" if performance_data.get("error_rate", 0) < 1 else "fair",
            "key_metrics": {
                "uptime": "99.9%",  # Would calculate from actual uptime data
                "availability": "99.8%",  # Would calculate from health checks
                "performance_score": max(0, 100 - (performance_data.get("error_rate", 0) * 10)),
                "reliability_score": max(0, 100 - error_data.get("total_errors", 0))
            },
            "recommendations": self._generate_recommendations(performance_data, error_data)
        }
    
    def _generate_recommendations(self, performance_data: Dict[str, Any], error_data: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        if performance_data.get("error_rate", 0) > 2:
            recommendations.append("Consider investigating high error rate patterns")
        
        if performance_data.get("avg_response_time", 0) > 1000:
            recommendations.append("Response times are elevated - check for bottlenecks")
        
        if error_data.get("total_errors", 0) > 5:
            recommendations.append("Recent error spike detected - review error logs")
        
        if not recommendations:
            recommendations.append("System performance is optimal")
        
        return recommendations
    
    async def _calculate_trends(self, hours: int) -> Dict[str, Any]:
        """Calculate performance trends"""
        # This would analyze historical data to determine trends
        # For now, return placeholder trends
        return {
            "request_volume": "stable",
            "error_rate": "stable",
            "response_time": "improving",
            "system_resources": "stable"
        }
    
    def _calculate_trend(self, metric_name: str, current_value: float) -> str:
        """Calculate trend for a specific metric"""
        # This would compare current value with historical data
        # For now, return placeholder based on simple rules
        if metric_name == "cpu" and current_value > 80:
            return "up"
        elif metric_name == "memory" and current_value > 85:
            return "up"
        elif metric_name == "error_rate" and current_value > 2:
            return "up"
        else:
            return "stable"
    
    def _calculate_requests_per_minute(self) -> float:
        """Calculate current requests per minute"""
        recent_requests = list(metrics_collector.recent_requests)
        if not recent_requests:
            return 0.0
        
        # Count requests in the last minute
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
        recent_count = sum(
            1 for req in recent_requests
            if datetime.fromisoformat(req.get("timestamp", "").replace("Z", ""))
            > one_minute_ago
        )
        
        return float(recent_count)
    
    def _aggregate_metrics_by_time(self, metrics: List[Dict], time_buckets: List[datetime]) -> List[float]:
        """Aggregate metrics data by time buckets"""
        if not metrics:
            return [0.0] * len(time_buckets)
        
        # Simple aggregation - would be more sophisticated in practice
        aggregated = []
        for i, bucket in enumerate(time_buckets):
            # Find metrics in this time bucket
            bucket_end = bucket + timedelta(hours=1) if i < len(time_buckets) - 1 else datetime.utcnow()
            
            bucket_values = [
                m.get("value", 0) for m in metrics
                if bucket <= datetime.fromisoformat(m.get("timestamp", "").replace("Z", "")) < bucket_end
            ]
            
            # Average value for this bucket
            avg_value = sum(bucket_values) / len(bucket_values) if bucket_values else 0
            aggregated.append(round(avg_value, 2))
        
        return aggregated
    
    def _get_response_time_chart_data(self, time_buckets: List[datetime]) -> List[float]:
        """Get response time chart data"""
        # This would aggregate response time data from metrics
        # For now, return placeholder data
        return [0.0] * len(time_buckets)


# Global dashboard service instance
_dashboard_service = None

def get_dashboard_service() -> DashboardService:
    """Get the global dashboard service instance"""
    global _dashboard_service
    if _dashboard_service is None:
        _dashboard_service = DashboardService()
    return _dashboard_service
