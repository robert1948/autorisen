from __future__ import annotations

import sys
import types
from types import SimpleNamespace

import pytest

from backend.src.modules.ai_router.bedrock import BedrockTextResult
from backend.src.modules.chat import service as chat_service
from backend.src.modules.rag.schemas import UnsupportedPolicy
from backend.src.modules.rag.service import RAGService
from backend.src.modules.usage.llm_cache import llm_cache


class _FakeVersionInfo:
    @staticmethod
    def parse(version: str):
        parts = []
        for token in version.replace("-", ".").split("."):
            parts.append(int(token) if token.isdigit() else 0)
        return tuple(parts)


sys.modules.setdefault("semver", SimpleNamespace(VersionInfo=_FakeVersionInfo))


class _FakeAsyncAnthropic:
    def __init__(self, *args, **kwargs) -> None:  # noqa: D401, ANN002, ANN003
        pass


class _FakeAsyncOpenAI:
    def __init__(self, *args, **kwargs) -> None:  # noqa: D401, ANN002, ANN003
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(create=lambda **_k: None)
        )


sys.modules.setdefault("anthropic", SimpleNamespace(AsyncAnthropic=_FakeAsyncAnthropic))
sys.modules.setdefault(
    "openai",
    SimpleNamespace(AsyncOpenAI=_FakeAsyncOpenAI, OpenAI=_FakeAsyncOpenAI),
)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class _DummyDB:
    def commit(self) -> None:
        return


def test_chat_generate_ai_response_uses_bedrock_when_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = SimpleNamespace(
        anthropic_api_key="",
        openai_api_key="",
        ai_provider_strategy="hybrid",
        ai_provider_fallback_order="bedrock,openai",
        ai_bedrock_enabled=True,
        ai_bedrock_model_id="bedrock-chat-model",
        ai_bedrock_region="eu-north-1",
    )
    monkeypatch.setattr(chat_service, "get_settings", lambda: settings)
    monkeypatch.setattr(
        chat_service,
        "_build_messages_for_ai",
        lambda *_args, **_kwargs: [{"role": "user", "content": "hello"}],
    )

    bedrock_calls: dict[str, str] = {}

    def _fake_bedrock(**kwargs: str) -> BedrockTextResult:
        bedrock_calls.update(kwargs)
        return BedrockTextResult(
            text="bedrock reply",
            model_id="bedrock-chat-model",
            region="eu-north-1",
            input_tokens=11,
            output_tokens=7,
            estimated_usd=0.0005,
            latency_ms=123,
        )

    monkeypatch.setattr(chat_service, "invoke_bedrock_text", _fake_bedrock)

    captured_event: dict[str, object] = {}

    def _fake_create_event(_db, **kwargs):
        captured_event.update(kwargs)
        return kwargs

    monkeypatch.setattr(chat_service, "create_event", _fake_create_event)

    import backend.src.modules.usage.service as usage_service

    monkeypatch.setattr(usage_service, "record_usage", lambda *_a, **_k: None)

    thread = SimpleNamespace(id="thread-1", placement="support", user_id="user-1")
    result = chat_service.generate_ai_response(
        _DummyDB(),
        thread=thread,
        user_message="hello",
    )

    assert result["event_metadata"]["provider"] == "bedrock"
    assert result["content"] == "bedrock reply"
    assert bedrock_calls["model_id"] == "bedrock-chat-model"
    assert bedrock_calls["region"] == "eu-north-1"


