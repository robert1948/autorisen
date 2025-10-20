from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional, Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings sourced from environment variables or .env files."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # don't crash on future unknown keys
    )

    # required / core
    secret_key: str = Field("dev-secret-change-me", alias="SECRET_KEY")
    database_url: str = Field("sqlite:///./dev.db", alias="DATABASE_URL")

    # optional
    email_api_key: Optional[str] = Field(default=None, alias="EMAIL_API_KEY")
    redis_url: Optional[str] = Field(default=None, alias="REDIS_URL")
    recaptcha_secret: Optional[str] = Field(default=None, alias="RECAPTCHA_SECRET")
    disable_recaptcha: bool = Field(default=False, alias="DISABLE_RECAPTCHA")
    rate_limit_per_min: int = Field(default=10, alias="RATE_LIMIT_PER_MIN")
    frontend_origin: str = Field(default="http://localhost:5173", alias="FRONTEND_ORIGIN")
    google_client_id: Optional[str] = Field(default=None, alias="GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = Field(default=None, alias="GOOGLE_CLIENT_SECRET")
    linkedin_client_id: Optional[str] = Field(default=None, alias="LINKEDIN_CLIENT_ID")
    linkedin_client_secret: Optional[str] = Field(default=None, alias="LINKEDIN_CLIENT_SECRET")

    # session/token lifetimes
    temp_token_ttl_minutes: int = Field(default=15, alias="TEMP_TOKEN_TTL_MINUTES")
    # canonical field going forward:
    access_token_ttl_minutes: int = Field(default=60 * 24 * 7, alias="ACCESS_TOKEN_TTL_MINUTES")
    # legacy/alternate name accepted from env:
    access_token_expire_minutes: Optional[int] = Field(
        default=None, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    # environment name
    env: Literal["dev", "test", "staging", "prod"] = Field("dev", alias="ENV")

    @model_validator(mode="after")
    def _apply_legacy_names(self) -> "Settings":
        """
        If ACCESS_TOKEN_EXPIRE_MINUTES is provided and ACCESS_TOKEN_TTL_MINUTES isn't,
        treat EXPIRE as the canonical TTL to stay backward-compatible.
        """
        if (
            self.access_token_expire_minutes is not None
            and "ACCESS_TOKEN_TTL_MINUTES" not in os.environ
        ):
            self.access_token_ttl_minutes = int(self.access_token_expire_minutes)
        return self


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


# backend/src/core/config.py  (append at bottom)
settings = get_settings()
