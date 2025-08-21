"""Stripe routes (guarded).

This module avoids importing `stripe` at import time so the app can start when
the Stripe SDK isn't installed. Any route using Stripe verifies availability
and returns 503 if the integration is not present.
"""

import logging
import os
from typing import Optional

try:
    import stripe
    STRIPE_AVAILABLE = True
except Exception:
    stripe = None
    STRIPE_AVAILABLE = False

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..core.auth import get_current_user
from ..models import User
from ..database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/stripe", tags=["stripe"])


# Dependency factory
def get_stripe_service(db: Session = Depends(get_db)):
    if not STRIPE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Stripe integration not available")
    from ..services.stripe_service import StripeService
    return StripeService(db)


class CreateCheckoutSessionRequest(BaseModel):
    price_id: str
    mode: str = "subscription"
    quantity: Optional[int] = 1
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class CreatePortalSessionRequest(BaseModel):
    return_url: Optional[str] = None


class WebhookResponse(BaseModel):
    received: bool = True


@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CreateCheckoutSessionRequest,
    current_user: User = Depends(get_current_user),
    stripe_service = Depends(get_stripe_service)
):
    try:
        session = await stripe_service.create_checkout_session(
            user=current_user,
            price_id=request.price_id,
            mode=request.mode,
            quantity=request.quantity,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
        )
        return {"session_id": getattr(session, 'id', None), "url": getattr(session, 'url', None)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request):
    if not STRIPE_AVAILABLE:
        return JSONResponse({"error": "Stripe integration not available"}, status_code=503)
    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

        if not webhook_secret:
            logger.warning("STRIPE_WEBHOOK_SECRET not configured")
            return JSONResponse({"error": "Webhook secret not configured"}, status_code=400)

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except ValueError:
            logger.error("Invalid payload in webhook")
            return JSONResponse({"error": "Invalid payload"}, status_code=400)
        except Exception:
            logger.error("Invalid signature in webhook")
            return JSONResponse({"error": "Invalid signature"}, status_code=400)

        from ..services.stripe_service import StripeService
        await StripeService.handle_webhook_event(event)
        return WebhookResponse()
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return JSONResponse({"error": "Webhook processing failed"}, status_code=500)


@router.get("/status")
async def stripe_status():
    if not STRIPE_AVAILABLE:
        return {"status": "unavailable"}
    try:
        account = stripe.Account.retrieve()
        return {
            "status": "ok",
            "account_id": account.id,
            "country": account.country,
            "charges_enabled": account.charges_enabled,
            "payouts_enabled": account.payouts_enabled,
        }
    except Exception as e:
        logger.error(f"Stripe status check failed: {e}")
        return {"status": "error", "error": str(e)}
    