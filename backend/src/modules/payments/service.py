"""PayFast adapter helpers for checkout sessions and ITN validation."""

from __future__ import annotations

import hashlib
import logging
import uuid
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Mapping, TypedDict
from urllib.parse import quote_plus

import httpx
from sqlalchemy.orm import Session

from backend.src.db import models
from .config import PayFastSettings

log = logging.getLogger(__name__)


def _activate_subscription_on_payment(db: Session, invoice: models.Invoice) -> None:
    """
    Post-payment hook: activate a user's subscription when payment completes.

    Looks up the user's subscription and transitions it from 'pending' or
    'trialing' to 'active' with proper period dates.
    """
    try:
        if not invoice.user_id:
            log.warning("Invoice %s has no user_id, skipping subscription activation", invoice.id)
            return

        sub = (
            db.query(models.Subscription)
            .filter(models.Subscription.user_id == invoice.user_id)
            .first()
        )

        if sub is None:
            log.info("No subscription found for user %s after payment", invoice.user_id)
            return

        if sub.status in ("pending", "trialing"):
            now = datetime.now()
            sub.status = "active"
            sub.current_period_start = now
            # Set period end based on plan interval
            if sub.plan_id in ("pro", "enterprise"):
                sub.current_period_end = now + _timedelta_30_days()
            elif sub.plan_id == "free":
                sub.current_period_end = None  # free tier has no expiry
            sub.cancel_at_period_end = False
            sub.cancelled_at = None
            db.commit()
            log.info(
                "Subscription activated for user %s on plan %s after payment on invoice %s",
                invoice.user_id, sub.plan_id, invoice.id,
            )
        else:
            log.info(
                "Subscription for user %s already in status %s, no activation needed",
                invoice.user_id, sub.status,
            )

    except Exception as e:
        log.error("Failed to activate subscription after payment: %s", e)
        # Don't fail the payment processing — subscription activation is best-effort


def _timedelta_30_days():
    """Return a timedelta of 30 days."""
    from datetime import timedelta
    return timedelta(days=30)


def _serialize_fields(data: Mapping[str, str | int | float | None]) -> Dict[str, str]:
    """Return PayFast-ready key/value pairs (excludes None/empty values)."""

    result: Dict[str, str] = {}
    for key, value in data.items():
        if value is None:
            continue
        string_value = str(value)
        if string_value == "":
            continue
        result[key] = string_value
    return result


def _encode_for_signature(data: Mapping[str, str], passphrase: str | None) -> str:
    """Build the PayFast signature string.

    Follows PayFast's official Python integration sample exactly:
    - Iterate fields in dict insertion order (same as the checkout form)
    - URL-encode each value with ``quote_plus`` (spaces → +)
    - Replace literal ``+`` in values with space before encoding
    - Append passphrase (also URL-encoded) at the end
    """

    payload = ""
    for key, value in data.items():
        if key == "signature":
            continue
        if value is None:
            continue
        value_str = str(value).strip()
        if value_str == "":
            continue
        payload += key + "=" + quote_plus(value_str.replace("+", " ")) + "&"

    # Remove trailing &
    if payload.endswith("&"):
        payload = payload[:-1]

    if passphrase is not None and passphrase.strip() != "":
        payload += f"&passphrase={quote_plus(passphrase.strip())}"
    return payload


def generate_signature(data: Mapping[str, str], passphrase: str | None) -> str:
    """Generate the PayFast signature for the provided fields."""

    encoded = _encode_for_signature(data, passphrase)
    log.info("PayFast signature string: %s", encoded)
    sig = hashlib.md5(encoded.encode("utf-8")).hexdigest()
    log.info("PayFast generated signature: %s", sig)
    return sig


def _format_amount(amount: Decimal | float | str) -> str:
    dec = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{dec:.2f}"


import re

_PAYFAST_SAFE_RE = re.compile(r"[^a-zA-Z0-9 \-]")


