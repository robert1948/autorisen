# backend/app/config.py
import os

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = Field("CapeControl", alias="PROJECT_NAME")
    postgres_db: str = Field("capecontrol", alias="POSTGRES_DB")
    postgres_user: str = Field("capecontrol_user", alias="POSTGRES_USER")
    postgres_password: str = Field("dev-password-123", alias="POSTGRES_PASSWORD")
    secret_key: str = Field("dev-secret-key-change-in-production", alias="SECRET_KEY")
    environment: str = Field("development", alias="ENVIRONMENT")
    debug: bool = Field(True, alias="DEBUG")
    allowed_hosts: str = Field("", alias="ALLOWED_HOSTS")
    cors_origins: str = Field("", alias="CORS_ORIGINS")
    api_url: str = Field("http://localhost:8000", alias="API_URL")
    database_url: str = Field("sqlite:///./capecontrol.db", alias="DATABASE_URL")
    frontend_origin: str = Field("http://localhost:3000", alias="FRONTEND_ORIGIN")
    
    # Email configuration
    smtp_server: str = Field("localhost", alias="SMTP_SERVER")
    smtp_port: int = Field(587, alias="SMTP_PORT")
    smtp_use_tls: bool = Field(True, alias="SMTP_USE_TLS")
    smtp_username: str = Field("", alias="SMTP_USERNAME")
    smtp_password: str = Field("", alias="SMTP_PASSWORD")
    from_email: str = Field("noreply@localhost", alias="FROM_EMAIL")
    
    # S3 configuration
    aws_access_key_id: str = Field("", alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field("", alias="AWS_SECRET_ACCESS_KEY")
    aws_storage_bucket_name: str = Field("", alias="AWS_STORAGE_BUCKET_NAME")
    aws_s3_region_name: str = Field("us-east-1", alias="AWS_S3_REGION_NAME")
    
    # Session configuration
    session_secret: str = Field("dev-session-secret", alias="SESSION_SECRET")
    jwt_secret_key: str = Field("dev-jwt-secret", alias="JWT_SECRET_KEY")
    
    # Rate limiting
    rate_limit_enabled: bool = Field(False, alias="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(100, alias="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(3600, alias="RATE_LIMIT_WINDOW")
    
    # Redis configuration for CapeAI and Context Enhancement (Task 2.1.3)
    redis_host: str = Field("localhost", alias="REDIS_HOST")
    redis_port: int = Field(6379, alias="REDIS_PORT")
    redis_password: str = Field("", alias="REDIS_PASSWORD")
    redis_url: str = Field("redis://localhost:6379/0", alias="REDIS_URL")
    
    # AI Provider Configuration (Task 2.1.1: Multi-Provider Support)
    openai_api_key: str = Field("", alias="OPENAI_API_KEY")
    claude_api_key: str = Field("", alias="CLAUDE_API_KEY")  # Claude API key
    gemini_api_key: str = Field("", alias="GEMINI_API_KEY")  # FIXED: Single definition only
    
    # Stripe Configuration (for payments)
    stripe_secret_key: str = Field("", alias="STRIPE_SECRET_KEY")
    stripe_publishable_key: str = Field("", alias="STRIPE_PUBLISHABLE_KEY")
    stripe_webhook_secret: str = Field("", alias="STRIPE_WEBHOOK_SECRET")
    
    @property
    def STRIPE_SECRET_KEY(self) -> str:
        return self.stripe_secret_key
        
    @property
    def STRIPE_PUBLISHABLE_KEY(self) -> str:
        return self.stripe_publishable_key
        
    @property
    def STRIPE_WEBHOOK_SECRET(self) -> str:
        return self.stripe_webhook_secret
    
    @property
    def REDIS_HOST(self) -> str:
        return self.redis_host
        
    @property 
    def REDIS_PORT(self) -> int:
        return self.redis_port
        
    @property
    def REDIS_PASSWORD(self) -> str:
        return self.redis_password or None
        
    @property
    def OPENAI_API_KEY(self) -> str:
        return self.openai_api_key
    
    @property
    def CLAUDE_API_KEY(self) -> str:
        return self.claude_api_key
    
    @property
    def GEMINI_API_KEY(self) -> str:  # ADDED: Missing property accessor
        return self.gemini_api_key
    
    @property
    def allowed_hosts_list(self) -> list[str]:
        if isinstance(self.allowed_hosts, str):
            return [host.strip() for host in self.allowed_hosts.split(",") if host.strip()]
        return []
    
    @property
    def cors_origins_list(self) -> list[str]:
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
        return []
    
    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"

    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def split_allowed_hosts(cls, v):
        # This validator is no longer needed but kept for compatibility
        return v or ""

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors_origins(cls, v):
        # This validator is no longer needed but kept for compatibility
        return v or ""

    @field_validator("debug", mode="before")
    @classmethod
    def coerce_debug(cls, v):
        """Coerce common string representations to boolean to avoid
        pydantic errors when DEBUG is set to an empty string or loose value
        in the environment.
        """
        if isinstance(v, str):
            s = v.strip().lower()
            if s in ("", "false", "0", "no", "off"):
                return False
            if s in ("true", "1", "yes", "on"):
                return True
        return v

    model_config = SettingsConfigDict(
        env_file=[".env.production" if os.getenv("ENVIRONMENT") == "production" else ".env"],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()

# Production safety checks
if settings.is_production:
    if settings.secret_key == "dev-secret-key-change-in-production":
        raise ValueError("CRITICAL: Production SECRET_KEY must be changed from development default!")
    
    if settings.debug:
        print("WARNING: DEBUG is True in production environment")
    
    if not settings.database_url.startswith("postgresql://"):
        print("WARNING: Production should use PostgreSQL database")
    
    if "localhost" in settings.cors_origins_list or "127.0.0.1" in settings.cors_origins_list:
        print("WARNING: Localhost CORS origins detected in production")
    
    if not settings.allowed_hosts_list or "localhost" in settings.allowed_hosts_list:
        print("WARNING: Production ALLOWED_HOSTS should not include localhost")