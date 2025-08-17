"""
Audit API Routes for Task 1.2.6 - Audit Logging
===============================================

API endpoints for viewing and managing audit logs, providing:
- Audit log viewing and filtering
- Security event monitoring
- User activity tracking
- Compliance reporting
- Administrative audit management
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from app.database import get_db
from app.models.audit_log import AuditLog, AuditEventType, AuditLogLevel
from app.services.audit_service import get_audit_logger
from app.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/api/audit", tags=["audit"])


# Pydantic models for API responses
class AuditLogResponse(BaseModel):
    """Response model for audit log entries"""
    id: int
    user_id: Optional[str]
    user_email: Optional[str]
    user_role: Optional[str]
    event_type: str
    event_category: str
    event_level: str
    event_description: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    endpoint: Optional[str]
    http_method: Optional[str]
    status_code: Optional[int]
    response_time_ms: Optional[int]
    success: bool
    error_message: Optional[str]
    metadata: Optional[Dict[str, Any]]
    risk_score: Optional[int]
    created_at: datetime
    event_timestamp: Optional[datetime]

    class Config:
        from_attributes = True


class AuditStatisticsResponse(BaseModel):
    """Response model for audit statistics"""
    period_days: int
    total_events: int
    failed_events: int
    high_risk_events: int
    success_rate: float
    events_by_category: Dict[str, int]
    top_users: List[Dict[str, Any]]


class SecurityEventResponse(BaseModel):
    """Response model for security events"""
    id: int
    event_type: str
    event_description: Optional[str]
    ip_address: Optional[str]
    user_id: Optional[str]
    user_email: Optional[str]
    risk_score: Optional[int]
    threat_indicators: Optional[List[str]]
    created_at: datetime
    requires_investigation: bool

    class Config:
        from_attributes = True


@router.get("/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, le=1000, description="Maximum number of logs to return"),
    offset: int = Query(0, ge=0, description="Number of logs to skip"),
    event_category: Optional[str] = Query(None, description="Filter by event category"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    start_date: Optional[datetime] = Query(None, description="Filter events after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter events before this date"),
    success_only: Optional[bool] = Query(None, description="Filter by success status"),
    min_risk_score: Optional[int] = Query(None, ge=0, le=100, description="Minimum risk score")
):
    """
    Get audit logs with filtering and pagination
    
    Requires admin role for full access, users can only see their own logs
    """
    
    # Check permissions
    if current_user.user_role != "admin" and user_id != current_user.id:
        # Non-admin users can only see their own logs
        user_id = current_user.id
    
    # Build query
    query = db.query(AuditLog)
    
    # Apply filters
    if event_category:
        query = query.filter(AuditLog.event_category == event_category)
    
    if event_type:
        query = query.filter(AuditLog.event_type == event_type)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)
    
    if success_only is not None:
        query = query.filter(AuditLog.success == success_only)
    
    if min_risk_score is not None:
        query = query.filter(AuditLog.risk_score >= min_risk_score)
    
    # Order by most recent first
    query = query.order_by(AuditLog.created_at.desc())
    
    # Apply pagination
    logs = query.offset(offset).limit(limit).all()
    
    return logs


@router.get("/logs/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific audit log entry by ID
    """
    
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found"
        )
    
    # Check permissions
    if current_user.user_role != "admin" and log.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return log


@router.get("/statistics", response_model=AuditStatisticsResponse)
async def get_audit_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    days: int = Query(7, ge=1, le=90, description="Number of days to analyze")
):
    """
    Get audit statistics for monitoring and dashboard
    
    Requires admin role
    """
    
    if current_user.user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    audit_logger = get_audit_logger()
    stats = audit_logger.get_audit_statistics(db, days=days)
    
    return AuditStatisticsResponse(**stats)


@router.get("/security-events", response_model=List[SecurityEventResponse])
async def get_security_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    severity: Optional[str] = Query(None, description="Filter by severity level")
):
    """
    Get recent security events for monitoring
    
    Requires admin role
    """
    
    if current_user.user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    audit_logger = get_audit_logger()
    
    # Convert severity string to enum if provided
    severity_level = None
    if severity:
        try:
            severity_level = AuditLogLevel(severity.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid severity level: {severity}"
            )
    
    security_events = audit_logger.get_security_events(db, hours=hours, severity_level=severity_level)
    
    # Transform to response format
    response_events = []
    for event in security_events:
        threat_indicators = []
        requires_investigation = False
        
        if event.metadata:
            threat_indicators = event.metadata.get("threat_indicators", [])
            requires_investigation = event.metadata.get("requires_investigation", False)
        
        response_events.append(SecurityEventResponse(
            id=event.id,
            event_type=event.event_type,
            event_description=event.event_description,
            ip_address=event.ip_address,
            user_id=event.user_id,
            user_email=event.user_email,
            risk_score=event.risk_score,
            threat_indicators=threat_indicators,
            created_at=event.created_at,
            requires_investigation=requires_investigation
        ))
    
    return response_events


