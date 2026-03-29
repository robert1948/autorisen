from backend.src.modules.ai_router.strategy import (
    filter_available_providers,
    parse_fallback_order,
    resolve_provider_order,
)


def test_parse_fallback_order_deduplicates_and_appends_missing() -> None:
    order = parse_fallback_order("openai,anthropic,openai")
    assert order == ["openai", "anthropic", "bedrock"]


def test_parse_fallback_order_ignores_unknown_values() -> None:
    order = parse_fallback_order("foo,bedrock,bar")
    assert order == ["bedrock", "anthropic", "openai"]


def test_resolve_provider_order_bedrock_first() -> None:
    order = resolve_provider_order("bedrock_first", "openai,anthropic")
    assert order == ["bedrock", "openai", "anthropic"]


def test_resolve_provider_order_direct_only() -> None:
    order = resolve_provider_order("direct_only", "bedrock,openai,anthropic")
    assert order == ["anthropic", "openai"]


def test_filter_available_providers() -> None:
    available = filter_available_providers(
        ["bedrock", "anthropic", "openai"],
        has_bedrock=False,
        has_anthropic=True,
        has_openai=False,
    )
    assert available == ["anthropic"]
