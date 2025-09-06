"""
AI Performance monitoring service for CapeControl API
Professional AI model performance tracking and optimization
"""

import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from app.utils.datetime import utc_now
from enum import Enum
from typing import Any, Optional

import psutil

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
    """AI Model types for tracking.

    NOTE: External provider identifiers (openai/claude/gemini) are intentionally
    NOT added here to keep this enum domain-specific. Multi-provider services
    should map external providers to an internal AIModelType (e.g. CAPE_AI) for
    performance aggregation. This avoids ValueError in tests attempting to cast
    provider strings directly.
    """

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
    metadata: dict[str, Any]
    request_id: str | None = None


class AIProvider(Enum):
    """Compatibility provider enum expected by legacy tests.

    These names are referenced in standalone / legacy tests. Values map to
    provider identifiers used elsewhere (multi_provider_ai_service).
    """

    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    LOCAL = "local"


@dataclass
class AIMetricRecord:
    """Legacy AI request metric structure expected by tests.

    Provides a unified representation for cost & performance tracking.
    """

    timestamp: datetime
    provider: AIProvider
    model: str
    endpoint: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    response_time_ms: int
    success: bool
    user_id: Optional[str] = None
    response_length: Optional[int] = None
    quality_score: Optional[float] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    estimated_cost: float = 0.0


