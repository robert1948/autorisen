"""
Payment API endpoints for Cape Control
Handles subscription, credit purchase, and payment management
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.models.payment import CREDIT_PACKS, SUBSCRIPTION_TIERS
from app.routes.auth_enhanced import get_current_user
from app.services.stripe_service import StripeService, WebhookService

router = APIRouter(prefix="/api/payment", tags=["Payment"])
logger = logging.getLogger(__name__)

# Pydantic models for request/response

class SubscriptionRequest(BaseModel):
    tier: str = Field(..., description="Subscription tier: Basic, Pro, or Enterprise")
    payment_method_id: str = Field(..., description="Stripe payment method ID")

class SubscriptionResponse(BaseModel):
    subscription_id: str | None
    status: str
    client_secret: str | None
    tier: str

class CreditPurchaseRequest(BaseModel):
    pack_size: str = Field(..., description="Credit pack size: small, medium, or large")
    payment_method_id: str = Field(..., description="Stripe payment method ID")

class CreditPurchaseResponse(BaseModel):
    payment_intent_id: str
    status: str
    credits_added: int | None
    client_secret: str | None

class SubscriptionStatusResponse(BaseModel):
    tier: str
    status: str
    start_date: str | None
    end_date: str | None
    features: list[str]
    api_calls_limit: int

class CreditBalanceResponse(BaseModel):
    balance: int
    recent_transactions: list[dict]

class CustomAgentRequest(BaseModel):
    description: str = Field(..., min_length=10, max_length=2000)
    requirements: dict | None = None
    budget_range: str | None = None
    timeline: str | None = None

# Subscription endpoints

@router.post("/subscription/subscribe", response_model=SubscriptionResponse)
async def create_subscription(
    request: SubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update user subscription"""
    try:
        # Validate tier
        if request.tier not in SUBSCRIPTION_TIERS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid subscription tier. Must be one of: {list(SUBSCRIPTION_TIERS.keys())}"
            )
        
        stripe_service = StripeService(db)
        result = await stripe_service.create_subscription(
            current_user, request.tier, request.payment_method_id
        )
        
        return SubscriptionResponse(
            subscription_id=result.get("subscription_id"),
            status=result["status"],
            client_secret=result.get("client_secret"),
            tier=request.tier
        )
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Subscription creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process subscription"
        )