def test_chat_generate_ai_response_falls_back_to_openai_when_bedrock_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = SimpleNamespace(
        anthropic_api_key="",
        openai_api_key="openai-key",
        ai_provider_strategy="hybrid",
        ai_provider_fallback_order="bedrock,openai",
        ai_bedrock_enabled=True,
        ai_bedrock_model_id="bedrock-chat-model",
        ai_bedrock_region="eu-north-1",
    )
    monkeypatch.setattr(chat_service, "get_settings", lambda: settings)
    monkeypatch.setattr(
        chat_service,
        "_build_messages_for_ai",
        lambda *_args, **_kwargs: [{"role": "user", "content": "hello"}],
    )
    monkeypatch.setattr(
        chat_service,
        "invoke_bedrock_text",
        lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("forced bedrock error")),
    )

    class _FakeOpenAIResponse:
        def __init__(self) -> None:
            self.model = "gpt-4o-mini"
            self.choices = [
                SimpleNamespace(
                    message=SimpleNamespace(content="openai fallback reply")
                )
            ]
            self.usage = SimpleNamespace(prompt_tokens=9, completion_tokens=5)

    class _FakeOpenAIClient:
        def __init__(self, *_args, **_kwargs) -> None:
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(create=lambda **_k: _FakeOpenAIResponse())
            )

    monkeypatch.setitem(
        sys.modules, "openai", types.SimpleNamespace(OpenAI=_FakeOpenAIClient)
    )

    captured_event: dict[str, object] = {}

    def _fake_create_event(_db, **kwargs):
        captured_event.update(kwargs)
        return kwargs

    monkeypatch.setattr(chat_service, "create_event", _fake_create_event)

    import backend.src.modules.usage.service as usage_service

    monkeypatch.setattr(usage_service, "record_usage", lambda *_a, **_k: None)

    thread = SimpleNamespace(id="thread-2", placement="support", user_id="user-2")
    result = chat_service.generate_ai_response(
        _DummyDB(),
        thread=thread,
        user_message="hello",
    )

    assert result["event_metadata"]["provider"] == "openai"
    assert result["content"] == "openai fallback reply"


@pytest.mark.anyio
async def test_rag_generate_response_falls_back_from_bedrock_to_openai(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = RAGService(openai_api_key="openai-key")

    monkeypatch.setattr(
        "backend.src.modules.rag.service.resolve_available_provider_order",
        lambda **_kwargs: ["bedrock", "openai"],
    )

    async def _fake_bedrock(*_args, **_kwargs):
        return "[Error generating response: forced bedrock error]", {}

    async def _fake_openai(*_args, **_kwargs):
        return "openai rag reply", {"provider": "openai"}

    monkeypatch.setattr(service, "_call_bedrock", _fake_bedrock)
    monkeypatch.setattr(service, "_call_openai", _fake_openai)

    response_text, usage = await service._generate_response(
        query="What changed this month?",
        citations=[],
        grounded=False,
        unsupported_policy=UnsupportedPolicy.FLAG,
    )

    assert response_text == "openai rag reply"
    assert usage["provider"] == "openai"


@pytest.mark.anyio
async def test_finance_call_llm_uses_bedrock_when_first(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from backend.src.modules.agents.finance_agent import service as finance_service

    llm_cache.clear()
    svc = finance_service.FinanceAgentService(
        openai_api_key=None,
        anthropic_api_key=None,
        ai_provider_strategy="hybrid",
        ai_provider_fallback_order="bedrock,openai",
    )

    monkeypatch.setattr(
        finance_service,
        "resolve_available_provider_order",
        lambda **_kwargs: ["bedrock"],
    )
    monkeypatch.setattr(
        finance_service,
        "get_settings",
        lambda: SimpleNamespace(
            ai_bedrock_model_id="bedrock-finance-model",
            ai_bedrock_region="eu-north-1",
        ),
    )
    monkeypatch.setattr(
        finance_service,
        "invoke_bedrock_text",
        lambda **_kwargs: BedrockTextResult(
            text="finance bedrock reply",
            model_id="bedrock-finance-model",
            region="eu-north-1",
            input_tokens=20,
            output_tokens=10,
            estimated_usd=0.001,
            latency_ms=50,
        ),
    )

    text, usage = await svc._call_llm("finance query bedrock test")

    assert text == "finance bedrock reply"
    assert usage["provider"] == "bedrock"
    assert usage["region"] == "eu-north-1"


@pytest.mark.anyio
async def test_finance_call_llm_returns_safe_fallback_when_bedrock_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from backend.src.modules.agents.finance_agent import service as finance_service

    llm_cache.clear()
    svc = finance_service.FinanceAgentService(
        openai_api_key=None,
        anthropic_api_key=None,
        ai_provider_strategy="bedrock_only",
        ai_provider_fallback_order="bedrock",
    )

    monkeypatch.setattr(
        finance_service,
        "resolve_available_provider_order",
        lambda **_kwargs: ["bedrock"],
    )
    monkeypatch.setattr(
        finance_service,
        "invoke_bedrock_text",
        lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("forced bedrock failure")),
    )

    text, usage = await svc._call_llm("finance query fallback test")

    assert "standard financial analysis frameworks" in text
    assert usage == {}
