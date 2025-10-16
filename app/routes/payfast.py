import hashlib
import logging
import os
from urllib.parse import urlencode

from fastapi import APIRouter, Request, status
from fastapi.responses import PlainTextResponse

router = APIRouter(prefix="/api/payment/payfast", tags=["payments:payfast"])
log = logging.getLogger("payfast")

def _env(key: str, default: str = "") -> str:
    v = os.getenv(key, default)
    if not v:
        log.warning("Missing ENV %s", key)
    return v

def _md5_signature(kv: dict, passphrase: str | None) -> str:
    # Build query string in the exact order of urlencode, spaces as %20
    data = {k: v for k, v in kv.items() if v is not None and k != "signature"}
    if passphrase:
        data["passphrase"] = passphrase
    qs = urlencode(data).replace("+", "%20")
    return hashlib.md5(qs.encode("utf-8")).hexdigest()

@router.post("/checkout")
async def create_checkout_session(payload: dict):
    """
    Minimal example: accept amount, item_name, name_first/last, email_address, etc.
    Returns a redirect_url to PayFast Sandbox.
    """
    amount = f'{float(payload.get("amount", 100.00)):.2f}'
    item_name = payload.get("item_name", "Cape Control Test Product")

    base = {
        "merchant_id": _env("PAYFAST_MERCHANT_ID"),
        "merchant_key": _env("PAYFAST_MERCHANT_KEY"),
        "return_url": _env("PAYFAST_RETURN_URL"),
        "cancel_url": _env("PAYFAST_CANCEL_URL"),
        "notify_url": _env("PAYFAST_NOTIFY_URL"),
        "amount": amount,
        "item_name": item_name,
        # Optional buyer details (improves UX)
        "name_first": payload.get("name_first"),
        "name_last": payload.get("name_last"),
        "email_address": payload.get("email_address"),
        # Recommended: a unique reference from your DB/order id
        "m_payment_id": payload.get("m_payment_id", "test-" + os.urandom(4).hex()),
    }

    passphrase = _env("PAYFAST_PASSPHRASE")
    signature = _md5_signature(base, passphrase)
    base["signature"] = signature

    process_url = _env("PAYFAST_PROCESS_URL", "https://sandbox.payfast.co.za/eng/process")
    redirect_url = f"{process_url}?{urlencode(base).replace('+', '%20')}"
    return {"redirect_url": redirect_url}

@router.post("/itn")
async def itn_notify(request: Request):
    """
    ITN (Instant Transaction Notification) handler.
    - Verifies signature
    - Logs payload
    - Returns 200 to acknowledge (required by PayFast)
    NOTE: For production, also perform server-side postback validation.
    """
    form = dict((await request.form()).items())
    log.info("PayFast ITN received: %s", form)

    # 1) Signature verification
    received_sig = form.get("signature", "").lower()
    passphrase = _env("PAYFAST_PASSPHRASE")
    expected_sig = _md5_signature(form, passphrase)

    if received_sig != expected_sig:
        log.error("PayFast ITN invalid signature: expected=%s got=%s", expected_sig, received_sig)
        # Per PayFast spec, still reply 200 OK to stop retries, but do not fulfil order.
        return PlainTextResponse("Invalid signature", status_code=status.HTTP_200_OK)

    # 2) (Recommended) Validate source & postback to PayFast (omitted here for simplicity).
    # You should:
    # - Whitelist PayFast domains/IPs if feasible
    # - POST the same payload back to PayFast's validation endpoint and expect 'VALID'
    # See their docs; implement before going live.

    # 3) Process the payment status
    payment_status = form.get("payment_status")  # 'COMPLETE', 'FAILED', 'PENDING'
    m_payment_id = form.get("m_payment_id")      # your order/ref
    pf_payment_id = form.get("pf_payment_id")    # payfast txn id
    amount_gross = form.get("amount_gross")

    log.info("ITN verified. status=%s m_payment_id=%s pf_payment_id=%s amount=%s",
             payment_status, m_payment_id, pf_payment_id, amount_gross)

    # TODO: Update your DB:
    # - Mark order as paid when payment_status == 'COMPLETE'
    # - Store pf_payment_id and raw payload for audit
    # IMPORTANT: Idempotency (avoid double-updates)

    # Always 200 OK (ack) so PayFast stops retrying
    return PlainTextResponse("OK", status_code=status.HTTP_200_OK)
