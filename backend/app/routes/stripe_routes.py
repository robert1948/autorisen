"""
Sfrom fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import stripe
import os
import logging

from ..services.stripe_service import StripeService
from ..core.auth import get_current_user
from ..models import User
from ..database import get_dbnt routes for CapeControl platform
Handles subscriptions, one-time payments, and webhooks
"""

import logging
import os

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ..core.auth import get_current_user
from ..models import User
from ..services.stripe_service import StripeService

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

router = APIRouter(prefix="/api/stripe", tags=["stripe"])

def get_stripe_service(db: Session = Depends(get_db)) -> StripeService:
    """Dependency to get StripeService instance"""
    return StripeService(db)

# Pydantic models
class CreateCheckoutSessionRequest(BaseModel):
    price_id: str
    mode: str = "subscription"  # 'subscription' or 'payment'
    quantity: int | None = 1
    success_url: str | None = None
    cancel_url: str | None = None

class CreatePortalSessionRequest(BaseModel):
    return_url: str | None = None

class WebhookResponse(BaseModel):
    received: bool = True

@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CreateCheckoutSessionRequest,
    current_user: User = Depends(get_current_user),
    stripe_service: StripeService = Depends(get_stripe_service)
):
    """
    Create a Stripe Checkout session for subscriptions or one-time payments
    """
    try:
        # Get frontend origin for URLs
        frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
        
        # Default URLs if not provided
        success_url = request.success_url or f"{frontend_origin}/billing/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = request.cancel_url or f"{frontend_origin}/billing/cancel"
        
        # Create checkout session
        session = await stripe_service.create_checkout_session(
            user=current_user,
            price_id=request.price_id,
            mode=request.mode,
            quantity=request.quantity,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        return {"session_id": session.id, "url": session.url}
        
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/create-portal-session")
async def create_portal_session(
    request: CreatePortalSessionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create a Stripe Customer Portal session for managing subscriptions
    """
    try:
        # Ensure user has a Stripe customer ID
        if not current_user.stripe_customer_id:
            # Create customer if doesn't exist
            customer = await stripe_service.create_customer(current_user)
            current_user.stripe_customer_id = customer.id
            # Note: You'll need to save this to database
        
        frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
        return_url = request.return_url or f"{frontend_origin}/billing"
        
        # Create portal session
        session = await stripe_service.create_portal_session(
            customer_id=current_user.stripe_customer_id,
            return_url=return_url
        )
        
        return {"url": session.url}
        
    except Exception as e:
        logger.error(f"Error creating portal session: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhooks for subscription and payment events
    """
    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        
        if not webhook_secret:
            logger.warning("STRIPE_WEBHOOK_SECRET not configured")
            return JSONResponse({"error": "Webhook secret not configured"}, status_code=400)
        
        # Verify webhook signature
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except ValueError:
            logger.error("Invalid payload in webhook")
            return JSONResponse({"error": "Invalid payload"}, status_code=400)
        except stripe.SignatureVerificationError:
            logger.error("Invalid signature in webhook")
            return JSONResponse({"error": "Invalid signature"}, status_code=400)
        
        # Process the event
        await stripe_service.handle_webhook_event(event)
        
        return WebhookResponse()
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return JSONResponse({"error": "Webhook processing failed"}, status_code=500)

@router.get("/customer")
async def get_customer_info(current_user: User = Depends(get_current_user)):
    """
    Get current user's Stripe customer information
    """
    try:
        if not current_user.stripe_customer_id:
            return {"customer": None, "subscriptions": []}
        
        customer_info = await stripe_service.get_customer_info(current_user.stripe_customer_id)
        return customer_info
        
    except Exception as e:
        logger.error(f"Error fetching customer info: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/prices")
async def get_prices():
    """
    Get available Stripe prices for subscriptions and credits
    """
    try:
        prices = await stripe_service.get_active_prices()
        return {"prices": prices}
        
    except Exception as e:
        logger.error(f"Error fetching prices: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status")
async def stripe_status():
    """
    Check Stripe integration status
    """
    try:
        # Test API key
        account = stripe.Account.retrieve()
        
        return {
            "status": "ok",
            "account_id": account.id,
            "country": account.country,
            "charges_enabled": account.charges_enabled,
            "payouts_enabled": account.payouts_enabled
        }
    except Exception as e:
        logger.error(f"Stripe status check failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }
