# backend/app/core/settings.py
"""
backend/app/core/settings.py
Simple Settings container without external dependencies
"""


class Settings:
    API_V1_PREFIX = "/api/v1"
    AI_PROVIDER = "demo"  # demo | openai | anthropic | gemini
    AI_MODEL = "gpt-4o-mini"
    OPENAI_API_KEY = None
    ANTHROPIC_API_KEY = None
    GEMINI_API_KEY = None


"""
Simple configuration container for CapeControl backend.
"""


class Settings:
    API_V1_PREFIX = "/api/v1"
    AI_PROVIDER = "demo"  # demo | openai | anthropic | gemini
    AI_MODEL = "gpt-4o-mini"
    OPENAI_API_KEY = None
    ANTHROPIC_API_KEY = None
    GEMINI_API_KEY = None


# Single settings instance used by app modules
settings = Settings()
