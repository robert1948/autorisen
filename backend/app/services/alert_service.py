"""
Alert Systems Service for Task 1.3.6 - Automated Notifications
================================================================

Comprehensive alert system providing:
- Real-time alert generation and management
- Multi-channel notification delivery (email, webhook, log)
- Configurable alert rules and thresholds
- Alert escalation and grouping
- Integration with monitoring, error tracking, and health checks
- Alert history and analytics
- Automated incident response
"""

import asyncio
import json
import logging
import os
import smtplib
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import Any

# ---- Optional dependency: aiohttp (defensive import) ------------------------
try:
    import aiohttp  # type: ignore
except ModuleNotFoundError:
    aiohttp = None  # type: ignore

from app.database import get_db
from app.services.audit_service import AuditEventType, get_audit_logger
from app.services.error_tracker import ErrorCategory, ErrorSeverity, get_error_tracker  # noqa: F401

# NOTE: Do NOT import get_health_service at module load to avoid circular import.
# from app.services.health_service import get_health_service, HealthStatus


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertChannel(Enum):
    """Alert delivery channels"""
    EMAIL = "email"
    WEBHOOK = "webhook"
    LOG = "log"
    SMS = "sms"
    SLACK = "slack"
    DISCORD = "discord"


class AlertType(Enum):
    """Types of alerts"""
    SYSTEM_HEALTH = "system_health"
    ERROR_RATE = "error_rate"
    PERFORMANCE = "performance"
    SECURITY = "security"
    CAPACITY = "capacity"
    ENDPOINT_DOWN = "endpoint_down"
    DATABASE = "database"
    CUSTOM = "custom"


