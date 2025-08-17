"""
Audit Log Model for Task 1.2.6 - Audit Logging
===============================================

Comprehensive audit logging system for security, compliance, and monitoring.
Tracks all important user actions, security events, and system activities.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from enum import Enum
from typing import Optional, Dict, Any


class AuditEventType(Enum):
    """Types of events that can be audited"""
    # Authentication Events
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTER = "user_register"
    LOGIN_FAILED = "login_failed"
    TOKEN_REFRESH = "token_refresh"
    TOKEN_REVOKED = "token_revoked"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET_REQUESTED = "password_reset_requested"
    PASSWORD_RESET_TOKEN_VERIFIED = "password_reset_token_verified"
    PASSWORD_RESET_COMPLETED = "password_reset_completed"
    PASSWORD_RESET_COMPLETE = "password_reset_complete"
    
    # Developer earnings events
    DEVELOPER_EARNINGS_ACCESSED = "developer_earnings_accessed"
    DEVELOPER_EARNINGS_ACCESS_FAILED = "developer_earnings_access_failed"
    DEVELOPER_PAYOUT_REQUESTED = "developer_payout_requested"
    DEVELOPER_PAYOUT_COMPLETED = "developer_payout_completed"
    
    # Authorization Events
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    ROLE_CHANGED = "role_changed"
    PERMISSION_ESCALATION = "permission_escalation"
    
    # Security Events
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    BRUTE_FORCE_ATTEMPT = "brute_force_attempt"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    DDOS_ATTEMPT = "ddos_attempt"
    CONTENT_BLOCKED = "content_blocked"
    INPUT_SANITIZED = "input_sanitized"
    MALICIOUS_REQUEST = "malicious_request"
    
    # AI Service Events
    AI_PROMPT_SUBMITTED = "ai_prompt_submitted"
    AI_RESPONSE_GENERATED = "ai_response_generated"
    AI_CONTENT_MODERATED = "ai_content_moderated"
    AI_RATE_LIMITED = "ai_rate_limited"
    
    # Profile/Account Events
    PROFILE_UPDATED = "profile_updated"
    PROFILE_VIEWED = "profile_viewed"
    EMAIL_CHANGED = "email_changed"
    EMAIL_VERIFIED = "email_verified"
    ACCOUNT_DEACTIVATED = "account_deactivated"
    ACCOUNT_REACTIVATED = "account_reactivated"
    
    # Admin Events
    ADMIN_ACTION = "admin_action"
    USER_IMPERSONATION = "user_impersonation"
    SYSTEM_CONFIG_CHANGE = "system_config_change"
    
    # Data Events
    DATA_EXPORT = "data_export"
    DATA_DELETION = "data_deletion"
    PII_ACCESS = "pii_access"
    
    # System Events
    SYSTEM_ERROR = "system_error"
    SYSTEM_WARNING = "system_warning"
    MAINTENANCE_START = "maintenance_start"
    MAINTENANCE_END = "maintenance_end"
    
    # Alert Events (Task 1.3.6)
    ALERT_TRIGGERED = "alert_triggered"
    ALERT_ACKNOWLEDGED = "alert_acknowledged"
    ALERT_RESOLVED = "alert_resolved"
    ALERT_ESCALATED = "alert_escalated"
    
    # Configuration Events  
    CONFIGURATION_CHANGED = "configuration_changed"
    
    # Enhanced Auth Events (Task 1.1.6)
    USER_REGISTRATION = "user_registration"
    USER_REGISTRATION_FAILED = "user_registration_failed"
    USER_LOGIN_FAILED = "user_login_failed"
    UNAUTHORIZED_ACCESS = "unauthorized_access"


class AuditLogLevel(Enum):
    """Severity levels for audit events"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditLog(Base):
    """
    Comprehensive audit log for security and compliance
    
    Features:
    - Complete event tracking
    - Security monitoring
    - Compliance reporting
    - Performance metrics
    - User activity tracking
    """
    __tablename__ = "audit_logs"
    __table_args__ = {"extend_existing": True}  # ✅ Fix for redefinition error
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User Information
    user_id = Column(Integer, ForeignKey("users_v2.id", ondelete="SET NULL"), nullable=True, index=True)
    user_email = Column(String(255), nullable=True, index=True)
    user_role = Column(String(50), nullable=True)
    
    # Event Details
    event_type = Column(String(50), nullable=False, index=True)
    event_category = Column(String(50), nullable=False, index=True)  # 'security', 'auth', 'ai', 'profile', etc.
    event_level = Column(String(20), nullable=False, default=AuditLogLevel.INFO.value)
    event_description = Column(Text, nullable=True)
    
    # Request Details
    ip_address = Column(String(45), nullable=True, index=True)
    user_agent = Column(String(1000), nullable=True)
    endpoint = Column(String(255), nullable=True, index=True)
    http_method = Column(String(10), nullable=True)
    request_id = Column(String(100), nullable=True, index=True)
    
    # Response Details
    status_code = Column(Integer, nullable=True, index=True)
    response_time_ms = Column(Integer, nullable=True)
    success = Column(Boolean, nullable=False, default=True, index=True)
    
    # Error Information
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    stack_trace = Column(Text, nullable=True)
    
    # Additional Context
    event_metadata = Column(JSON, nullable=True)  # Store additional structured data
    session_id = Column(String(100), nullable=True, index=True)
    device_info = Column(String(500), nullable=True)
    location_info = Column(String(200), nullable=True)
    
    # Security Context
    risk_score = Column(Integer, nullable=True)  # 0-100 risk assessment
    threat_indicators = Column(JSON, nullable=True)  # List of security indicators
    
    # Compliance Fields
    data_sensitivity = Column(String(20), nullable=True)  # 'public', 'internal', 'confidential', 'restricted'
    retention_policy = Column(String(50), nullable=True)  # How long to keep this log
    regulatory_tags = Column(JSON, nullable=True)  # GDPR, CCPA, SOX, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    event_timestamp = Column(DateTime(timezone=True), nullable=True)  # When the actual event occurred
    
    # Relationships
    # Note: User relationship defined here to avoid circular import issues
    # user = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, event_type={self.event_type}, user_id={self.user_id}, timestamp={self.created_at})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit log to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_email': self.user_email,
            'user_role': self.user_role,
            'event_type': self.event_type,
            'event_category': self.event_category,
            'event_level': self.event_level,
            'event_description': self.event_description,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'endpoint': self.endpoint,
            'http_method': self.http_method,
            'status_code': self.status_code,
            'response_time_ms': self.response_time_ms,
            'success': self.success,
            'error_message': self.error_message,
            'metadata': self.event_metadata,
            'risk_score': self.risk_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'event_timestamp': self.event_timestamp.isoformat() if self.event_timestamp else None
        }
    
    @classmethod
    def create_event(cls, 
                    event_type: AuditEventType,
                    event_category: str,
                    user_id: Optional[str] = None,
                    user_email: Optional[str] = None,
                    user_role: Optional[str] = None,
                    event_description: Optional[str] = None,
                    ip_address: Optional[str] = None,
                    user_agent: Optional[str] = None,
                    endpoint: Optional[str] = None,
                    http_method: Optional[str] = None,
                    status_code: Optional[int] = None,
                    success: bool = True,
                    error_message: Optional[str] = None,
                    metadata: Optional[Dict[str, Any]] = None,
                    event_level: AuditLogLevel = AuditLogLevel.INFO,
                    **kwargs) -> 'AuditLog':
        """
        Factory method to create audit log entries with proper validation
        """
        return cls(
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            event_type=event_type.value,
            event_category=event_category,
            event_level=event_level.value,
            event_description=event_description,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            http_method=http_method,
            status_code=status_code,
            success=success,
            error_message=error_message,
            event_metadata=metadata,
            **kwargs
        )
