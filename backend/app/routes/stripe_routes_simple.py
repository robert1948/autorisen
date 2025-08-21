import logging
import os

import stripe
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

router = APIRouter()

# Pydantic models
class CreateCheckoutSessionRequest(BaseModel):
    price_id: str
    mode: str = "subscription"  # 'subscription' or 'payment'
    quantity: int | None = 1
    success_url: str | None = None
    cancel_url: str | None = None

@router.post("/create-checkout-session")
async def create_checkout_session(request: CreateCheckoutSessionRequest):
    """Create a Stripe checkout session for subscriptions or one-time payments"""
    try:
        # Default URLs
        success_url = request.success_url or "http://localhost:3000/success"
        cancel_url = request.cancel_url or "http://localhost:3000/cancel"
        
        # Create checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': request.price_id,
                'quantity': request.quantity,
            }],
            mode=request.mode,
            success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=cancel_url,
        )
        
        return {"checkout_url": session.url, "session_id": session.id}
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Checkout session creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create checkout session")

@router.post("/create-portal-session")
async def create_portal_session():
    """Create a Stripe customer portal session"""
    try:
        # For now, return a placeholder - would need customer ID in real implementation
        return {"message": "Customer portal session endpoint ready"}
    except Exception as e:
        logger.error(f"Portal session creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create portal session")

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    try:
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        
        # Verify webhook signature
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        if webhook_secret:
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, webhook_secret
                )
            except ValueError:
                logger.error("Invalid payload")
                raise HTTPException(status_code=400, detail="Invalid payload")
            except stripe.error.SignatureVerificationError:
                logger.error("Invalid signature")
                raise HTTPException(status_code=400, detail="Invalid signature")
        else:
            # For development without webhook secret
            import json
            event = json.loads(payload)
        
        # Handle the event
        event_type = event['type']
        logger.info(f"Received webhook event: {event_type}")
        
        if event_type == 'checkout.session.completed':
            session = event['data']['object']
            logger.info(f"Checkout session completed: {session['id']}")
        elif event_type == 'customer.subscription.created':
            subscription = event['data']['object']
            logger.info(f"Subscription created: {subscription['id']}")
        elif event_type == 'invoice.payment_succeeded':
            invoice = event['data']['object']
            logger.info(f"Invoice payment succeeded: {invoice['id']}")
        else:
            logger.info(f"Unhandled event type: {event_type}")
        
        return {"received": True}
        
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.get("/customer")
async def get_customer():
    """Get customer information"""
    return {"message": "Customer endpoint ready"}

@router.get("/prices")
async def get_prices():
    """Get available pricing plans"""
    try:
        # Fetch prices from Stripe
        prices = stripe.Price.list(active=True, expand=['data.product'])
        
        formatted_prices = []
        for price in prices.data:
            formatted_prices.append({
                "id": price.id,
                "product_name": price.product.name if price.product else "Unknown",
                "amount": price.unit_amount,
                "currency": price.currency,
                "interval": price.recurring.interval if price.recurring else None,
                "interval_count": price.recurring.interval_count if price.recurring else None
            })
        
        return {"prices": formatted_prices}
        
    except stripe.error.StripeError as e:
        logger.error(f"Failed to fetch prices: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status")
async def stripe_status():
    """Check Stripe integration status"""
    try:
        # Test Stripe API connection
        account = stripe.Account.retrieve()
        
        return {
            "status": "connected",
            "account_id": account.id,
            "country": account.country,
            "webhook_configured": bool(os.getenv("STRIPE_WEBHOOK_SECRET")),
            "api_version": stripe.api_version
        }
        
    except stripe.error.AuthenticationError:
        return {
            "status": "authentication_failed",
            "message": "Invalid Stripe API key"
        }
    except Exception as e:
        logger.error(f"Stripe status check failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
