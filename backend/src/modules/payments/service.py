"""PayFast adapter helpers for checkout sessions and ITN validation."""

from __future__ import annotations

import hashlib
import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Mapping, TypedDict
from urllib.parse import quote

from .config import PayFastSettings

log = logging.getLogger(__name__)


def _serialize_fields(data: Mapping[str, str | int | float | None]) -> Dict[str, str]:
    """Return PayFast-ready key/value pairs (excludes None/empty values)."""

    result: Dict[str, str] = {}
    for key, value in data.items():
        if value is None:
            continue
        string_value = str(value).strip()
        if string_value == "":
            continue
        result[key] = string_value
    return result


def _encode_for_signature(data: Mapping[str, str], passphrase: str | None) -> str:
    segments: list[str] = []
    for key in sorted(data.keys()):
        encoded_key = quote(key)
        encoded_value = quote(data[key])
        segments.append(f"{encoded_key}={encoded_value}")
    payload = "&".join(segments)
    if passphrase:
        payload = f"{payload}&passphrase={quote(passphrase)}"
    return payload


def generate_signature(data: Mapping[str, str], passphrase: str | None) -> str:
    """Generate the PayFast signature for the provided fields."""

    encoded = _encode_for_signature(data, passphrase)
    return hashlib.md5(encoded.encode("utf-8")).hexdigest()


def _format_amount(amount: Decimal | float | str) -> str:
    dec = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{dec:.2f}"


def build_checkout_fields(
    *,
    settings: PayFastSettings,
    amount: Decimal | float | str,
    item_name: str,
    item_description: str | None = None,
    customer_email: str,
    customer_first_name: str | None = None,
    customer_last_name: str | None = None,
    metadata: Mapping[str, str | int | float | None] | None = None,
) -> Dict[str, str]:
    """Create a signed payload for the PayFast checkout form."""

    base_fields = {
        "merchant_id": settings.merchant_id,
        "merchant_key": settings.merchant_key,
        "return_url": settings.return_url,
        "cancel_url": settings.cancel_url,
        "notify_url": settings.notify_url,
        "amount": _format_amount(amount),
        "item_name": item_name,
        "item_description": item_description,
        "email_address": customer_email,
        "name_first": customer_first_name,
        "name_last": customer_last_name,
    }

    if metadata:
        for idx, (key, value) in enumerate(metadata.items(), start=1):
            if idx > 5:
                break
            base_fields[f"custom_str{idx}"] = value

    serialized = _serialize_fields(base_fields)
    signature = generate_signature(serialized, settings.passphrase)
    serialized["signature"] = signature
    return serialized


class CheckoutSession(TypedDict):
    process_url: str
    fields: Dict[str, str]


def create_checkout_session(
    *,
    settings: PayFastSettings,
    amount: Decimal | float | str,
    item_name: str,
    item_description: str | None,
    customer_email: str,
    customer_first_name: str | None,
    customer_last_name: str | None,
    metadata: Mapping[str, str | int | float | None] | None = None,
) -> CheckoutSession:
    fields = build_checkout_fields(
        settings=settings,
        amount=amount,
        item_name=item_name,
        item_description=item_description,
        customer_email=customer_email,
        customer_first_name=customer_first_name,
        customer_last_name=customer_last_name,
        metadata=metadata,
    )
    return {
        "process_url": settings.process_url,
        "fields": fields,
    }


def verify_itn_signature(
    payload: Mapping[str, str],
    *,
    settings: PayFastSettings,
) -> bool:
    """Validate the ITN payload signature (does not perform remote verification)."""

    sanitized = _serialize_fields(payload)
    remote_signature = sanitized.pop("signature", None)
    if not remote_signature:
        log.warning("Missing PayFast signature in ITN payload")
        return False

    local_signature = generate_signature(sanitized, settings.passphrase)
    return local_signature == remote_signature
