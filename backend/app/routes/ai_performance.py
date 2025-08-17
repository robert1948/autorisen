"""
AI Performance Metrics API Routes for Task 1.3.2
=================================================

RESTful API endpoints for AI performance monitoring:
- Real-time AI metrics and statistics
- Cost analytics and usage tracking
- Performance optimization recommendations
- AI service health monitoring
- Usage pattern analysis
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
import asyncio

from app.database import get_db
from app.core.auth import get_current_user
from app.services.ai_performance_service import (
    get_ai_performance_monitor,
    AIModelType,
    PerformanceMetric
)
from app.services.audit_service import get_audit_logger, AuditEventType


# Pydantic models for API
class AIMetricsQuery(BaseModel):
    provider: Optional[AIModelType] = None
    model: Optional[str] = None
    time_period: str = "1h"
    metric_types: Optional[List[PerformanceMetric]] = None


class AIUsageRecord(BaseModel):
    provider: AIModelType
    model: str
    endpoint: str
    prompt_tokens: int
    completion_tokens: int
    response_time_ms: int
    success: bool
    user_id: Optional[str] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    response_length: int = 0
    quality_score: Optional[float] = None


class CostAnalyticsQuery(BaseModel):
    time_period: str = "24h"
    group_by: str = "provider"  # provider, model, user
    include_breakdown: bool = True


# Create router
router = APIRouter(prefix="/api/v1/ai-performance", tags=["ai-performance"])


@router.get("/status", summary="Get AI performance system status")
async def get_ai_performance_status(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get current AI performance monitoring system status"""
    
    try:
        monitor = get_ai_performance_monitor()
        health_status = monitor.get_health_status()
        
        return {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "ai_service_health": health_status,
            "monitoring_active": True,
            "supported_providers": [provider.value for provider in AIModelType],
            "cost_tracking_enabled": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get AI performance status: {str(e)}")


@router.get("/metrics/real-time", summary="Get real-time AI metrics")
async def get_real_time_ai_metrics(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get real-time AI performance metrics"""
    
    try:
        monitor = get_ai_performance_monitor()
        metrics = monitor.get_real_time_metrics()
        
        return {
            "real_time_metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get real-time metrics: {str(e)}")


@router.get("/metrics/performance", summary="Get AI performance statistics")
async def get_ai_performance_statistics(
    provider: Optional[AIModelType] = Query(None),
    model: Optional[str] = Query(None),
    time_period: str = Query("1h", regex="^(\\d+[mhd]|1h|24h|7d)$"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get detailed AI performance statistics"""
    
    try:
        monitor = get_ai_performance_monitor()
        stats = monitor.get_performance_stats(
            provider=provider,
            model=model,
            time_period=time_period
        )
        
        return {
            "performance_stats": stats,
            "time_period": time_period,
            "filters": {
                "provider": provider.value if provider else None,
                "model": model
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance statistics: {str(e)}")


@router.get("/metrics/costs", summary="Get AI cost analytics")
async def get_ai_cost_analytics(
    time_period: str = Query("24h", regex="^(\\d+[mhd]|1h|24h|7d|30d)$"),
    include_breakdown: bool = Query(True),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get detailed AI cost analytics and breakdown"""
    
    try:
        monitor = get_ai_performance_monitor()
        cost_analytics = monitor.get_cost_analytics(time_period=time_period)
        
        return {
            "cost_analytics": cost_analytics,
            "time_period": time_period,
            "include_breakdown": include_breakdown,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cost analytics: {str(e)}")


@router.get("/metrics/usage-patterns", summary="Get AI usage patterns")
async def get_ai_usage_patterns(
    time_period: str = Query("24h", regex="^(\\d+[mhd]|1h|24h|7d)$"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Analyze AI usage patterns and trends"""
    
    try:
        monitor = get_ai_performance_monitor()
        patterns = monitor.get_usage_patterns(time_period=time_period)
        
        return {
            "usage_patterns": patterns,
            "time_period": time_period,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get usage patterns: {str(e)}")


@router.get("/health", summary="Get AI services health status")
async def get_ai_services_health(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get comprehensive AI services health status"""
    
    try:
        monitor = get_ai_performance_monitor()
        health_status = monitor.get_health_status()
        
        return {
            "health_status": health_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get AI health status: {str(e)}")


@router.get("/optimization/recommendations", summary="Get AI optimization recommendations")
async def get_ai_optimization_recommendations(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get AI performance optimization recommendations"""
    
    try:
        monitor = get_ai_performance_monitor()
        recommendations = monitor.get_optimization_recommendations()
        
        return {
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "critical_issues": len([r for r in recommendations if r["priority"] == "critical"]),
            "high_priority_issues": len([r for r in recommendations if r["priority"] == "high"]),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get optimization recommendations: {str(e)}")


@router.post("/metrics/record", summary="Record AI usage metrics")
async def record_ai_usage_metrics(
    usage_data: AIUsageRecord,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Record AI service usage metrics (for integration purposes)"""
    
    try:
        monitor = get_ai_performance_monitor()
        
        metrics_id = monitor.record_ai_request(
            provider=usage_data.provider,
            model=usage_data.model,
            endpoint=usage_data.endpoint,
            prompt_tokens=usage_data.prompt_tokens,
            completion_tokens=usage_data.completion_tokens,
            response_time_ms=usage_data.response_time_ms,
            success=usage_data.success,
            user_id=usage_data.user_id,
            error_type=usage_data.error_type,
            error_message=usage_data.error_message,
            response_length=usage_data.response_length,
            quality_score=usage_data.quality_score
        )
        
        return {
            "message": "AI usage metrics recorded successfully",
            "metrics_id": metrics_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record AI metrics: {str(e)}")


@router.get("/stream/metrics", summary="Stream real-time AI metrics")
async def stream_ai_metrics(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Stream real-time AI performance metrics using Server-Sent Events"""
    
    async def generate_metrics_stream():
        """Generate real-time AI metrics updates"""
        monitor = get_ai_performance_monitor()
        
        while True:
            try:
                # Get current metrics
                real_time_metrics = monitor.get_real_time_metrics()
                health_status = monitor.get_health_status()
                
                # Send metrics update
                data = {
                    "type": "metrics_update",
                    "timestamp": datetime.utcnow().isoformat(),
                    "metrics": real_time_metrics,
                    "health": health_status
                }
                
                yield f"data: {json.dumps(data)}\n\n"
                
                # Send heartbeat every 30 seconds
                await asyncio.sleep(30)
                
            except Exception as e:
                error_data = {
                    "type": "error",
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": str(e)
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                await asyncio.sleep(60)  # Wait longer on error
    
    return StreamingResponse(
        generate_metrics_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


@router.get("/providers", summary="Get supported AI providers")
async def get_supported_ai_providers(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of supported AI providers and their configurations"""
    
    try:
        monitor = get_ai_performance_monitor()
        
        providers_info = []
        for provider in AIModelType:
            config = monitor.ai_configs.get(provider.value, {})
            cost_models = monitor.cost_models.get(provider.value, {})
            
            providers_info.append({
                "provider": provider.value,
                "configured": bool(config.get("api_key")),
                "base_url": config.get("base_url", ""),
                "supported_models": list(cost_models.keys()),
                "cost_tracking": len(cost_models) > 0
            })
        
        return {
            "providers": providers_info,
            "total_providers": len(providers_info),
            "configured_providers": len([p for p in providers_info if p["configured"]]),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get provider information: {str(e)}")


@router.get("/models/{provider}", summary="Get AI models for provider")
async def get_ai_models_for_provider(
    provider: AIModelType,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get available AI models for a specific provider"""
    
    try:
        monitor = get_ai_performance_monitor()
        cost_models = monitor.cost_models.get(provider.value, {})
        
        models_info = []
        for model_name, cost_config in cost_models.items():
            models_info.append({
                "model": model_name,
                "provider": provider.value,
                "prompt_cost_per_1k": cost_config.get("prompt_cost_per_1k", 0),
                "completion_cost_per_1k": cost_config.get("completion_cost_per_1k", 0),
                "cost_tracking": True
            })
        
        return {
            "provider": provider.value,
            "models": models_info,
            "total_models": len(models_info),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get models for provider: {str(e)}")


@router.get("/analytics/summary", summary="Get AI analytics summary")
async def get_ai_analytics_summary(
    time_period: str = Query("24h", regex="^(\\d+[mhd]|1h|24h|7d|30d)$"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get comprehensive AI analytics summary"""
    
    try:
        monitor = get_ai_performance_monitor()
        
        # Get all analytics data
        performance_stats = monitor.get_performance_stats(time_period=time_period)
        cost_analytics = monitor.get_cost_analytics(time_period=time_period)
        usage_patterns = monitor.get_usage_patterns(time_period=time_period)
        health_status = monitor.get_health_status()
        recommendations = monitor.get_optimization_recommendations()
        
        # Calculate summary metrics
        total_requests = sum(stats.total_requests for stats in performance_stats.values())
        total_cost = cost_analytics.get("total_cost", 0)
        avg_success_rate = (
            sum(stats.success_rate for stats in performance_stats.values()) / 
            len(performance_stats)
        ) if performance_stats else 0
        
        return {
            "summary": {
                "time_period": time_period,
                "total_requests": total_requests,
                "total_cost": total_cost,
                "avg_success_rate": avg_success_rate,
                "unique_users": usage_patterns.get("unique_users", 0),
                "active_providers": len(set(
                    stats.provider.value for stats in performance_stats.values()
                )),
                "health_status": health_status.get("status", "unknown"),
                "critical_issues": len([
                    r for r in recommendations if r["priority"] == "critical"
                ])
            },
            "performance_overview": performance_stats,
            "cost_overview": cost_analytics,
            "usage_overview": usage_patterns,
            "health_overview": health_status,
            "recommendations_count": len(recommendations),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics summary: {str(e)}")


@router.get("/debug/metrics-history", summary="Get AI metrics history for debugging")
async def get_ai_metrics_history(
    limit: int = Query(100, ge=1, le=1000),
    provider: Optional[AIModelType] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get recent AI metrics history for debugging purposes"""
    
    try:
        monitor = get_ai_performance_monitor()
        
        # Get recent metrics
        metrics_list = list(monitor.metrics_history)
        
        # Filter by provider if specified
        if provider:
            metrics_list = [m for m in metrics_list if m.provider == provider]
        
        # Limit results
        metrics_list = metrics_list[-limit:]
        
        # Convert to dict format for JSON serialization
        metrics_data = []
        for metric in metrics_list:
            metrics_data.append({
                "timestamp": metric.timestamp.isoformat(),
                "provider": metric.provider.value,
                "model": metric.model,
                "endpoint": metric.endpoint,
                "success": metric.success,
                "response_time_ms": metric.response_time_ms,
                "total_tokens": metric.total_tokens,
                "estimated_cost": metric.estimated_cost,
                "error_type": metric.error_type
            })
        
        return {
            "metrics_history": metrics_data,
            "total_metrics": len(metrics_data),
            "filter_provider": provider.value if provider else None,
            "limit": limit,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics history: {str(e)}")


# Export router
__all__ = ["router"]
