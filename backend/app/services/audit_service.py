"""
Audit Logging Service for Task 1.2.6 - Audit Logging
====================================================

Comprehensive audit logging service that provides:
- Event tracking and logging
- Security monitoring
- Compliance reporting
- Performance analytics
- User activity tracking
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func
from fastapi import Request
import hashlib
import re
from user_agents import parse

from app.models.audit_log import AuditLog, AuditEventType, AuditLogLevel
from app.database import get_db


class AuditLogger:
    """
    Central audit logging service for comprehensive event tracking
    """
    
    def __init__(self):
        self.logger = logging.getLogger("capecontrol.audit")
        self.setup_logging()
        
        # Risk assessment patterns
        self.suspicious_patterns = [
            r'(?i)(script|javascript|vbscript)',  # Script injection
            r'(?i)(union|select|insert|delete|drop|alter)',  # SQL injection
            r'(?i)(eval|exec|system|cmd)',  # Command injection
            r'[<>"\'\(\)]',  # HTML/XSS patterns
            r'(?i)(password|token|key|secret)',  # Sensitive data exposure
        ]
        
    def setup_logging(self):
        """Setup structured logging for audit events"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create audit-specific logger
        audit_handler = logging.StreamHandler()
        audit_formatter = logging.Formatter(
            '%(asctime)s - AUDIT - %(levelname)s - %(message)s'
        )
        audit_handler.setFormatter(audit_formatter)
        self.logger.addHandler(audit_handler)
        
    def log_event(self,
                  db: Session,
                  event_type: AuditEventType,
                  event_category: str,
                  request: Optional[Request] = None,
                  user_id: Optional[str] = None,
                  user_email: Optional[str] = None,
                  user_role: Optional[str] = None,
                  event_description: Optional[str] = None,
                  success: bool = True,
                  error_message: Optional[str] = None,
                  metadata: Optional[Dict[str, Any]] = None,
                  event_level: AuditLogLevel = AuditLogLevel.INFO,
                  **kwargs) -> AuditLog:
        """
        Log an audit event with comprehensive context
        """
        try:
            # Extract request information if available
            ip_address = None
            user_agent = None
            endpoint = None
            http_method = None
            request_id = None
            
            if request:
                ip_address = self._get_client_ip(request)
                user_agent = request.headers.get("user-agent", "")
                endpoint = str(request.url.path)
                http_method = request.method
                request_id = getattr(request.state, 'request_id', None)
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(
                event_type=event_type,
                success=success,
                ip_address=ip_address,
                user_agent=user_agent,
                endpoint=endpoint,
                metadata=metadata
            )
            
            # Create audit log entry
            audit_log = AuditLog.create_event(
                event_type=event_type,
                event_category=event_category,
                user_id=user_id,
                user_email=user_email,
                user_role=user_role,
                event_description=event_description,
                ip_address=ip_address,
                user_agent=user_agent,
                endpoint=endpoint,
                http_method=http_method,
                request_id=request_id,
                success=success,
                error_message=error_message,
                metadata=metadata,
                event_level=event_level,
                risk_score=risk_score,
                event_timestamp=datetime.utcnow(),
                **kwargs
            )
            
            # Save to database
            db.add(audit_log)
            db.commit()
            
            # Log to application logs as well
            log_message = f"AUDIT: {event_type.value} - User: {user_email or 'Anonymous'} - " \
                         f"IP: {ip_address} - Success: {success}"
            
            if event_level == AuditLogLevel.CRITICAL:
                self.logger.critical(log_message)
            elif event_level == AuditLogLevel.ERROR:
                self.logger.error(log_message)
            elif event_level == AuditLogLevel.WARNING:
                self.logger.warning(log_message)
            else:
                self.logger.info(log_message)
            
            return audit_log
            
        except Exception as e:
            self.logger.error(f"Failed to log audit event: {e}")
            # Don't raise exception to avoid breaking main application flow
            return None
    
    def log_authentication_event(self,
                                db: Session,
                                event_type: AuditEventType,
                                request: Request,
                                user_id: Optional[str] = None,
                                user_email: Optional[str] = None,
                                user_role: Optional[str] = None,
                                success: bool = True,
                                error_message: Optional[str] = None,
                                additional_data: Optional[Dict[str, Any]] = None) -> AuditLog:
        """
        Log authentication-related events
        """
        metadata = {
            "authentication_method": "jwt",
            "session_type": "stateless",
            **(additional_data or {})
        }
        
        return self.log_event(
            db=db,
            event_type=event_type,
            event_category="authentication",
            request=request,
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            success=success,
            error_message=error_message,
            metadata=metadata,
            event_level=AuditLogLevel.WARNING if not success else AuditLogLevel.INFO
        )
    
    def log_security_event(self,
                          db: Session,
                          event_type: AuditEventType,
                          request: Request,
                          event_description: str,
                          threat_indicators: Optional[List[str]] = None,
                          user_id: Optional[str] = None,
                          additional_data: Optional[Dict[str, Any]] = None) -> AuditLog:
        """
        Log security-related events with enhanced context
        """
        metadata = {
            "security_event": True,
            "threat_indicators": threat_indicators or [],
            "requires_investigation": len(threat_indicators or []) > 0,
            **(additional_data or {})
        }
        
        return self.log_event(
            db=db,
            event_type=event_type,
            event_category="security",
            request=request,
            user_id=user_id,
            event_description=event_description,
            metadata=metadata,
            event_level=AuditLogLevel.WARNING,
            threat_indicators=threat_indicators
        )
    
    def log_ai_event(self,
                    db: Session,
                    event_type: AuditEventType,
                    request: Request,
                    user_id: str,
                    user_email: str,
                    prompt_data: Optional[Dict[str, Any]] = None,
                    response_data: Optional[Dict[str, Any]] = None,
                    moderation_applied: bool = False,
                    processing_time_ms: Optional[int] = None) -> AuditLog:
        """
        Log AI service events with detailed context
        """
        metadata = {
            "ai_service": True,
            "prompt_length": len(str(prompt_data.get("message", ""))) if prompt_data else 0,
            "response_length": len(str(response_data.get("response", ""))) if response_data else 0,
            "moderation_applied": moderation_applied,
            "processing_time_ms": processing_time_ms,
            "model_used": response_data.get("model", "unknown") if response_data else None
        }
        
        return self.log_event(
            db=db,
            event_type=event_type,
            event_category="ai_service",
            request=request,
            user_id=user_id,
            user_email=user_email,
            metadata=metadata,
            response_time_ms=processing_time_ms
        )
    
    def log_profile_event(self,
                         db: Session,
                         event_type: AuditEventType,
                         request: Request,
                         user_id: str,
                         user_email: str,
                         changes_made: Optional[Dict[str, Any]] = None,
                         data_sensitivity: str = "internal") -> AuditLog:
        """
        Log profile and account-related events
        """
        metadata = {
            "profile_event": True,
            "changes_made": changes_made or {},
            "fields_modified": list(changes_made.keys()) if changes_made else []
        }
        
        return self.log_event(
            db=db,
            event_type=event_type,
            event_category="profile",
            request=request,
            user_id=user_id,
            user_email=user_email,
            metadata=metadata,
            data_sensitivity=data_sensitivity
        )
    
    def get_user_activity(self,
                         db: Session,
                         user_id: str,
                         days: int = 30,
                         event_categories: Optional[List[str]] = None) -> List[AuditLog]:
        """
        Get user activity logs for a specific time period
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(AuditLog).filter(
            and_(
                AuditLog.user_id == user_id,
                AuditLog.created_at >= cutoff_date
            )
        )
        
        if event_categories:
            query = query.filter(AuditLog.event_category.in_(event_categories))
        
        return query.order_by(desc(AuditLog.created_at)).limit(1000).all()
    
    def get_security_events(self,
                           db: Session,
                           hours: int = 24,
                           severity_level: Optional[AuditLogLevel] = None) -> List[AuditLog]:
        """
        Get recent security events for monitoring
        """
        cutoff_date = datetime.utcnow() - timedelta(hours=hours)
        
        query = db.query(AuditLog).filter(
            and_(
                AuditLog.event_category == "security",
                AuditLog.created_at >= cutoff_date
            )
        )
        
        if severity_level:
            query = query.filter(AuditLog.event_level == severity_level.value)
        
        return query.order_by(desc(AuditLog.created_at)).all()
    
    def get_failed_authentication_attempts(self,
                                         db: Session,
                                         hours: int = 1,
                                         ip_address: Optional[str] = None) -> List[AuditLog]:
        """
        Get failed authentication attempts for brute force detection
        """
        cutoff_date = datetime.utcnow() - timedelta(hours=hours)
        
        filters = [
            AuditLog.event_category == "authentication",
            AuditLog.success == False,
            AuditLog.created_at >= cutoff_date
        ]
        
        if ip_address:
            filters.append(AuditLog.ip_address == ip_address)
        
        return db.query(AuditLog).filter(and_(*filters)).all()
    
    def get_audit_statistics(self, db: Session, days: int = 7) -> Dict[str, Any]:
        """
        Get audit statistics for dashboard and monitoring
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Total events
        total_events = db.query(func.count(AuditLog.id)).filter(
            AuditLog.created_at >= cutoff_date
        ).scalar()
        
        # Events by category
        category_stats = db.query(
            AuditLog.event_category,
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.created_at >= cutoff_date
        ).group_by(AuditLog.event_category).all()
        
        # Failed events
        failed_events = db.query(func.count(AuditLog.id)).filter(
            and_(
                AuditLog.created_at >= cutoff_date,
                AuditLog.success == False
            )
        ).scalar()
        
        # High-risk events
        high_risk_events = db.query(func.count(AuditLog.id)).filter(
            and_(
                AuditLog.created_at >= cutoff_date,
                AuditLog.risk_score >= 70
            )
        ).scalar()
        
        # Top users by activity
        top_users = db.query(
            AuditLog.user_email,
            func.count(AuditLog.id).label('event_count')
        ).filter(
            and_(
                AuditLog.created_at >= cutoff_date,
                AuditLog.user_email.isnot(None)
            )
        ).group_by(AuditLog.user_email).order_by(
            desc('event_count')
        ).limit(10).all()
        
        return {
            "period_days": days,
            "total_events": total_events,
            "failed_events": failed_events,
            "high_risk_events": high_risk_events,
            "success_rate": round((total_events - failed_events) / max(total_events, 1) * 100, 2),
            "events_by_category": {cat: count for cat, count in category_stats},
            "top_users": [{"email": email, "event_count": count} for email, count in top_users]
        }
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request headers
        """
        # Check common proxy headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"
    
    def _calculate_risk_score(self,
                             event_type: AuditEventType,
                             success: bool,
                             ip_address: Optional[str] = None,
                             user_agent: Optional[str] = None,
                             endpoint: Optional[str] = None,
                             metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Calculate risk score for the event (0-100)
        """
        risk_score = 0
        
        # Base score based on event type
        high_risk_events = [
            AuditEventType.LOGIN_FAILED,
            AuditEventType.BRUTE_FORCE_ATTEMPT,
            AuditEventType.DDOS_ATTEMPT,
            AuditEventType.MALICIOUS_REQUEST,
            AuditEventType.PERMISSION_ESCALATION,
            AuditEventType.SUSPICIOUS_ACTIVITY
        ]
        
        if event_type in high_risk_events:
            risk_score += 40
        elif not success:
            risk_score += 20
        
        # Check for suspicious patterns in user agent
        if user_agent:
            for pattern in self.suspicious_patterns:
                if re.search(pattern, user_agent):
                    risk_score += 15
                    break
        
        # Check for suspicious endpoints
        if endpoint:
            suspicious_endpoints = ['/admin', '/debug', '/test', '/backup']
            if any(sus in endpoint.lower() for sus in suspicious_endpoints):
                risk_score += 10
        
        # Check metadata for additional risk indicators
        if metadata:
            if metadata.get("threat_indicators"):
                risk_score += len(metadata["threat_indicators"]) * 10
            
            if metadata.get("security_event"):
                risk_score += 15
            
            if metadata.get("requires_investigation"):
                risk_score += 20
        
        return min(risk_score, 100)  # Cap at 100
    
    def log_system_event(self,
                        db: Session,
                        event_type: AuditEventType,
                        component: str,
                        status: str,
                        metadata: Optional[Dict[str, Any]] = None,
                        event_level: AuditLogLevel = AuditLogLevel.INFO) -> AuditLog:
        """
        Log system-level events (alerts, configuration changes, etc.)
        """
        event_description = f"System event in {component}: {status}"
        
        system_metadata = {
            "system_event": True,
            "component": component,
            "status": status,
            **(metadata or {})
        }
        
        return self.log_event(
            db=db,
            event_type=event_type,
            event_category="system",
            event_description=event_description,
            metadata=system_metadata,
            event_level=event_level
        )


# Global audit logger instance
audit_logger = AuditLogger()


def get_audit_logger() -> AuditLogger:
    """Get the global audit logger instance"""
    return audit_logger