def _sanitize_for_payfast(value: str | None, max_len: int = 100) -> str | None:
    """Strip characters not allowed by PayFast (alpha-numeric, hyphens, spaces only)."""
    if value is None:
        return None
    # Replace em/en dashes with hyphens, then strip everything else
    cleaned = value.replace("\u2014", "-").replace("\u2013", "-")
    cleaned = _PAYFAST_SAFE_RE.sub("", cleaned)
    # Collapse multiple spaces
    cleaned = " ".join(cleaned.split())
    return cleaned[:max_len] if cleaned else None


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
    m_payment_id: str | None = None,
) -> Dict[str, str]:
    """Create a signed payload for the PayFast checkout form."""

    # PayFast requires fields in a SPECIFIC order for signature generation.
    # See: https://developers.payfast.co.za/docs#step_1_form_fields
    base_fields = {
        # 1 – Merchant details
        "merchant_id": settings.merchant_id,
        "merchant_key": settings.merchant_key,
        # 2 – Redirect URLs
        "return_url": settings.return_url,
        "cancel_url": settings.cancel_url,
        "notify_url": settings.notify_url,
        # 3 – Buyer details
        "name_first": customer_first_name,
        "name_last": customer_last_name,
        "email_address": customer_email,
        # 4 – Transaction details
        "m_payment_id": m_payment_id,
        "amount": _format_amount(amount),
        "item_name": _sanitize_for_payfast(item_name, 100),
        "item_description": _sanitize_for_payfast(item_description, 255),
    }

    if metadata:
        for idx, value in enumerate(metadata.values(), start=1):
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


def _create_checkout_invoice(
    *,
    db: Session,
    amount: Decimal | float | str,
    item_name: str,
    item_description: str | None,
    customer_email: str,
    customer_first_name: str | None,
    customer_last_name: str | None,
    metadata: Mapping[str, str | int | float | None] | None,
) -> models.Invoice:
    user = db.query(models.User).filter(models.User.email == customer_email).first()
    if not user:
        raise ValueError("No user found for customer_email")

    invoice_id = str(uuid.uuid4())
    invoice = models.Invoice(
        id=invoice_id,
        user_id=user.id,
        amount=Decimal(_format_amount(amount)),
        currency="ZAR",
        status="pending",
        item_name=item_name,
        item_description=item_description,
        customer_email=customer_email,
        customer_first_name=customer_first_name,
        customer_last_name=customer_last_name,
        payment_provider="payfast",
        external_reference=invoice_id,
        metadata_json=dict(metadata) if metadata else None,
    )
    db.add(invoice)
    db.commit()
    return invoice


def create_checkout_session(
    *,
    settings: PayFastSettings,
    db: Session,
    amount: Decimal | float | str,
    item_name: str,
    item_description: str | None,
    customer_email: str,
    customer_first_name: str | None,
    customer_last_name: str | None,
    metadata: Mapping[str, str | int | float | None] | None = None,
) -> CheckoutSession:
    invoice = _create_checkout_invoice(
        db=db,
        amount=amount,
        item_name=item_name,
        item_description=item_description,
        customer_email=customer_email,
        customer_first_name=customer_first_name,
        customer_last_name=customer_last_name,
        metadata=metadata,
    )
    fields = build_checkout_fields(
        settings=settings,
        amount=amount,
        item_name=item_name,
        item_description=item_description,
        customer_email=customer_email,
        customer_first_name=customer_first_name,
        customer_last_name=customer_last_name,
        metadata=metadata,
        m_payment_id=invoice.external_reference,
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

    # Work with a mutable copy — keep insertion order from PayFast
    data: Dict[str, str] = {}
    for key, value in payload.items():
        if key == "signature":
            continue
        if value is None or str(value).strip() == "":
            continue
        data[key] = str(value).strip()

    remote_signature = payload.get("signature")
    if not remote_signature:
        log.warning("Missing PayFast signature in ITN payload")
        return False

    local_signature = generate_signature(data, settings.passphrase)
    if local_signature != remote_signature:
        log.warning(
            "ITN signature mismatch: local=%s remote=%s",
            local_signature,
            remote_signature,
        )
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
            # Post-payment hooks: activate subscription if linked
            _activate_subscription_on_payment(db, invoice)

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