@router.get("/subscription/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user subscription status"""
    try:
        stripe_service = StripeService(db)
        subscription = await stripe_service.get_subscription_status(current_user.id)
        
        if not subscription:
            # Default to Basic tier
            tier = "Basic"
            status = "Active"
        else:
            tier = subscription["tier"]
            status = subscription["status"]
        
        tier_config = SUBSCRIPTION_TIERS[tier]
        
        return SubscriptionStatusResponse(
            tier=tier,
            status=status,
            start_date=subscription["start_date"].isoformat() if subscription and subscription["start_date"] else None,
            end_date=subscription["end_date"].isoformat() if subscription and subscription["end_date"] else None,
            features=tier_config["features"],
            api_calls_limit=tier_config["api_calls"]
        )
        
    except Exception as e:
        logger.error(f"Failed to get subscription status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subscription status"
        )

@router.post("/subscription/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel user subscription"""
    try:
        stripe_service = StripeService(db)
        success = await stripe_service.cancel_subscription(current_user)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )
        
        return {"message": "Subscription cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )

# Credit endpoints

@router.post("/credits/purchase", response_model=CreditPurchaseResponse)
async def purchase_credits(
    request: CreditPurchaseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Purchase credit pack"""
    try:
        # Validate pack size
        if request.pack_size not in CREDIT_PACKS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid pack size. Must be one of: {list(CREDIT_PACKS.keys())}"
            )
        
        stripe_service = StripeService(db)
        result = await stripe_service.purchase_credits(
            current_user, request.pack_size, request.payment_method_id
        )
        
        return CreditPurchaseResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Credit purchase failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process credit purchase"
        )

@router.get("/credits/balance", response_model=CreditBalanceResponse)
async def get_credit_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user credit balance and recent transactions"""
    try:
        stripe_service = StripeService(db)
        balance = await stripe_service.get_credit_balance(current_user.id)
        
        # Get recent transactions
        from app.models.payment import CreditTransaction
        recent_transactions = db.query(CreditTransaction).filter(
            CreditTransaction.user_id == current_user.id
        ).order_by(CreditTransaction.created_at.desc()).limit(10).all()
        
        transactions = [
            {
                "id": str(t.id),
                "type": t.transaction_type,
                "amount": t.amount,
                "description": t.description,
                "created_at": t.created_at.isoformat(),
                "agent_id": t.agent_id
            }
            for t in recent_transactions
        ]
        
        return CreditBalanceResponse(
            balance=balance,
            recent_transactions=transactions
        )
        
    except Exception as e:
        logger.error(f"Failed to get credit balance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve credit balance"
        )

@router.post("/credits/deduct")
async def deduct_credits(
    amount: int,
    description: str,
    agent_id: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deduct credits for agent usage (internal API)"""
    try:
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Credit amount must be positive"
            )
        
        stripe_service = StripeService(db)
        success = await stripe_service.deduct_credits(
            current_user.id, amount, description, agent_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Insufficient credits"
            )
        
        # Return new balance
        new_balance = await stripe_service.get_credit_balance(current_user.id)
        
        return {
            "success": True,
            "credits_deducted": amount,
            "new_balance": new_balance
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to deduct credits: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deduct credits"
        )

# Upsell endpoints

@router.post("/custom-agent/request")
async def request_custom_agent(
    request: CustomAgentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request custom agent development"""
    try:
        from app.models.payment import CustomRequest
        
        # Create custom request
        custom_request = CustomRequest(
            user_id=current_user.id,
            description=request.description,
            requirements=request.requirements,
            budget_range=request.budget_range,
            timeline=request.timeline,
            status="Pending"
        )
        
        db.add(custom_request)
        db.commit()
        
        # Log analytics event
        stripe_service = StripeService(db)
        await stripe_service._log_event("custom_agent_requested", current_user.id, {
            "request_id": str(custom_request.id),
            "budget_range": request.budget_range,
            "timeline": request.timeline
        })
        
        return {
            "request_id": str(custom_request.id),
            "status": "pending",
            "message": "Custom agent request submitted. We'll contact you with a quote within 24 hours."
        }
        
    except Exception as e:
        logger.error(f"Failed to create custom agent request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit request"
        )

@router.get("/custom-agent/requests")
async def get_custom_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's custom agent requests"""
    try:
        from app.models.payment import CustomRequest
        
        requests = db.query(CustomRequest).filter(
            CustomRequest.user_id == current_user.id
        ).order_by(CustomRequest.created_at.desc()).all()
        
        return [
            {
                "id": str(r.id),
                "description": r.description,
                "status": r.status,
                "quote_amount": float(r.quote_amount) if r.quote_amount else None,
                "budget_range": r.budget_range,
                "timeline": r.timeline,
                "created_at": r.created_at.isoformat(),
                "updated_at": r.updated_at.isoformat()
            }
            for r in requests
        ]
        
    except Exception as e:
        logger.error(f"Failed to get custom requests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve requests"
        )

# Support endpoints

@router.post("/support/ticket")
async def create_support_ticket(
    title: str,
    description: str,
    priority: str = "Medium",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create support ticket"""
    try:
        from app.models.payment import SupportTicket
        
        if priority not in ["Low", "Medium", "High", "Critical"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid priority level"
            )
        
        ticket = SupportTicket(
            user_id=current_user.id,
            title=title,
            description=description,
            priority=priority,
            status="Open"
        )
        
        db.add(ticket)
        db.commit()
        
        return {
            "ticket_id": str(ticket.id),
            "status": "open",
            "message": "Support ticket created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create support ticket: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create support ticket"
        )

# Pricing information endpoint

@router.get("/pricing")
async def get_pricing_info():
    """Get pricing information for tiers and credit packs"""
    return {
        "subscription_tiers": {
            tier: {
                "price_usd": config["price"] / 100,  # Convert cents to dollars
                "api_calls": config["api_calls"],
                "features": config["features"],
                "support": config["support"]
            }
            for tier, config in SUBSCRIPTION_TIERS.items()
        },
        "credit_packs": {
            pack: {
                "credits": config["credits"],
                "bonus": config["bonus"],
                "total_credits": config["credits"] + config["bonus"],
                "price_usd": config["price"] / 100,  # Convert cents to dollars
                "value": f"${(config['price'] / 100) / (config['credits'] + config['bonus']):.4f} per credit"
            }
            for pack, config in CREDIT_PACKS.items()
        }
    }

# Webhook endpoint

@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Stripe webhooks"""
    try:
        payload = await request.body()
        signature = request.headers.get("Stripe-Signature")
        
        webhook_service = WebhookService(db)
        event = webhook_service.verify_webhook(payload, signature)
        
        success = await webhook_service.handle_webhook(event)
        
        if success:
            return JSONResponse(content={"status": "success"})
        else:
            return JSONResponse(
                content={"status": "error"}, 
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=status.HTTP_400_BAD_REQUEST
        )
