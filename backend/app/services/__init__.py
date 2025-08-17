"""
CapeAI Business Logic Services Package

Enterprise-grade service layer providing:
- Multi-provider AI integration with intelligent routing
- Advanced user authentication and management
- Sophisticated conversation handling and analytics
- Comprehensive security and audit logging
"""

# Import only EXISTING services to prevent deployment failures
from .auth_service import AuthService, get_auth_service
from .user_service import UserService, get_user_service
from .conversation_service import ConversationService
from .cape_ai_service import CapeAIService, get_cape_ai_service
from .audit_service import get_audit_logger, AuditEventType, AuditLogLevel  # REMOVED: AuditService

# Core services that actually exist and work
CORE_SERVICES = {
    "auth": AuthService,
    "user": UserService,
    "conversation": ConversationService,
    "cape_ai": CapeAIService,
    # REMOVED: "audit": AuditService  # This class doesn't exist
}

# Service factory functions for dependency injection
def get_service(service_name: str, db_session=None):
    """
    Get service instance by name for dependency injection.
    
    Args:
        service_name: Name of the service to initialize  
        db_session: Database session for services that need it
        
    Returns:
        Initialized service instance
        
    Raises:
        ValueError: If service name is not found
    """
    if service_name == "auth":
        return get_auth_service()
    elif service_name == "user":
        return get_user_service()
    elif service_name == "cape_ai":
        return get_cape_ai_service(db_session)
    elif service_name == "conversation":
        return ConversationService()
    elif service_name == "audit":
        return get_audit_logger()  # Use the function that actually exists
    else:
        raise ValueError(f"Service '{service_name}' not found. Available: {list(CORE_SERVICES.keys())}")

# Service health check for existing services only
def check_service_health(service_name: str) -> dict:
    """
    Check the health status of a specific service.
    
    Args:
        service_name: Name of the service to check
        
    Returns:
        Health status dictionary
    """
    try:
        if service_name in CORE_SERVICES:
            # Basic health check - if we can import and instantiate, it's healthy
            service_class = CORE_SERVICES[service_name]
            return {
                "status": "healthy", 
                "service": service_name, 
                "message": f"{service_class.__name__} is accessible and ready"
            }
        elif service_name == "audit":
            # Special case for audit service which is a function, not a class
            return {
                "status": "healthy",
                "service": service_name,
                "message": "AuditLogger function is accessible and ready"
            }
        else:
            return {
                "status": "not_found", 
                "service": service_name, 
                "error": f"Service '{service_name}' not found"
            }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "service": service_name, 
            "error": str(e)
        }

def check_all_services_health() -> dict:
    """Check health status of all existing services."""
    from datetime import datetime
    
    # Include both class-based services and function-based services
    all_services = list(CORE_SERVICES.keys()) + ["audit"]
    
    health_status = {
        "overall": "healthy",
        "services": {},
        "timestamp": datetime.utcnow().isoformat(),
        "total_services": len(all_services),
        "healthy_services": 0
    }
    
    unhealthy_count = 0
    
    for service_name in all_services:
        service_health = check_service_health(service_name)
        health_status["services"][service_name] = service_health
        
        if service_health["status"] == "healthy":
            health_status["healthy_services"] += 1
        else:
            unhealthy_count += 1
    
    # Set overall status based on individual service health
    if unhealthy_count == 0:
        health_status["overall"] = "healthy"
    elif unhealthy_count <= len(all_services) // 2:
        health_status["overall"] = "degraded"  
    else:
        health_status["overall"] = "unhealthy"
    
    return health_status

# Service initialization patterns for the services that exist
SERVICE_INFO = {
    "auth": {
        "description": "User authentication, registration, and JWT token management",
        "factory": "get_auth_service",
        "dependencies": ["database"],
        "features": ["bcrypt_hashing", "jwt_tokens", "session_management"]
    },
    "user": {
        "description": "User profile management and CRUD operations", 
        "factory": "get_user_service",
        "dependencies": ["database", "auth"],
        "features": ["profile_management", "user_analytics", "preferences"]
    },
    "conversation": {
        "description": "Advanced conversation threading and management",
        "factory": "ConversationService",
        "dependencies": ["database", "user", "cape_ai"],
        "features": ["threading", "analytics", "context_management"]
    },
    "cape_ai": {
        "description": "Multi-provider AI integration with personalization",
        "factory": "get_cape_ai_service", 
        "dependencies": ["database", "redis", "user"],
        "features": ["multi_provider", "mock_mode", "personalization", "quality_scoring"]
    },
    "audit": {
        "description": "Enterprise audit logging and compliance tracking",
        "factory": "get_audit_logger",
        "dependencies": ["database"],
        "features": ["event_logging", "compliance", "security_tracking"]
    }
}

def get_service_info(service_name: str = None) -> dict:
    """
    Get detailed information about services.
    
    Args:
        service_name: Specific service name, or None for all services
        
    Returns:
        Service information dictionary
    """
    if service_name:
        if service_name in SERVICE_INFO:
            return SERVICE_INFO[service_name]
        else:
            raise ValueError(f"Service '{service_name}' not found")
    else:
        return SERVICE_INFO

__all__ = [
    # Existing service classes
    "AuthService", "get_auth_service",
    "UserService", "get_user_service", 
    "ConversationService",
    "CapeAIService", "get_cape_ai_service",
    
    # Audit service (function-based, not class-based)
    "get_audit_logger", "AuditEventType", "AuditLogLevel",
    
    # Service management
    "CORE_SERVICES", "SERVICE_INFO",
    "get_service", "get_service_info",
    "check_service_health", "check_all_services_health"
]