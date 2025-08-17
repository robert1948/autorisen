"""
CapeAI Middleware Package
Enterprise-grade middleware components for security, monitoring, and performance
"""

import logging
logger = logging.getLogger(__name__)

# Initialize middleware registry
AVAILABLE_MIDDLEWARE = {}
MIDDLEWARE_CLASSES = {}

# Try to import monitoring middleware (REQUIRED)
try:
    from .monitoring import (
        MonitoringMiddleware, 
        set_monitoring_middleware_instance,
        get_monitoring_middleware_instance,
        get_current_metrics,
        get_health_status,
        get_recent_requests
    )
    AVAILABLE_MIDDLEWARE["monitoring"] = True
    MIDDLEWARE_CLASSES["MonitoringMiddleware"] = MonitoringMiddleware
    logger.info("✅ MonitoringMiddleware loaded successfully")
except ImportError as e:
    logger.error(f"❌ Failed to load MonitoringMiddleware: {e}")
    AVAILABLE_MIDDLEWARE["monitoring"] = False

# Try to import input sanitization middleware (REQUIRED)
try:
    from .input_sanitization import InputSanitizationMiddleware
    AVAILABLE_MIDDLEWARE["input_sanitization"] = True
    MIDDLEWARE_CLASSES["InputSanitizationMiddleware"] = InputSanitizationMiddleware
    logger.info("✅ InputSanitizationMiddleware loaded successfully")
except ImportError as e:
    logger.error(f"❌ Failed to load InputSanitizationMiddleware: {e}")
    AVAILABLE_MIDDLEWARE["input_sanitization"] = False

# Try to import content moderation middleware (REQUIRED)
try:
    from .content_moderation import ContentModerationMiddleware
    AVAILABLE_MIDDLEWARE["content_moderation"] = True
    MIDDLEWARE_CLASSES["ContentModerationMiddleware"] = ContentModerationMiddleware
    logger.info("✅ ContentModerationMiddleware loaded successfully")
except ImportError as e:
    logger.error(f"❌ Failed to load ContentModerationMiddleware: {e}")
    AVAILABLE_MIDDLEWARE["content_moderation"] = False

# Try to import CORS middleware (OPTIONAL)
try:
    from .cors_middleware import CORSMiddleware
    AVAILABLE_MIDDLEWARE["cors"] = True
    MIDDLEWARE_CLASSES["CORSMiddleware"] = CORSMiddleware
    logger.info("✅ CORSMiddleware loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ CORSMiddleware not available: {e}")
    AVAILABLE_MIDDLEWARE["cors"] = False

# Try to import DDoS protection middleware (OPTIONAL)
try:
    from .ddos_protection import DDoSProtectionMiddleware
    AVAILABLE_MIDDLEWARE["ddos_protection"] = True
    MIDDLEWARE_CLASSES["DDoSProtectionMiddleware"] = DDoSProtectionMiddleware
    logger.info("✅ DDoSProtectionMiddleware loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ DDoSProtectionMiddleware not available: {e}")
    AVAILABLE_MIDDLEWARE["ddos_protection"] = False

# Try to import rate limiting middleware (OPTIONAL)
try:
    from .rate_limiting import RateLimitingMiddleware
    AVAILABLE_MIDDLEWARE["rate_limiting"] = True
    MIDDLEWARE_CLASSES["RateLimitingMiddleware"] = RateLimitingMiddleware
    logger.info("✅ RateLimitingMiddleware loaded successfully")
except ImportError as e:
    try:
        # Try alternative name
        from .rate_limiting import RateLimitMiddleware
        AVAILABLE_MIDDLEWARE["rate_limiting"] = True
        MIDDLEWARE_CLASSES["RateLimitMiddleware"] = RateLimitMiddleware
        logger.info("✅ RateLimitMiddleware loaded successfully")
    except ImportError as e2:
        logger.warning(f"⚠️ Rate limiting middleware not available: {e}")
        AVAILABLE_MIDDLEWARE["rate_limiting"] = False

# Define middleware execution order (most important first)
MIDDLEWARE_STACK = []

# Add available middleware to stack
if AVAILABLE_MIDDLEWARE.get("cors", False):
    MIDDLEWARE_STACK.append(("CORS", MIDDLEWARE_CLASSES.get("CORSMiddleware")))

if AVAILABLE_MIDDLEWARE.get("ddos_protection", False):
    MIDDLEWARE_STACK.append(("DDoSProtection", MIDDLEWARE_CLASSES.get("DDoSProtectionMiddleware")))

if AVAILABLE_MIDDLEWARE.get("rate_limiting", False):
    rate_limit_class = MIDDLEWARE_CLASSES.get("RateLimitingMiddleware") or MIDDLEWARE_CLASSES.get("RateLimitMiddleware")
    if rate_limit_class:
        MIDDLEWARE_STACK.append(("RateLimiting", rate_limit_class))

