"""
Input sanitization helpers and middleware.

This module is a lightweight-but-practical implementation that supports:
* Text sanitization across multiple strictness levels.
* Prompt-injection and PII detection for AI-facing endpoints.
* FastAPI middleware that rewrites incoming JSON payloads with sanitized data.

The implementation favours simplicity and deterministic behaviour so tests can
exercise the security stack without external dependencies.
"""

from __future__ import annotations

import html
import json
import logging
import re
import time
from enum import Enum
from typing import Any, Dict, Iterable, List, MutableMapping, Optional, Tuple

from starlette.datastructures import MutableHeaders
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

log = logging.getLogger("input_sanitization")


class SanitizationLevel(str, Enum):
    BASIC = "basic"
    STRICT = "strict"
    AI_PROMPT = "ai_prompt"
    USER_DATA = "user_data"
    SEARCH = "search"


PROMPT_INJECTION_PATTERNS: Tuple[re.Pattern[str], ...] = tuple(
    re.compile(pat, re.IGNORECASE)
    for pat in [
        r"\bignore\b.+\binstruction",
        r"\boverride\b.+\bprotocol",
        r"\bdo\s+anything\s+now\b",
        r"\bpretend\b.+\bno\s+restrictions\b",
        r"\breveal\b.+\bsecret",
    ]
)

XSS_PATTERNS: Tuple[re.Pattern[str], ...] = tuple(
    re.compile(pat, re.IGNORECASE)
    for pat in [
        r"<\s*script",
        r"javascript:",
        r"on\w+\s*=",
        r"<\s*iframe",
    ]
)

SQLI_PATTERNS: Tuple[re.Pattern[str], ...] = tuple(
    re.compile(pat, re.IGNORECASE)
    for pat in [
        r"'\s*or\s*'1'='1",
        r"union\s+select",
        r";\s*drop\s+table",
        r"--\s*$",
    ]
)

SEARCH_OPERATOR_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(r"\bsite:\S+", re.IGNORECASE),
    re.compile(r"\binurl:\S+", re.IGNORECASE),
    re.compile(r"\bfiletype:\S+", re.IGNORECASE),
)

