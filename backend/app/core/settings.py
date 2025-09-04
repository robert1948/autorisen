# backend/app/core/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_PREFIX: str = "/api/v1"
    AI_PROVIDER: str = "demo"  # demo | openai | anthropic | gemini
    AI_MODEL: str = "gpt-4o-mini"
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
