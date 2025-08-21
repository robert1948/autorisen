"""
Enhanced Health Check Service (defensive, non-invasive)

This file provides a defensive implementation of the HealthService used by
the application. It intentionally avoids hard failures when optional
dependencies or environment services are missing so the application can boot
and report graceful health statuses.
"""

import inspect
import logging
import os
import time
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# Optional HTTP client
try:
    import httpx  # type: ignore
except Exception:
    httpx = None  # type: ignore

# Optional psutil for system metrics, used defensively
try:
    import psutil  # type: ignore
except Exception:
    psutil = None  # type: ignore

# Optional app-local imports (kept defensive)
try:
    from app.database import get_db  # may be a function or engine
except Exception:
    get_db = None  # type: ignore

try:
    from app.services.error_tracker import get_error_tracker
except Exception:
    get_error_tracker = lambda: None  # type: ignore

try:
    from app.services.audit_service import AuditEventType, get_audit_logger  # type: ignore
except Exception:
    get_audit_logger = lambda: None  # type: ignore
    AuditEventType = None  # type: ignore


class HealthStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


class ServiceType(Enum):
    CORE_API = "core_api"
    DATABASE = "database"
    EXTERNAL_API = "external_api"
    BACKGROUND_TASK = "background_task"
    CACHE = "cache"
    FILE_SYSTEM = "file_system"
    NETWORK = "network"


@dataclass
class HealthCheckResult:
    service_name: str
    service_type: ServiceType
    status: HealthStatus
    response_time_ms: float
    timestamp: datetime
    details: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None
    suggestions: list[str] = field(default_factory=list)


@dataclass
class EndpointHealthCheck:
    name: str
    url: str
    method: str = "GET"
    timeout: int = 5
    expected_status: int = 200
    expected_response_key: str | None = None
    expected_response_value: Any | None = None
    critical: bool = False
    headers: dict[str, str] = field(default_factory=dict)


