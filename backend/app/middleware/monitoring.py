"""
Enhanced Monitoring Middleware with Performance Tracking
Enterprise-grade monitoring with metrics collection and performance insights
"""

import time
import json
import asyncio
import psutil
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# Global monitoring instance for external access
_monitoring_middleware_instance: Optional['MonitoringMiddleware'] = None

class MonitoringMiddleware(BaseHTTPMiddleware):
    """Enterprise monitoring middleware with comprehensive metrics"""

    def __init__(self, app, max_requests: int = 1000):
        super().__init__(app)
        self.max_requests = max_requests
        self.requests: List[Dict[str, Any]] = []
        self.metrics: Dict[str, Any] = {
            "total_requests": 0,
            "total_response_time": 0.0,
            "errors": 0,
            "slow_requests": 0,
            "avg_response_time": 0.0,
            "requests_per_minute": 0.0,
            "memory_usage": 0.0,
            "cpu_usage": 0.0
        }
        self.start_time = datetime.now()
        self.last_cleanup = datetime.now()
        self._last_system_update = datetime.min

        # Set global instance
        global _monitoring_middleware_instance
        _monitoring_middleware_instance = self

        logger.info("MonitoringMiddleware initialized")

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with comprehensive monitoring"""
        start_time = time.time()
        request_id = f"{int(time.time())}-{id(request)}"

        # Collect request info
        request_info = {
            "id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "start_time": start_time
        }

        try:
            # Process request
            response = await call_next(request)

            # Calculate response time
            end_time = time.time()
            response_time = end_time - start_time

            # Update request info with response data
            request_info.update({
                "status_code": response.status_code,
                "response_time": response_time,
                "success": 200 <= response.status_code < 400,
                "end_time": end_time
            })

            # Add monitoring headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{response_time:.3f}s"
            response.headers["X-Timestamp"] = datetime.now().isoformat()

            # Update metrics
            await self._update_metrics(request_info)

            return response

        except Exception as e:
            # Handle errors
            end_time = time.time()
            response_time = end_time - start_time

            request_info.update({
                "status_code": 500,
                "response_time": response_time,
                "success": False,
                "error": str(e),
                "end_time": end_time
            })

            await self._update_metrics(request_info)

            logger.error(f"Request {request_id} failed: {e}")

            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error", "request_id": request_id},
                headers={
                    "X-Request-ID": request_id,
                    "X-Response-Time": f"{response_time:.3f}s",
                    "X-Error": "true"
                }
            )

    async def _update_metrics(self, request_info: Dict[str, Any]) -> None:
        """Update comprehensive metrics"""
        try:
            # Add to requests list (with rotation)
            self.requests.append(request_info)
            if len(self.requests) > self.max_requests:
                self.requests = self.requests[-self.max_requests:]

            # Update counters
            self.metrics["total_requests"] += 1
            self.metrics["total_response_time"] += request_info["response_time"]

            if not request_info["success"]:
                self.metrics["errors"] += 1

            if request_info["response_time"] > 1.0:  # Slow request threshold
                self.metrics["slow_requests"] += 1

            # Calculate averages
            if self.metrics["total_requests"] > 0:
                self.metrics["avg_response_time"] = (
                    self.metrics["total_response_time"] / self.metrics["total_requests"]
                )

            # Calculate requests per minute
            uptime_minutes = max(1, (datetime.now() - self.start_time).total_seconds() / 60)
            self.metrics["requests_per_minute"] = self.metrics["total_requests"] / uptime_minutes

            # Update system metrics periodically
            await self._update_system_metrics()

            # Clean up old requests periodically
            await self._cleanup_old_requests()

        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")

    async def _update_system_metrics(self) -> None:
        """Update system resource metrics"""
        try:
            # Update system metrics every 30 seconds
            now = datetime.now()
            if (now - self._last_system_update).total_seconds() < 30:
                return

            self._last_system_update = now

            # Get system metrics
            self.metrics["memory_usage"] = psutil.virtual_memory().percent
            self.metrics["cpu_usage"] = psutil.cpu_percent(interval=None)

        except Exception as e:
            logger.warning(f"Failed to update system metrics: {e}")

    async def _cleanup_old_requests(self) -> None:
        """Clean up old request data"""
        try:
            now = datetime.now()
            if (now - self.last_cleanup).total_seconds() < 300:  # Clean every 5 minutes
                return

            self.last_cleanup = now

            # Keep only requests from last hour
            cutoff_time = now - timedelta(hours=1)

            self.requests = [
                req for req in self.requests
                if datetime.fromisoformat(req["timestamp"]) > cutoff_time
            ]

            logger.info(f"Cleaned up old requests, keeping {len(self.requests)} recent requests")

        except Exception as e:
            logger.error(f"Failed to cleanup old requests: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        try:
            # Calculate additional metrics
            recent_requests = [
                req for req in self.requests
                if datetime.fromisoformat(req["timestamp"]) > datetime.now() - timedelta(minutes=5)
            ]

            recent_errors = sum(1 for req in recent_requests if not req["success"])
            recent_slow = sum(1 for req in recent_requests if req["response_time"] > 1.0)

            enhanced_metrics = self.metrics.copy()
            enhanced_metrics.update({
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                "recent_requests_5min": len(recent_requests),
                "recent_errors_5min": recent_errors,
                "recent_slow_requests_5min": recent_slow,
                "error_rate": (self.metrics["errors"] / max(1, self.metrics["total_requests"])) * 100,
                "slow_request_rate": (self.metrics["slow_requests"] / max(1, self.metrics["total_requests"])) * 100,
                "timestamp": datetime.now().isoformat()
            })

            return enhanced_metrics

        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def get_recent_requests(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent requests"""
        try:
            return self.requests[-limit:] if self.requests else []
        except Exception as e:
            logger.error(f"Failed to get recent requests: {e}")
            return []

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status"""
        try:
            metrics = self.get_metrics()

            # Determine health status
            health_score = 100
            status = "healthy"
            issues = []

            # Check error rate
            if metrics.get("error_rate", 0) > 5:
                health_score -= 20
                issues.append("High error rate")

            # Check response time
            if metrics.get("avg_response_time", 0) > 2:
                health_score -= 15
                issues.append("Slow response times")

            # Check memory usage
            if metrics.get("memory_usage", 0) > 90:
                health_score -= 25
                issues.append("High memory usage")

            # Check CPU usage
            if metrics.get("cpu_usage", 0) > 90:
                health_score -= 20
                issues.append("High CPU usage")

            # Determine overall status
            if health_score >= 80:
                status = "healthy"
            elif health_score >= 60:
                status = "degraded"
            else:
                status = "unhealthy"

            return {
                "status": status,
                "health_score": health_score,
                "issues": issues,
                "metrics": metrics,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get health status: {e}")
            return {
                "status": "unknown",
                "health_score": 0,
                "issues": [f"Health check error: {str(e)}"],
                "timestamp": datetime.now().isoformat()
            }

# Global access functions
def get_monitoring_middleware_instance() -> Optional[MonitoringMiddleware]:
    """Get the current monitoring middleware instance"""
    return _monitoring_middleware_instance

def set_monitoring_middleware_instance(instance: MonitoringMiddleware) -> None:
    """Set the monitoring middleware instance"""
    global _monitoring_middleware_instance
    _monitoring_middleware_instance = instance

def get_current_metrics() -> Dict[str, Any]:
    """Get current monitoring metrics"""
    instance = get_monitoring_middleware_instance()
    if instance:
        return instance.get_metrics()
    return {"error": "Monitoring middleware not initialized"}

def get_health_status() -> Dict[str, Any]:
    """Get current health status"""
    instance = get_monitoring_middleware_instance()
    if instance:
        return instance.get_health_status()
    return {"status": "unknown", "error": "Monitoring middleware not initialized"}

def get_recent_requests(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recent requests from the monitoring middleware

    Args:
        limit: Maximum number of requests to return

    Returns:
        List of recent request data
    """
    try:
        instance = get_monitoring_middleware_instance()
        if instance:
            recent = instance.get_recent_requests(limit)
            return [
                {
                    "request_id": req.get("id", "unknown"),
                    "method": req.get("method", "unknown"),
                    "path": req.get("path", "unknown"),
                    "timestamp": req.get("timestamp", "unknown"),
                    "response_time": req.get("response_time", 0),
                    "status_code": req.get("status_code", 0),
                    "ip_address": req.get("client_ip", "unknown")
                }
                for req in recent
            ]
        return []
    except Exception as e:
        logger.error(f"Error getting recent requests: {e}")
        return []

__all__ = [
    "MonitoringMiddleware",
    "get_monitoring_middleware_instance",
    "set_monitoring_middleware_instance",
    "get_current_metrics",
    "get_health_status",
    "get_recent_requests"
]