@router.get("/user-activity/{user_id}")
async def get_user_activity(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    days: int = Query(30, ge=1, le=90, description="Days to look back"),
    categories: Optional[str] = Query(None, description="Comma-separated event categories")
):
    """
    Get activity logs for a specific user
    
    Users can see their own activity, admins can see any user's activity
    """
    
    # Check permissions
    if current_user.user_role != "admin" and user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    audit_logger = get_audit_logger()
    
    # Parse categories if provided
    event_categories = None
    if categories:
        event_categories = [cat.strip() for cat in categories.split(",")]
    
    activity_logs = audit_logger.get_user_activity(
        db, user_id=user_id, days=days, event_categories=event_categories
    )
    
    return {
        "user_id": user_id,
        "period_days": days,
        "total_events": len(activity_logs),
        "event_categories": event_categories,
        "events": [log.to_dict() for log in activity_logs]
    }


@router.get("/failed-logins")
async def get_failed_login_attempts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    ip_address: Optional[str] = Query(None, description="Filter by IP address")
):
    """
    Get failed login attempts for security monitoring
    
    Requires admin role
    """
    
    if current_user.user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    audit_logger = get_audit_logger()
    failed_attempts = audit_logger.get_failed_authentication_attempts(
        db, hours=hours, ip_address=ip_address
    )
    
    return {
        "period_hours": hours,
        "ip_filter": ip_address,
        "total_failed_attempts": len(failed_attempts),
        "attempts": [log.to_dict() for log in failed_attempts]
    }


@router.get("/event-types")
async def get_available_event_types(
    current_user: User = Depends(get_current_user)
):
    """
    Get list of available audit event types for filtering
    """
    
    return {
        "event_types": [event_type.value for event_type in AuditEventType],
        "event_categories": [
            "authentication",
            "authorization", 
            "security",
            "ai_service",
            "profile",
            "admin",
            "data",
            "system",
            "request"
        ],
        "event_levels": [level.value for level in AuditLogLevel]
    }


@router.post("/export")
async def export_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    start_date: datetime = Query(..., description="Export start date"),
    end_date: datetime = Query(..., description="Export end date"),
    format: str = Query("json", regex="^(json|csv)$", description="Export format")
):
    """
    Export audit logs for compliance reporting
    
    Requires admin role
    """
    
    if current_user.user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Validate date range (max 1 year)
    if (end_date - start_date).days > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Export date range cannot exceed 1 year"
        )
    
    # Get logs for export
    logs = db.query(AuditLog).filter(
        AuditLog.created_at >= start_date,
        AuditLog.created_at <= end_date
    ).order_by(AuditLog.created_at).all()
    
    if format == "json":
        return {
            "export_info": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_records": len(logs),
                "exported_by": current_user.email,
                "export_timestamp": datetime.utcnow().isoformat()
            },
            "audit_logs": [log.to_dict() for log in logs]
        }
    
    elif format == "csv":
        # For CSV export, you would typically return a file response
        # This is a simplified version returning CSV-like data
        csv_data = []
        if logs:
            # Header
            headers = list(logs[0].to_dict().keys())
            csv_data.append(headers)
            
            # Data rows
            for log in logs:
                row = []
                log_dict = log.to_dict()
                for header in headers:
                    value = log_dict.get(header, "")
                    if isinstance(value, (dict, list)):
                        value = str(value)
                    row.append(str(value) if value is not None else "")
                csv_data.append(row)
        
        return {
            "format": "csv",
            "headers": csv_data[0] if csv_data else [],
            "data": csv_data[1:] if len(csv_data) > 1 else [],
            "total_records": len(logs)
        }


@router.delete("/logs/{log_id}")
async def delete_audit_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    reason: str = Query(..., description="Reason for deletion")
):
    """
    Delete an audit log entry (should be used very rarely)
    
    Requires admin role and logs the deletion action
    """
    
    if current_user.user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found"
        )
    
    # Log the deletion action before deleting
    audit_logger = get_audit_logger()
    audit_logger.log_event(
        db=db,
        event_type=AuditEventType.ADMIN_ACTION,
        event_category="admin",
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.user_role,
        event_description=f"Audit log {log_id} deleted by admin",
        metadata={
            "deleted_log_id": log_id,
            "deleted_log_type": log.event_type,
            "deletion_reason": reason,
            "original_log_data": log.to_dict()
        },
        event_level=AuditLogLevel.WARNING
    )
    
    # Delete the log
    db.delete(log)
    db.commit()
    
    return {
        "message": f"Audit log {log_id} deleted successfully",
        "deleted_by": current_user.email,
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat()
    }
