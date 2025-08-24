"""
CapeAI Enterprise Platform - Configuration Settings
Production-ready configuration with environment variable support
"""

import os

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Enterprise configuration settings"""
    
    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://localhost:5432/capeai_dev"
    )
    
    # Security Configuration
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", 
        "your-super-secret-key-change-in-production"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI Provider Configuration
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY")
    GOOGLE_AI_API_KEY: str | None = os.getenv("GOOGLE_AI_API_KEY")
    
    # Payment Configuration (Stripe)
    STRIPE_SECRET_KEY: str | None = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY: str | None = os.getenv("STRIPE_PUBLISHABLE_KEY")
    STRIPE_WEBHOOK_SECRET: str | None = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    # Application Configuration
    APP_NAME: str = "CapeAI Enterprise Platform"
    VERSION: str = "1.0.0"
    # Use pydantic Field with alias so env file values are parsed by pydantic.
    # Provide a pre-validator to coerce common string values (including empty string)
    # into a boolean to avoid ValidationError on import when DEBUG is set to ''.
    DEBUG: bool = Field(False, alias="DEBUG")

    @field_validator("DEBUG", mode="before")
    @classmethod
    def _coerce_debug(cls, v):
        if isinstance(v, str):
            s = v.strip().lower()
            if s in ("", "false", "0", "no", "off"):
                return False
            if s in ("true", "1", "yes", "on"):
                return True
        return v
    
    # CORS Configuration
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://your-domain.com"
    ]
    
    # Rate Limiting Configuration
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Monitoring Configuration
    SENTRY_DSN: str | None = os.getenv("SENTRY_DSN")
    
    # Pydantic v2 settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore unexpected env vars instead of raising ValidationError
    )

# Global settings instance
settings = Settings()
