"""Health Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
import time
import psutil
import sys
from datetime import datetime

from app.dependencies import get_db
from app.database import engine

router = APIRouter()

@router.get("/")
async def health_root():
    return {"message": "health endpoint", "status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@router.get("/status")
async def get_api_status():
    """Get overall API health status"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "python_version": sys.version,
            "uptime": "running"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API health check failed: {str(e)}")

@router.get("/database")
async def get_database_health(db: Session = Depends(get_db)):
    """Check database connectivity and performance"""
    start_time = time.time()
    
    try:
        # Test basic connectivity
        result = db.execute(text("SELECT 1")).fetchone()
        
        # Test a simple query
        db.execute(text("SELECT COUNT(*) FROM users")).fetchone()
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            "status": "healthy",
            "response_time_ms": response_time,
            "timestamp": datetime.utcnow().isoformat(),
            "connection_pool": {
                "size": engine.pool.size(),
                "checked_in": engine.pool.checkedin(),
                "checked_out": engine.pool.checkedout(),
                "overflow": engine.pool.overflow(),
                "invalid": engine.pool.invalid()
            }
        }
    except Exception as e:
        response_time = round((time.time() - start_time) * 1000, 2)
        return {
            "status": "unhealthy",
            "response_time_ms": response_time,
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

@router.get("/performance")
async def get_performance_metrics():
    """Get system performance metrics"""
    try:
        # Get CPU and memory usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": {
                "usage_percent": cpu_percent,
                "count": psutil.cpu_count()
            },
            "memory": {
                "usage_percent": memory.percent,
                "available_mb": round(memory.available / 1024 / 1024, 2),
                "total_mb": round(memory.total / 1024 / 1024, 2)
            },
            "load_average": list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else None
        }
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }
