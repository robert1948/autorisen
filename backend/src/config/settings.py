# filepath: /workspaces/autoagent/backend/src/config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URL: str
    FRONTEND_ORIGIN: str

model_config = SettingsConfigDict(
    env_file="../../.env", env_file_encoding="utf-8")


settings = Settings()
print("🔍 Loaded DATABASE_URL from .env:", settings.DATABASE_URL)

