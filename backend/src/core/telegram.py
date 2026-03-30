"""Telegram notification helper for operational alerts."""

from __future__ import annotations

import logging

import httpx
from backend.src.core.config import settings

log = logging.getLogger("telegram")


def send_telegram_alert(message: str) -> None:
    """Send an operational alert to Telegram when enabled.

    This is best-effort and must never raise to callers.
    """

    if not settings.telegram_alerts_enabled:
        return

    token = settings.telegram_bot_token
    chat_id = settings.telegram_chat_id
    if not token or not chat_id:
        log.warning(
            "Telegram alerts enabled but TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID missing"
        )
        return

    payload = {
        "chat_id": chat_id,
        "text": message[:4096],
        "disable_web_page_preview": True,
    }
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    try:
        with httpx.Client(timeout=6.0) as client:
            response = client.post(url, json=payload)
        if response.status_code >= 400:
            log.warning(
                "Telegram alert failed status=%s body=%s",
                response.status_code,
                response.text[:400],
            )
    except Exception as exc:  # pragma: no cover - network-specific
        log.warning("Telegram alert send exception: %s", exc)
