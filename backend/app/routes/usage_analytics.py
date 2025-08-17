"""
Usage Analytics Enhancement API Routes
Provides detailed usage tracking and analytics for user behavior analysis
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, validator
from datetime import datetime, timedelta
import logging

from ..database import get_db
from ..auth.auth_enhanced import get_current_user
from ..models.user import User

logger = logging.getLogger(__name__)

# Pydantic models for request/response
class EventTrackingRequest(BaseModel):
    event_type: str
    event_name: str
    event_data: Dict[str, Any] = {}
    session_id: Optional[str] = None
    page_url: Optional[str] = None
    user_agent: Optional[str] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        allowed_types = ['page_view', 'user_action', 'ai_interaction', 'feature_usage', 'error', 'performance']
        if v not in allowed_types:
            raise ValueError(f'event_type must be one of: {allowed_types}')
        return v

class BulkEventTrackingRequest(BaseModel):
    events: List[EventTrackingRequest]
    session_id: Optional[str] = None

class AnalyticsQuery(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    event_types: Optional[List[str]] = None
    group_by: Optional[str] = "day"  # day, hour, week, month
    
    @validator('group_by')
    def validate_group_by(cls, v):
        allowed_values = ['hour', 'day', 'week', 'month']
        if v not in allowed_values:
            raise ValueError(f'group_by must be one of: {allowed_values}')
        return v

router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["usage-analytics"],
    responses={404: {"description": "Not found"}}
)

# Initialize analytics service - will be injected via dependency
def get_analytics_service(db: Session = Depends(get_db)):
    """Get analytics service instance"""
    try:
        # Import here to avoid circular imports
        from ..services.usage_analytics_enhancement import UsageAnalyticsService
        import redis
        
        # Initialize Redis client
        redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        return UsageAnalyticsService(db, redis_client)
    except Exception as e:
        logger.error(f"Failed to initialize analytics service: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analytics service unavailable"
        )

@router.post("/track")
async def track_event(
    event: EventTrackingRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    analytics_service = Depends(get_analytics_service)
):
    """
    Track a single analytics event
    
    - **event_type**: Type of event (page_view, user_action, ai_interaction, etc.)
    - **event_name**: Specific name of the event
    - **event_data**: Additional event metadata
    - **session_id**: Optional session identifier
    - **page_url**: URL where event occurred
    - **user_agent**: User's browser information
    """
    try:
        # Track the event
        event_id = await analytics_service.track_event(
            user_id=current_user.id,
            event_type=event.event_type,
            event_name=event.event_name,
            event_data=event.event_data,
            session_id=event.session_id or "",
            page_url=event.page_url,
            user_agent=event.user_agent
        )
        
        # Background task: Process analytics in real-time
        background_tasks.add_task(
            process_real_time_analytics,
            current_user.id,
            event.event_type,
            event.event_name
        )
        
        return {
            "success": True,
            "event_id": event_id,
            "user_id": current_user.id,
            "event_type": event.event_type,
            "event_name": event.event_name,
            "tracked_at": datetime.utcnow().isoformat(),
            "message": "Event tracked successfully"
        }
    except Exception as e:
        logger.error(f"Error tracking event for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track event: {str(e)}"
        )

@router.post("/track/bulk")
async def track_bulk_events(
    bulk_request: BulkEventTrackingRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    analytics_service = Depends(get_analytics_service)
):
    """
    Track multiple analytics events in a single request
    
    - **events**: List of events to track
    - **session_id**: Common session ID for all events (optional)
    """
    try:
        if not bulk_request.events:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No events provided"
            )
        
        if len(bulk_request.events) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 100 events per bulk request"
            )
        
        results = []
        successful_tracks = 0
        
        for event in bulk_request.events:
            try:
                event_id = await analytics_service.track_event(
                    user_id=current_user.id,
                    event_type=event.event_type,
                    event_name=event.event_name,
                    event_data=event.event_data,
                    session_id=event.session_id or bulk_request.session_id or "",
                    page_url=event.page_url,
                    user_agent=event.user_agent
                )
                
                results.append({
                    "success": True,
                    "event_id": event_id,
                    "event_type": event.event_type,
                    "event_name": event.event_name
                })
                successful_tracks += 1
                
            except Exception as event_error:
                logger.error(f"Error tracking individual event: {event_error}")
                results.append({
                    "success": False,
                    "error": str(event_error),
                    "event_type": event.event_type,
                    "event_name": event.event_name
                })
        
        # Background task: Process bulk analytics
        background_tasks.add_task(
            process_bulk_analytics,
            current_user.id,
            successful_tracks,
            len(bulk_request.events)
        )
        
        return {
            "success": successful_tracks > 0,
            "user_id": current_user.id,
            "results": results,
            "summary": {
                "total_events": len(bulk_request.events),
                "successful_tracks": successful_tracks,
                "failed_tracks": len(bulk_request.events) - successful_tracks,
                "success_rate": f"{(successful_tracks/len(bulk_request.events)*100):.1f}%"
            },
            "tracked_at": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk event tracking for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track bulk events: {str(e)}"
        )

@router.get("/summary")
async def get_analytics_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    analytics_service = Depends(get_analytics_service)
):
    """
    Get user analytics summary for specified time period
    
    - **days**: Number of days to analyze (1-365, default: 30)
    - Returns comprehensive usage statistics
    """
    try:
        summary = await analytics_service.get_user_analytics_summary(current_user.id, days)
        
        return {
            "success": True,
            "user_id": current_user.id,
            "analysis_period": {
                "days": days,
                "start_date": (datetime.utcnow() - timedelta(days=days)).isoformat(),
                "end_date": datetime.utcnow().isoformat()
            },
            "summary": summary,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting analytics summary for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate analytics summary: {str(e)}"
        )

@router.get("/detailed")
async def get_detailed_analytics(
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis"),
    event_types: Optional[str] = Query(None, description="Comma-separated event types to filter"),
    group_by: str = Query("day", description="Group results by: hour, day, week, month"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    current_user: User = Depends(get_current_user),
    analytics_service = Depends(get_analytics_service)
):
    """
    Get detailed analytics with filtering and grouping options
    
    - **start_date**: Start date for analysis (ISO format)
    - **end_date**: End date for analysis (ISO format)
    - **event_types**: Comma-separated list of event types to include
    - **group_by**: How to group results (hour, day, week, month)
    - **limit**: Maximum number of results to return
    """
    try:
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Parse event types filter
        event_types_list = None
        if event_types:
            event_types_list = [t.strip() for t in event_types.split(',')]
        
        # Create query object
        query = AnalyticsQuery(
            start_date=start_date,
            end_date=end_date,
            event_types=event_types_list,
            group_by=group_by
        )
        
        detailed_analytics = await analytics_service.get_detailed_analytics(
            current_user.id,
            query.start_date,
            query.end_date,
            query.event_types,
            query.group_by,
            limit
        )
        
        return {
            "success": True,
            "user_id": current_user.id,
            "query_parameters": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "event_types_filter": event_types_list,
                "group_by": group_by,
                "limit": limit
            },
            "analytics": detailed_analytics,
            "result_count": len(detailed_analytics.get("data", [])),
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting detailed analytics for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate detailed analytics: {str(e)}"
        )

@router.get("/patterns")
async def get_usage_patterns(
    current_user: User = Depends(get_current_user),
    analytics_service = Depends(get_analytics_service)
):
    """
    Get usage patterns and insights for the current user
    
    - Analyzes user behavior patterns
    - Identifies peak usage times
    - Provides personalization insights
    """
    try:
        patterns = await analytics_service.analyze_usage_patterns(current_user.id)
        
        return {
            "success": True,
            "user_id": current_user.id,
            "patterns": patterns,
            "insights": {
                "most_active_time": patterns.get("peak_usage_hour", "Unknown"),
                "most_used_features": patterns.get("top_features", []),
                "session_patterns": patterns.get("session_analytics", {}),
                "ai_interaction_patterns": patterns.get("ai_patterns", {})
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error analyzing usage patterns for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze usage patterns: {str(e)}"
        )

@router.get("/sessions")
async def get_session_analytics(
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    analytics_service = Depends(get_analytics_service)
):
    """
    Get session-based analytics
    
    - **days**: Number of days to analyze (1-30, default: 7)
    - Returns session duration, frequency, and patterns
    """
    try:
        session_analytics = await analytics_service.get_session_analytics(current_user.id, days)
        
        return {
            "success": True,
            "user_id": current_user.id,
            "analysis_period": {
                "days": days,
                "start_date": (datetime.utcnow() - timedelta(days=days)).isoformat(),
                "end_date": datetime.utcnow().isoformat()
            },
            "session_analytics": session_analytics,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting session analytics for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate session analytics: {str(e)}"
        )

@router.get("/performance")
async def get_performance_metrics(
    current_user: User = Depends(get_current_user),
    analytics_service = Depends(get_analytics_service)
):
    """
    Get performance-related analytics
    
    - Page load times
    - API response times
    - Error rates
    - User experience metrics
    """
    try:
        performance_metrics = await analytics_service.get_performance_metrics(current_user.id)
        
        return {
            "success": True,
            "user_id": current_user.id,
            "performance_metrics": performance_metrics,
            "recommendations": {
                "optimization_suggestions": performance_metrics.get("suggestions", []),
                "performance_score": performance_metrics.get("overall_score", "Unknown"),
                "critical_issues": performance_metrics.get("critical_issues", [])
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting performance metrics for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate performance metrics: {str(e)}"
        )

@router.delete("/data")
async def delete_analytics_data(
    confirm: bool = Query(False, description="Confirmation required to delete data"),
    days_to_keep: int = Query(0, ge=0, le=365, description="Days of data to keep (0 = delete all)"),
    current_user: User = Depends(get_current_user),
    analytics_service = Depends(get_analytics_service)
):
    """
    Delete user analytics data (GDPR compliance)
    
    - **confirm**: Must be true to proceed with deletion
    - **days_to_keep**: Number of recent days to preserve (0 = delete all)
    """
    try:
        if not confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Confirmation required to delete analytics data. Set confirm=true"
            )
        
        deleted_count = await analytics_service.delete_user_analytics_data(
            current_user.id,
            days_to_keep
        )
        
        return {
            "success": True,
            "user_id": current_user.id,
            "deleted_records": deleted_count,
            "days_kept": days_to_keep,
            "message": f"Analytics data deleted successfully. Kept {days_to_keep} days of recent data.",
            "deleted_at": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting analytics data for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete analytics data: {str(e)}"
        )

@router.get("/health")
async def analytics_service_health(
    analytics_service = Depends(get_analytics_service)
):
    """Health check for usage analytics service"""
    try:
        # Test basic functionality
        health_info = await analytics_service.get_service_health()
        
        return {
            "service": "usage_analytics",
            "status": "healthy",
            "version": "1.0.0",
            "features": {
                "event_tracking": "available",
                "bulk_tracking": "available",
                "analytics_summary": "available",
                "detailed_analytics": "available",
                "pattern_analysis": "available",
                "session_analytics": "available",
                "performance_metrics": "available",
                "data_deletion": "available"
            },
            "statistics": health_info,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "service": "usage_analytics",
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Background task functions
async def process_real_time_analytics(user_id: str, event_type: str, event_name: str):
    """Process real-time analytics for immediate insights"""
    try:
        logger.info(f"Processing real-time analytics for user {user_id}: {event_type}.{event_name}")
        # Add real-time processing logic here
    except Exception as e:
        logger.error(f"Failed to process real-time analytics: {e}")

async def process_bulk_analytics(user_id: str, successful_tracks: int, total_events: int):
    """Process bulk analytics for batch insights"""
    try:
        logger.info(f"Processed bulk analytics for user {user_id}: {successful_tracks}/{total_events} events")
        # Add bulk processing logic here
    except Exception as e:
        logger.error(f"Failed to process bulk analytics: {e}")