class AIPerformanceMonitor:
    """Professional AI performance monitoring system with legacy compatibility layer.

    Existing test suites (e.g. test_ai_performance_standalone) rely on attributes:
      - metrics_history
      - cost_models
      - ai_configs
    and methods:
      - record_ai_request
      - calculate_cost
      - get_real_time_metrics
      - get_performance_stats

    This class now exposes those while preserving newer metric APIs already
    used elsewhere (metrics, record_metric, etc.).
    """

    def __init__(self):
        # Core in-memory data stores (newer system metrics)
        self.metrics = []  # List[PerformanceRecord]
        self.active_requests = {}
        self.model_stats = {}

        # Legacy compatibility stores
        self._legacy_metrics_history: list[AIMetricRecord] = []
        # Very small representative cost model (USD per 1K tokens)
        self.cost_models = {
            AIProvider.OPENAI: {
                "gpt-4": {"prompt": 0.03, "completion": 0.06},
                "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03},
                "gpt-3.5-turbo": {"prompt": 0.001, "completion": 0.002},
            },
            AIProvider.CLAUDE: {
                "claude-3-opus": {"prompt": 0.015, "completion": 0.075},
                "claude-3-sonnet": {"prompt": 0.003, "completion": 0.015},
                "claude-3-haiku": {"prompt": 0.0008, "completion": 0.004},
            },
            AIProvider.GEMINI: {
                "gemini-pro": {"prompt": 0.001, "completion": 0.002},
            },
            AIProvider.LOCAL: {
                "local-llm": {"prompt": 0.0, "completion": 0.0},
            },
        }
        # Simplified ai_configs: provider -> list of models
        self.ai_configs = {
            p.value: list(models.keys()) for p, models in self.cost_models.items()
        }

        # Control flags & timestamps
        self.is_monitoring = True
        self.start_time = utc_now()

        # Kick off background system monitoring thread
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
                        {"source": "system"},
                    )

                    # Monitor memory usage
                    memory = psutil.virtual_memory()
                    self.record_metric(
                        AIModelType.CAPE_AI,
                        PerformanceMetric.MEMORY_USAGE,
                        memory.percent,
                        {"available_gb": memory.available / (1024**3)},
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
        metadata: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> str:
        """Record a performance metric"""
        try:
            record = PerformanceRecord(
                timestamp=utc_now(),
                model_type=model_type,
                metric_type=metric_type,
                value=value,
                metadata=metadata or {},
                request_id=request_id,
            )

            self.metrics.append(record)

            # Update model stats
            model_key = model_type.value
            if model_key not in self.model_stats:
                self.model_stats[model_key] = {
                    "total_requests": 0,
                    "avg_response_time": 0.0,
                    "error_count": 0,
                    "last_updated": utc_now(),
                }

            # Update stats based on metric type
            if metric_type == PerformanceMetric.RESPONSE_TIME:
                stats = self.model_stats[model_key]
                stats["total_requests"] += 1
                # Running average calculation
                current_avg = stats["avg_response_time"]
                total_requests = stats["total_requests"]
                stats["avg_response_time"] = (
                    (current_avg * (total_requests - 1)) + value
                ) / total_requests
                stats["last_updated"] = utc_now()

            elif metric_type == PerformanceMetric.ERROR_RATE:
                self.model_stats[model_key]["error_count"] += 1

            # Keep only last 1000 metrics to prevent memory issues
            if len(self.metrics) > 1000:
                self.metrics = self.metrics[-1000:]

            record_id = f"perf_{utc_now().strftime('%Y%m%d_%H%M%S')}_{id(record)}"

            logger.info(
                f"Performance metric recorded: {model_type.value} - {metric_type.value}: {value}"
            )
            return record_id

        except Exception as e:
            logger.error(f"Failed to record performance metric: {e}")
            return "recording_failed"

    # ---------------- Legacy compatibility API ---------------- #
    def record_ai_request(
        self,
        provider: AIProvider,
        model: str,
        endpoint: str,
        prompt_tokens: int,
        completion_tokens: int,
        response_time_ms: int,
        success: bool,
        user_id: str | None = None,
        response_length: int | None = None,
        quality_score: float | None = None,
        error_type: str | None = None,
        error_message: str | None = None,
    ) -> str:
        """Record a legacy AI request metric (used in standalone tests)."""
        try:
            total_tokens = prompt_tokens + completion_tokens
            estimated_cost = self.calculate_cost(
                provider, model, prompt_tokens, completion_tokens
            )
            rec = AIMetricRecord(
                timestamp=utc_now(),
                provider=provider,
                model=model,
                endpoint=endpoint,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                response_time_ms=response_time_ms,
                success=success,
                user_id=user_id,
                response_length=response_length,
                quality_score=quality_score,
                error_type=error_type,
                error_message=error_message,
                estimated_cost=estimated_cost,
            )
            self._legacy_metrics_history.append(rec)
            # Keep bounded
            if len(self._legacy_metrics_history) > 2000:
                self._legacy_metrics_history = self._legacy_metrics_history[-2000:]
            rec_id = f"ai_req_{utc_now().strftime('%Y%m%d_%H%M%S')}_{len(self._legacy_metrics_history)}"
            return rec_id
        except Exception as e:
            logger.error(f"Failed to record AI request: {e}")
            return "ai_record_failed"

    def calculate_cost(
        self,
        provider: AIProvider,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> float:
        """Estimate cost for a request using provider cost table."""
        provider_models = self.cost_models.get(provider, {})
        rates = provider_models.get(model)
        if not rates:
            return 0.0
        return (prompt_tokens * rates["prompt"]) / 1000.0 + (
            completion_tokens * rates["completion"]
        ) / 1000.0

    def get_real_time_metrics(self) -> dict[str, Any]:
        """Aggregate metrics for the last 5 minutes (approx)."""
        cutoff = utc_now() - timedelta(minutes=5)
        recent = [m for m in self._legacy_metrics_history if m.timestamp >= cutoff]
        total = len(recent)
        successes = sum(1 for m in recent if m.success)
        failures = total - successes
        avg_response = (
            int(sum(m.response_time_ms for m in recent) / total) if total else 0
        )
        total_cost = sum(m.estimated_cost for m in recent)
        return {
            "metrics_5m": {
                "total_requests": total,
                "successful_requests": successes,
                "failed_requests": failures,
                "avg_response_time": avg_response,
                "total_cost": total_cost,
            }
        }

    def get_performance_stats(self, time_period: str = "1h") -> dict[str, Any]:
        """Return simple stats grouped by provider+model for recent window."""
        mapping = {"5m": 5, "1h": 60, "24h": 24 * 60}
        minutes = mapping.get(time_period, 60)
        cutoff = utc_now() - timedelta(minutes=minutes)
        window = [m for m in self._legacy_metrics_history if m.timestamp >= cutoff]
        from types import SimpleNamespace

        stats: dict[str, SimpleNamespace] = {}
        for m in window:
            key = f"{m.provider.value}:{m.model}"
            d = stats.get(key)
            if not d:
                d = SimpleNamespace(
                    provider=m.provider.value,
                    model=m.model,
                    requests=0,
                    total_requests=0,  # alias for legacy tests
                    success=0,
                    failures=0,
                    success_rate=0.0,
                    avg_response_time=0.0,
                    total_prompt_tokens=0,
                    total_completion_tokens=0,
                    total_cost=0.0,
                )
                stats[key] = d
            d.requests += 1
            d.total_requests = d.requests
            if m.success:
                d.success += 1
            else:
                d.failures += 1
            r = d.requests
            d.avg_response_time = (
                (d.avg_response_time * (r - 1)) + m.response_time_ms
            ) / r
            d.total_prompt_tokens += m.prompt_tokens
            d.total_completion_tokens += m.completion_tokens
            d.total_cost += m.estimated_cost
        # finalize success rates
        for d in stats.values():
            if d.requests:
                d.success_rate = (d.success / d.requests) * 100.0
            else:
                d.success_rate = 0.0
        return stats

    def get_cost_analytics(self, time_period: str = "1h") -> dict[str, Any]:
        """Aggregate cost analytics for window (used by tests)."""
        mapping = {"5m": 5, "1h": 60, "24h": 24 * 60}
        minutes = mapping.get(time_period, 60)
        cutoff = utc_now() - timedelta(minutes=minutes)
        window = [m for m in self._legacy_metrics_history if m.timestamp >= cutoff]
        total_cost = 0.0
        cost_by_provider: dict[str, float] = {}
        cost_by_model: dict[str, float] = {}
        for m in window:
            total_cost += m.estimated_cost
            cost_by_provider[m.provider.value] = (
                cost_by_provider.get(m.provider.value, 0.0) + m.estimated_cost
            )
            model_key = f"{m.provider.value}:{m.model}"
            cost_by_model[model_key] = (
                cost_by_model.get(model_key, 0.0) + m.estimated_cost
            )
        return {
            "total_cost": total_cost,
            "cost_by_provider": cost_by_provider,
            "cost_by_model": cost_by_model,
            "total_requests": len(window),
        }

    def get_health_status(self) -> dict[str, Any]:
        """Compute simple service health metrics based on last hour."""
        cutoff = utc_now() - timedelta(minutes=60)
        window = [m for m in self._legacy_metrics_history if m.timestamp >= cutoff]
        if not window:
            return {"status": "no_data", "message": "No metrics recorded"}
        total = len(window)
        successes = sum(1 for m in window if m.success)
        failures = total - successes
        success_rate = (successes / total) * 100.0 if total else 0.0
        error_rate = (failures / total) * 100.0 if total else 0.0
        avg_response = sum(m.response_time_ms for m in window) / total if total else 0.0
        status = "healthy"
        if success_rate < 85 or avg_response > 4000 or error_rate > 15:
            status = "critical"
        elif success_rate < 95 or avg_response > 2000 or error_rate > 5:
            status = "warning"
        return {
            "status": status,
            "overall_success_rate": success_rate,
            "error_rate": error_rate,
            "avg_response_time_ms": avg_response,
            "total_requests": total,
        }

    def get_optimization_recommendations(self) -> list[dict[str, Any]]:
        """Provide basic optimization recommendations based on last 24h metrics."""
        from statistics import mean

        cutoff = utc_now() - timedelta(hours=24)
        window = [m for m in self._legacy_metrics_history if m.timestamp >= cutoff]
        if not window:
            return []
        grouped: dict[str, list[AIMetricRecord]] = {}
        for m in window:
            key = f"{m.provider.value}:{m.model}"
            grouped.setdefault(key, []).append(m)
        recs: list[dict[str, Any]] = []
        for key, records in grouped.items():
            successes = sum(1 for r in records if r.success)
            failures = len(records) - successes
            avg_latency = mean(r.response_time_ms for r in records)
            total_cost = sum(r.estimated_cost for r in records)
            failure_rate = (failures / len(records)) * 100.0 if records else 0.0
            if avg_latency > 1500:
                recs.append(
                    {
                        "issue": "high_latency",
                        "model": key,
                        "avg_response_time_ms": avg_latency,
                        "priority": "high" if avg_latency < 3000 else "critical",
                        "recommendation": "Investigate bottlenecks or try faster model variant",
                    }
                )
            if failure_rate > 20:
                recs.append(
                    {
                        "issue": "high_failure_rate",
                        "model": key,
                        "failure_rate": failure_rate,
                        "priority": "critical" if failure_rate > 40 else "high",
                        "recommendation": "Add retries/backoff and inspect error logs",
                    }
                )
            if total_cost > 1.0:
                recs.append(
                    {
                        "issue": "high_cost_usage",
                        "model": key,
                        "total_cost": total_cost,
                        "priority": "high" if total_cost < 5 else "critical",
                        "recommendation": "Optimize prompts, cache responses, or downgrade model",
                    }
                )
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        recs.sort(key=lambda r: priority_order.get(r.get("priority", "low"), 4))
        return recs

    @property
    def metrics_history(self) -> list[AIMetricRecord]:  # Needed by legacy tests
        return self._legacy_metrics_history

    def start_request_timing(self, model_type: AIModelType, request_id: str) -> None:
        """Start timing a request"""
        self.active_requests[request_id] = {
            "model_type": model_type,
            "start_time": time.time(),
            "timestamp": utc_now(),
        }

    def end_request_timing(
        self, request_id: str, metadata: dict[str, Any] | None = None
    ) -> float:
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
            request_id,
        )

        return response_time

    def get_model_stats(self, model_type: AIModelType | None = None) -> dict[str, Any]:
        """Get performance statistics for models"""
        if model_type:
            return self.model_stats.get(model_type.value, {})
        return self.model_stats.copy()

    def get_recent_metrics(
        self,
        model_type: AIModelType | None = None,
        metric_type: PerformanceMetric | None = None,
        minutes: int = 60,
    ) -> list[dict[str, Any]]:
        """Get recent performance metrics"""
        cutoff_time = utc_now() - timedelta(minutes=minutes)

        filtered_metrics = []
        for record in self.metrics:
            if record.timestamp < cutoff_time:
                continue

            if model_type and record.model_type != model_type:
                continue

            if metric_type and record.metric_type != metric_type:
                continue

            filtered_metrics.append(
                {
                    "timestamp": record.timestamp.isoformat(),
                    "model_type": record.model_type.value,
                    "metric_type": record.metric_type.value,
                    "value": record.value,
                    "metadata": record.metadata,
                    "request_id": record.request_id,
                }
            )

        return filtered_metrics

    def get_performance_summary(self) -> dict[str, Any]:
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
                "disk_usage": psutil.disk_usage("/").percent,
            },
        }

    # (Duplicate record_ai_request removed; legacy implementation retained earlier.)

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
    metadata: dict[str, Any] | None = None,
    request_id: str | None = None,
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
                monitor.end_request_timing(
                    request_id, {"success": False, "error": str(e)}
                )
                monitor.record_metric(
                    model_type,
                    PerformanceMetric.ERROR_RATE,
                    1.0,
                    {"error": str(e)},
                    request_id,
                )
                raise

        return wrapper

    return decorator


def get_model_performance_stats(
    model_type: AIModelType | None = None,
) -> dict[str, Any]:
    """Convenience function to get model performance statistics"""
    return get_ai_performance_monitor().get_model_stats(model_type)


def get_recent_ai_metrics(
    model_type: AIModelType | None = None,
    metric_type: PerformanceMetric | None = None,
    minutes: int = 60,
) -> list[dict[str, Any]]:
    """Convenience function to get recent AI metrics"""
    return get_ai_performance_monitor().get_recent_metrics(
        model_type, metric_type, minutes
    )


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
    "get_recent_ai_metrics",
]
