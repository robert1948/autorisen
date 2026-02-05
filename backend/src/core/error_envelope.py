from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError


ErrorFields = Dict[str, str]


def build_error_envelope(
    code: str, message: str, fields: Optional[ErrorFields] = None
) -> Dict[str, Any]:
    error: Dict[str, Any] = {"code": code, "message": message}
    if fields:
        error["fields"] = fields
    return {"error": error}


def _coerce_message(detail: Any) -> str:
    if isinstance(detail, str):
        return detail
    if isinstance(detail, dict) and "detail" in detail:
        return str(detail.get("detail"))
    return str(detail)


def map_http_exception(exc: HTTPException) -> Tuple[str, str, Optional[ErrorFields]]:
    message = _coerce_message(exc.detail)
    status = exc.status_code

    if status == 401:
        if "refresh" in message.lower():
            return "INVALID_REFRESH_TOKEN", message, None
        if "registration token" in message.lower():
            return "MISSING_REGISTRATION_TOKEN", message, None
        if "invalid credentials" in message.lower():
            return "INVALID_CREDENTIALS", message, None
        return "UNAUTHORIZED", message, None

    if status == 403:
        if "csrf" in message.lower():
            return "CSRF_FAILED", message, None
        return "FORBIDDEN", message, None

    if status == 409:
        return "CONFLICT", message, None

    if status == 429:
        return "RATE_LIMITED", message, None

    if status == 422:
        return "VALIDATION_ERROR", message, None

    if status == 404:
        return "NOT_FOUND", message, None

    if status == 400:
        return "BAD_REQUEST", message, None

    return "ERROR", message, None


def validation_fields(exc: RequestValidationError) -> ErrorFields:
    fields: ErrorFields = {}
    for err in exc.errors():
        loc = list(err.get("loc", []))
        if loc and loc[0] in {"body", "query", "path", "header"}:
            loc = loc[1:]
        key = ".".join(str(item) for item in loc) if loc else "non_field"
        msg = err.get("msg") or "Invalid value"
        fields.setdefault(key, str(msg))
    return fields
