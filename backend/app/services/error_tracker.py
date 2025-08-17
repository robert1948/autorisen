"""
Error tracking service for CapeControl API
Professional error monitoring and alerting system
"""

import logging
import traceback
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import json
import os

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"  
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories for classification"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    DATABASE = "database"
    EXTERNAL_API = "external_api"
    SYSTEM = "system"
    NETWORK = "network"
    UNKNOWN = "unknown"

class ErrorTracker:
    """Professional error tracking and monitoring"""
    
    def __init__(self):
        self.errors = []
        self.error_counts = {}
        self.is_enabled = True
        
    def track_error(
        self, 
        error: Exception, 
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> str:
        """Track an error with full context"""
        try:
            error_id = f"err_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{id(error)}"
            
            error_data = {
                "error_id": error_id,
                "timestamp": datetime.utcnow().isoformat(),
                "error_type": type(error).__name__,
                "message": str(error),
                "severity": severity.value,
                "category": category.value,
                "traceback": traceback.format_exc(),
                "context": context or {},
                "user_id": user_id
            }
            
            # Store error
            self.errors.append(error_data)
            
            # Update counts
            error_key = f"{category.value}_{type(error).__name__}"
            self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
            
            # Log error
            log_level = {
                ErrorSeverity.LOW: logging.INFO,
                ErrorSeverity.MEDIUM: logging.WARNING,
                ErrorSeverity.HIGH: logging.ERROR,
                ErrorSeverity.CRITICAL: logging.CRITICAL
            }.get(severity, logging.ERROR)
            
            logger.log(log_level, f"Error tracked: {error_id} - {error}")
            
            return error_id
            
        except Exception as e:
            logger.error(f"Failed to track error: {e}")
            return "error_tracking_failed"
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        return {
            "total_errors": len(self.errors),
            "error_counts": self.error_counts.copy(),
            "recent_errors": self.errors[-10:] if self.errors else [],
            "is_enabled": self.is_enabled
        }
    
    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[Dict[str, Any]]:
        """Get errors by severity level"""
        return [error for error in self.errors if error.get("severity") == severity.value]
    
    def clear_errors(self) -> int:
        """Clear all tracked errors and return count"""
        count = len(self.errors)
        self.errors.clear()
        self.error_counts.clear()
        logger.info(f"Cleared {count} tracked errors")
        return count

# Global error tracker instance
_global_error_tracker = ErrorTracker()

def get_error_tracker() -> ErrorTracker:
    """
    Get the global error tracker instance
    This is the main function that alert_service.py imports
    """
    return _global_error_tracker

def track_error(
    error: Exception,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None
) -> str:
    """Convenience function to track an error"""
    return get_error_tracker().track_error(error, severity, category, context, user_id)

def get_error_stats() -> Dict[str, Any]:
    """Convenience function to get error statistics"""
    return get_error_tracker().get_error_stats()

# Additional utility functions
def handle_api_error(error: Exception, endpoint: str, user_id: Optional[str] = None) -> str:
    """Handle API-specific errors"""
    context = {"endpoint": endpoint, "error_source": "api"}
    return track_error(error, ErrorSeverity.HIGH, ErrorCategory.SYSTEM, context, user_id)

def handle_auth_error(error: Exception, user_id: Optional[str] = None) -> str:
    """Handle authentication-specific errors"""
    return track_error(error, ErrorSeverity.HIGH, ErrorCategory.AUTHENTICATION, user_id=user_id)

def handle_db_error(error: Exception, operation: str, user_id: Optional[str] = None) -> str:
    """Handle database-specific errors"""
    context = {"operation": operation, "error_source": "database"}
    return track_error(error, ErrorSeverity.CRITICAL, ErrorCategory.DATABASE, context, user_id)

# Export all required functions and classes
__all__ = [
    "get_error_tracker",
    "ErrorSeverity", 
    "ErrorCategory",
    "ErrorTracker",
    "track_error",
    "get_error_stats",
    "handle_api_error",
    "handle_auth_error", 
    "handle_db_error"
]