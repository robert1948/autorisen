import os
from pydantic_settings import BaseSettings

def _env_alias(primary: str, *aliases: str, default: str | None = None):
    for key in (primary, *aliases):
        val = os.getenv(key)
        if val is not None and val != "":
            return val
    return default

class Settings(BaseSettings):
    # Environment
    environment: str = _env_alias("ENVIRONMENT", "ENV", "NODE_ENV", default="development")

    # JWT
    jwt_secret_key: str = _env_alias("JWT_SECRET_KEY", "JWT_SECRET", default="")

    # Mail
    mail_from: str = _env_alias("MAIL_FROM", "FROM_EMAIL", default="noreply@example.com")
    mail_server: str = _env_alias("MAIL_SERVER", "SMTP_HOST", default="")
    mail_user: str = _env_alias("MAIL_USER", "SMTP_USERNAME", default="")
    mail_password: str = _env_alias("MAIL_PASSWORD", "SMTP_PASSWORD", default="")
    mail_port: int = int(_env_alias("MAIL_PORT", "SMTP_PORT", default="587"))
    mail_tls: bool = True  # or add a MAIL_TLS alias if you use it

    # Redis
    redis_url: str = _env_alias("REDIS_URL", default="redis://localhost:6379/0")

    # CORS / Frontend
    cors_allow_origins: str = _env_alias("CORS_ALLOW_ORIGINS", "CORS_ORIGINS", default="")
    frontend_origin: str = _env_alias("FRONTEND_ORIGIN", "CLIENT_URL", default="")

settings = Settings()