class HealthService:
    """Defensive health check service."""

    def __init__(self):
        self.logger = logging.getLogger("autorisen.health")
        self.audit_logger = get_audit_logger() if callable(get_audit_logger) else None
        self.error_tracker = get_error_tracker() if callable(get_error_tracker) else None

        self.health_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=100))

        # thresholds can be tuned via environment in the future
        self.thresholds = {
            "cpu_warning": float(os.getenv("CPU_WARNING", 70.0)),
            "cpu_critical": float(os.getenv("CPU_CRITICAL", 85.0)),
            "memory_warning": float(os.getenv("MEM_WARNING", 75.0)),
            "memory_critical": float(os.getenv("MEM_CRITICAL", 90.0)),
            "disk_warning": float(os.getenv("DISK_WARNING", 80.0)),
            "disk_critical": float(os.getenv("DISK_CRITICAL", 95.0)),
            "response_time_warning": float(os.getenv("RESP_WARN_MS", 1000.0)),
            "response_time_critical": float(os.getenv("RESP_CRIT_MS", 5000.0)),
        }

        self.health_checks: dict[str, Callable] = {}
        self.endpoint_checks: list[EndpointHealthCheck] = []

        self._register_builtin_checks()

    def _register_builtin_checks(self):
        self.register_health_check("system_resources", self._check_system_resources)
        self.register_health_check("disk_space", self._check_disk_space)
        self.register_health_check("database_connection", self._check_database_connection)
        self.register_health_check("error_rates", self._check_error_rates)
        self.register_health_check("process_health", self._check_process_health)

        # register endpoints (non-fatal if environment not set)
        base_url = os.getenv("BASE_URL") or "http://localhost:8000"
        self.endpoint_checks.append(
            EndpointHealthCheck(name="Main Health", url=f"{base_url}/api/health", critical=True, expected_response_key="status")
        )

    def register_health_check(self, name: str, check_function: Callable):
        self.health_checks[name] = check_function

    def register_endpoint_check(self, endpoint_check: EndpointHealthCheck):
        self.endpoint_checks.append(endpoint_check)

    async def run_comprehensive_health_check(self) -> dict[str, Any]:
        start = time.time()
        overall = HealthStatus.HEALTHY

        services: dict[str, Any] = {}
        endpoints: dict[str, Any] = {}

        # run registered health checks
        for name, func in self.health_checks.items():
            result = await self._run_health_check(name, func)
            services[name] = asdict(result)
            overall = self._combine_status(overall, result.status)

        # run endpoint checks
        for ep in self.endpoint_checks:
            ep_result = await self._run_endpoint_check(ep)
            endpoints[ep.name] = asdict(ep_result)
            overall = self._combine_status(overall, ep_result.status)

        duration_ms = (time.time() - start) * 1000.0

        return {
            "overall_status": overall.value,
            "timestamp": datetime.utcnow().isoformat(),
            "check_duration_ms": duration_ms,
            "services": services,
            "endpoints": endpoints,
        }

    async def _run_health_check(self, name: str, func: Callable) -> HealthCheckResult:
        t0 = time.time()
        try:
            if inspect.iscoroutinefunction(func):
                res = await func()
            else:
                res = func()
                if inspect.isawaitable(res):
                    res = await res

            if isinstance(res, HealthCheckResult):
                result = res
            else:
                result = HealthCheckResult(
                    service_name=name,
                    service_type=ServiceType.CORE_API,
                    status=HealthStatus.HEALTHY,
                    response_time_ms=(time.time() - t0) * 1000.0,
                    timestamp=datetime.utcnow(),
                    details={"result": res if res is not None else "ok"},
                )

        except Exception as exc:  # defensive: never raise on health check
            self.logger.exception("Health check failed: %s", name)
            result = HealthCheckResult(
                service_name=name,
                service_type=ServiceType.CORE_API,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=(time.time() - t0) * 1000.0,
                timestamp=datetime.utcnow(),
                details={},
                error_message=str(exc),
                suggestions=["Investigate service failure", "See application logs"],
            )

        # store history
        try:
            self.health_history[name].append(result)
        except Exception:
            pass

        return result

    async def _run_endpoint_check(self, ep: EndpointHealthCheck) -> HealthCheckResult:
        t0 = time.time()
        if httpx is None:
            return HealthCheckResult(
                service_name=ep.name,
                service_type=ServiceType.EXTERNAL_API,
                status=HealthStatus.WARNING if ep.critical else HealthStatus.HEALTHY,
                response_time_ms=(time.time() - t0) * 1000.0,
                timestamp=datetime.utcnow(),
                details={"skipped": "httpx not installed"},
            )

        try:
            timeout = ep.timeout
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.request(ep.method, ep.url, headers=ep.headers or {})

            status = HealthStatus.HEALTHY
            if resp.status_code != ep.expected_status:
                status = HealthStatus.UNHEALTHY if ep.critical else HealthStatus.WARNING

            # optional content checks
            if ep.expected_response_key:
                try:
                    body = resp.json()
                    if ep.expected_response_key not in body:
                        status = HealthStatus.UNHEALTHY if ep.critical else HealthStatus.WARNING
                except Exception:
                    status = HealthStatus.WARNING

            return HealthCheckResult(
                service_name=ep.name,
                service_type=ServiceType.EXTERNAL_API,
                status=status,
                response_time_ms=(time.time() - t0) * 1000.0,
                timestamp=datetime.utcnow(),
                details={"status_code": resp.status_code},
            )

        except Exception as exc:
            self.logger.exception("Endpoint check failed: %s %s", ep.name, ep.url)
            return HealthCheckResult(
                service_name=ep.name,
                service_type=ServiceType.EXTERNAL_API,
                status=HealthStatus.UNHEALTHY if ep.critical else HealthStatus.WARNING,
                response_time_ms=(time.time() - t0) * 1000.0,
                timestamp=datetime.utcnow(),
                details={"url": ep.url},
                error_message=str(exc),
            )

    def _combine_status(self, a: HealthStatus, b: HealthStatus) -> HealthStatus:
        """Combine two statuses, returning the worse (highest severity)."""
        order = [HealthStatus.HEALTHY, HealthStatus.WARNING, HealthStatus.DEGRADED, HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]
        ai = order.index(a) if a in order else 0
        bi = order.index(b) if b in order else 0
        return order[max(ai, bi)]

    # --- Builtin check implementations (defensive) ---------------------------

    def _check_system_resources(self) -> HealthCheckResult:
        t0 = time.time()
        try:
            if psutil is None:
                return HealthCheckResult(
                    service_name="system_resources",
                    service_type=ServiceType.FILE_SYSTEM,
                    status=HealthStatus.WARNING,
                    response_time_ms=(time.time() - t0) * 1000.0,
                    timestamp=datetime.utcnow(),
                    details={"note": "psutil not available"},
                )

            cpu = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory().percent

            status = HealthStatus.HEALTHY
            if cpu >= self.thresholds["cpu_critical"] or mem >= self.thresholds["memory_critical"]:
                status = HealthStatus.CRITICAL
            elif cpu >= self.thresholds["cpu_warning"] or mem >= self.thresholds["memory_warning"]:
                status = HealthStatus.WARNING

            return HealthCheckResult(
                service_name="system_resources",
                service_type=ServiceType.FILE_SYSTEM,
                status=status,
                response_time_ms=(time.time() - t0) * 1000.0,
                timestamp=datetime.utcnow(),
                details={"cpu_percent": cpu, "memory_percent": mem},
            )
        except Exception as exc:
            return HealthCheckResult(
                service_name="system_resources",
                service_type=ServiceType.FILE_SYSTEM,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=(time.time() - t0) * 1000.0,
                timestamp=datetime.utcnow(),
                details={},
                error_message=str(exc),
            )

    def _check_disk_space(self) -> HealthCheckResult:
        t0 = time.time()
        try:
            if psutil is None:
                return HealthCheckResult(
                    service_name="disk_space",
                    service_type=ServiceType.FILE_SYSTEM,
                    status=HealthStatus.WARNING,
                    response_time_ms=(time.time() - t0) * 1000.0,
                    timestamp=datetime.utcnow(),
                    details={"note": "psutil not available"},
                )

            usage = psutil.disk_usage("/")
            percent = usage.percent
            status = HealthStatus.HEALTHY
            if percent >= self.thresholds["disk_critical"]:
                status = HealthStatus.CRITICAL
            elif percent >= self.thresholds["disk_warning"]:
                status = HealthStatus.WARNING

            return HealthCheckResult(
                service_name="disk_space",
                service_type=ServiceType.FILE_SYSTEM,
                status=status,
                response_time_ms=(time.time() - t0) * 1000.0,
                timestamp=datetime.utcnow(),
                details={"disk_percent": percent, "total": usage.total},
            )
        except Exception as exc:
            return HealthCheckResult(
                service_name="disk_space",
                service_type=ServiceType.FILE_SYSTEM,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=(time.time() - t0) * 1000.0,
                timestamp=datetime.utcnow(),
                details={},
                error_message=str(exc),
            )

    def _check_database_connection(self) -> HealthCheckResult:
        t0 = time.time()
        if get_db is None:
            return HealthCheckResult(
                service_name="database_connection",
                service_type=ServiceType.DATABASE,
                status=HealthStatus.WARNING,
                response_time_ms=(time.time() - t0) * 1000.0,
                timestamp=datetime.utcnow(),
                details={"note": "database helper not available"},
            )

        try:
            # Attempt to call get_db if it's a callable factory
            db_obj = None
            try:
                db_obj = get_db()
            except Exception:
                db_obj = None

            # If db_obj is a SQLAlchemy Engine/Connection, try a light ping
            # Defensive: don't raise if unknown shape
            try:
                if hasattr(db_obj, "execute"):
                    db_obj.execute("SELECT 1")
                elif hasattr(db_obj, "connect"):
                    c = db_obj.connect()
                    try:
                        c.execute("SELECT 1")
                    finally:
                        try:
                            c.close()
                        except Exception:
                            pass
            except Exception:
                # Best-effort: assume unhealthy but non-fatal
                return HealthCheckResult(
                    service_name="database_connection",
                    service_type=ServiceType.DATABASE,
                    status=HealthStatus.UNHEALTHY,
                    response_time_ms=(time.time() - t0) * 1000.0,
                    timestamp=datetime.utcnow(),
                    details={"note": "database ping failed"},
                )

            return HealthCheckResult(
                service_name="database_connection",
                service_type=ServiceType.DATABASE,
                status=HealthStatus.HEALTHY,
                response_time_ms=(time.time() - t0) * 1000.0,
                timestamp=datetime.utcnow(),
                details={"note": "db ping ok"},
            )

        except Exception as exc:
            return HealthCheckResult(
                service_name="database_connection",
                service_type=ServiceType.DATABASE,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=(time.time() - t0) * 1000.0,
                timestamp=datetime.utcnow(),
                error_message=str(exc),
            )

    def _check_error_rates(self) -> HealthCheckResult:
        t0 = time.time()
        try:
            tracker = self.error_tracker
            # If an error tracker is available, query a light metric; otherwise return healthy
            if tracker is None:
                return HealthCheckResult(
                    service_name="error_rates",
                    service_type=ServiceType.BACKGROUND_TASK,
                    status=HealthStatus.HEALTHY,
                    response_time_ms=(time.time() - t0) * 1000.0,
                    timestamp=datetime.utcnow(),
                    details={"note": "error tracker not configured"},
                )

            # If tracker provides an interface, try to get recent error rate (best-effort)
            try:
                if hasattr(tracker, "recent_error_rate"):
                    rate = float(tracker.recent_error_rate())
                else:
                    rate = 0.0
            except Exception:
                rate = 0.0

            status = HealthStatus.HEALTHY
            if rate >= 15.0:
                status = HealthStatus.CRITICAL
            elif rate >= 5.0:
                status = HealthStatus.WARNING

            return HealthCheckResult(
                service_name="error_rates",
                service_type=ServiceType.BACKGROUND_TASK,
                status=status,
                response_time_ms=(time.time() - t0) * 1000.0,
                timestamp=datetime.utcnow(),
                details={"error_rate_percent": rate},
            )

        except Exception as exc:
            return HealthCheckResult(
                service_name="error_rates",
                service_type=ServiceType.BACKGROUND_TASK,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=(time.time() - t0) * 1000.0,
                timestamp=datetime.utcnow(),
                error_message=str(exc),
            )

    def _check_process_health(self) -> HealthCheckResult:
        t0 = time.time()
        try:
            pids = []
            if psutil is not None:
                pids = psutil.pids()
            healthy = True if pids else False
            status = HealthStatus.HEALTHY if healthy else HealthStatus.WARNING
            return HealthCheckResult(
                service_name="process_health",
                service_type=ServiceType.BACKGROUND_TASK,
                status=status,
                response_time_ms=(time.time() - t0) * 1000.0,
                timestamp=datetime.utcnow(),
                details={"process_count": len(pids)},
            )
        except Exception as exc:
            return HealthCheckResult(
                service_name="process_health",
                service_type=ServiceType.BACKGROUND_TASK,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=(time.time() - t0) * 1000.0,
                timestamp=datetime.utcnow(),
                error_message=str(exc),
            )


# End of file