class AlertStatus(Enum):
    """Alert lifecycle status"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    SUPPRESSED = "suppressed"
    ESCALATED = "escalated"


@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    alert_type: AlertType
    severity: AlertSeverity
    condition: str  # JSON-ish condition or DSL fragment
    threshold: float
    duration: int  # seconds
    channels: list[AlertChannel]
    enabled: bool = True
    cooldown: int = 300  # 5 minutes cooldown between alerts
    escalation_time: int = 1800  # 30 minutes to escalate
    tags: list[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class Alert:
    """Alert instance"""
    id: str
    rule_name: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    description: str
    timestamp: datetime
    status: AlertStatus = AlertStatus.ACTIVE
    source_data: dict[str, Any] = None
    tags: list[str] = None
    acknowledged_by: str | None = None
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None
    escalated_at: datetime | None = None

    def __post_init__(self):
        if self.source_data is None:
            self.source_data = {}
        if self.tags is None:
            self.tags = []


@dataclass
class NotificationChannel:
    """Notification channel configuration"""
    name: str
    channel_type: AlertChannel
    config: dict[str, Any]
    enabled: bool = True
    rate_limit: int = 60  # seconds between notifications


class AlertSystem:
    """Comprehensive alert management system"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.audit_logger = get_audit_logger()
        self.error_tracker = get_error_tracker()
        self._health_service = None  # lazy-loaded to avoid circular import

        # Alert storage and management
        self.active_alerts: dict[str, Alert] = {}
        self.alert_history = deque(maxlen=1000)
        self.alert_rules: dict[str, AlertRule] = {}
        self.notification_channels: dict[str, NotificationChannel] = {}

        # Rate limiting and cooldowns
        self.last_alert_times: dict[str, datetime] = {}
        self.alert_counts = defaultdict(int)

        # Background tasks
        self.monitoring_task = None
        self.escalation_task = None

        # Initialize defaults
        self._initialize_default_rules()
        self._initialize_default_channels()

        # Start background monitoring
        self._start_background_monitoring()

    # ---------- Lazy import helpers (break circular imports) ----------

    def _get_health_service(self):
        """Import and cache the health service on first use (avoids circular import)."""
        if self._health_service is None:
            from app.services.health_service import get_health_service  # lazy import
            self._health_service = get_health_service()
        return self._health_service

    # ---------- Setup: rules & channels ----------

    def _initialize_default_rules(self):
        """Initialize default alert rules"""
        default_rules = [
            AlertRule(
                name="high_error_rate",
                alert_type=AlertType.ERROR_RATE,
                severity=AlertSeverity.ERROR,
                condition="error_rate > threshold",
                threshold=10.0,  # 10% error rate
                duration=300,  # 5 minutes
                channels=[AlertChannel.LOG, AlertChannel.EMAIL],
                tags=["production", "errors"]
            ),
            AlertRule(
                name="critical_error_rate",
                alert_type=AlertType.ERROR_RATE,
                severity=AlertSeverity.CRITICAL,
                condition="error_rate > threshold",
                threshold=25.0,  # 25% error rate
                duration=120,  # 2 minutes
                channels=[AlertChannel.LOG, AlertChannel.EMAIL, AlertChannel.WEBHOOK],
                escalation_time=600,  # 10 minutes
                tags=["production", "critical"]
            ),
            AlertRule(
                name="system_health_degraded",
                alert_type=AlertType.SYSTEM_HEALTH,
                severity=AlertSeverity.WARNING,
                condition="health_status != healthy",
                threshold=0,
                duration=180,  # 3 minutes
                channels=[AlertChannel.LOG, AlertChannel.EMAIL],
                tags=["infrastructure", "health"]
            ),
            AlertRule(
                name="system_health_critical",
                alert_type=AlertType.SYSTEM_HEALTH,
                severity=AlertSeverity.CRITICAL,
                condition="health_status == critical",
                threshold=0,
                duration=60,  # 1 minute
                channels=[AlertChannel.LOG, AlertChannel.EMAIL, AlertChannel.WEBHOOK],
                escalation_time=300,  # 5 minutes
                tags=["infrastructure", "critical"]
            ),
            AlertRule(
                name="high_cpu_usage",
                alert_type=AlertType.PERFORMANCE,
                severity=AlertSeverity.WARNING,
                condition="cpu_percent > threshold",
                threshold=80.0,
                duration=600,  # 10 minutes
                channels=[AlertChannel.LOG, AlertChannel.EMAIL],
                tags=["performance", "cpu"]
            ),
            AlertRule(
                name="critical_cpu_usage",
                alert_type=AlertType.PERFORMANCE,
                severity=AlertSeverity.CRITICAL,
                condition="cpu_percent > threshold",
                threshold=95.0,
                duration=300,  # 5 minutes
                channels=[AlertChannel.LOG, AlertChannel.EMAIL, AlertChannel.WEBHOOK],
                tags=["performance", "critical"]
            ),
            AlertRule(
                name="high_memory_usage",
                alert_type=AlertType.PERFORMANCE,
                severity=AlertSeverity.WARNING,
                condition="memory_percent > threshold",
                threshold=85.0,
                duration=600,  # 10 minutes
                channels=[AlertChannel.LOG, AlertChannel.EMAIL],
                tags=["performance", "memory"]
            ),
            AlertRule(
                name="critical_memory_usage",
                alert_type=AlertType.PERFORMANCE,
                severity=AlertSeverity.CRITICAL,
                condition="memory_percent > threshold",
                threshold=95.0,
                duration=300,  # 5 minutes
                channels=[AlertChannel.LOG, AlertChannel.EMAIL, AlertChannel.WEBHOOK],
                tags=["performance", "critical"]
            ),
            AlertRule(
                name="disk_space_warning",
                alert_type=AlertType.CAPACITY,
                severity=AlertSeverity.WARNING,
                condition="disk_percent > threshold",
                threshold=80.0,
                duration=600,  # 10 minutes
                channels=[AlertChannel.LOG, AlertChannel.EMAIL],
                tags=["capacity", "disk"]
            ),
            AlertRule(
                name="disk_space_critical",
                alert_type=AlertType.CAPACITY,
                severity=AlertSeverity.CRITICAL,
                condition="disk_percent > threshold",
                threshold=95.0,
                duration=300,  # 5 minutes
                channels=[AlertChannel.LOG, AlertChannel.EMAIL, AlertChannel.WEBHOOK],
                tags=["capacity", "critical"]
            ),
            AlertRule(
                name="database_connection_failure",
                alert_type=AlertType.DATABASE,
                severity=AlertSeverity.CRITICAL,
                condition="database_connected == false",
                threshold=0,
                duration=60,  # 1 minute
                channels=[AlertChannel.LOG, AlertChannel.EMAIL, AlertChannel.WEBHOOK],
                escalation_time=300,  # 5 minutes
                tags=["database", "critical"]
            ),
            AlertRule(
                name="security_threat_detected",
                alert_type=AlertType.SECURITY,
                severity=AlertSeverity.ERROR,
                condition="security_events > threshold",
                threshold=10.0,  # 10 security events in timeframe
                duration=300,  # 5 minutes
                channels=[AlertChannel.LOG, AlertChannel.EMAIL, AlertChannel.WEBHOOK],
                tags=["security", "threats"]
            )
        ]

        for rule in default_rules:
            self.alert_rules[rule.name] = rule

        self.logger.info(f"Initialized {len(default_rules)} default alert rules")

    def _initialize_default_channels(self):
        """Initialize default notification channels"""
        # Log channel (always available)
        self.notification_channels["log"] = NotificationChannel(
            name="log",
            channel_type=AlertChannel.LOG,
            config={},
            enabled=True
        )

        # Email channel
        email_config = {
            "smtp_server": os.getenv("SMTP_SERVER", "localhost"),
            "smtp_port": int(os.getenv("SMTP_PORT", "587")),
            "smtp_username": os.getenv("SMTP_USERNAME", ""),
            "smtp_password": os.getenv("SMTP_PASSWORD", ""),
            "from_email": os.getenv("ALERT_FROM_EMAIL", "alerts@localstorm.com"),
            "to_emails": os.getenv("ALERT_TO_EMAILS", "admin@localstorm.com").split(","),
        }

        self.notification_channels["email"] = NotificationChannel(
            name="email",
            channel_type=AlertChannel.EMAIL,
            config=email_config,
            enabled=bool(email_config["smtp_username"])  # Enable only if SMTP configured
        )

        # Webhook channel
        webhook_config = {
            "url": os.getenv("ALERT_WEBHOOK_URL", ""),
            "headers": {
                "Content-Type": "application/json",
                "Authorization": os.getenv("ALERT_WEBHOOK_TOKEN", "")
            },
            "timeout": 30
        }

        self.notification_channels["webhook"] = NotificationChannel(
            name="webhook",
            channel_type=AlertChannel.WEBHOOK,
            config=webhook_config,
            enabled=bool(webhook_config["url"])
        )

        self.logger.info(f"Initialized {len(self.notification_channels)} notification channels")

    # ---------- Public API ----------

    def add_alert_rule(self, rule: AlertRule):
        """Add a custom alert rule"""
        self.alert_rules[rule.name] = rule
        self.logger.info(f"Added alert rule: {rule.name}")

    def remove_alert_rule(self, rule_name: str):
        """Remove an alert rule"""
        if rule_name in self.alert_rules:
            del self.alert_rules[rule_name]
            self.logger.info(f"Removed alert rule: {rule_name}")

    def add_notification_channel(self, channel: NotificationChannel):
        """Add a notification channel"""
        self.notification_channels[channel.name] = channel
        self.logger.info(f"Added notification channel: {channel.name}")

    async def create_alert(
        self,
        rule_name: str,
        title: str,
        description: str,
        source_data: dict[str, Any] = None
    ) -> str | None:
        """Create a new alert"""
        if rule_name not in self.alert_rules:
            self.logger.error(f"Alert rule not found: {rule_name}")
            return None

        rule = self.alert_rules[rule_name]

        # Cooldown
        cooldown_key = f"{rule_name}_{title}"
        if cooldown_key in self.last_alert_times:
            time_since_last = datetime.utcnow() - self.last_alert_times[cooldown_key]
            if time_since_last.total_seconds() < rule.cooldown:
                self.logger.debug(f"Alert {rule_name} in cooldown, skipping")
                return None

        # Generate alert ID
        alert_id = f"{rule_name}_{int(time.time() * 1000)}"

        # Create alert
        alert = Alert(
            id=alert_id,
            rule_name=rule_name,
            alert_type=rule.alert_type,
            severity=rule.severity,
            title=title,
            description=description,
            timestamp=datetime.utcnow(),
            source_data=source_data or {},
            tags=rule.tags.copy()
        )

        # Store
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        self.last_alert_times[cooldown_key] = alert.timestamp

        # Send notifications
        await self._send_alert_notifications(alert, rule)

        # Audit log (ensure DB session is closed)
        db = None
        try:
            db = next(get_db())
            self.audit_logger.log_system_event(
                db=db,
                event_type=AuditEventType.ALERT_TRIGGERED,
                component="alert_system",
                status="active",
                metadata={
                    "alert_id": alert_id,
                    "rule_name": rule_name,
                    "severity": alert.severity.value,
                    "alert_type": alert.alert_type.value,
                    "title": title
                }
            )
        except Exception as e:
            self.logger.error(f"Failed to log alert to audit system: {e}")
        finally:
            if db is not None:
                try:
                    db.close()
                except Exception:
                    pass

        self.logger.info(f"Created alert: {alert_id} ({rule_name})")
        return alert_id

    # ---------- Notification sending ----------

    async def _send_alert_notifications(self, alert: Alert, rule: AlertRule):
        """Send alert notifications through configured channels"""
        for channel_type in rule.channels:
            try:
                # Find an enabled channel of this type
                channel = next(
                    (ch for ch in self.notification_channels.values()
                     if ch.channel_type == channel_type and ch.enabled),
                    None
                )
                if not channel:
                    self.logger.warning(f"No enabled channel found for type: {channel_type.value}")
                    continue

                # Rate limit per (channel, rule)
                rate_limit_key = f"{channel.name}_{alert.rule_name}"
                if rate_limit_key in self.last_alert_times:
                    time_since_last = datetime.utcnow() - self.last_alert_times[rate_limit_key]
                    if time_since_last.total_seconds() < channel.rate_limit:
                        self.logger.debug(f"Channel {channel.name} rate limited, skipping")
                        continue

                # Send
                success = await self._send_notification(alert, channel)
                if success:
                    self.last_alert_times[rate_limit_key] = datetime.utcnow()

            except Exception as e:
                self.logger.error(f"Failed to send alert via {channel_type.value}: {e}")

    async def _send_notification(self, alert: Alert, channel: NotificationChannel) -> bool:
        """Send notification through specific channel"""
        try:
            if channel.channel_type == AlertChannel.LOG:
                return self._send_log_notification(alert)
            elif channel.channel_type == AlertChannel.EMAIL:
                return await self._send_email_notification(alert, channel)
            elif channel.channel_type == AlertChannel.WEBHOOK:
                return await self._send_webhook_notification(alert, channel)
            else:
                self.logger.warning(f"Unsupported notification channel: {channel.channel_type.value}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to send notification via {channel.name}: {e}")
            return False

    def _send_log_notification(self, alert: Alert) -> bool:
        """Send alert notification to logs"""
        try:
            log_level = {
                AlertSeverity.INFO: logging.INFO,
                AlertSeverity.WARNING: logging.WARNING,
                AlertSeverity.ERROR: logging.ERROR,
                AlertSeverity.CRITICAL: logging.CRITICAL,
                AlertSeverity.EMERGENCY: logging.CRITICAL,
            }.get(alert.severity, logging.INFO)

            self.logger.log(log_level, f"ALERT [{alert.severity.value.upper()}] {alert.title}: {alert.description}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send log notification: {e}")
            return False

    async def _send_email_notification(self, alert: Alert, channel: NotificationChannel) -> bool:
        """Send alert notification via email"""
        try:
            config = channel.config
            if not config.get("smtp_username") or not config.get("to_emails"):
                self.logger.warning("Email configuration incomplete, skipping email notification")
                return False

            # Compose
            msg = MIMEMultipart()
            msg["From"] = config["from_email"]
            msg["To"] = ", ".join(config["to_emails"])
            msg["Subject"] = f"[LocalStorm Alert] {alert.severity.value.upper()}: {alert.title}"

            body = f"""
LocalStorm Alert Notification

Alert ID: {alert.id}
Severity: {alert.severity.value.upper()}
Type: {alert.alert_type.value}
Time: {alert.timestamp.isoformat()}

Title: {alert.title}
Description: {alert.description}

Tags: {', '.join(alert.tags)}

Source Data:
{json.dumps(alert.source_data, indent=2)}

--
LocalStorm Alert System
            """.strip()
            msg.attach(MIMEText(body, "plain"))

            # Send
            server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
            server.starttls()
            server.login(config["smtp_username"], config["smtp_password"])
            server.sendmail(config["from_email"], config["to_emails"], msg.as_string())
            server.quit()

            self.logger.info(f"Sent email notification for alert {alert.id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {e}")
            return False

    async def _send_webhook_notification(self, alert: Alert, channel: NotificationChannel) -> bool:
        """Send alert notification via webhook"""
        try:
            if aiohttp is None:
                self.logger.warning("aiohttp is not installed; skipping webhook notification")
                return False

            config = channel.config
            if not config.get("url"):
                self.logger.warning("Webhook URL not configured, skipping webhook notification")
                return False

            payload = {
                "alert_id": alert.id,
                "rule_name": alert.rule_name,
                "severity": alert.severity.value,
                "alert_type": alert.alert_type.value,
                "title": alert.title,
                "description": alert.description,
                "timestamp": alert.timestamp.isoformat(),
                "status": alert.status.value,
                "tags": alert.tags,
                "source_data": alert.source_data,
            }

            timeout = aiohttp.ClientTimeout(total=config.get("timeout", 30))
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    config["url"],
                    json=payload,
                    headers=config.get("headers", {})
                ) as response:
                    if response.status == 200:
                        self.logger.info(f"Sent webhook notification for alert {alert.id}")
                        return True
                    else:
                        self.logger.error(f"Webhook returned status {response.status}")
                        return False
        except Exception as e:
            self.logger.error(f"Failed to send webhook notification: {e}")
            return False

    # ---------- Alert lifecycle ----------

    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        if alert_id not in self.active_alerts:
            return False

        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_by = acknowledged_by
        alert.acknowledged_at = datetime.utcnow()

        self.logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
        return True

    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        if alert_id not in self.active_alerts:
            return False

        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.utcnow()

        # Remove from active alerts
        del self.active_alerts[alert_id]

        self.logger.info(f"Alert {alert_id} resolved")
        return True

    # ---------- Monitoring loop ----------

    def _start_background_monitoring(self):
        """Start background monitoring tasks"""

        async def monitor_alerts():
            """Background task to monitor conditions and generate alerts"""
            while True:
                try:
                    await self._check_alert_conditions()
                    await self._check_alert_escalations()
                    await asyncio.sleep(60)  # run every minute
                except Exception as e:
                    self.logger.error(f"Error in alert monitoring: {e}")
                    await asyncio.sleep(60)

        try:
            loop = asyncio.get_event_loop()
            # Only schedule if not already scheduled and loop is running
            if self.monitoring_task is None or self.monitoring_task.done():
                self.monitoring_task = loop.create_task(monitor_alerts())
        except RuntimeError:
            # No event loop running yet (e.g., import time); will be started later when a loop exists
            pass

    async def _check_alert_conditions(self):
        """Check all alert rule conditions"""
        try:
            # Current system state
            health_service = self._get_health_service()
            health_result = await health_service.run_comprehensive_health_check()
            error_stats = self.error_tracker.get_error_statistics()

            # Extract metrics
            system_metrics = health_result.get("system_metrics", {})
            overall_status = health_result.get("overall_status")

            # Normalize health status to string
            health_status = overall_status.value if hasattr(overall_status, "value") else str(overall_status)

            current_data = {
                "error_rate": error_stats.get("error_rates", {}).get("1min", 0),
                "critical_errors": error_stats.get("errors_by_severity", {}).get("critical", 0),
                "total_errors": error_stats.get("total_errors", 0),
                "health_status": health_status,
                "cpu_percent": system_metrics.get("cpu", {}).get("percent", 0),
                "memory_percent": system_metrics.get("memory", {}).get("percent", 0),
                "disk_percent": system_metrics.get("disk", {}).get("percent", 0),
                "database_connected": health_result.get("application", {}).get("database_connected", True),
                "security_events": 0,  # populate from security monitoring if available
                "timestamp": datetime.utcnow(),
            }

            # Evaluate rules
            for rule_name, rule in self.alert_rules.items():
                if not rule.enabled:
                    continue
                try:
                    condition_met = self._evaluate_condition(rule, current_data)
                    if condition_met:
                        title = self._generate_alert_title(rule, current_data)
                        description = self._generate_alert_description(rule, current_data)
                        await self.create_alert(
                            rule_name=rule_name,
                            title=title,
                            description=description,
                            source_data=current_data
                        )
                except Exception as e:
                    self.logger.error(f"Error evaluating rule {rule_name}: {e}")

        except Exception as e:
            self.logger.error(f"Error checking alert conditions: {e}")

    def _evaluate_condition(self, rule: AlertRule, data: dict[str, Any]) -> bool:
        """Evaluate if alert condition is met (simple DSL)"""
        try:
            condition = rule.condition
            threshold = rule.threshold

            if "error_rate > threshold" in condition:
                return data.get("error_rate", 0) > threshold
            elif "health_status != healthy" in condition:
                return data.get("health_status") != "healthy"
            elif "health_status == critical" in condition:
                return data.get("health_status") == "critical"
            elif "cpu_percent > threshold" in condition:
                return data.get("cpu_percent", 0) > threshold
            elif "memory_percent > threshold" in condition:
                return data.get("memory_percent", 0) > threshold
            elif "disk_percent > threshold" in condition:
                return data.get("disk_percent", 0) > threshold
            elif "database_connected == false" in condition:
                return not data.get("database_connected", True)
            elif "security_events > threshold" in condition:
                return data.get("security_events", 0) > threshold
            else:
                self.logger.warning(f"Unknown condition: {condition}")
                return False
        except Exception as e:
            self.logger.error(f"Error evaluating condition: {e}")
            return False

    def _generate_alert_title(self, rule: AlertRule, data: dict[str, Any]) -> str:
        """Generate alert title based on rule and data"""
        if rule.alert_type == AlertType.ERROR_RATE:
            return f"High Error Rate: {data.get('error_rate', 0):.1f}%"
        elif rule.alert_type == AlertType.SYSTEM_HEALTH:
            return f"System Health: {data.get('health_status', 'unknown').title()}"
        elif rule.alert_type == AlertType.PERFORMANCE:
            if "cpu" in rule.name:
                return f"High CPU Usage: {data.get('cpu_percent', 0):.1f}%"
            elif "memory" in rule.name:
                return f"High Memory Usage: {data.get('memory_percent', 0):.1f}%"
        elif rule.alert_type == AlertType.CAPACITY:
            return f"Disk Space Warning: {data.get('disk_percent', 0):.1f}% used"
        elif rule.alert_type == AlertType.DATABASE:
            return "Database Connection Failure"
        elif rule.alert_type == AlertType.SECURITY:
            return f"Security Threat Detected: {data.get('security_events', 0)} events"
        return f"Alert: {rule.name}"

    def _generate_alert_description(self, rule: AlertRule, data: dict[str, Any]) -> str:
        """Generate alert description with context"""
        base_desc = f"Alert rule '{rule.name}' triggered. "

        if rule.alert_type == AlertType.ERROR_RATE:
            return base_desc + f"Current error rate is {data.get('error_rate', 0):.1f}%, threshold is {rule.threshold}%."
        elif rule.alert_type == AlertType.SYSTEM_HEALTH:
            return base_desc + f"System health status is '{data.get('health_status', 'unknown')}'."
        elif rule.alert_type == AlertType.PERFORMANCE:
            if "cpu" in rule.name:
                return base_desc + f"CPU usage is {data.get('cpu_percent', 0):.1f}%, threshold is {rule.threshold}%."
            elif "memory" in rule.name:
                return base_desc + f"Memory usage is {data.get('memory_percent', 0):.1f}%, threshold is {rule.threshold}%."
        elif rule.alert_type == AlertType.CAPACITY:
            return base_desc + f"Disk usage is {data.get('disk_percent', 0):.1f}%, threshold is {rule.threshold}%."
        elif rule.alert_type == AlertType.DATABASE:
            return base_desc + "Database connection check failed."
        elif rule.alert_type == AlertType.SECURITY:
            return base_desc + f"{data.get('security_events', 0)} security events detected in the last period."
        return base_desc + "Condition met."

    async def _check_alert_escalations(self):
        """Check for alerts that need escalation"""
        current_time = datetime.utcnow()

        for alert_id, alert in list(self.active_alerts.items()):
            if alert.status == AlertStatus.ACTIVE:
                rule = self.alert_rules.get(alert.rule_name)
                if rule and rule.escalation_time > 0:
                    time_since_alert = (current_time - alert.timestamp).total_seconds()
                    if time_since_alert > rule.escalation_time and not alert.escalated_at:
                        alert.status = AlertStatus.ESCALATED
                        alert.escalated_at = current_time
                        await self._send_escalation_notifications(alert, rule)
                        self.logger.warning(f"Alert {alert_id} escalated after {rule.escalation_time} seconds")

    async def _send_escalation_notifications(self, alert: Alert, rule: AlertRule):
        """Send escalation notifications"""
        escalation_title = f"ESCALATED: {alert.title}"
        escalation_description = (
            f"Alert has been active for {rule.escalation_time} seconds without resolution. "
            f"Original: {alert.description}"
        )

        escalation_channels = [AlertChannel.LOG, AlertChannel.EMAIL, AlertChannel.WEBHOOK]
        for channel_type in escalation_channels:
            channel = next(
                (ch for ch in self.notification_channels.values()
                 if ch.channel_type == channel_type and ch.enabled),
                None
            )
            if channel:
                escalated_alert = Alert(
                    id=f"{alert.id}_escalated",
                    rule_name=alert.rule_name,
                    alert_type=alert.alert_type,
                    severity=AlertSeverity.CRITICAL,
                    title=escalation_title,
                    description=escalation_description,
                    timestamp=datetime.utcnow(),
                    source_data=alert.source_data,
                    tags=alert.tags + ["escalated"]
                )
                await self._send_notification(escalated_alert, channel)

    # ---------- Queries / Stats ----------

    def get_active_alerts(
        self,
        severity: AlertSeverity | None = None,
        alert_type: AlertType | None = None,
        tags: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """Get active alerts with optional filtering"""
        alerts: list[dict[str, Any]] = []
        for alert in self.active_alerts.values():
            if severity and alert.severity != severity:
                continue
            if alert_type and alert.alert_type != alert_type:
                continue
            if tags and not any(tag in alert.tags for tag in tags):
                continue
            alerts.append(asdict(alert))
        return alerts

    def get_alert_statistics(self) -> dict[str, Any]:
        """Get alert system statistics"""
        severity_counts = defaultdict(int)
        type_counts = defaultdict(int)
        status_counts = defaultdict(int)

        for alert in self.active_alerts.values():
            severity_counts[alert.severity.value] += 1
            type_counts[alert.alert_type.value] += 1
            status_counts[alert.status.value] += 1

        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_alerts = [alert for alert in self.alert_history if alert.timestamp > recent_cutoff]

        return {
            "active_alerts": len(self.active_alerts),
            "total_rules": len(self.alert_rules),
            "enabled_rules": len([r for r in self.alert_rules.values() if r.enabled]),
            "notification_channels": len(self.notification_channels),
            "enabled_channels": len([c for c in self.notification_channels.values() if c.enabled]),
            "severity_counts": dict(severity_counts),
            "type_counts": dict(type_counts),
            "status_counts": dict(status_counts),
            "recent_alerts_24h": len(recent_alerts),
            "alert_history_size": len(self.alert_history),
        }


# Global alert system instance
_alert_system_instance: AlertSystem | None = None

def get_alert_system() -> AlertSystem:
    """Get global alert system instance"""
    global _alert_system_instance
    if _alert_system_instance is None:
        _alert_system_instance = AlertSystem()
    return _alert_system_instance
