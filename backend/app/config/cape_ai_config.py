# CapeAI Configuration Settings

import os
from typing import Optional

class CapeAISettings:
    """Configuration settings for CapeAI service"""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    # Prefer env var, then feature flag, then default
    ENABLE_GPT5_PREVIEW: bool = os.getenv("ENABLE_GPT5_PREVIEW", "true").lower() == "true"
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-5-preview" if ENABLE_GPT5_PREVIEW else "gpt-4")
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "500"))
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    # Redis Configuration (for conversation memory)
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD", None)
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    
    # AI Service Configuration
    AI_CONVERSATION_HISTORY_LIMIT: int = int(os.getenv("AI_CONVERSATION_HISTORY_LIMIT", "10"))
    AI_CONVERSATION_TTL_DAYS: int = int(os.getenv("AI_CONVERSATION_TTL_DAYS", "7"))
    AI_RESPONSE_TIMEOUT: int = int(os.getenv("AI_RESPONSE_TIMEOUT", "30"))
    
    # Feature Flags
    ENABLE_AI_VOICE: bool = os.getenv("ENABLE_AI_VOICE", "false").lower() == "true"
    ENABLE_AI_ANALYTICS: bool = os.getenv("ENABLE_AI_ANALYTICS", "true").lower() == "true"
    ENABLE_AI_LEARNING: bool = os.getenv("ENABLE_AI_LEARNING", "true").lower() == "true"
    
    # Fallback Configuration
    ENABLE_FALLBACK_RESPONSES: bool = os.getenv("ENABLE_FALLBACK_RESPONSES", "true").lower() == "true"
    FALLBACK_RESPONSE_DELAY: float = float(os.getenv("FALLBACK_RESPONSE_DELAY", "1.0"))
    
    # Security Configuration
    AI_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("AI_RATE_LIMIT_PER_MINUTE", "30"))
    AI_MAX_MESSAGE_LENGTH: int = int(os.getenv("AI_MAX_MESSAGE_LENGTH", "1000"))
    
    @classmethod
    def validate_config(cls) -> dict:
        """Validate configuration and return status"""
        issues = []
        
        if not cls.OPENAI_API_KEY:
            issues.append("OPENAI_API_KEY not configured")
        
        if not cls.REDIS_HOST:
            issues.append("REDIS_HOST not configured")
            
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "config": {
                "openai_model": cls.OPENAI_MODEL,
                "redis_host": cls.REDIS_HOST,
                "features": {
                    "voice": cls.ENABLE_AI_VOICE,
                    "analytics": cls.ENABLE_AI_ANALYTICS,
                    "learning": cls.ENABLE_AI_LEARNING
                }
            }
        }

# Environment-specific configurations
DEVELOPMENT_CONFIG = {
    "OPENAI_MODEL": "gpt-3.5-turbo",  # Cheaper for development
    "AI_RESPONSE_TIMEOUT": 60,  # Longer timeout for debugging
    "ENABLE_AI_ANALYTICS": False,  # Disable analytics in dev
}

PRODUCTION_CONFIG = {
    "OPENAI_MODEL": "gpt-5-preview",  # Enable GPT-5 (Preview) by default in production
    "AI_RESPONSE_TIMEOUT": 15,  # Faster response in production
    "ENABLE_AI_ANALYTICS": True,
    "AI_RATE_LIMIT_PER_MINUTE": 20,  # Stricter rate limiting
}

# Apply environment-specific overrides
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
if ENVIRONMENT == "production":
    for key, value in PRODUCTION_CONFIG.items():
        setattr(CapeAISettings, key, value)
elif ENVIRONMENT == "development":
    for key, value in DEVELOPMENT_CONFIG.items():
        setattr(CapeAISettings, key, value)
