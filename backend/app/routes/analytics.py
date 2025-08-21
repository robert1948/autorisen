"""
Analytics API Routes for Performance Dashboard
Provides endpoints for system metrics, user analytics, and performance data.
"""
import logging
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.routes.auth_v2 import get_current_user
from app.services.analytics_service import analytics_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/dashboard", summary="Get comprehensive dashboard data")
async def get_analytics_dashboard(
    hours: int = Query(24, ge=1, le=168, description="Hours of data to retrieve (1-168)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """
    Get comprehensive analytics dashboard data including:
    - System performance metrics
    - User activity statistics
    - API usage metrics
    - Performance trends
    """
    try:
        # Check if user has analytics access (admin or developer)
        if current_user.role not in ['ADMIN', 'DEVELOPER']:
            raise HTTPException(status_code=403, detail="Analytics access requires admin or developer role")
        
        dashboard_data = await analytics_service.get_dashboard_data(db, hours)
        
        return {
            "status": "success",
            "data": dashboard_data,
            "user": {
                "id": str(current_user.id),
                "role": current_user.role,
                "email": current_user.email
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analytics dashboard: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/metrics/realtime", summary="Get real-time system metrics")
async def get_realtime_metrics(
    current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    """
    Get real-time system performance metrics without database queries.
    Updates every few seconds for live monitoring.
    """
    try:
        # Check analytics access
        if current_user.role not in ['ADMIN', 'DEVELOPER']:
            raise HTTPException(status_code=403, detail="Analytics access requires admin or developer role")
        
        metrics = await analytics_service.get_real_time_metrics()
        
        return {
            "status": "success",
            "data": metrics,
            "user_role": current_user.role
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting real-time metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/system/performance", summary="Get system performance history")
async def get_system_performance(
    hours: int = Query(24, ge=1, le=168),
    metric_type: str | None = Query(None, description="Filter by metric type (cpu_usage, memory_usage, etc.)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Get historical system performance data"""
    try:
        if current_user.role not in ['ADMIN', 'DEVELOPER']:
            raise HTTPException(status_code=403, detail="Analytics access requires admin or developer role")
        
        from sqlalchemy import desc

        from app.models.analytics import SystemMetrics
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        query = db.query(SystemMetrics).filter(
            SystemMetrics.recorded_at >= cutoff_time
        )
        
        if metric_type:
            query = query.filter(SystemMetrics.metric_type == metric_type)
        
        metrics = query.order_by(desc(SystemMetrics.recorded_at)).limit(1000).all()
        
        performance_data = [
            {
                "metric_type": m.metric_type,
                "value": m.metric_value,
                "unit": m.metric_unit,
                "timestamp": m.recorded_at.isoformat(),
                "source": m.source
            }
            for m in metrics
        ]
        
        return {
            "status": "success",
            "data": performance_data,
            "period_hours": hours,
            "metric_type_filter": metric_type,
            "total_records": len(performance_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting system performance: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/users/activity", summary="Get user activity analytics")
async def get_user_activity(
    hours: int = Query(24, ge=1, le=168),
    event_type: str | None = Query(None, description="Filter by event type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Get user activity and behavior analytics"""
    try:
        if current_user.role != 'ADMIN':
            raise HTTPException(status_code=403, detail="User activity analytics requires admin role")
        
        from sqlalchemy import desc, func

        from app.models.analytics import AnalyticsEvent
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Base query
        base_query = db.query(AnalyticsEvent).filter(
            AnalyticsEvent.created_at >= cutoff_time
        )
        
        if event_type:
            base_query = base_query.filter(AnalyticsEvent.event_type == event_type)
        
        # Event distribution by type
        event_distribution = db.query(
            AnalyticsEvent.event_type,
            func.count(AnalyticsEvent.id).label('count')
        ).filter(
            AnalyticsEvent.created_at >= cutoff_time
        ).group_by(AnalyticsEvent.event_type).order_by(desc('count')).all()
        
        # Unique users
        unique_users = base_query.filter(
            AnalyticsEvent.user_id.isnot(None)
        ).distinct(AnalyticsEvent.user_id).count()
        
        # Recent events
        recent_events = base_query.order_by(desc(AnalyticsEvent.created_at)).limit(50).all()
        
        return {
            "status": "success",
            "data": {
                "event_distribution": [
                    {"event_type": event_type, "count": count}
                    for event_type, count in event_distribution
                ],
                "unique_users": unique_users,
                "total_events": base_query.count(),
                "recent_events": [
                    {
                        "event_type": e.event_type,
                        "event_category": e.event_category,
                        "user_id": str(e.user_id) if e.user_id else None,
                        "endpoint": e.endpoint,
                        "status_code": e.status_code,
                        "duration_ms": e.duration_ms,
                        "timestamp": e.created_at.isoformat()
                    }
                    for e in recent_events
                ]
            },
            "period_hours": hours,
            "event_type_filter": event_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user activity: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/record/event", summary="Record a custom analytics event")
async def record_custom_event(
    event_data: dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Record a custom analytics event for tracking specific user actions"""
    try:
        required_fields = ['event_type', 'event_category']
        for field in required_fields:
            if field not in event_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        await analytics_service.record_user_event(
            db=db,
            user_id=str(current_user.id),
            event_type=event_data['event_type'],
            event_category=event_data['event_category'],
            event_data=event_data.get('additional_data'),
            endpoint=event_data.get('endpoint'),
            method=event_data.get('method'),
            status_code=event_data.get('status_code'),
            duration_ms=event_data.get('duration_ms')
        )
        
        return {
            "status": "success",
            "message": "Event recorded successfully",
            "event_type": event_data['event_type'],
            "user_id": str(current_user.id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording custom event: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health", summary="Analytics service health check")
async def analytics_health():
    """Health check endpoint for analytics service"""
    try:
        real_time_data = await analytics_service.get_real_time_metrics()
        
        return {
            "status": "healthy",
            "service": "analytics",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": real_time_data.get('uptime_seconds', 0),
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Analytics health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "analytics",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
