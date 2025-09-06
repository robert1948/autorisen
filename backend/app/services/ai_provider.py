# backend/app/services/ai_provider.py
from abc import ABC, abstractmethod
from typing import Dict, Any
from app.core.settings import settings

# Import moved into get_ai_provider to avoid circular import issues
# from app.services.providers.openai_provider import OpenAIProvider
# from app.services.providers.anthropic_provider import AnthropicProvider
# from app.services.providers.gemini_provider import GeminiProvider


class AIProvider(ABC):
    @abstractmethod
    async def answer_faq(
        self, question: str, meta: Dict[str, Any] | None = None
    ) -> str: ...
    @abstractmethod
    async def schedule(
        self, command: str, meta: Dict[str, Any] | None = None
    ) -> Dict[str, Any]: ...


def get_ai_provider() -> AIProvider:
    from app.services.providers.demo_cape_ai import DemoCapeAIService

    p = settings.AI_PROVIDER.lower()
    if p == "openai":
        # return OpenAIProvider(model=settings.AI_MODEL, api_key=settings.OPENAI_API_KEY)
        return DemoCapeAIService()  # placeholder until wired
    if p == "anthropic":
        # return AnthropicProvider(api_key=settings.ANTHROPIC_API_KEY)
        return DemoCapeAIService()
    if p == "gemini":
        # return GeminiProvider(api_key=settings.GEMINI_API_KEY)
        return DemoCapeAIService()
    # default / local dev
    return DemoCapeAIService()
