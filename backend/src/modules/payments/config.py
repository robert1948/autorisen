"""Configuration helpers for the PayFast adapter."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class PayFastSettings:
    """Runtime configuration for interacting with PayFast."""

    merchant_id: str
    merchant_key: str
    return_url: str
    cancel_url: str
    notify_url: str
    mode: str = "sandbox"
    passphrase: str | None = None

    @property
    def process_url(self) -> str:
        if self.mode.lower() == "production":
            return "https://www.payfast.co.za/eng/process"
        return "https://sandbox.payfast.co.za/eng/process"

    @property
    def validate_url(self) -> str:
        if self.mode.lower() == "production":
            return "https://www.payfast.co.za/eng/query/validate"
        return "https://sandbox.payfast.co.za/eng/query/validate"


def _env(key: str, *, required: bool = True) -> str | None:
    value = os.getenv(key)
    if required and not value:
        raise RuntimeError(f"Missing required PayFast configuration: {key}")
    return value


@lru_cache(maxsize=1)
def get_payfast_settings() -> PayFastSettings:
    """Load PayFast settings from environment variables (cached)."""

    return PayFastSettings(
        merchant_id=_env("PAYFAST_MERCHANT_ID") or "",
        merchant_key=_env("PAYFAST_MERCHANT_KEY") or "",
        return_url=_env("PAYFAST_RETURN_URL") or "",
        cancel_url=_env("PAYFAST_CANCEL_URL") or "",
        notify_url=_env("PAYFAST_NOTIFY_URL") or "",
        mode=os.getenv("PAYFAST_MODE", "sandbox"),
        passphrase=os.getenv("PAYFAST_PASSPHRASE") or None,
    )


def reset_payfast_settings_cache() -> None:
    """Clear the cached settings (useful for tests)."""

    get_payfast_settings.cache_clear()
