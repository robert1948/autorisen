import logging
import os
from typing import Any, Dict

try:
    import stripe  # type: ignore
    STRIPE_AVAILABLE = True
except Exception:
    stripe = None  # type: ignore
    STRIPE_AVAILABLE = False

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

logger = logging.getLogger(__name__)

if STRIPE_AVAILABLE and stripe is not None:
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

router = APIRouter()


class CreateCheckoutSessionRequest(BaseModel):
    price_id: str
    mode: str = "subscription"
    quantity: int | None = 1
    success_url: str | None = None
    cancel_url: str | None = None


@router.post("/create-checkout-session")
async def create_checkout_session(request: CreateCheckoutSessionRequest) -> Dict[str, Any]:
    if not STRIPE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Stripe integration not available")

    try:
        success_url = request.success_url or "http://localhost:3000/success"
        cancel_url = request.cancel_url or "http://localhost:3000/cancel"

        session = stripe.checkout.Session.create(  # type: ignore
            payment_method_types=["card"],
            line_items=[{"price": request.price_id, "quantity": request.quantity}],
            mode=request.mode,
            success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=cancel_url,
        )
        return {"checkout_url": session.url, "session_id": session.id}
    except Exception as e:
        logger.error("Checkout creation failed: %s", e)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request) -> Dict[str, Any]:
    payload = await request.body()
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    if webhook_secret and STRIPE_AVAILABLE:
        try:
            event = stripe.Webhook.construct_event(payload, request.headers.get("stripe-signature"), webhook_secret)  # type: ignore
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid webhook payload")
    else:
        # best-effort parse
        import json

        try:
            event = json.loads(payload)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # minimal handling
    event_type = event.get("type") if isinstance(event, dict) else None
    logger.info("Stripe event: %s", event_type)
    return {"received": True}


@router.get("/status")
async def stripe_status() -> Dict[str, Any]:
    if not STRIPE_AVAILABLE:
        return {"status": "unavailable"}

    try:
        account = stripe.Account.retrieve()  # type: ignore
        return {"status": "connected", "account_id": getattr(account, "id", None)}
    except Exception as e:
        logger.error("Stripe status failed: %s", e)
        return {"status": "error", "message": str(e)}
