"""
Stripe Payment Service for Cape Control
Handles subscription management, credit purchases, and webhook processing
"""

import logging
import os

"""
Stripe Payment Service for Cape Control
Handles subscription management, credit purchases, and webhook processing

This implementation keeps the Stripe SDK optional at import-time. If the
Stripe SDK is missing or the secret key is not configured, Stripe-related
methods will raise RuntimeError at call-time. Local database fallbacks are
used where possible for read-only operations.
"""


try:
    import stripe
    STRIPE_AVAILABLE = True
except Exception:
    stripe = None
    STRIPE_AVAILABLE = False

from sqlalchemy.exc import SQLAlchemyError
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

logger = logging.getLogger(__name__)

# Configure stripe api key at import if available. Keep this defensive so import
# does not fail in environments without the SDK or configuration.
if STRIPE_AVAILABLE and stripe is not None:
    try:
        stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", None)
    except Exception:
        # ignore import-time failures
        pass


class StripeService:
    """Service for handling Stripe payment operations. Methods that require
    Stripe will call ``self._require_stripe()`` which raises when Stripe is
    unavailable. Read-only methods (like credit balance) will attempt a local
    DB fallback.
    """

    def __init__(self, db: Session):
        self.db = db
        self.enabled = STRIPE_AVAILABLE and stripe is not None and getattr(settings, "STRIPE_SECRET_KEY", None)
        # Set api key again in case settings were loaded after import
        if self.enabled:
            try:
                stripe.api_key = settings.STRIPE_SECRET_KEY
            except Exception:
                self.enabled = False

    def _require_stripe(self) -> None:
        if not self.enabled:
            raise RuntimeError("Stripe SDK not installed or STRIPE_SECRET_KEY unset. Stripe features are disabled.")

    async def create_customer(self, user: User) -> str:
        self._require_stripe()
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=f"{user.first_name} {user.last_name}".strip(),
                metadata={"user_id": str(user.id), "platform": "cape_control"},
            )
            await self._log_event("customer_created", user.id, {"stripe_customer_id": customer.id})
            return customer.id
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer for user {user.id}: {e}")
            raise Exception(getattr(e, "user_message", str(e)))

    async def _get_or_create_customer_id(self, user: User) -> str:
        # Try to read from DB
        subscription = self.db.query(Subscription).filter(Subscription.user_id == user.id).first()
        if subscription and subscription.stripe_customer_id:
            return subscription.stripe_customer_id
        # Otherwise create via Stripe
        return await self.create_customer(user)

    async def create_subscription(self, user: User, tier: str, payment_method_id: str) -> dict:
        self._require_stripe()
        try:
            if tier not in SUBSCRIPTION_TIERS:
                raise ValueError(f"Invalid subscription tier: {tier}")

            tier_config = SUBSCRIPTION_TIERS[tier]

            # Get or create Stripe customer
            subscription_record = self.db.query(Subscription).filter(Subscription.user_id == user.id).first()
            if subscription_record and subscription_record.stripe_customer_id:
                customer_id = subscription_record.stripe_customer_id
            else:
                customer_id = await self.create_customer(user)

            # Handle free tier locally
            if tier == "Basic" and tier_config.get("price", 0) == 0:
                return await self._create_free_subscription(user, customer_id, tier)

            # Ensure a price exists in Stripe (development helper)
            price_id = await self._get_or_create_price(tier, tier_config)

            # Attach payment method and set default
            stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)
            stripe.Customer.modify(customer_id, invoice_settings={"default_payment_method": payment_method_id})

            stripe_subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                payment_behavior="default_incomplete",
                payment_settings={"save_default_payment_method": "on_subscription"},
                expand=["latest_invoice.payment_intent"],
            )

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
                    status="Active",
                )
                self.db.add(subscription_record)

            await self._save_payment_method(user.id, payment_method_id, customer_id)
            self.db.commit()

            await self._log_event("subscription_created", user.id, {"tier": tier, "price": tier_config.get("price"), "stripe_subscription_id": stripe_subscription.id})

            return {
                "subscription_id": stripe_subscription.id,
                "status": stripe_subscription.status,
                "client_secret": getattr(getattr(stripe_subscription, "latest_invoice", None), "payment_intent", None) and stripe_subscription.latest_invoice.payment_intent.client_secret,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create subscription for user {user.id}: {e}")
            self.db.rollback()
            raise Exception(getattr(e, "user_message", str(e)))
        except Exception:
            self.db.rollback()
            raise

    async def purchase_credits(self, user: User, pack_size: str, payment_method_id: str) -> dict:
        self._require_stripe()
        try:
            if pack_size not in CREDIT_PACKS:
                raise ValueError(f"Invalid credit pack: {pack_size}")

            pack_config = CREDIT_PACKS[pack_size]
            total_credits = pack_config.get("credits", 0) + pack_config.get("bonus", 0)

            customer_id = await self._get_or_create_customer_id(user)

            payment_intent = stripe.PaymentIntent.create(
                amount=pack_config["price"],
                currency="usd",
                customer=customer_id,
                payment_method=payment_method_id,
                confirmation_method="manual",
                confirm=True,
                metadata={"user_id": str(user.id), "pack_size": pack_size, "credits": str(total_credits), "type": "credit_purchase"},
            )

            if payment_intent.status == "succeeded":
                await self._add_credits(user.id, total_credits, payment_intent.id, pack_size)
                await self._log_event("credits_purchased", user.id, {"pack_size": pack_size, "credits": total_credits, "price": pack_config["price"], "payment_intent_id": payment_intent.id})
                return {"payment_intent_id": payment_intent.id, "status": "succeeded", "credits_added": total_credits}

            return {"payment_intent_id": payment_intent.id, "status": payment_intent.status, "client_secret": getattr(payment_intent, "client_secret", None)}

        except stripe.error.StripeError as e:
            logger.error(f"Failed to purchase credits for user {user.id}: {e}")
            raise Exception(getattr(e, "user_message", str(e)))

    async def deduct_credits(self, user_id: int, amount: int, description: str, agent_id: str | None = None) -> bool:
        """Deduct credits locally. This method does not require Stripe and will
        operate on local DB state.
        """
        try:
            credits_record = self.db.query(Credits).filter(Credits.user_id == user_id).first()
            if not credits_record or credits_record.balance < amount:
                return False

            credits_record.balance -= amount

            transaction = CreditTransaction(
                user_id=user_id,
                transaction_type="usage",
                amount=-amount,
                description=description,
                agent_id=agent_id,
            )
            self.db.add(transaction)
            self.db.commit()

            await self._log_event("credits_used", user_id, {"amount": amount, "description": description, "agent_id": agent_id, "new_balance": credits_record.balance})
            return True

        except SQLAlchemyError as e:
            logger.error(f"Database error deducting credits: {e}")
            self.db.rollback()
            return False

    async def cancel_subscription(self, user: User) -> bool:
        self._require_stripe()
        try:
            subscription = self.db.query(Subscription).filter(Subscription.user_id == user.id, Subscription.status == "Active").first()
            if not subscription or not subscription.stripe_subscription_id:
                return False

            stripe.Subscription.cancel(subscription.stripe_subscription_id)

            subscription.status = "Cancelled"
            self.db.commit()

            await self._log_event("subscription_cancelled", user.id, {"tier": subscription.tier, "stripe_subscription_id": subscription.stripe_subscription_id})
            return True
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription for user {user.id}: {e}")
            self.db.rollback()
            return False

    async def get_subscription_status(self, user_id: int) -> dict | None:
        # Attempt to use Stripe if available, otherwise return local DB record
        try:
            if self.enabled:
                # Fetch from Stripe using customer/subscription IDs stored locally
                subscription = self.db.query(Subscription).filter(Subscription.user_id == user_id).first()
                if subscription and subscription.stripe_subscription_id:
                    stripe_sub = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
                    return {
                        "tier": subscription.tier,
                        "status": stripe_sub.status,
                        "start_date": getattr(subscription, "start_date", None),
                        "end_date": getattr(subscription, "end_date", None),
                        "stripe_subscription_id": subscription.stripe_subscription_id,
                    }
            # Fallback to local DB
            subscription = self.db.query(Subscription).filter(Subscription.user_id == user_id).first()
            if not subscription:
                return None
            return {
                "tier": subscription.tier,
                "status": subscription.status,
                "start_date": subscription.start_date,
                "end_date": subscription.end_date,
                "stripe_subscription_id": subscription.stripe_subscription_id,
            }
        except Exception:
            logger.exception("Error fetching subscription status")
            return None

    async def get_credit_balance(self, user_id: int) -> int:
        credits = self.db.query(Credits).filter(Credits.user_id == user_id).first()
        return credits.balance if credits else 0

    async def _create_free_subscription(self, user: User, customer_id: str, tier: str) -> dict:
        subscription = self.db.query(Subscription).filter(Subscription.user_id == user.id).first()
        if subscription:
            subscription.tier = tier
            subscription.status = "Active"
            subscription.stripe_customer_id = customer_id
        else:
            subscription = Subscription(user_id=user.id, stripe_customer_id=customer_id, tier=tier, status="Active")
            self.db.add(subscription)
        self.db.commit()
        await self._log_event("free_subscription_created", user.id, {"tier": tier})
        return {"subscription_id": None, "status": "active"}

    async def _get_or_create_price(self, tier: str, tier_config: dict) -> str:
        # Ensure Stripe is available for price creation/retrieval
        self._require_stripe()
        try:
            # This is a development helper. In production prices should be created
            # in the Stripe dashboard and referenced by ID.
            price = stripe.Price.create(
                unit_amount=tier_config["price"],
                currency="usd",
                recurring={"interval": "month"},
                product_data={"name": f"Cape Control {tier} Plan"},
                metadata={"tier": tier},
            )
            return price.id
        except stripe.error.StripeError:
            raise Exception("Price creation failed. Please configure prices in Stripe dashboard.")

    async def _add_credits(self, user_id: int, amount: int, payment_intent_id: str, pack_size: str):
        credits_record = self.db.query(Credits).filter(Credits.user_id == user_id).first()
        if credits_record:
            credits_record.balance += amount
        else:
            credits_record = Credits(user_id=user_id, balance=amount, stripe_payment_intent_id=payment_intent_id)
            self.db.add(credits_record)

        transaction = CreditTransaction(
            user_id=user_id,
            transaction_type="purchase",
            amount=amount,
            description=f"Purchased {pack_size} credit pack",
            stripe_payment_intent_id=payment_intent_id,
        )
        self.db.add(transaction)
        self.db.commit()

    async def _save_payment_method(self, user_id: int, payment_method_id: str, customer_id: str):
        try:
            pm = stripe.PaymentMethod.retrieve(payment_method_id)
            existing = self.db.query(PaymentMethod).filter(PaymentMethod.stripe_payment_method_id == payment_method_id).first()
            if not existing:
                payment_method = PaymentMethod(
                    user_id=user_id,
                    stripe_payment_method_id=payment_method_id,
                    type=pm.type,
                    last_four=pm.card.last4 if getattr(pm, "card", None) else None,
                    brand=pm.card.brand if getattr(pm, "card", None) else None,
                    exp_month=pm.card.exp_month if getattr(pm, "card", None) else None,
                    exp_year=pm.card.exp_year if getattr(pm, "card", None) else None,
                    is_default=True,
                )
                self.db.add(payment_method)
        except Exception:
            logger.warning("Could not save payment method details")

    async def _log_event(self, event_type: str, user_id: int, data: dict):
        try:
            event = PaymentAnalyticsEvent(event_type=event_type, user_id=user_id, data=data)
            self.db.add(event)
            self.db.commit()
        except Exception:
            logger.exception("Failed to log analytics event")


class WebhookService:
    """Service for handling Stripe webhooks"""

    def __init__(self, db: Session):
        self.db = db
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    def verify_webhook(self, payload: bytes, signature: str | None):
        # If stripe is not installed, fall back to parsing JSON without signature verification
        if not STRIPE_AVAILABLE:
            import json
            try:
                return json.loads(payload)
            except Exception:
                logger.error("Invalid JSON payload (stripe SDK missing)")
                raise

        try:
            event = stripe.Webhook.construct_event(payload, signature, settings.STRIPE_WEBHOOK_SECRET)
            return event
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            raise
        except Exception as e:
            logger.error(f"Invalid signature or webhook error: {e}")
            raise

    async def handle_webhook(self, event: dict) -> bool:
        try:
            etype = event.get("type") if isinstance(event, dict) else getattr(event, "type", None)
            if etype == "customer.subscription.updated":
                return await self._handle_subscription_updated(event["data"]["object"])
            elif etype == "payment_intent.succeeded":
                return await self._handle_payment_succeeded(event["data"]["object"])
            elif etype == "payment_intent.payment_failed":
                return await self._handle_payment_failed(event["data"]["object"])
            else:
                logger.info(f"Unhandled webhook event: {etype}")
                return True
        except Exception:
            logger.exception("Error handling webhook")
            return False

    async def _handle_subscription_updated(self, subscription: dict) -> bool:
        try:
            sub_record = self.db.query(Subscription).filter(Subscription.stripe_subscription_id == subscription["id"]).first()
            if sub_record:
                status_map = {"active": "Active", "canceled": "Cancelled", "past_due": "PastDue", "incomplete": "Inactive"}
                new_status = status_map.get(subscription.get("status"), "Inactive")
                old_status = sub_record.status
                sub_record.status = new_status
                self.db.commit()
                event = PaymentAnalyticsEvent(event_type="subscription_status_changed", user_id=sub_record.user_id, data={"old_status": old_status, "new_status": subscription.get("status"), "stripe_subscription_id": subscription["id"]})
                self.db.add(event)
                self.db.commit()
            return True
        except Exception:
            logger.exception("Error handling subscription update")
            return False

    async def _handle_payment_succeeded(self, payment_intent: dict) -> bool:
        try:
            metadata = payment_intent.get("metadata", {})
            if metadata.get("type") == "credit_purchase":
                user_id = int(metadata.get("user_id"))
                event = PaymentAnalyticsEvent(event_type="payment_succeeded", user_id=user_id, data={"payment_intent_id": payment_intent["id"], "amount": payment_intent.get("amount"), "type": "credit_purchase"})
                self.db.add(event)
                self.db.commit()
            return True
        except Exception:
            logger.exception("Error handling payment success")
            return False

    async def _handle_payment_failed(self, payment_intent: dict) -> bool:
        try:
            metadata = payment_intent.get("metadata", {})
            user_id = metadata.get("user_id")
            if user_id:
                event = PaymentAnalyticsEvent(event_type="payment_failed", user_id=int(user_id), data={"payment_intent_id": payment_intent["id"], "failure_reason": payment_intent.get("last_payment_error", {}).get("message"), "amount": payment_intent.get("amount")})
                self.db.add(event)
                self.db.commit()
            return True
        except Exception:
            logger.exception("Error handling payment failure")
            return False
    


class WebhookService:
    """Service for handling Stripe webhooks"""
    
    def __init__(self, db: Session):
        self.db = db
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    def verify_webhook(self, payload: bytes, signature: str):
        """Verify Stripe webhook signature and return event.
        If stripe SDK is unavailable, parse the payload as JSON and return it.
        """
        # If stripe is not installed, fall back to parsing JSON without signature verification
        if not STRIPE_AVAILABLE:
            import json
            try:
                return json.loads(payload)
            except Exception:
                logger.error("Invalid JSON payload (stripe SDK missing)")
                raise

        try:
            event = stripe.Webhook.construct_event(
                payload, signature, settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            raise
        except Exception as e:
            # Catch stripe.error.SignatureVerificationError and other stripe errors
            logger.error(f"Invalid signature or webhook error: {e}")
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
