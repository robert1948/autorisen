"""
Content Moderation Configuration - Task 1.2.5
=============================================

Configuration settings for content moderation system.
Supports environment-specific configurations and feature toggles.
"""

import os
from typing import Dict, Any, List
from enum import Enum

class ContentModerationConfig:
    """Configuration settings for content moderation system"""
    
    # Core Settings
    CONTENT_MODERATION_ENABLED: bool = os.getenv("CONTENT_MODERATION_ENABLED", "true").lower() == "true"
    DEFAULT_MODERATION_LEVEL: str = os.getenv("DEFAULT_MODERATION_LEVEL", "standard")
    
    # Performance Settings
    MAX_CONTENT_LENGTH: int = int(os.getenv("MAX_CONTENT_LENGTH", "10000"))
    MODERATION_TIMEOUT_SECONDS: int = int(os.getenv("MODERATION_TIMEOUT_SECONDS", "5"))
    ENABLE_CONTENT_CACHING: bool = os.getenv("ENABLE_CONTENT_CACHING", "true").lower() == "true"
    
    # AI-Specific Settings
    ENABLE_AI_DISCLAIMERS: bool = os.getenv("ENABLE_AI_DISCLAIMERS", "true").lower() == "true"
    REQUIRE_MEDICAL_DISCLAIMERS: bool = os.getenv("REQUIRE_MEDICAL_DISCLAIMERS", "true").lower() == "true"
    REQUIRE_LEGAL_DISCLAIMERS: bool = os.getenv("REQUIRE_LEGAL_DISCLAIMERS", "true").lower() == "true"
    REQUIRE_FINANCIAL_DISCLAIMERS: bool = os.getenv("REQUIRE_FINANCIAL_DISCLAIMERS", "true").lower() == "true"
    
    # Violation Handling
    BLOCK_HATE_SPEECH: bool = os.getenv("BLOCK_HATE_SPEECH", "true").lower() == "true"
    BLOCK_VIOLENCE: bool = os.getenv("BLOCK_VIOLENCE", "true").lower() == "true"
    BLOCK_HARASSMENT: bool = os.getenv("BLOCK_HARASSMENT", "true").lower() == "true"
    BLOCK_ADULT_CONTENT: bool = os.getenv("BLOCK_ADULT_CONTENT", "true").lower() == "true"
    WARN_ON_SPAM: bool = os.getenv("WARN_ON_SPAM", "true").lower() == "true"
    WARN_ON_MISINFORMATION: bool = os.getenv("WARN_ON_MISINFORMATION", "true").lower() == "true"
    
    # Confidence Thresholds (0-100)
    MINIMUM_CONFIDENCE_BLOCK: int = int(os.getenv("MINIMUM_CONFIDENCE_BLOCK", "70"))
    MINIMUM_CONFIDENCE_WARN: int = int(os.getenv("MINIMUM_CONFIDENCE_WARN", "50"))
    
    # Logging and Monitoring
    LOG_ALL_MODERATION: bool = os.getenv("LOG_ALL_MODERATION", "false").lower() == "true"
    LOG_BLOCKED_CONTENT: bool = os.getenv("LOG_BLOCKED_CONTENT", "true").lower() == "true"
    ENABLE_MODERATION_METRICS: bool = os.getenv("ENABLE_MODERATION_METRICS", "true").lower() == "true"
    
    # Rate Limiting for Moderation
    MAX_MODERATIONS_PER_MINUTE: int = int(os.getenv("MAX_MODERATIONS_PER_MINUTE", "100"))
    MAX_MODERATIONS_PER_HOUR: int = int(os.getenv("MAX_MODERATIONS_PER_HOUR", "1000"))
    
    @classmethod
    def get_environment_config(cls) -> Dict[str, Any]:
        """Get environment-specific configuration"""
        environment = os.getenv("ENVIRONMENT", "development").lower()
        
        configs = {
            "development": {
                "moderation_level": "permissive",
                "log_all_moderation": True,
                "enable_content_caching": False,
                "minimum_confidence_block": 80,
                "minimum_confidence_warn": 60
            },
            
            "staging": {
                "moderation_level": "standard", 
                "log_all_moderation": True,
                "enable_content_caching": True,
                "minimum_confidence_block": 75,
                "minimum_confidence_warn": 55
            },
            
            "production": {
                "moderation_level": "strict",
                "log_all_moderation": False,
                "enable_content_caching": True,
                "minimum_confidence_block": 70,
                "minimum_confidence_warn": 50
            }
        }
        
        return configs.get(environment, configs["development"])
    
    @classmethod
    def get_endpoint_configs(cls) -> Dict[str, Dict[str, Any]]:
        """Get endpoint-specific moderation configurations"""
        base_config = cls.get_environment_config()
        
        return {
            # AI Endpoints - Strict moderation
            "/api/ai/prompt": {
                "moderation_level": "standard",
                "moderate_input": True,
                "moderate_output": True,
                "max_content_length": 8000,
                "require_disclaimers": cls.ENABLE_AI_DISCLAIMERS,
                "block_confidence_threshold": cls.MINIMUM_CONFIDENCE_BLOCK,
                "warn_confidence_threshold": cls.MINIMUM_CONFIDENCE_WARN
            },
            
            "/api/ai/conversation": {
                "moderation_level": "standard", 
                "moderate_input": False,
                "moderate_output": True,
                "max_content_length": 10000,
                "require_disclaimers": cls.ENABLE_AI_DISCLAIMERS
            },
            
            # User Content - Moderate filtering
            "/api/users/profile": {
                "moderation_level": "permissive",
                "moderate_input": True,
                "moderate_output": False,
                "max_content_length": 2000,
                "block_confidence_threshold": 80
            },
            
            "/api/feedback": {
                "moderation_level": "strict",
                "moderate_input": True,
                "moderate_output": False,
                "max_content_length": 1000,
                "block_confidence_threshold": 60
            },
            
            # Public Content - Strict moderation
            "/api/comments": {
                "moderation_level": "strict",
                "moderate_input": True,
                "moderate_output": False,
                "max_content_length": 500,
                "block_confidence_threshold": 60
            },
            
            # Support/Help - Standard moderation
            "/api/support": {
                "moderation_level": "standard",
                "moderate_input": True,
                "moderate_output": True,
                "max_content_length": 3000,
                "require_disclaimers": False
            }
        }
    
    @classmethod
    def get_violation_rules(cls) -> Dict[str, Any]:
        """Get violation-specific rules and actions"""
        return {
            "hate_speech": {
                "enabled": cls.BLOCK_HATE_SPEECH,
                "action": "block",
                "confidence_threshold": 70,
                "escalate_to_admin": True
            },
            
            "violence": {
                "enabled": cls.BLOCK_VIOLENCE,
                "action": "block", 
                "confidence_threshold": 75,
                "escalate_to_admin": True
            },
            
            "harassment": {
                "enabled": cls.BLOCK_HARASSMENT,
                "action": "block",
                "confidence_threshold": 70,
                "escalate_to_admin": True
            },
            
            "adult_content": {
                "enabled": cls.BLOCK_ADULT_CONTENT,
                "action": "block",
                "confidence_threshold": 65,
                "escalate_to_admin": False
            },
            
            "spam": {
                "enabled": cls.WARN_ON_SPAM,
                "action": "warn",
                "confidence_threshold": 60,
                "escalate_to_admin": False
            },
            
            "misinformation": {
                "enabled": cls.WARN_ON_MISINFORMATION,
                "action": "warn",
                "confidence_threshold": 55,
                "escalate_to_admin": False
            },
            
            "malicious_code": {
                "enabled": True,
                "action": "block",
                "confidence_threshold": 80,
                "escalate_to_admin": True
            },
            
            "phishing": {
                "enabled": True,
                "action": "block",
                "confidence_threshold": 75,
                "escalate_to_admin": True
            },
            
            "financial_fraud": {
                "enabled": True,
                "action": "block",
                "confidence_threshold": 70,
                "escalate_to_admin": True
            },
            
            "privacy_violation": {
                "enabled": True,
                "action": "warn",
                "confidence_threshold": 60,
                "escalate_to_admin": True
            },
            
            "inappropriate_language": {
                "enabled": True,
                "action": "filter",
                "confidence_threshold": 50,
                "escalate_to_admin": False
            }
        }
    
    @classmethod
    def get_disclaimer_templates(cls) -> Dict[str, str]:
        """Get disclaimer templates for different content types"""
        return {
            "medical": (
                "\n\n*⚕️ Medical Disclaimer: This information is for educational purposes only "
                "and is not medical advice. Always consult with a qualified healthcare "
                "professional for medical concerns, diagnosis, or treatment.*"
            ),
            
            "legal": (
                "\n\n*⚖️ Legal Disclaimer: This information is for educational purposes only "
                "and is not legal advice. Always consult with a qualified attorney "
                "for legal matters and specific legal guidance.*"
            ),
            
            "financial": (
                "\n\n*💰 Financial Disclaimer: This information is for educational purposes only "
                "and is not financial advice. Always consult with a licensed financial "
                "advisor before making investment decisions. Past performance does not "
                "guarantee future results.*"
            ),
            
            "professional": (
                "\n\n*💼 Professional Disclaimer: This information is general guidance only. "
                "Professional situations vary significantly, and specific advice should "
                "be sought from qualified professionals in your field.*"
            ),
            
            "ai_generated": (
                "\n\n*🤖 AI-Generated Content: This response was generated by AI and should "
                "be verified independently. AI responses may contain errors or outdated "
                "information.*"
            )
        }
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate current configuration and return status"""
        issues = []
        warnings = []
        
        # Check required settings
        if not cls.CONTENT_MODERATION_ENABLED:
            warnings.append("Content moderation is disabled")
        
        # Check confidence thresholds
        if cls.MINIMUM_CONFIDENCE_BLOCK < 50:
            warnings.append("Block confidence threshold is very low (< 50%)")
        
        if cls.MINIMUM_CONFIDENCE_WARN < 30:
            warnings.append("Warning confidence threshold is very low (< 30%)")
        
        # Check content length limits
        if cls.MAX_CONTENT_LENGTH > 50000:
            warnings.append("Maximum content length is very high (> 50KB)")
        
        # Check timeout settings
        if cls.MODERATION_TIMEOUT_SECONDS > 10:
            warnings.append("Moderation timeout is high (> 10 seconds)")
        
        return {
            "status": "valid" if not issues else "invalid",
            "issues": issues,
            "warnings": warnings,
            "config_summary": {
                "enabled": cls.CONTENT_MODERATION_ENABLED,
                "default_level": cls.DEFAULT_MODERATION_LEVEL,
                "max_content_length": cls.MAX_CONTENT_LENGTH,
                "block_threshold": cls.MINIMUM_CONFIDENCE_BLOCK,
                "warn_threshold": cls.MINIMUM_CONFIDENCE_WARN,
                "ai_disclaimers": cls.ENABLE_AI_DISCLAIMERS
            }
        }

# Environment-specific configuration presets
ENVIRONMENT_CONFIGS = {
    "development": ContentModerationConfig.get_environment_config(),
    "staging": ContentModerationConfig.get_environment_config(), 
    "production": ContentModerationConfig.get_environment_config()
}

# Export commonly used configurations
MODERATION_ENABLED = ContentModerationConfig.CONTENT_MODERATION_ENABLED
DEFAULT_MODERATION_LEVEL = ContentModerationConfig.DEFAULT_MODERATION_LEVEL
ENDPOINT_CONFIGS = ContentModerationConfig.get_endpoint_configs()
VIOLATION_RULES = ContentModerationConfig.get_violation_rules()
DISCLAIMER_TEMPLATES = ContentModerationConfig.get_disclaimer_templates()
