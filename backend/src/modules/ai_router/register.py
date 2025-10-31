# backend/src/modules/ai_router/register.py

from __future__ import annotations

from typing import Dict, Iterable

from .provider_base import Provider


class ProviderRegistry:
    """Simple name-indexed registry for dynamic AI providers."""

    def __init__(self) -> None:
        self._providers: Dict[str, Provider] = {}

    def register(self, provider: Provider) -> None:
        """Add ``provider`` to the registry, guarding against duplicates."""

        if provider.name in self._providers:
            raise ValueError(f"Provider {provider.name} already registered")
        self._providers[provider.name] = provider

    def get(self, name: str) -> Provider:
        """Fetch a provider by name."""

        return self._providers[name]

    def all(self) -> Iterable[Provider]:
        """Return an iterable of all registered providers."""

        return tuple(self._providers.values())


registry = ProviderRegistry()
