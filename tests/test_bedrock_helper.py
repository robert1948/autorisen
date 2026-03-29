from __future__ import annotations

import json
import types

import pytest

from backend.src.modules.ai_router.bedrock import invoke_bedrock_text


class _FakeBody:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")


class _FakeBedrockClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def invoke_model(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(kwargs)
        return {
            "body": _FakeBody(
                {
                    "content": [{"type": "text", "text": "ok"}],
                    "usage": {"input_tokens": 1000, "output_tokens": 2000},
                }
            )
        }


def test_invoke_bedrock_text_uses_openclaw_cost_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = _FakeBedrockClient()

    monkeypatch.setenv("AI_BEDROCK_ENABLED", "1")
    monkeypatch.setenv("AI_BEDROCK_REGION", "eu-north-1")
    monkeypatch.setenv("AI_BEDROCK_MODEL_ID", "anthropic.test-model")
    monkeypatch.delenv("AI_BEDROCK_COST_PER_1K_INPUT_USD", raising=False)
    monkeypatch.delenv("AI_BEDROCK_COST_PER_1K_OUTPUT_USD", raising=False)
    monkeypatch.setenv("OPENCLAW_COST_PER_1K_INPUT_USD", "0.01")
    monkeypatch.setenv("OPENCLAW_COST_PER_1K_OUTPUT_USD", "0.02")

    fake_boto3 = types.SimpleNamespace(
        client=lambda service_name, region_name=None: fake_client
    )
    monkeypatch.setitem(__import__("sys").modules, "boto3", fake_boto3)

    result = invoke_bedrock_text(system_prompt="system", user_prompt="user")

    assert result.text == "ok"
    assert result.input_tokens == 1000
    assert result.output_tokens == 2000
    assert result.estimated_usd == pytest.approx(0.05)
    assert fake_client.calls, "expected invoke_model to be called"
    assert fake_client.calls[0]["modelId"] == "anthropic.test-model"
