"""PayFast adapter helpers for checkout sessions and ITN validation."""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Mapping, TypedDict
from urllib.parse import quote

import httpx
from sqlalchemy.orm import Session

from backend.src.db import models
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


async def validate_itn_with_server(
    payload: Mapping[str, str],
    *,
    settings: PayFastSettings,
) -> bool:
    """
    Validate the ITN payload by posting it back to PayFast.
    Returns True if PayFast responds with 'VALID'.
    """
    try:
        async with httpx.AsyncClient() as client:
            # PayFast expects the data exactly as received
            response = await client.post(settings.validate_url, data=payload)
            response.raise_for_status()
            return response.text.strip() == "VALID"
    except httpx.HTTPError as e:
        log.error(f"PayFast validation failed: {e}")
        return False


def process_itn(
    payload: Mapping[str, str],
    db: Session,
) -> None:
    """
    Process a validated ITN payload:
    1. Find the invoice by external_reference (m_payment_id).
    2. Create/Update the transaction record.
    3. Update the invoice status.
    """
    # 1. Extract key fields
    pf_payment_id = payload.get("pf_payment_id")
    payment_status = payload.get("payment_status")
    m_payment_id = payload.get("m_payment_id")
    amount_gross = payload.get("amount_gross")

    if not m_payment_id:
        log.error("ITN missing m_payment_id")
        return

    # 2. Find Invoice
    invoice = (
        db.query(models.Invoice)
        .filter(models.Invoice.external_reference == m_payment_id)
        .first()
    )

    if not invoice:
        log.error(f"Invoice not found for m_payment_id: {m_payment_id}")
        return

    # 3. Check for existing transaction to avoid duplicates
    transaction = (
        db.query(models.Transaction)
        .filter(models.Transaction.provider_transaction_id == pf_payment_id)
        .first()
    )

    if not transaction:
        transaction = models.Transaction(
            invoice_id=invoice.id,
            amount=Decimal(amount_gross) if amount_gross else Decimal("0.00"),
            currency="ZAR",  # PayFast is ZAR only usually
            payment_provider="payfast",
            provider_transaction_id=pf_payment_id,
            provider_reference=m_payment_id,
            transaction_type="payment",
            status="pending",  # Will update below
            itn_data=payload,
        )
        db.add(transaction)
    else:
        # Update existing transaction with latest ITN data
        transaction.itn_data = payload
        transaction.updated_at = datetime.now()

    # 4. Update Statuses
    # PayFast statuses: COMPLETE, FAILED, PENDING, CANCELLED

    if payment_status == "COMPLETE":
        transaction.status = "completed"
        transaction.processed_at = datetime.now()

        # Only mark invoice paid if it wasn't already
        if invoice.status != "paid":
            invoice.status = "paid"
            # TODO: Trigger post-payment hooks (e.g. allocate credits)

    elif payment_status == "FAILED":
        transaction.status = "failed"
        if invoice.status == "pending":
            invoice.status = "failed"

    elif payment_status == "CANCELLED":
        transaction.status = "cancelled"
        if invoice.status == "pending":
            invoice.status = "cancelled"

    elif payment_status == "PENDING":
        transaction.status = "pending"
        # Invoice stays pending

    db.commit()
    log.info(f"Processed ITN for Invoice {invoice.id}: {payment_status}")
