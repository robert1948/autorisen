"""Shared Bedrock invocation helpers for text generation."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass


def _as_bool(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def is_bedrock_enabled() -> bool:
    """Return True when shared Bedrock execution is enabled."""
    return _as_bool(os.getenv("AI_BEDROCK_ENABLED")) or _as_bool(
        os.getenv("OPENCLAW_BEDROCK_ENABLED")
    )


def default_bedrock_region() -> str:
    return os.getenv("AI_BEDROCK_REGION") or os.getenv(
        "OPENCLAW_BEDROCK_REGION", "eu-north-1"
    )


def default_bedrock_model_id() -> str:
    return os.getenv("AI_BEDROCK_MODEL_ID") or os.getenv(
        "OPENCLAW_BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"
    )


@dataclass
class BedrockTextResult:
    text: str
    model_id: str
    region: str
    input_tokens: int
    output_tokens: int
    estimated_usd: float
    latency_ms: int


def invoke_bedrock_text(
    *,
    system_prompt: str,
    user_prompt: str,
    model_id: str | None = None,
    region: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    input_cost_per_1k: float | None = None,
    output_cost_per_1k: float | None = None,
) -> BedrockTextResult:
    """Invoke Amazon Bedrock (Anthropic format) and return normalized metadata."""
    if not is_bedrock_enabled():
        raise RuntimeError("Bedrock is disabled (AI_BEDROCK_ENABLED != 1)")

    resolved_model_id = model_id or default_bedrock_model_id()
    resolved_region = region or default_bedrock_region()
    resolved_max_tokens = max_tokens or int(
        os.getenv("AI_BEDROCK_MAX_TOKENS")
        or os.getenv("OPENCLAW_BEDROCK_MAX_TOKENS", "2048")
    )
    resolved_temperature = (
        temperature
        if temperature is not None
        else float(
            os.getenv("AI_BEDROCK_TEMPERATURE")
            or os.getenv("OPENCLAW_BEDROCK_TEMPERATURE", "0.2")
        )
    )

    import boto3  # type: ignore

    started = time.perf_counter()
    client = boto3.client("bedrock-runtime", region_name=resolved_region)
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": resolved_max_tokens,
        "temperature": resolved_temperature,
        "system": system_prompt,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt,
                    }
                ],
            }
        ],
    }

    response = client.invoke_model(
        modelId=resolved_model_id,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(payload),
    )

    raw_body = response.get("body")
    body_bytes = raw_body.read() if hasattr(raw_body, "read") else raw_body
    data = json.loads(
        body_bytes.decode("utf-8") if isinstance(body_bytes, bytes) else str(body_bytes)
    )

    segments = data.get("content", []) if isinstance(data, dict) else []
    text_parts = [
        str(seg.get("text", ""))
        for seg in segments
        if isinstance(seg, dict) and seg.get("type") == "text"
    ]
    text = "\n".join(part for part in text_parts if part).strip()

    usage = data.get("usage", {}) if isinstance(data, dict) else {}
    input_tokens = int(usage.get("input_tokens", 0) or 0)
    output_tokens = int(usage.get("output_tokens", 0) or 0)

    resolved_input_cost = (
        input_cost_per_1k
        if input_cost_per_1k is not None
        else float(
            os.getenv("AI_BEDROCK_COST_PER_1K_INPUT_USD")
            or os.getenv("OPENCLAW_COST_PER_1K_INPUT_USD")
            or "0"
        )
    )
    resolved_output_cost = (
        output_cost_per_1k
        if output_cost_per_1k is not None
        else float(
            os.getenv("AI_BEDROCK_COST_PER_1K_OUTPUT_USD")
            or os.getenv("OPENCLAW_COST_PER_1K_OUTPUT_USD")
            or "0"
        )
    )
    estimated_usd = ((input_tokens / 1000.0) * resolved_input_cost) + (
        (output_tokens / 1000.0) * resolved_output_cost
    )
    latency_ms = int((time.perf_counter() - started) * 1000)

    return BedrockTextResult(
        text=text,
        model_id=resolved_model_id,
        region=resolved_region,
        input_tokens=max(input_tokens, 0),
        output_tokens=max(output_tokens, 0),
        estimated_usd=max(estimated_usd, 0.0),
        latency_ms=max(latency_ms, 1),
    )
