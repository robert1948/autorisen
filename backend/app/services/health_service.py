"""
Enhanced Health Check Service for Task 1.3.5 - Advanced Endpoint Monitoring
============================================================================

Comprehensive health check system providing:
- Advanced endpoint monitoring with detailed status checks
- Service dependency health verification
- Real-time system health assessment
- Custom health check plugins
- Health trend analysis and alerting
- Performance threshold monitoring
- Automated recovery suggestions
"""

import logging
import time
import asyncio
import psutil
import os
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import httpx
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.error_tracker import get_error_tracker, ErrorSeverity
from app.services.audit_service import get_audit_logger, AuditEventType


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    WARNING = "warning" 
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


class ServiceType(Enum):
    """Service types for health checks"""
    CORE_API = "core_api"
    DATABASE = "database"
    EXTERNAL_API = "external_api"
    BACKGROUND_TASK = "background_task"
    CACHE = "cache"
    FILE_SYSTEM = "file_system"
    NETWORK = "network"


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    service_name: str
    service_type: ServiceType
    status: HealthStatus
    response_time_ms: float
    timestamp: datetime
    details: Dict[str, Any]
    error_message: Optional[str] = None
    suggestions: List[str] = None
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []


@dataclass
class EndpointHealthCheck:
    """Configuration for endpoint health monitoring"""
    name: str
    url: str
    method: str = "GET"
    timeout: int = 5
    expected_status: int = 200
    expected_response_key: Optional[str] = None
    expected_response_value: Optional[Any] = None
    critical: bool = False
    headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}


