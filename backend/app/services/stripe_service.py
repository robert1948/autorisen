"""
Stripe Payment Service for Cape Control
Handles subscription management, credit purchases, and webhook processing
"""

import logging
import os

import stripe
from sqlalchemy.orm import Session

from app.config import settings
from app.models import User
from app.models.payment import (
    CREDIT_PACKS,
    SUBSCRIPTION_TIERS,
    Credits,
    CreditTransaction,
    PaymentAnalyticsEvent,
    PaymentMethod,
    Subscription,
)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)

import logging

import stripe
from sqlalchemy.exc import SQLAlchemyError

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

logger = logging.getLogger(__name__)


class StripeService:
    """Service for handling Stripe payment operations"""
    
    def __init__(self, db: Session):
        self.db = db
        
    async def create_customer(self, user: User) -> str:
        """Create a Stripe customer for a user"""
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=f"{user.first_name} {user.last_name}".strip(),
                metadata={
                    "user_id": str(user.id),
                    "platform": "cape_control"
                }
            )
            
            # Log analytics event
            await self._log_event("customer_created", user.id, {
                "stripe_customer_id": customer.id
            })
            
            return customer.id
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer for user {user.id}: {e}")
            raise Exception(f"Payment service error: {e.user_message}")
    
    async def create_subscription(self, user: User, tier: str, payment_method_id: str) -> dict:
        """Create or update a user subscription"""
        try:
            # Validate tier
            if tier not in SUBSCRIPTION_TIERS:
                raise ValueError(f"Invalid subscription tier: {tier}")
            
            tier_config = SUBSCRIPTION_TIERS[tier]
            
            # Get or create Stripe customer
            subscription_record = self.db.query(Subscription).filter(
                Subscription.user_id == user.id
            ).first()
            
            if subscription_record and subscription_record.stripe_customer_id:
                customer_id = subscription_record.stripe_customer_id
            else:
                customer_id = await self.create_customer(user)
            
            # Handle free tier
            if tier == "Basic" and tier_config["price"] == 0:
                return await self._create_free_subscription(user, customer_id, tier)
            
            # Create price if not exists (in production, these should be pre-created in Stripe)
            price_id = await self._get_or_create_price(tier, tier_config)
            
            # Attach payment method to customer
            stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)
            
            # Set as default payment method
            stripe.Customer.modify(
                customer_id,
                invoice_settings={"default_payment_method": payment_method_id}
            )
            
            # Create subscription
            stripe_subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                payment_behavior="default_incomplete",
                payment_settings={"save_default_payment_method": "on_subscription"},
                expand=["latest_invoice.payment_intent"]
            )
            
            # Save subscription to database
            if subscription_record:
                subscription_record.tier = tier
                subscription_record.stripe_subscription_id = stripe_subscription.id
                subscription_record.status = "Active"
                subscription_record.stripe_customer_id = customer_id
            else:
                subscription_record = Subscription(
                    user_id=user.id,
                    stripe_customer_id=customer_id,
                    stripe_subscription_id=stripe_subscription.id,
                    tier=tier,
                    status="Active"
                )
                self.db.add(subscription_record)
            
            # Save payment method
            await self._save_payment_method(user.id, payment_method_id, customer_id)
            
            self.db.commit()
            
            # Log analytics event
            await self._log_event("subscription_created", user.id, {
                "tier": tier,
                "price": tier_config["price"],
                "stripe_subscription_id": stripe_subscription.id
            })
            
            return {
                "subscription_id": stripe_subscription.id,
                "status": stripe_subscription.status,
                "client_secret": stripe_subscription.latest_invoice.payment_intent.client_secret
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create subscription for user {user.id}: {e}")
            self.db.rollback()
            raise Exception(f"Payment service error: {e.user_message}")
        except Exception as e:
            logger.error(f"Unexpected error creating subscription: {e}")
            self.db.rollback()
            raise
    
    async def purchase_credits(self, user: User, pack_size: str, payment_method_id: str) -> dict:
        """Purchase credit pack"""
        try:
            # Validate pack size
            if pack_size not in CREDIT_PACKS:
                raise ValueError(f"Invalid credit pack: {pack_size}")
            
            pack_config = CREDIT_PACKS[pack_size]
            total_credits = pack_config["credits"] + pack_config["bonus"]
            
            # Get or create Stripe customer
            customer_id = await self._get_or_create_customer_id(user)
            
            # Create payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=pack_config["price"],
                currency="usd",
                customer=customer_id,
                payment_method=payment_method_id,
                confirmation_method="manual",
                confirm=True,
                metadata={
                    "user_id": str(user.id),
                    "pack_size": pack_size,
                    "credits": str(total_credits),
                    "type": "credit_purchase"
                }
            )
            
            if payment_intent.status == "succeeded":
                # Add credits to user account
                await self._add_credits(user.id, total_credits, payment_intent.id, pack_size)
                
                # Log analytics event
                await self._log_event("credits_purchased", user.id, {
                    "pack_size": pack_size,
                    "credits": total_credits,
                    "price": pack_config["price"],
                    "payment_intent_id": payment_intent.id
                })
                
                return {
                    "payment_intent_id": payment_intent.id,
                    "status": "succeeded",
                    "credits_added": total_credits
                }
            else:
                return {
                    "payment_intent_id": payment_intent.id,
                    "status": payment_intent.status,
                    "client_secret": payment_intent.client_secret
                }
                
        except stripe.error.StripeError as e:
            logger.error(f"Failed to purchase credits for user {user.id}: {e}")
            raise Exception(f"Payment service error: {e.user_message}")
        except Exception as e:
            logger.error(f"Unexpected error purchasing credits: {e}")
            raise
    
    async def deduct_credits(self, user_id: int, amount: int, description: str, agent_id: str = None) -> bool:
        """Deduct credits from user account"""
        try:
            credits_record = self.db.query(Credits).filter(Credits.user_id == user_id).first()
            
            if not credits_record or credits_record.balance < amount:
                return False
            
            # Deduct credits
            credits_record.balance -= amount
            
            # Log transaction
            transaction = CreditTransaction(
                user_id=user_id,
                transaction_type="usage",
                amount=-amount,
                description=description,
                agent_id=agent_id
            )
            self.db.add(transaction)
            self.db.commit()
            
            # Log analytics event
            await self._log_event("credits_used", user_id, {
                "amount": amount,
                "description": description,
                "agent_id": agent_id,
                "new_balance": credits_record.balance
            })
            
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Database error deducting credits: {e}")
            self.db.rollback()
            return False
    
    async def cancel_subscription(self, user: User) -> bool:
        """Cancel user subscription"""
        try:
            subscription = self.db.query(Subscription).filter(
                Subscription.user_id == user.id,
                Subscription.status == "Active"
            ).first()
            
            if not subscription or not subscription.stripe_subscription_id:
                return False
            
            # Cancel in Stripe
            stripe.Subscription.cancel(subscription.stripe_subscription_id)
            
            # Update in database
            subscription.status = "Cancelled"
            self.db.commit()
            
            # Log analytics event
            await self._log_event("subscription_cancelled", user.id, {
                "tier": subscription.tier,
                "stripe_subscription_id": subscription.stripe_subscription_id
            })
            
            return True
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription for user {user.id}: {e}")
            self.db.rollback()
            return False
    
    async def get_subscription_status(self, user_id: int) -> dict | None:
        """Get user subscription status"""
        subscription = self.db.query(Subscription).filter(
            Subscription.user_id == user_id
        ).first()
        
        if not subscription:
            return None
        
        return {
            "tier": subscription.tier,
            "status": subscription.status,
            "start_date": subscription.start_date,
            "end_date": subscription.end_date,
            "stripe_subscription_id": subscription.stripe_subscription_id
        }
    
    async def get_credit_balance(self, user_id: int) -> int:
        """Get user credit balance"""
        credits = self.db.query(Credits).filter(Credits.user_id == user_id).first()
        return credits.balance if credits else 0
    
    # Private helper methods
    
    async def _create_free_subscription(self, user: User, customer_id: str, tier: str) -> dict:
        """Create a free subscription record"""
        subscription = self.db.query(Subscription).filter(
            Subscription.user_id == user.id
        ).first()
        
        if subscription:
            subscription.tier = tier
            subscription.status = "Active"
            subscription.stripe_customer_id = customer_id
        else:
            subscription = Subscription(
                user_id=user.id,
                stripe_customer_id=customer_id,
                tier=tier,
                status="Active"
            )
            self.db.add(subscription)
        
        self.db.commit()
        
        await self._log_event("free_subscription_created", user.id, {"tier": tier})
        
        return {
            "subscription_id": None,
            "status": "active"
        }
    
    async def _get_or_create_price(self, tier: str, tier_config: dict) -> str:
        """Get or create Stripe price for subscription tier"""
        # In production, prices should be pre-created in Stripe dashboard
        # This is for development/testing
        try:
            price = stripe.Price.create(
                unit_amount=tier_config["price"],
                currency="usd",
                recurring={"interval": "month"},
                product_data={"name": f"Cape Control {tier} Plan"},
                metadata={"tier": tier}
            )
            return price.id
        except stripe.error.StripeError:
            # If price creation fails, you should have pre-created prices
            # This is a fallback for development
            raise Exception("Price creation failed. Please configure prices in Stripe dashboard.")
    
    async def _get_or_create_customer_id(self, user: User) -> str:
        """Get existing customer ID or create new one"""
        subscription = self.db.query(Subscription).filter(
            Subscription.user_id == user.id
        ).first()
        
        if subscription and subscription.stripe_customer_id:
            return subscription.stripe_customer_id
        
        return await self.create_customer(user)
    
    async def _add_credits(self, user_id: int, amount: int, payment_intent_id: str, pack_size: str):
        """Add credits to user account"""
        credits_record = self.db.query(Credits).filter(Credits.user_id == user_id).first()
        
        if credits_record:
            credits_record.balance += amount
        else:
            credits_record = Credits(
                user_id=user_id,
                balance=amount,
                stripe_payment_intent_id=payment_intent_id
            )
            self.db.add(credits_record)
        
        # Log transaction
        transaction = CreditTransaction(
            user_id=user_id,
            transaction_type="purchase",
            amount=amount,
            description=f"Purchased {pack_size} credit pack",
            stripe_payment_intent_id=payment_intent_id
        )
        self.db.add(transaction)
        self.db.commit()
    
    async def _save_payment_method(self, user_id: int, payment_method_id: str, customer_id: str):
        """Save payment method details"""
        try:
            pm = stripe.PaymentMethod.retrieve(payment_method_id)
            
            # Check if already exists
            existing = self.db.query(PaymentMethod).filter(
                PaymentMethod.stripe_payment_method_id == payment_method_id
            ).first()
            
            if not existing:
                payment_method = PaymentMethod(
                    user_id=user_id,
                    stripe_payment_method_id=payment_method_id,
                    type=pm.type,
                    last_four=pm.card.last4 if pm.card else None,
                    brand=pm.card.brand if pm.card else None,
                    exp_month=pm.card.exp_month if pm.card else None,
                    exp_year=pm.card.exp_year if pm.card else None,
                    is_default=True
                )
                self.db.add(payment_method)
                
        except stripe.error.StripeError as e:
            logger.warning(f"Could not save payment method details: {e}")
    
    async def _log_event(self, event_type: str, user_id: int, data: dict):
        """Log analytics event"""
        try:
            event = PaymentAnalyticsEvent(
                event_type=event_type,
                user_id=user_id,
                data=data
            )
            self.db.add(event)
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to log analytics event: {e}")


