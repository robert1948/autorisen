"""
AI Performance monitoring service for CapeControl API
Professional AI model performance tracking and optimization
"""

import logging
import time
import psutil
import threading
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)

class PerformanceMetric(Enum):
    """AI Performance metric types"""
    RESPONSE_TIME = "response_time"
    ACCURACY = "accuracy"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    MODEL_CONFIDENCE = "model_confidence"

class AIModelType(Enum):
    """AI Model types for tracking"""
    CAPE_AI = "cape_ai"
    CONTENT_MODERATION = "content_moderation"
    INPUT_VALIDATION = "input_validation"
    WEATHER_PREDICTION = "weather_prediction"
    STORM_TRACKING = "storm_tracking"

@dataclass
class PerformanceRecord:
    """Performance record data structure"""
    timestamp: datetime
    model_type: AIModelType
    metric_type: PerformanceMetric
    value: float
    metadata: Dict[str, Any]
    request_id: Optional[str] = None

class AIPerformanceMonitor:
    """Professional AI performance monitoring system"""
    
    def __init__(self):
        self.metrics = []
        self.active_requests = {}
        self.model_stats = {}
        self.is_monitoring = True
        self.start_time = datetime.utcnow()
        
        # Start background monitoring
        self._start_system_monitoring()
        
    def _start_system_monitoring(self):
        """Start background system monitoring"""
        def monitor_system():
            while self.is_monitoring:
                try:
                    # Monitor CPU usage
                    cpu_percent = psutil.cpu_percent(interval=1)
                    self.record_metric(
                        AIModelType.CAPE_AI,
                        PerformanceMetric.CPU_USAGE,
                        cpu_percent,
                        {"source": "system"}
                    )
                    
                    # Monitor memory usage
                    memory = psutil.virtual_memory()
                    self.record_metric(
                        AIModelType.CAPE_AI,
                        PerformanceMetric.MEMORY_USAGE,
                        memory.percent,
                        {"available_gb": memory.available / (1024**3)}
                    )
                    
                    time.sleep(30)  # Monitor every 30 seconds
                except Exception as e:
                    logger.error(f"System monitoring error: {e}")
                    time.sleep(60)  # Wait longer on error
                    
        # Start monitoring thread
        monitor_thread = threading.Thread(target=monitor_system, daemon=True)
        monitor_thread.start()
        
    def record_metric(
        self,
        model_type: AIModelType,
        metric_type: PerformanceMetric,
        value: float,
        metadata: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> str:
        """Record a performance metric"""
        try:
            record = PerformanceRecord(
                timestamp=datetime.utcnow(),
                model_type=model_type,
                metric_type=metric_type,
                value=value,
                metadata=metadata or {},
                request_id=request_id
            )
            
            self.metrics.append(record)
            
            # Update model stats
            model_key = model_type.value
            if model_key not in self.model_stats:
                self.model_stats[model_key] = {
                    "total_requests": 0,
                    "avg_response_time": 0.0,
                    "error_count": 0,
                    "last_updated": datetime.utcnow()
                }
            
            # Update stats based on metric type
            if metric_type == PerformanceMetric.RESPONSE_TIME:
                stats = self.model_stats[model_key]
                stats["total_requests"] += 1
                # Running average calculation
                current_avg = stats["avg_response_time"]
                total_requests = stats["total_requests"]
                stats["avg_response_time"] = ((current_avg * (total_requests - 1)) + value) / total_requests
                stats["last_updated"] = datetime.utcnow()
                
            elif metric_type == PerformanceMetric.ERROR_RATE:
                self.model_stats[model_key]["error_count"] += 1
                
            # Keep only last 1000 metrics to prevent memory issues
            if len(self.metrics) > 1000:
                self.metrics = self.metrics[-1000:]
                
            record_id = f"perf_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{id(record)}"
            
            logger.info(f"Performance metric recorded: {model_type.value} - {metric_type.value}: {value}")
            return record_id
            
        except Exception as e:
            logger.error(f"Failed to record performance metric: {e}")
            return "recording_failed"
    
    def start_request_timing(self, model_type: AIModelType, request_id: str) -> None:
        """Start timing a request"""
        self.active_requests[request_id] = {
            "model_type": model_type,
            "start_time": time.time(),
            "timestamp": datetime.utcnow()
        }
        
    def end_request_timing(self, request_id: str, metadata: Optional[Dict[str, Any]] = None) -> float:
        """End timing a request and record the metric"""
        if request_id not in self.active_requests:
            logger.warning(f"Request {request_id} not found in active requests")
            return 0.0
            
        request_data = self.active_requests.pop(request_id)
        response_time = time.time() - request_data["start_time"]
        
        self.record_metric(
            request_data["model_type"],
            PerformanceMetric.RESPONSE_TIME,
            response_time * 1000,  # Convert to milliseconds
            metadata,
            request_id
        )
        
        return response_time
    
    def get_model_stats(self, model_type: Optional[AIModelType] = None) -> Dict[str, Any]:
        """Get performance statistics for models"""
        if model_type:
            return self.model_stats.get(model_type.value, {})
        return self.model_stats.copy()
    
    def get_recent_metrics(
        self, 
        model_type: Optional[AIModelType] = None,
        metric_type: Optional[PerformanceMetric] = None,
        minutes: int = 60
    ) -> List[Dict[str, Any]]:
        """Get recent performance metrics"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        filtered_metrics = []
        for record in self.metrics:
            if record.timestamp < cutoff_time:
                continue
                
            if model_type and record.model_type != model_type:
                continue
                
            if metric_type and record.metric_type != metric_type:
                continue
                
            filtered_metrics.append({
                "timestamp": record.timestamp.isoformat(),
                "model_type": record.model_type.value,
                "metric_type": record.metric_type.value,
                "value": record.value,
                "metadata": record.metadata,
                "request_id": record.request_id
            })
            
        return filtered_metrics
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        return {
            "monitoring_started": self.start_time.isoformat(),
            "total_metrics": len(self.metrics),
            "active_requests": len(self.active_requests),
            "model_stats": self.model_stats,
            "is_monitoring": self.is_monitoring,
            "system_info": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent
            }
        }
    
    def stop_monitoring(self) -> None:
        """Stop the performance monitoring"""
        self.is_monitoring = False
        logger.info("AI Performance monitoring stopped")

# Global performance monitor instance
_global_performance_monitor = AIPerformanceMonitor()

def get_ai_performance_monitor() -> AIPerformanceMonitor:
    """
    Get the global AI performance monitor instance
    This is the main function that ai_performance.py imports
    """
    return _global_performance_monitor

def record_ai_metric(
    model_type: AIModelType,
    metric_type: PerformanceMetric,
    value: float,
    metadata: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> str:
    """Convenience function to record AI performance metric"""
    return get_ai_performance_monitor().record_metric(
        model_type, metric_type, value, metadata, request_id
    )

def time_ai_request(model_type: AIModelType):
    """Decorator to automatically time AI requests"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            request_id = f"req_{int(time.time() * 1000)}"
            monitor = get_ai_performance_monitor()
            
            monitor.start_request_timing(model_type, request_id)
            try:
                result = func(*args, **kwargs)
                monitor.end_request_timing(request_id, {"success": True})
                return result
            except Exception as e:
                monitor.end_request_timing(request_id, {"success": False, "error": str(e)})
                monitor.record_metric(
                    model_type,
                    PerformanceMetric.ERROR_RATE,
                    1.0,
                    {"error": str(e)},
                    request_id
                )
                raise
        return wrapper
    return decorator

def get_model_performance_stats(model_type: Optional[AIModelType] = None) -> Dict[str, Any]:
    """Convenience function to get model performance statistics"""
    return get_ai_performance_monitor().get_model_stats(model_type)

def get_recent_ai_metrics(
    model_type: Optional[AIModelType] = None,
    metric_type: Optional[PerformanceMetric] = None,
    minutes: int = 60
) -> List[Dict[str, Any]]:
    """Convenience function to get recent AI metrics"""
    return get_ai_performance_monitor().get_recent_metrics(model_type, metric_type, minutes)

# Export all required functions and classes
__all__ = [
    "get_ai_performance_monitor",
    "AIPerformanceMonitor",
    "PerformanceMetric",
    "AIModelType", 
    "PerformanceRecord",
    "record_ai_metric",
    "time_ai_request",
    "get_model_performance_stats",
    "get_recent_ai_metrics"
]