PII_PATTERNS: Tuple[Tuple[str, re.Pattern[str]], ...] = (
    ("email", re.compile(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", re.IGNORECASE)),
    ("phone", re.compile(r"\b(?:\+?\d[\d\-\s]{7,}\d)\b")),
    ("ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
)

FIELD_LENGTH_LIMITS: Dict[str, int] = {
    "general_text": 1000,
    "ai_prompt": 4000,
}


def _lift_list(obj: Any) -> List[Any]:
    if isinstance(obj, list):
        return obj
    return [obj]


class InputSanitizer:
    """Sanitize free-form user input with multiple strictness levels."""

    def __init__(self) -> None:
        self._pii_patterns = PII_PATTERNS

    def sanitize_input(
        self,
        text: Any,
        level: SanitizationLevel = SanitizationLevel.BASIC,
        *,
        field_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        original = "" if text is None else str(text)
        sanitized = original
        threats: List[str] = []
        pii_found: List[str] = []
        sanitization_applied = False

        max_length = FIELD_LENGTH_LIMITS.get(
            field_type or ("ai_prompt" if level == SanitizationLevel.AI_PROMPT else "")
        )
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
            threats.append("input_too_long")
            sanitization_applied = True

        if level in {SanitizationLevel.BASIC, SanitizationLevel.STRICT}:
            escaped = html.escape(sanitized, quote=False)
            if escaped != sanitized:
                sanitization_applied = True
                sanitized = escaped
            if level == SanitizationLevel.STRICT:
                stripped = re.sub(r"<[^>]+>", "", sanitized)
                if stripped != sanitized:
                    sanitization_applied = True
                    sanitized = stripped

        if level in {SanitizationLevel.USER_DATA, SanitizationLevel.STRICT}:
            sanitized, changed = self._strip_scripts(sanitized)
            if changed:
                sanitization_applied = True
                threats.append("html_removed")

        if level == SanitizationLevel.SEARCH:
            for pattern in SEARCH_OPERATOR_PATTERNS:
                if pattern.search(sanitized):
                    threats.append("search_operator_detected")
                    sanitized = pattern.sub("", sanitized)
                    sanitization_applied = True

        # Always scan for classic XSS and SQLi markers
        for pattern in XSS_PATTERNS:
            if pattern.search(original):
                threats.append("xss_detected")
                break

        for pattern in SQLI_PATTERNS:
            if pattern.search(original):
                threats.append("sql_injection_detected")
                break

        if level == SanitizationLevel.AI_PROMPT:
            sanitized, changed, prompt_threats = self._handle_prompt_injection(
                sanitized
            )
            if changed:
                sanitization_applied = True
            threats.extend(prompt_threats)

        sanitized, pii, changed = self._redact_pii(sanitized)
        if changed:
            sanitization_applied = True
        if pii:
            pii_found.extend(pii)
            threats.append("pii_redacted")

        is_safe = len(threats) == 0

        return {
            "original": original,
            "sanitized": sanitized,
            "is_safe": is_safe,
            "sanitization_applied": sanitization_applied,
            "threats_detected": list(dict.fromkeys(threats)),
            "pii_found": pii_found,
            "level": level.value,
        }

    def _strip_scripts(self, text: str) -> Tuple[str, bool]:
        cleaned = re.sub(r"<\s*script[^>]*>.*?<\s*/\s*script\s*>", "", text, flags=re.I | re.S)
        cleaned = re.sub(r"javascript:", "", cleaned, flags=re.I)
        return cleaned, cleaned != text

    def _handle_prompt_injection(
        self, text: str
    ) -> Tuple[str, bool, List[str]]:
        threats: List[str] = []
        sanitized = text
        changed = False
        for pattern in PROMPT_INJECTION_PATTERNS:
            if pattern.search(sanitized):
                threats.append("prompt_injection_detected")
                sanitized = pattern.sub("[FILTERED]", sanitized)
                changed = True
        return sanitized, changed, threats

    def _redact_pii(self, text: str) -> Tuple[str, List[str], bool]:
        sanitized = text
        pii_found: List[str] = []
        changed = False

        replacements = {
            "email": "[EMAIL_REDACTED]",
            "phone": "[PHONE_REDACTED]",
            "ssn": "[SSN_REDACTED]",
        }

        for label, pattern in self._pii_patterns:
            matches = list(pattern.finditer(sanitized))
            if not matches:
                continue
            pii_found.append(label)
            sanitized = pattern.sub(replacements[label], sanitized)
            changed = True

        return sanitized, pii_found, changed


_GLOBAL_SANITIZER = InputSanitizer()


def validate_ai_prompt(
    prompt: str,
    context: Optional[MutableMapping[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Validate an AI prompt and optional context metadata.

    Returns a dict with:
        - sanitized_prompt
        - sanitized_context
        - threats_detected / context_threats
        - safety_score (0-100)
        - is_ai_safe (bool)
    """

    prompt_result = _GLOBAL_SANITIZER.sanitize_input(
        prompt, SanitizationLevel.AI_PROMPT, field_type="ai_prompt"
    )
    context_threats: List[str] = []
    sanitized_context: Dict[str, Any] = {}

    if context:
        for key, value in context.items():
            if isinstance(value, str):
                ctx_result = _GLOBAL_SANITIZER.sanitize_input(
                    value, SanitizationLevel.USER_DATA
                )
                sanitized_context[key] = ctx_result["sanitized"]
                context_threats.extend(
                    f"{key}:{threat}" for threat in ctx_result["threats_detected"]
                )
            else:
                sanitized_context[key] = value

    # Simple scoring heuristic: deduct for threats and context issues.
    safety_score = 100
    penalty = 12
    safety_score -= penalty * len(prompt_result["threats_detected"])
    safety_score -= 5 * len(context_threats)
    safety_score = max(0, min(100, safety_score))

    is_ai_safe = safety_score >= 80 and prompt_result["is_safe"]

    return {
        "sanitized_prompt": prompt_result["sanitized"],
        "sanitized_context": sanitized_context,
        "threats_detected": prompt_result["threats_detected"],
        "context_threats": context_threats,
        "pii_found": prompt_result["pii_found"],
        "safety_score": safety_score,
        "is_ai_safe": is_ai_safe,
    }


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """
    Middleware that sanitizes incoming JSON payloads and annotates responses.
    """

    def __init__(
        self,
        app,
        *,
        sanitizer: Optional[InputSanitizer] = None,
        ai_reject_score: int = 70,
    ) -> None:
        super().__init__(app)
        self.sanitizer = sanitizer or _GLOBAL_SANITIZER
        self.ai_reject_score = ai_reject_score

    async def dispatch(self, request: Request, call_next) -> Response:
        sanitized_flag = False
        sanitization_meta: Dict[str, Any] = {}

        if self._should_process(request):
            body_bytes = await request.body()
            if body_bytes:
                try:
                    payload = json.loads(body_bytes)
                except json.JSONDecodeError:
                    payload = None
                if isinstance(payload, dict):
                    (
                        payload,
                        sanitized_flag,
                        sanitization_meta,
                        reject_response,
                    ) = self._process_payload(request, payload)
                    if reject_response is not None:
                        return reject_response
                    if sanitized_flag:
                        self._set_request_body(request, payload)
                elif isinstance(payload, list):
                    new_items = []
                    for item in payload:
                        if not isinstance(item, dict):
                            new_items.append(item)
                            continue
                        (
                            processed,
                            item_sanitized,
                            item_meta,
                            reject_response,
                        ) = self._process_payload(request, item)
                        if reject_response is not None:
                            return reject_response
                        if item_sanitized:
                            sanitized_flag = True
                        new_items.append(processed)
                        sanitization_meta = self._merge_meta(
                            sanitization_meta, item_meta
                        )
                    if sanitized_flag:
                        self._set_request_body(request, new_items)

        response = await call_next(request)

        if sanitized_flag or getattr(request.state, "input_sanitized", False):
            headers = MutableHeaders(response.headers)
            headers["X-Input-Sanitized"] = "true"
            if sanitization_meta.get("threats"):
                headers["X-Input-Sanitization-Threats"] = ",".join(
                    sanitization_meta["threats"]
                )

        return response

    def _should_process(self, request: Request) -> bool:
        if request.method not in {"POST", "PUT", "PATCH"}:
            return False
        content_type = request.headers.get("content-type", "")
        return "application/json" in content_type

    def _process_payload(
        self, request: Request, payload: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], bool, Dict[str, Any], Optional[Response]]:
        sanitized_flag = False
        meta: Dict[str, Any] = {"threats": []}

        path = request.url.path
        if path.startswith("/api/ai/prompt"):
            message = str(payload.get("message", ""))
            context = payload.get("context") if isinstance(payload.get("context"), dict) else {}
            validation = validate_ai_prompt(message, context)
            payload["message"] = validation["sanitized_prompt"]
            payload["context"] = validation["sanitized_context"]
            sanitized_flag = True
            meta["threats"].extend(validation["threats_detected"])
            if not validation["is_ai_safe"] or validation["safety_score"] < self.ai_reject_score:
                return payload, sanitized_flag, meta, JSONResponse(
                    {"error": "Input validation failed", "detail": validation},
                    status_code=400,
                )
            request.state.input_sanitized = True
            return payload, sanitized_flag, meta, None

        for key, value in list(payload.items()):
            if isinstance(value, str):
                level = SanitizationLevel.USER_DATA
                if key.lower() in {"message", "prompt", "notes"}:
                    level = SanitizationLevel.AI_PROMPT
                result = self.sanitizer.sanitize_input(
                    value,
                    level,
                    field_type="general_text",
                )
                if result["sanitized"] != value:
                    sanitized_flag = True
                    payload[key] = result["sanitized"]
                    meta["threats"].extend(result["threats_detected"])
            elif isinstance(value, dict):
                sub_payload, sub_changed = self._sanitize_nested(value)
                if sub_changed:
                    sanitized_flag = True
                    payload[key] = sub_payload

        return payload, sanitized_flag, meta, None

    def _sanitize_nested(
        self, value: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], bool]:
        changed = False
        new_value = dict(value)
        for sub_key, sub_value in list(new_value.items()):
            if isinstance(sub_value, str):
                result = self.sanitizer.sanitize_input(
                    sub_value, SanitizationLevel.USER_DATA
                )
                if result["sanitized"] != sub_value:
                    new_value[sub_key] = result["sanitized"]
                    changed = True
            elif isinstance(sub_value, dict):
                nested, nested_changed = self._sanitize_nested(sub_value)
                if nested_changed:
                    new_value[sub_key] = nested
                    changed = True
            elif isinstance(sub_value, list):
                sanitized_list = []
                list_changed = False
                for item in sub_value:
                    if isinstance(item, str):
                        result = self.sanitizer.sanitize_input(
                            item, SanitizationLevel.USER_DATA
                        )
                        sanitized_list.append(result["sanitized"])
                        if result["sanitized"] != item:
                            list_changed = True
                    elif isinstance(item, dict):
                        nested, nested_changed = self._sanitize_nested(item)
                        sanitized_list.append(nested)
                        if nested_changed:
                            list_changed = True
                    else:
                        sanitized_list.append(item)
                if list_changed:
                    new_value[sub_key] = sanitized_list
                    changed = True
        return new_value, changed

    def _merge_meta(
        self,
        primary: Dict[str, Any],
        secondary: Dict[str, Any],
    ) -> Dict[str, Any]:
        merged = dict(primary)
        if "threats" not in merged:
            merged["threats"] = []
        merged["threats"].extend(_lift_list(secondary.get("threats", [])))
        return merged

    def _set_request_body(self, request: Request, payload: Any) -> None:
        new_body = json.dumps(payload).encode("utf-8")

        async def receive() -> Dict[str, Any]:
            return {"type": "http.request", "body": new_body, "more_body": False}

        request._receive = receive  # type: ignore[attr-defined]
        request._body = new_body  # type: ignore[attr-defined]


__all__ = [
    "InputSanitizer",
    "InputSanitizationMiddleware",
    "SanitizationLevel",
    "validate_ai_prompt",
]