class WebhookService:
    """Service for handling Stripe webhooks"""
    
    def __init__(self, db: Session):
        self.db = db
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    def verify_webhook(self, payload: bytes, signature: str) -> stripe.Event:
        """Verify Stripe webhook signature and return event"""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            raise
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            raise
    
    async def handle_webhook(self, event: dict) -> bool:
        """Handle webhook event"""
        try:
            if event["type"] == "customer.subscription.updated":
                return await self._handle_subscription_updated(event["data"]["object"])
            elif event["type"] == "payment_intent.succeeded":
                return await self._handle_payment_succeeded(event["data"]["object"])
            elif event["type"] == "payment_intent.payment_failed":
                return await self._handle_payment_failed(event["data"]["object"])
            else:
                logger.info(f"Unhandled webhook event: {event['type']}")
                return True
                
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return False
    
    async def _handle_subscription_updated(self, subscription: dict) -> bool:
        """Handle subscription status updates"""
        try:
            sub_record = self.db.query(Subscription).filter(
                Subscription.stripe_subscription_id == subscription["id"]
            ).first()
            
            if sub_record:
                # Map Stripe status to our status
                status_map = {
                    "active": "Active",
                    "canceled": "Cancelled",
                    "past_due": "PastDue",
                    "incomplete": "Inactive"
                }
                
                sub_record.status = status_map.get(subscription["status"], "Inactive")
                self.db.commit()
                
                # Log analytics event
                event = PaymentAnalyticsEvent(
                    event_type="subscription_status_changed",
                    user_id=sub_record.user_id,
                    data={
                        "old_status": sub_record.status,
                        "new_status": subscription["status"],
                        "stripe_subscription_id": subscription["id"]
                    }
                )
                self.db.add(event)
                self.db.commit()
                
            return True
            
        except Exception as e:
            logger.error(f"Error handling subscription update: {e}")
            return False
    
    async def _handle_payment_succeeded(self, payment_intent: dict) -> bool:
        """Handle successful payments"""
        try:
            metadata = payment_intent.get("metadata", {})
            
            if metadata.get("type") == "credit_purchase":
                # Credit purchase succeeded - credits should already be added
                user_id = int(metadata.get("user_id"))
                
                # Log success event
                event = PaymentAnalyticsEvent(
                    event_type="payment_succeeded",
                    user_id=user_id,
                    data={
                        "payment_intent_id": payment_intent["id"],
                        "amount": payment_intent["amount"],
                        "type": "credit_purchase"
                    }
                )
                self.db.add(event)
                self.db.commit()
                
            return True
            
        except Exception as e:
            logger.error(f"Error handling payment success: {e}")
            return False
    
    async def _handle_payment_failed(self, payment_intent: dict) -> bool:
        """Handle failed payments"""
        try:
            metadata = payment_intent.get("metadata", {})
            user_id = metadata.get("user_id")
            
            if user_id:
                # Log failure event
                event = PaymentAnalyticsEvent(
                    event_type="payment_failed",
                    user_id=int(user_id),
                    data={
                        "payment_intent_id": payment_intent["id"],
                        "failure_reason": payment_intent.get("last_payment_error", {}).get("message"),
                        "amount": payment_intent["amount"]
                    }
                )
                self.db.add(event)
                self.db.commit()
                
                # TODO: Send notification email to user
                
            return True
            
        except Exception as e:
            logger.error(f"Error handling payment failure: {e}")
            return False
