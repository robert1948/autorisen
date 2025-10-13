"""Google reCAPTCHA verification helper."""

from __future__ import annotations

from typing import Optional

import httpx

from backend.src.core.config import settings

_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


async def verify(token: str, remote_ip: Optional[str] = None) -> bool:
    """Return True when the provided token passes verification."""

    if settings.disable_recaptcha or not settings.recaptcha_secret:
        return True

    data: dict[str, str] = {
        "secret": settings.recaptcha_secret,
        "response": token,
    }
    if remote_ip:
        data["remoteip"] = remote_ip

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(_VERIFY_URL, data=data)
            response.raise_for_status()
    except httpx.HTTPError:
        return False

    payload = response.json()
    return bool(payload.get("success"))