class HealthService:
    """Enhanced health check service with advanced monitoring"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.audit_logger = get_audit_logger()
        self.error_tracker = get_error_tracker()
        
        # Health check history for trend analysis
        self.health_history = defaultdict(lambda: deque(maxlen=100))
        
        # Health check configuration
        self.thresholds = {
            'cpu_warning': 70.0,
            'cpu_critical': 85.0,
            'memory_warning': 75.0,
            'memory_critical': 90.0,
            'disk_warning': 80.0,
            'disk_critical': 95.0,
            'response_time_warning': 1000.0,  # ms
            'response_time_critical': 5000.0,  # ms
            'error_rate_warning': 5.0,  # percentage
            'error_rate_critical': 15.0,  # percentage
        }
        
        # Registered health checks
        self.health_checks: Dict[str, Callable] = {}
        self.endpoint_checks: List[EndpointHealthCheck] = []
        
        # Initialize built-in health checks
        self._register_builtin_checks()
    
    def _register_builtin_checks(self):
        """Register built-in health checks"""
        self.register_health_check("system_resources", self._check_system_resources)
        self.register_health_check("database_connection", self._check_database_connection)
        self.register_health_check("error_rates", self._check_error_rates)
        self.register_health_check("disk_space", self._check_disk_space)
        self.register_health_check("process_health", self._check_process_health)
        
        # Register critical endpoints
        self._register_critical_endpoints()
    
    def _register_critical_endpoints(self):
        """Register critical endpoints for monitoring"""
        base_url = os.getenv("BASE_URL", "http://localhost:8000")
        
        # Core API endpoints
        self.endpoint_checks.extend([
            EndpointHealthCheck(
                name="Main Health Check",
                url=f"{base_url}/api/health",
                critical=True,
                expected_response_key="status"
            ),
            EndpointHealthCheck(
                name="Authentication Service", 
                url=f"{base_url}/api/auth/health",
                critical=True
            ),
            EndpointHealthCheck(
                name="Monitoring API",
                url=f"{base_url}/api/monitoring/health",
                critical=False
            ),
            EndpointHealthCheck(
                name="Dashboard API",
                url=f"{base_url}/api/dashboard/health", 
                critical=False
            ),
            EndpointHealthCheck(
                name="Error Tracking API",
                url=f"{base_url}/api/errors/health",
                critical=False
            )
        ])
    
    def register_health_check(self, name: str, check_function: Callable):
        """Register a custom health check function"""
        self.health_checks[name] = check_function
        self.logger.info(f"Registered health check: {name}")
    
    def register_endpoint_check(self, endpoint_check: EndpointHealthCheck):
        """Register an endpoint for health monitoring"""
        self.endpoint_checks.append(endpoint_check)
        self.logger.info(f"Registered endpoint check: {endpoint_check.name}")
    
    async def run_comprehensive_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check with all registered checks"""
        start_time = time.time()
        
        results = {
            "overall_status": HealthStatus.HEALTHY,
            "timestamp": datetime.utcnow().isoformat(),
            "check_duration_ms": 0,
            "services": {},
            "endpoints": {},
            "system_metrics": {},
            "alerts": [],
            "suggestions": [],
            "trends": {}
        }
        
        try:
            # Run system health checks
            for check_name, check_function in self.health_checks.items():
                try:
                    check_result = await self._run_health_check(check_name, check_function)
                    results["services"][check_name] = asdict(check_result)
                    
                    # Update overall status
                    if check_result.status.value == HealthStatus.CRITICAL.value:
                        results["overall_status"] = HealthStatus.CRITICAL
                    elif (check_result.status.value == HealthStatus.UNHEALTHY.value and 
                          results["overall_status"].value != HealthStatus.CRITICAL.value):
                        results["overall_status"] = HealthStatus.UNHEALTHY
                    elif (check_result.status.value == HealthStatus.DEGRADED.value and 
                          results["overall_status"].value not in [HealthStatus.CRITICAL.value, HealthStatus.UNHEALTHY.value]):
                        results["overall_status"] = HealthStatus.DEGRADED
                    elif (check_result.status.value == HealthStatus.WARNING.value and 
                          results["overall_status"].value == HealthStatus.HEALTHY.value):
                        results["overall_status"] = HealthStatus.WARNING
                    
                    # Collect alerts and suggestions
                    if check_result.error_message:
                        results["alerts"].append({
                            "service": check_name,
                            "message": check_result.error_message,
                            "severity": check_result.status.value
                        })
                    
                    results["suggestions"].extend(check_result.suggestions)
                    
                    # Store in history for trend analysis
                    self.health_history[check_name].append({
                        "timestamp": check_result.timestamp,
                        "status": check_result.status.value,
                        "response_time": check_result.response_time_ms
                    })
                    
                except Exception as e:
                    self.logger.error(f"Health check {check_name} failed: {str(e)}")
                    results["services"][check_name] = {
                        "service_name": check_name,
                        "status": HealthStatus.UNHEALTHY.value,
                        "error_message": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    }
            
            # Run endpoint health checks
            endpoint_results = await self._check_endpoints()
            results["endpoints"] = endpoint_results
            
            # Generate system metrics summary
            results["system_metrics"] = await self._get_system_metrics_summary()
            
            # Analyze trends
            results["trends"] = self._analyze_health_trends()
            
            # Calculate overall check duration
            results["check_duration_ms"] = round((time.time() - start_time) * 1000, 2)
            
            # Log health check completion
            self.audit_logger.log_system_event(
                db=next(get_db()),
                event_type=AuditEventType.SYSTEM_HEALTH_CHECK,
                component="health_service",
                status="completed",
                metadata={
                    "overall_status": results["overall_status"].value if hasattr(results["overall_status"], 'value') else results["overall_status"],
                    "services_checked": len(results["services"]),
                    "endpoints_checked": len(results["endpoints"]),
                    "duration_ms": results["check_duration_ms"]
                }
            )
            
        except Exception as e:
            self.logger.error(f"Comprehensive health check failed: {str(e)}")
            results["overall_status"] = HealthStatus.CRITICAL
            results["alerts"].append({
                "service": "health_service",
                "message": f"Health check system failure: {str(e)}",
                "severity": HealthStatus.CRITICAL.value
            })
        
        return results
    
    async def _run_health_check(self, name: str, check_function: Callable) -> HealthCheckResult:
        """Run a single health check with timing"""
        start_time = time.time()
        
        try:
            result = await check_function()
            response_time = (time.time() - start_time) * 1000
            
            if isinstance(result, HealthCheckResult):
                result.response_time_ms = response_time
                return result
            else:
                # Convert legacy result format
                return HealthCheckResult(
                    service_name=name,
                    service_type=ServiceType.CORE_API,
                    status=result.get("status", HealthStatus.HEALTHY),
                    response_time_ms=response_time,
                    timestamp=datetime.utcnow(),
                    details=result
                )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                service_name=name,
                service_type=ServiceType.CORE_API,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                details={},
                error_message=str(e),
                suggestions=[f"Check {name} service configuration and logs"]
            )
    
    async def _check_system_resources(self) -> HealthCheckResult:
        """Check system resource utilization"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        status = HealthStatus.HEALTHY
        suggestions = []
        error_message = None
        
        if cpu_percent > self.thresholds['cpu_critical']:
            status = HealthStatus.CRITICAL
            error_message = f"Critical CPU usage: {cpu_percent}%"
            suggestions.append("Scale up server resources or optimize high-CPU processes")
        elif cpu_percent > self.thresholds['cpu_warning']:
            status = HealthStatus.WARNING
            error_message = f"High CPU usage: {cpu_percent}%"
            suggestions.append("Monitor CPU usage and consider optimization")
        
        if memory.percent > self.thresholds['memory_critical']:
            if status.value != HealthStatus.CRITICAL.value:
                status = HealthStatus.CRITICAL
            error_message = f"Critical memory usage: {memory.percent}%"
            suggestions.append("Increase memory or reduce memory usage")
        elif memory.percent > self.thresholds['memory_warning']:
            if status.value == HealthStatus.HEALTHY.value:
                status = HealthStatus.WARNING
            if not error_message:
                error_message = f"High memory usage: {memory.percent}%"
            suggestions.append("Monitor memory usage patterns")
        
        return HealthCheckResult(
            service_name="system_resources",
            service_type=ServiceType.CORE_API,
            status=status,
            response_time_ms=0,
            timestamp=datetime.utcnow(),
            details={
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "memory_total": memory.total
            },
            error_message=error_message,
            suggestions=suggestions
        )
    
    async def _check_database_connection(self) -> HealthCheckResult:
        """Check database connectivity and performance"""
        start_time = time.time()
        
        try:
            db = next(get_db())
            
            # Test basic connectivity
            db.execute("SELECT 1")
            
            # Test performance with a more complex query
            result = db.execute("SELECT COUNT(*) FROM information_schema.tables")
            table_count = result.scalar()
            
            response_time = (time.time() - start_time) * 1000
            
            status = HealthStatus.HEALTHY
            suggestions = []
            error_message = None
            
            if response_time > self.thresholds['response_time_critical']:
                status = HealthStatus.CRITICAL
                error_message = f"Database response time critical: {response_time:.2f}ms"
                suggestions.append("Check database performance and connection pool")
            elif response_time > self.thresholds['response_time_warning']:
                status = HealthStatus.WARNING
                error_message = f"Database response time high: {response_time:.2f}ms"
                suggestions.append("Monitor database query performance")
            
            db.close()
            
            return HealthCheckResult(
                service_name="database_connection",
                service_type=ServiceType.DATABASE,
                status=status,
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                details={
                    "connected": True,
                    "table_count": table_count,
                    "query_time_ms": response_time
                },
                error_message=error_message,
                suggestions=suggestions
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                service_name="database_connection",
                service_type=ServiceType.DATABASE,
                status=HealthStatus.CRITICAL,
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                details={"connected": False},
                error_message=f"Database connection failed: {str(e)}",
                suggestions=["Check database server status and connection configuration"]
            )
    
    async def _check_error_rates(self) -> HealthCheckResult:
        """Check application error rates"""
        try:
            error_stats = self.error_tracker.get_error_statistics()
            error_rate_1min = error_stats.get("error_rates", {}).get("1min", 0)
            critical_errors = error_stats.get("errors_by_severity", {}).get("critical", 0)
            
            status = HealthStatus.HEALTHY
            suggestions = []
            error_message = None
            
            if error_rate_1min > self.thresholds['error_rate_critical'] or critical_errors > 10:
                status = HealthStatus.CRITICAL
                error_message = f"Critical error rate: {error_rate_1min}% (Critical errors: {critical_errors})"
                suggestions.append("Investigate critical errors immediately")
            elif error_rate_1min > self.thresholds['error_rate_warning'] or critical_errors > 0:
                status = HealthStatus.WARNING
                error_message = f"High error rate: {error_rate_1min}% (Critical errors: {critical_errors})"
                suggestions.append("Review recent error logs and patterns")
            
            return HealthCheckResult(
                service_name="error_rates",
                service_type=ServiceType.CORE_API,
                status=status,
                response_time_ms=0,
                timestamp=datetime.utcnow(),
                details={
                    "error_rate_1min": error_rate_1min,
                    "critical_errors": critical_errors,
                    "total_errors": error_stats.get("total_errors", 0),
                    "patterns_detected": error_stats.get("patterns_count", 0)
                },
                error_message=error_message,
                suggestions=suggestions
            )
            
        except Exception as e:
            return HealthCheckResult(
                service_name="error_rates",
                service_type=ServiceType.CORE_API,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0,
                timestamp=datetime.utcnow(),
                details={},
                error_message=f"Error rate check failed: {str(e)}",
                suggestions=["Check error tracking service configuration"]
            )
    
    async def _check_disk_space(self) -> HealthCheckResult:
        """Check disk space availability"""
        try:
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            status = HealthStatus.HEALTHY
            suggestions = []
            error_message = None
            
            if disk_percent > self.thresholds['disk_critical']:
                status = HealthStatus.CRITICAL
                error_message = f"Critical disk usage: {disk_percent:.1f}%"
                suggestions.append("Free up disk space immediately or add more storage")
            elif disk_percent > self.thresholds['disk_warning']:
                status = HealthStatus.WARNING
                error_message = f"High disk usage: {disk_percent:.1f}%"
                suggestions.append("Monitor disk usage and plan for additional storage")
            
            return HealthCheckResult(
                service_name="disk_space",
                service_type=ServiceType.FILE_SYSTEM,
                status=status,
                response_time_ms=0,
                timestamp=datetime.utcnow(),
                details={
                    "disk_percent": disk_percent,
                    "free_gb": disk.free / (1024**3),
                    "total_gb": disk.total / (1024**3),
                    "used_gb": disk.used / (1024**3)
                },
                error_message=error_message,
                suggestions=suggestions
            )
            
        except Exception as e:
            return HealthCheckResult(
                service_name="disk_space",
                service_type=ServiceType.FILE_SYSTEM,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0,
                timestamp=datetime.utcnow(),
                details={},
                error_message=f"Disk space check failed: {str(e)}",
                suggestions=["Check file system permissions and disk access"]
            )
    
    async def _check_process_health(self) -> HealthCheckResult:
        """Check process health and resource usage"""
        try:
            current_process = psutil.Process()
            
            # Get process metrics
            cpu_percent = current_process.cpu_percent()
            memory_info = current_process.memory_info()
            memory_percent = current_process.memory_percent()
            num_threads = current_process.num_threads()
            open_files = len(current_process.open_files())
            
            status = HealthStatus.HEALTHY
            suggestions = []
            error_message = None
            
            # Check for process health issues
            if memory_percent > 50:  # Process using >50% of system memory
                status = HealthStatus.WARNING
                error_message = f"Process memory usage high: {memory_percent:.1f}%"
                suggestions.append("Monitor for memory leaks")
            
            if num_threads > 200:  # High thread count
                if status.value == HealthStatus.HEALTHY.value:
                    status = HealthStatus.WARNING
                if not error_message:
                    error_message = f"High thread count: {num_threads}"
                suggestions.append("Review thread pool configuration")
            
            return HealthCheckResult(
                service_name="process_health",
                service_type=ServiceType.CORE_API,
                status=status,
                response_time_ms=0,
                timestamp=datetime.utcnow(),
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                    "memory_mb": memory_info.rss / (1024*1024),
                    "num_threads": num_threads,
                    "open_files": open_files,
                    "pid": current_process.pid
                },
                error_message=error_message,
                suggestions=suggestions
            )
            
        except Exception as e:
            return HealthCheckResult(
                service_name="process_health",
                service_type=ServiceType.CORE_API,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0,
                timestamp=datetime.utcnow(),
                details={},
                error_message=f"Process health check failed: {str(e)}",
                suggestions=["Check process permissions and system access"]
            )
    
    async def _check_endpoints(self) -> Dict[str, Any]:
        """Check all registered endpoints"""
        endpoint_results = {}
        
        async with httpx.AsyncClient() as client:
            for endpoint_check in self.endpoint_checks:
                try:
                    start_time = time.time()
                    
                    response = await client.request(
                        method=endpoint_check.method,
                        url=endpoint_check.url,
                        headers=endpoint_check.headers,
                        timeout=endpoint_check.timeout
                    )
                    
                    response_time = (time.time() - start_time) * 1000
                    
                    # Determine status
                    status = HealthStatus.HEALTHY
                    error_message = None
                    suggestions = []
                    
                    if response.status_code != endpoint_check.expected_status:
                        status = HealthStatus.UNHEALTHY if endpoint_check.critical else HealthStatus.WARNING
                        error_message = f"Unexpected status code: {response.status_code}"
                        suggestions.append(f"Check {endpoint_check.name} service configuration")
                    
                    # Check response content if specified
                    if endpoint_check.expected_response_key and response.status_code == 200:
                        try:
                            json_response = response.json()
                            if endpoint_check.expected_response_key not in json_response:
                                status = HealthStatus.WARNING
                                error_message = f"Missing expected key: {endpoint_check.expected_response_key}"
                        except Exception:
                            pass  # Non-JSON response is okay if not specifically checking content
                    
                    # Check response time
                    if response_time > self.thresholds['response_time_critical']:
                        if status.value == HealthStatus.HEALTHY.value:
                            status = HealthStatus.WARNING
                        suggestions.append("Optimize endpoint performance")
                    
                    endpoint_results[endpoint_check.name] = {
                        "status": status.value,
                        "response_time_ms": round(response_time, 2),
                        "status_code": response.status_code,
                        "url": endpoint_check.url,
                        "critical": endpoint_check.critical,
                        "error_message": error_message,
                        "suggestions": suggestions,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                except Exception as e:
                    endpoint_results[endpoint_check.name] = {
                        "status": HealthStatus.UNHEALTHY.value if endpoint_check.critical else HealthStatus.WARNING.value,
                        "response_time_ms": 0,
                        "status_code": 0,
                        "url": endpoint_check.url,
                        "critical": endpoint_check.critical,
                        "error_message": str(e),
                        "suggestions": [f"Check {endpoint_check.name} service availability"],
                        "timestamp": datetime.utcnow().isoformat()
                    }
        
        return endpoint_results
    
    async def _get_system_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive system metrics summary"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network stats if available
            network_stats = {}
            try:
                net_io = psutil.net_io_counters()
                network_stats = {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv
                }
            except Exception:
                pass
            
            # Load average if available
            load_avg = None
            if hasattr(os, 'getloadavg'):
                load_avg = os.getloadavg()
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "load_average": load_avg
                },
                "memory": {
                    "percent": memory.percent,
                    "available_gb": memory.available / (1024**3),
                    "total_gb": memory.total / (1024**3),
                    "used_gb": memory.used / (1024**3)
                },
                "disk": {
                    "percent": (disk.used / disk.total) * 100,
                    "free_gb": disk.free / (1024**3),
                    "total_gb": disk.total / (1024**3),
                    "used_gb": disk.used / (1024**3)
                },
                "network": network_stats,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_health_trends(self) -> Dict[str, Any]:
        """Analyze health trends from historical data"""
        trends = {}
        
        for service_name, history in self.health_history.items():
            if len(history) < 2:
                continue
            
            # Convert to lists for analysis
            timestamps = [h["timestamp"] for h in history]
            statuses = [h["status"] for h in history]
            response_times = [h["response_time"] for h in history]
            
            # Recent trend analysis (last 10 checks)
            recent_history = list(history)[-10:]
            recent_statuses = [h["status"] for h in recent_history]
            
            # Calculate trend metrics
            healthy_count = recent_statuses.count(HealthStatus.HEALTHY.value)
            warning_count = recent_statuses.count(HealthStatus.WARNING.value)
            degraded_count = recent_statuses.count(HealthStatus.DEGRADED.value)
            unhealthy_count = recent_statuses.count(HealthStatus.UNHEALTHY.value)
            critical_count = recent_statuses.count(HealthStatus.CRITICAL.value)
            
            # Determine trend direction
            trend_direction = "stable"
            if len(recent_history) >= 3:
                last_three = recent_statuses[-3:]
                if all(s in [HealthStatus.UNHEALTHY.value, HealthStatus.CRITICAL.value] for s in last_three):
                    trend_direction = "deteriorating"
                elif all(s == HealthStatus.HEALTHY.value for s in last_three):
                    trend_direction = "improving"
            
            trends[service_name] = {
                "trend_direction": trend_direction,
                "recent_status_distribution": {
                    "healthy": healthy_count,
                    "warning": warning_count,
                    "degraded": degraded_count,
                    "unhealthy": unhealthy_count,
                    "critical": critical_count
                },
                "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
                "last_status": statuses[-1] if statuses else None,
                "checks_analyzed": len(recent_history)
            }
        
        return trends
    
    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Get health status for a specific service"""
        if service_name not in self.health_checks:
            return {
                "error": f"Service '{service_name}' not found",
                "available_services": list(self.health_checks.keys())
            }
        
        check_function = self.health_checks[service_name]
        result = await self._run_health_check(service_name, check_function)
        
        return {
            "service": asdict(result),
            "history": list(self.health_history[service_name])[-10:],  # Last 10 checks
            "trend": self._analyze_health_trends().get(service_name, {})
        }
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a quick health summary"""
        summary = {
            "registered_checks": len(self.health_checks),
            "registered_endpoints": len(self.endpoint_checks),
            "thresholds": self.thresholds,
            "last_check_results": {}
        }
        
        # Get latest results for each service
        for service_name in self.health_checks.keys():
            if self.health_history[service_name]:
                latest = self.health_history[service_name][-1]
                summary["last_check_results"][service_name] = latest
        
        return summary


# Global health service instance
_health_service_instance = None

def get_health_service() -> HealthService:
    """Get global health service instance"""
    global _health_service_instance
    if _health_service_instance is None:
        _health_service_instance = HealthService()
    return _health_service_instance
