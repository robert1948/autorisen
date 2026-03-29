"""Provider routing helpers for strategy-driven AI execution order."""

from __future__ import annotations

from typing import Iterable, Literal

ProviderName = Literal["bedrock", "anthropic", "openai"]
StrategyName = Literal[
    "hybrid", "bedrock_first", "direct_first", "bedrock_only", "direct_only"
]

_ALL_PROVIDERS: tuple[ProviderName, ...] = ("bedrock", "anthropic", "openai")


def _normalize_provider_name(name: str) -> ProviderName | None:
    cleaned = (name or "").strip().lower()
    if cleaned in _ALL_PROVIDERS:
        return cleaned
    return None


def parse_fallback_order(raw: str | None) -> list[ProviderName]:
    """Parse and sanitize a comma-separated provider order string."""
    if not raw:
        return list(_ALL_PROVIDERS)

    ordered: list[ProviderName] = []
    for token in raw.split(","):
        provider = _normalize_provider_name(token)
        if provider and provider not in ordered:
            ordered.append(provider)

    if not ordered:
        return list(_ALL_PROVIDERS)

    for provider in _ALL_PROVIDERS:
        if provider not in ordered:
            ordered.append(provider)

    return ordered


def _prepend(items: Iterable[ProviderName], first: ProviderName) -> list[ProviderName]:
    rest = [item for item in items if item != first]
    return [first, *rest]


def resolve_provider_order(
    strategy: StrategyName,
    fallback_order: str | None,
) -> list[ProviderName]:
    """Resolve execution order from strategy and optional fallback order."""
    base = parse_fallback_order(fallback_order)

    if strategy == "bedrock_only":
        return ["bedrock"]
    if strategy == "direct_only":
        return ["anthropic", "openai"]
    if strategy == "bedrock_first":
        return _prepend(base, "bedrock")
    if strategy == "direct_first":
        return ["anthropic", "openai", "bedrock"]

    return base


def filter_available_providers(
    ordered: Iterable[ProviderName],
    *,
    has_bedrock: bool,
    has_anthropic: bool,
    has_openai: bool,
) -> list[ProviderName]:
    """Filter ordered providers by runtime availability."""
    availability = {
        "bedrock": has_bedrock,
        "anthropic": has_anthropic,
        "openai": has_openai,
    }
    return [provider for provider in ordered if availability.get(provider, False)]


def resolve_available_provider_order(
    *,
    strategy: StrategyName,
    fallback_order: str | None,
    has_bedrock: bool,
    has_anthropic: bool,
    has_openai: bool,
) -> list[ProviderName]:
    """Convenience helper that returns strategy-resolved, available providers."""
    ordered = resolve_provider_order(strategy, fallback_order)
    return filter_available_providers(
        ordered,
        has_bedrock=has_bedrock,
        has_anthropic=has_anthropic,
        has_openai=has_openai,
    )
