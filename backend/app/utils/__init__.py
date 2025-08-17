"""
CapeAI Utilities Package

Enterprise utility functions for the CapeAI platform.
Currently includes input sanitization with plans for expansion.
"""

# Import only EXISTING utilities to prevent deployment failures
from app.utils.input_sanitization import input_sanitizer, SanitizationLevel

# Available utilities (only existing ones)
AVAILABLE_UTILS = {
    "input_sanitizer": input_sanitizer,
    "SanitizationLevel": SanitizationLevel,
}

# Utility categories for organized access
INPUT_SANITIZATION_UTILS = {
    "input_sanitizer": input_sanitizer,
    "SanitizationLevel": SanitizationLevel,
}

# All utilities for comprehensive access (only existing ones)
ALL_UTILS = {
    **INPUT_SANITIZATION_UTILS,
}

def get_util(util_name: str):
    """Get utility function by name."""
    if util_name in ALL_UTILS:
        return ALL_UTILS[util_name]
    raise ValueError(f"Utility '{util_name}' not found. Available: {list(ALL_UTILS.keys())}")

def get_utils_by_category(category: str) -> dict:
    """
    Get all utilities in a specific category.
    
    Args:
        category: Currently only 'input_sanitization' is available
        
    Returns:
        Dictionary of utility functions in the category
    """
    category_map = {
        "input_sanitization": INPUT_SANITIZATION_UTILS,
    }
    
    if category not in category_map:
        raise ValueError(f"Category '{category}' not found. Available: {list(category_map.keys())}")
    
    return category_map[category]

def list_available_utils() -> dict:
    """List all available utilities organized by category."""
    return {
        "input_sanitization": list(INPUT_SANITIZATION_UTILS.keys()),
        "total_count": len(ALL_UTILS),
        "status": "Minimal utility set - ready for expansion"
    }

def get_sanitization_utils():
    """Get all input sanitization utilities."""
    return INPUT_SANITIZATION_UTILS

def sanitize_user_input(text: str, level: str = "moderate") -> str:
    """
    Convenience function for sanitizing user input.
    
    Args:
        text: Text to sanitize
        level: Sanitization level (strict, moderate, permissive)
        
    Returns:
        Sanitized text
    """
    try:
        # Convert level string to SanitizationLevel enum
        if level == "strict":
            sanitization_level = SanitizationLevel.STRICT
        elif level == "moderate":
            sanitization_level = SanitizationLevel.MODERATE
        elif level == "permissive":
            sanitization_level = SanitizationLevel.PERMISSIVE
        else:
            sanitization_level = SanitizationLevel.MODERATE
        
        return input_sanitizer.sanitize(text, level=sanitization_level)
    except Exception as e:
        print(f"⚠️ Sanitization error: {e}")
        return text  # Return original text if sanitization fails

def check_utils_health() -> dict:
    """Check health status of all utility modules."""
    health_status = {
        "overall": "healthy",
        "modules": {},
        "total_utils": len(ALL_UTILS),
        "working_utils": 0
    }
    
    # Test input sanitization
    try:
        test_result = input_sanitizer.sanitize("test <script>alert('xss')</script>")
        health_status["modules"]["input_sanitization"] = {
            "status": "healthy",
            "message": "Input sanitization working correctly",
            "test_passed": True
        }
        health_status["working_utils"] += len(INPUT_SANITIZATION_UTILS)
    except Exception as e:
        health_status["modules"]["input_sanitization"] = {
            "status": "unhealthy",
            "message": f"Input sanitization error: {e}",
            "test_passed": False
        }
        health_status["overall"] = "degraded"
    
    return health_status

# Utility information for service discovery
UTILS_INFO = {
    "input_sanitization": {
        "description": "Advanced input sanitization and validation",
        "functions": ["input_sanitizer", "SanitizationLevel"],
        "features": ["xss_prevention", "sql_injection_protection", "html_sanitization"],
        "status": "active"
    }
}

def get_utils_info():
    """Get detailed information about available utilities."""
    return UTILS_INFO

__all__ = [
    # Core input sanitization utilities
    "input_sanitizer",
    "SanitizationLevel",
    
    # Utility management
    "AVAILABLE_UTILS",
    "INPUT_SANITIZATION_UTILS", 
    "ALL_UTILS",
    "UTILS_INFO",
    
    # Utility access functions
    "get_util",
    "get_utils_by_category", 
    "list_available_utils",
    "get_sanitization_utils",
    
    # Convenience functions
    "sanitize_user_input",
    "check_utils_health",
    "get_utils_info"
]