# Always add core security middleware (if available)
if AVAILABLE_MIDDLEWARE.get("input_sanitization", False):
    MIDDLEWARE_STACK.append(("InputSanitization", MIDDLEWARE_CLASSES.get("InputSanitizationMiddleware")))

if AVAILABLE_MIDDLEWARE.get("content_moderation", False):
    MIDDLEWARE_STACK.append(("ContentModeration", MIDDLEWARE_CLASSES.get("ContentModerationMiddleware")))

if AVAILABLE_MIDDLEWARE.get("monitoring", False):
    MIDDLEWARE_STACK.append(("Monitoring", MIDDLEWARE_CLASSES.get("MonitoringMiddleware")))

def configure_middleware(app, environment: str = "production"):
    """
    Configure middleware stack based on environment and availability.
    
    Args:
        app: FastAPI application instance
        environment: Environment type (production, development, testing)
        
    Returns:
        FastAPI app with configured middleware
    """
    logger.info(f"🔧 Configuring middleware for {environment} environment")
    
    # Determine which middleware to use based on environment
    if environment == "production":
        middleware_list = MIDDLEWARE_STACK
    elif environment == "development":
        middleware_list = MIDDLEWARE_STACK
    else:  # testing
        # Testing uses minimal middleware (only core ones)
        middleware_list = [
            (name, cls) for name, cls in MIDDLEWARE_STACK 
            if name in ["Monitoring", "InputSanitization", "ContentModeration"]
        ]
    
    # Apply middleware in reverse order (FastAPI requirement)
    applied_count = 0
    for name, middleware_class in reversed(middleware_list):
        if middleware_class:
            try:
                app.add_middleware(middleware_class)
                logger.info(f"✅ {name} middleware applied successfully")
                applied_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to apply {name} middleware: {e}")
        else:
            logger.warning(f"⚠️ {name} middleware class not available")
    
    logger.info(f"🎯 Applied {applied_count}/{len(middleware_list)} middleware components")
    return app

def get_available_middleware():
    """Get dictionary of available middleware classes."""
    return {k: v for k, v in AVAILABLE_MIDDLEWARE.items() if v}

def get_middleware_status():
    """Get comprehensive middleware status report."""
    total = len(AVAILABLE_MIDDLEWARE)
    available = sum(1 for v in AVAILABLE_MIDDLEWARE.values() if v)
    
    return {
        "total_middleware": total,
        "available_middleware": available,
        "availability_rate": f"{(available/total)*100:.1f}%",
        "status": AVAILABLE_MIDDLEWARE,
        "middleware_stack_size": len(MIDDLEWARE_STACK),
        "critical_middleware": {
            "monitoring": AVAILABLE_MIDDLEWARE.get("monitoring", False),
            "input_sanitization": AVAILABLE_MIDDLEWARE.get("input_sanitization", False),
            "content_moderation": AVAILABLE_MIDDLEWARE.get("content_moderation", False)
        }
    }

def check_middleware_health():
    """Check if all critical middleware is available."""
    critical_middleware = ["monitoring", "input_sanitization", "content_moderation"]
    
    health_status = {
        "overall": "healthy",
        "critical_issues": [],
        "available": get_available_middleware(),
        "middleware_stack": [name for name, _ in MIDDLEWARE_STACK]
    }
    
    # Check critical middleware
    for middleware in critical_middleware:
        if not AVAILABLE_MIDDLEWARE.get(middleware, False):
            health_status["critical_issues"].append(f"Missing critical middleware: {middleware}")
    
    # Set overall status
    if health_status["critical_issues"]:
        health_status["overall"] = "degraded" if len(health_status["critical_issues"]) < len(critical_middleware) else "unhealthy"
    
    return health_status

# Build __all__ dynamically based on available middleware
__all__ = [
    # Core functions
    "configure_middleware",
    "get_available_middleware", 
    "get_middleware_status",
    "check_middleware_health",
    "AVAILABLE_MIDDLEWARE",
    "MIDDLEWARE_STACK",
    "MIDDLEWARE_CLASSES"
]

# Add monitoring functions if available
if AVAILABLE_MIDDLEWARE.get("monitoring", False):
    __all__.extend([
        "MonitoringMiddleware",
        "set_monitoring_middleware_instance",
        "get_monitoring_middleware_instance",
        "get_current_metrics",
        "get_health_status",
        "get_recent_requests"
    ])

# Add available middleware classes
for class_name, middleware_class in MIDDLEWARE_CLASSES.items():
    if middleware_class:
        __all__.append(class_name)

# Log final status
logger.info(f"🎯 Middleware package initialized: {len(MIDDLEWARE_CLASSES)} classes available")
logger.info(f"📊 Critical middleware status: {get_middleware_status()['critical_middleware']}")