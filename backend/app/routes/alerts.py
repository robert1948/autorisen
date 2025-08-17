"""
Alert System API Routes for Task 1.3.6
========================================

RESTful API endpoints for alert system management:
- Alert rule management (CRUD)
- Active alert monitoring
- Alert acknowledgment and resolution
- Notification channel configuration
- Alert statistics and history
- Real-time alert streaming
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
import asyncio

from app.database import get_db
from app.core.auth import get_current_user
from app.services.alert_service import (
    get_alert_system, 
    AlertRule, 
    AlertSeverity, 
    AlertType, 
    AlertChannel,
    AlertStatus,
    NotificationChannel
)
from app.services.audit_service import get_audit_logger, AuditEventType


# Pydantic models for API
class AlertRuleCreate(BaseModel):
    name: str
    alert_type: AlertType
    severity: AlertSeverity
    condition: str
    threshold: float
    duration: int
    channels: List[AlertChannel]
    enabled: bool = True
    cooldown: int = 300
    escalation_time: int = 1800
    tags: List[str] = []


class AlertRuleUpdate(BaseModel):
    alert_type: Optional[AlertType] = None
    severity: Optional[AlertSeverity] = None
    condition: Optional[str] = None
    threshold: Optional[float] = None
    duration: Optional[int] = None
    channels: Optional[List[AlertChannel]] = None
    enabled: Optional[bool] = None
    cooldown: Optional[int] = None
    escalation_time: Optional[int] = None
    tags: Optional[List[str]] = None


class NotificationChannelCreate(BaseModel):
    name: str
    channel_type: AlertChannel
    config: Dict[str, Any]
    enabled: bool = True
    rate_limit: int = 60


class NotificationChannelUpdate(BaseModel):
    config: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None
    rate_limit: Optional[int] = None


class AlertAcknowledge(BaseModel):
    acknowledged_by: str


class AlertFilter(BaseModel):
    severity: Optional[AlertSeverity] = None
    alert_type: Optional[AlertType] = None
    status: Optional[AlertStatus] = None
    tags: Optional[List[str]] = None


class ManualAlert(BaseModel):
    rule_name: str
    title: str
    description: str
    source_data: Optional[Dict[str, Any]] = None


# Create router
router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


@router.get("/status", summary="Get alert system status")
async def get_alert_system_status(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get current alert system status and statistics"""
    
    try:
        alert_system = get_alert_system()
        stats = alert_system.get_alert_statistics()
        
        return {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "statistics": stats,
            "monitoring_active": alert_system.monitoring_task is not None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alert system status: {str(e)}")


@router.get("/active", summary="Get active alerts")
async def get_active_alerts(
    severity: Optional[AlertSeverity] = Query(None),
    alert_type: Optional[AlertType] = Query(None),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of active alerts with optional filtering"""
    
    try:
        alert_system = get_alert_system()
        
        # Parse tags
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
        
        alerts = alert_system.get_active_alerts(
            severity=severity,
            alert_type=alert_type,
            tags=tag_list
        )
        
        return {
            "alerts": alerts,
            "count": len(alerts),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active alerts: {str(e)}")


@router.get("/stream", summary="Stream real-time alerts")
async def stream_alerts(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Stream real-time alert updates using Server-Sent Events"""
    
    async def generate_alert_stream():
        """Generate real-time alert updates"""
        alert_system = get_alert_system()
        last_count = 0
        
        while True:
            try:
                # Get current alerts
                alerts = alert_system.get_active_alerts()
                current_count = len(alerts)
                
                # Send update if count changed or every 30 seconds
                if current_count != last_count:
                    data = {
                        "type": "alert_update",
                        "timestamp": datetime.utcnow().isoformat(),
                        "active_count": current_count,
                        "alerts": alerts[-5:] if alerts else []  # Last 5 alerts
                    }
                    
                    yield f"data: {json.dumps(data)}\n\n"
                    last_count = current_count
                
                # Send heartbeat
                heartbeat = {
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat(),
                    "active_count": current_count
                }
                yield f"data: {json.dumps(heartbeat)}\n\n"
                
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                error_data = {
                    "type": "error",
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": str(e)
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                await asyncio.sleep(60)  # Wait longer on error
    
    return StreamingResponse(
        generate_alert_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


@router.post("/{alert_id}/acknowledge", summary="Acknowledge alert")
async def acknowledge_alert(
    alert_id: str,
    acknowledge_data: AlertAcknowledge,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Acknowledge an active alert"""
    
    try:
        alert_system = get_alert_system()
        success = await alert_system.acknowledge_alert(alert_id, acknowledge_data.acknowledged_by)
        
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Log to audit system
        audit_logger = get_audit_logger()
        audit_logger.log_system_event(
            db=db,
            event_type=AuditEventType.ALERT_ACKNOWLEDGED,
            component="alert_system",
            status="acknowledged",
            metadata={
                "alert_id": alert_id,
                "acknowledged_by": acknowledge_data.acknowledged_by
            }
        )
        
        return {
            "message": "Alert acknowledged successfully",
            "alert_id": alert_id,
            "acknowledged_by": acknowledge_data.acknowledged_by,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {str(e)}")


@router.post("/{alert_id}/resolve", summary="Resolve alert")
async def resolve_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Resolve an active alert"""
    
    try:
        alert_system = get_alert_system()
        success = await alert_system.resolve_alert(alert_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Log to audit system
        audit_logger = get_audit_logger()
        audit_logger.log_system_event(
            db=db,
            event_type=AuditEventType.ALERT_RESOLVED,
            component="alert_system",
            status="resolved",
            metadata={
                "alert_id": alert_id,
                "resolved_by": current_user.get("username", "system")
            }
        )
        
        return {
            "message": "Alert resolved successfully",
            "alert_id": alert_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")


@router.post("/manual", summary="Create manual alert")
async def create_manual_alert(
    alert_data: ManualAlert,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a manual alert for testing or custom notifications"""
    
    try:
        alert_system = get_alert_system()
        
        # Create the alert
        alert_id = await alert_system.create_alert(
            rule_name=alert_data.rule_name,
            title=alert_data.title,
            description=alert_data.description,
            source_data=alert_data.source_data or {}
        )
        
        if not alert_id:
            raise HTTPException(status_code=400, detail="Failed to create alert (rule not found or in cooldown)")
        
        # Log to audit system
        audit_logger = get_audit_logger()
        audit_logger.log_system_event(
            db=db,
            event_type=AuditEventType.ALERT_TRIGGERED,
            component="alert_system",
            status="manual",
            metadata={
                "alert_id": alert_id,
                "rule_name": alert_data.rule_name,
                "created_by": current_user.get("username", "unknown"),
                "manual": True
            }
        )
        
        return {
            "message": "Manual alert created successfully",
            "alert_id": alert_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create manual alert: {str(e)}")


# Alert Rules Management
@router.get("/rules", summary="Get alert rules")
async def get_alert_rules(
    enabled_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of alert rules"""
    
    try:
        alert_system = get_alert_system()
        rules = []
        
        for rule_name, rule in alert_system.alert_rules.items():
            if enabled_only and not rule.enabled:
                continue
            
            rule_data = {
                "name": rule.name,
                "alert_type": rule.alert_type.value,
                "severity": rule.severity.value,
                "condition": rule.condition,
                "threshold": rule.threshold,
                "duration": rule.duration,
                "channels": [ch.value for ch in rule.channels],
                "enabled": rule.enabled,
                "cooldown": rule.cooldown,
                "escalation_time": rule.escalation_time,
                "tags": rule.tags
            }
            rules.append(rule_data)
        
        return {
            "rules": rules,
            "count": len(rules),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alert rules: {str(e)}")


@router.post("/rules", summary="Create alert rule")
async def create_alert_rule(
    rule_data: AlertRuleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new alert rule"""
    
    try:
        alert_system = get_alert_system()
        
        # Check if rule already exists
        if rule_data.name in alert_system.alert_rules:
            raise HTTPException(status_code=400, detail="Alert rule with this name already exists")
        
        # Create rule
        rule = AlertRule(
            name=rule_data.name,
            alert_type=rule_data.alert_type,
            severity=rule_data.severity,
            condition=rule_data.condition,
            threshold=rule_data.threshold,
            duration=rule_data.duration,
            channels=rule_data.channels,
            enabled=rule_data.enabled,
            cooldown=rule_data.cooldown,
            escalation_time=rule_data.escalation_time,
            tags=rule_data.tags
        )
        
        alert_system.add_alert_rule(rule)
        
        # Log to audit system
        audit_logger = get_audit_logger()
        audit_logger.log_system_event(
            db=db,
            event_type=AuditEventType.CONFIGURATION_CHANGED,
            component="alert_system",
            status="rule_created",
            metadata={
                "rule_name": rule_data.name,
                "created_by": current_user.get("username", "unknown"),
                "rule_config": rule_data.dict()
            }
        )
        
        return {
            "message": "Alert rule created successfully",
            "rule_name": rule_data.name,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create alert rule: {str(e)}")


@router.put("/rules/{rule_name}", summary="Update alert rule")
async def update_alert_rule(
    rule_name: str,
    rule_updates: AlertRuleUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing alert rule"""
    
    try:
        alert_system = get_alert_system()
        
        if rule_name not in alert_system.alert_rules:
            raise HTTPException(status_code=404, detail="Alert rule not found")
        
        rule = alert_system.alert_rules[rule_name]
        
        # Update fields
        update_data = rule_updates.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)
        
        # Log to audit system
        audit_logger = get_audit_logger()
        audit_logger.log_system_event(
            db=db,
            event_type=AuditEventType.CONFIGURATION_CHANGED,
            component="alert_system",
            status="rule_updated",
            metadata={
                "rule_name": rule_name,
                "updated_by": current_user.get("username", "unknown"),
                "updates": update_data
            }
        )
        
        return {
            "message": "Alert rule updated successfully",
            "rule_name": rule_name,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update alert rule: {str(e)}")


@router.delete("/rules/{rule_name}", summary="Delete alert rule")
async def delete_alert_rule(
    rule_name: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete an alert rule"""
    
    try:
        alert_system = get_alert_system()
        
        if rule_name not in alert_system.alert_rules:
            raise HTTPException(status_code=404, detail="Alert rule not found")
        
        alert_system.remove_alert_rule(rule_name)
        
        # Log to audit system
        audit_logger = get_audit_logger()
        audit_logger.log_system_event(
            db=db,
            event_type=AuditEventType.CONFIGURATION_CHANGED,
            component="alert_system",
            status="rule_deleted",
            metadata={
                "rule_name": rule_name,
                "deleted_by": current_user.get("username", "unknown")
            }
        )
        
        return {
            "message": "Alert rule deleted successfully",
            "rule_name": rule_name,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete alert rule: {str(e)}")


# Notification Channels Management
@router.get("/channels", summary="Get notification channels")
async def get_notification_channels(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of notification channels"""
    
    try:
        alert_system = get_alert_system()
        channels = []
        
        for channel_name, channel in alert_system.notification_channels.items():
            # Don't expose sensitive config data
            safe_config = {k: v for k, v in channel.config.items() if "password" not in k.lower() and "token" not in k.lower()}
            
            channel_data = {
                "name": channel.name,
                "channel_type": channel.channel_type.value,
                "config": safe_config,
                "enabled": channel.enabled,
                "rate_limit": channel.rate_limit
            }
            channels.append(channel_data)
        
        return {
            "channels": channels,
            "count": len(channels),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get notification channels: {str(e)}")


@router.post("/channels", summary="Create notification channel")
async def create_notification_channel(
    channel_data: NotificationChannelCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new notification channel"""
    
    try:
        alert_system = get_alert_system()
        
        # Check if channel already exists
        if channel_data.name in alert_system.notification_channels:
            raise HTTPException(status_code=400, detail="Notification channel with this name already exists")
        
        # Create channel
        channel = NotificationChannel(
            name=channel_data.name,
            channel_type=channel_data.channel_type,
            config=channel_data.config,
            enabled=channel_data.enabled,
            rate_limit=channel_data.rate_limit
        )
        
        alert_system.add_notification_channel(channel)
        
        # Log to audit system (without sensitive config)
        safe_config = {k: v for k, v in channel_data.config.items() if "password" not in k.lower() and "token" not in k.lower()}
        audit_logger = get_audit_logger()
        audit_logger.log_system_event(
            db=db,
            event_type=AuditEventType.CONFIGURATION_CHANGED,
            component="alert_system",
            status="channel_created",
            metadata={
                "channel_name": channel_data.name,
                "channel_type": channel_data.channel_type.value,
                "created_by": current_user.get("username", "unknown"),
                "config": safe_config
            }
        )
        
        return {
            "message": "Notification channel created successfully",
            "channel_name": channel_data.name,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create notification channel: {str(e)}")


@router.get("/statistics", summary="Get alert statistics")
async def get_alert_statistics(
    include_history: bool = Query(False),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get comprehensive alert system statistics"""
    
    try:
        alert_system = get_alert_system()
        stats = alert_system.get_alert_statistics()
        
        # Add additional statistics if requested
        if include_history:
            # Get recent alert trends
            recent_alerts = []
            for alert in list(alert_system.alert_history)[-50:]:  # Last 50 alerts
                alert_data = {
                    "id": alert.id,
                    "rule_name": alert.rule_name,
                    "severity": alert.severity.value,
                    "alert_type": alert.alert_type.value,
                    "timestamp": alert.timestamp.isoformat(),
                    "status": alert.status.value
                }
                recent_alerts.append(alert_data)
            
            stats["recent_history"] = recent_alerts
        
        return {
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alert statistics: {str(e)}")


@router.post("/test/{channel_name}", summary="Test notification channel")
async def test_notification_channel(
    channel_name: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Send a test notification through the specified channel"""
    
    try:
        alert_system = get_alert_system()
        
        if channel_name not in alert_system.notification_channels:
            raise HTTPException(status_code=404, detail="Notification channel not found")
        
        channel = alert_system.notification_channels[channel_name]
        
        # Create a test alert
        from app.services.alert_service import Alert
        test_alert = Alert(
            id=f"test_{int(datetime.utcnow().timestamp())}",
            rule_name="test_rule",
            alert_type=AlertType.CUSTOM,
            severity=AlertSeverity.INFO,
            title="Test Notification",
            description=f"This is a test notification sent through the {channel_name} channel.",
            timestamp=datetime.utcnow(),
            source_data={"test": True, "triggered_by": current_user.get("username", "unknown")}
        )
        
        # Send test notification
        success = await alert_system._send_notification(test_alert, channel)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to send test notification")
        
        return {
            "message": f"Test notification sent successfully via {channel_name}",
            "channel_name": channel_name,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test notification channel: {str(e)}")


# Export router
__all__ = ["router"]
