"""REST routes for PayFast payments integration."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qsl

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_verified_user
from .config import PayFastSettings, get_payfast_settings
from .constants import get_payfast_product_by_code, get_plan_by_id, PLANS
from . import schemas, service

log = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])


# ---------------------------------------------------------------------------
# Plan catalog (public)
# ---------------------------------------------------------------------------


@router.get("/plans", response_model=schemas.PlansResponse)
def list_plans() -> schemas.PlansResponse:
    """Return the available subscription plans and pricing."""
    plan_list = [
        schemas.PlanOut(
            id=p.id,
            name=p.name,
            description=p.description,
            price_monthly_zar=str(p.price_monthly_zar),
            price_yearly_zar=str(p.price_yearly_zar),
            product_code_monthly=p.product_code_monthly,
            product_code_yearly=p.product_code_yearly,
            features=list(p.features),
            is_default=p.is_default,
            is_enterprise=p.is_enterprise,
        )
        for p in PLANS
    ]
    return schemas.PlansResponse(plans=plan_list)


# ---------------------------------------------------------------------------
# Subscription management (authenticated)
# ---------------------------------------------------------------------------


@router.get("/subscription", response_model=schemas.SubscriptionOut)
def get_subscription(
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> schemas.SubscriptionOut:
    """Get the current user's subscription."""
    sub = (
        db.query(models.Subscription)
        .filter(models.Subscription.user_id == current_user.id)
        .first()
    )
    if not sub:
        # Return a default free subscription representation
        return schemas.SubscriptionOut(
            id="",
            plan_id="free",
            plan_name="Free",
            status="active",
            cancel_at_period_end=False,
        )

    plan = get_plan_by_id(sub.plan_id)
    return schemas.SubscriptionOut(
        id=sub.id,
        plan_id=sub.plan_id,
        plan_name=plan.name if plan else sub.plan_id.title(),
        status=sub.status,
        current_period_start=sub.current_period_start,
        current_period_end=sub.current_period_end,
        cancel_at_period_end=sub.cancel_at_period_end,
        cancelled_at=sub.cancelled_at,
        created_at=sub.created_at,
    )


@router.post("/subscription", response_model=schemas.SubscriptionOut, status_code=201)
def create_subscription(
    payload: schemas.SubscriptionCreateRequest,
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> schemas.SubscriptionOut:
    """Create or update a subscription (initiates checkout for paid plans)."""
    plan = get_plan_by_id(payload.plan_id)
    if not plan:
        raise HTTPException(status_code=400, detail=f"Unknown plan: {payload.plan_id}")

    # Check for existing subscription
    existing = (
        db.query(models.Subscription)
        .filter(models.Subscription.user_id == current_user.id)
        .first()
    )

    now = datetime.now(timezone.utc)

    if existing:
        existing.plan_id = payload.plan_id
        existing.status = "active" if payload.plan_id == "free" else "pending"
        existing.cancel_at_period_end = False
        existing.cancelled_at = None
        if payload.plan_id != "free":
            existing.current_period_start = now
            if payload.billing_cycle == "yearly":
                existing.current_period_end = now + timedelta(days=365)
            else:
                existing.current_period_end = now + timedelta(days=30)
        else:
            existing.current_period_start = now
            existing.current_period_end = None
        existing.payment_provider = "payfast" if payload.plan_id != "free" else None
        db.commit()
        sub = existing
    else:
        sub = models.Subscription(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            plan_id=payload.plan_id,
            status="active" if payload.plan_id == "free" else "pending",
            current_period_start=now,
            current_period_end=(
                (now + timedelta(days=365 if payload.billing_cycle == "yearly" else 30))
                if payload.plan_id != "free"
                else None
            ),
            payment_provider="payfast" if payload.plan_id != "free" else None,
        )
        db.add(sub)
        db.commit()

    log.info("subscription_created user=%s plan=%s cycle=%s", current_user.id, payload.plan_id, payload.billing_cycle)

    return schemas.SubscriptionOut(
        id=sub.id,
        plan_id=sub.plan_id,
        plan_name=plan.name,
        status=sub.status,
        current_period_start=sub.current_period_start,
        current_period_end=sub.current_period_end,
        cancel_at_period_end=sub.cancel_at_period_end,
        cancelled_at=sub.cancelled_at,
        created_at=sub.created_at,
    )


@router.post("/subscription/cancel", response_model=schemas.SubscriptionCancelResponse)
def cancel_subscription(
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> schemas.SubscriptionCancelResponse:
    """Cancel the current subscription at period end."""
    sub = (
        db.query(models.Subscription)
        .filter(models.Subscription.user_id == current_user.id)
        .first()
    )
    if not sub:
        raise HTTPException(status_code=404, detail="No active subscription found")

    if sub.plan_id == "free":
        raise HTTPException(status_code=400, detail="Cannot cancel a free plan")

    sub.cancel_at_period_end = True
    sub.cancelled_at = datetime.now(timezone.utc)
    db.commit()

    log.info("subscription_cancelled user=%s plan=%s", current_user.id, sub.plan_id)

    return schemas.SubscriptionCancelResponse(
        message="Subscription will be cancelled at the end of the current period",
        cancel_at_period_end=True,
        current_period_end=sub.current_period_end,
    )


# ---------------------------------------------------------------------------
# Invoice history (authenticated)
# ---------------------------------------------------------------------------


@router.get("/invoices", response_model=schemas.InvoiceListResponse)
def list_invoices(
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
    limit: int = 50,
    offset: int = 0,
) -> schemas.InvoiceListResponse:
    """List invoices for the current user."""
    query = (
        db.query(models.Invoice)
        .filter(models.Invoice.user_id == current_user.id)
        .order_by(models.Invoice.created_at.desc())
    )
    total = query.count()
    invoices = query.offset(offset).limit(min(limit, 100)).all()

    return schemas.InvoiceListResponse(
        invoices=[
            schemas.InvoiceOut(
                id=inv.id,
                amount=str(inv.amount),
                currency=inv.currency,
                status=inv.status,
                item_name=inv.item_name,
                item_description=inv.item_description,
                payment_provider=inv.payment_provider,
                created_at=inv.created_at,
            )
            for inv in invoices
        ],
        total=total,
    )


# ---------------------------------------------------------------------------
# PayFast checkout
# ---------------------------------------------------------------------------


@router.post("/payfast/checkout", response_model=schemas.PayFastCheckoutResponse)
def create_checkout_session(
    payload: schemas.PayFastCheckoutRequest,
    current_user: models.User = Depends(get_verified_user),
    settings: PayFastSettings = Depends(get_payfast_settings),
    db: Session = Depends(get_session),
) -> schemas.PayFastCheckoutResponse:
    """Generate a signed set of form fields for the PayFast hosted checkout."""

    # Use the authenticated user's email — ignore any email in the payload
    customer_email = current_user.email
    log.info("Checkout initiated by user %s for %s", current_user.id, payload.product_code or payload.item_name)

    amount = payload.amount
    item_name = payload.item_name
    item_description = payload.item_description
    metadata = payload.metadata

    if payload.product_code:
        product = get_payfast_product_by_code(payload.product_code)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown product_code: {payload.product_code}",
            )

        amount = product.amount_zar
        item_name = product.item_name
        item_description = product.item_description

        merged_metadata = {
            "product_code": product.code,
            "purpose": "payfast_live_verification",
            **(payload.metadata or {}),
        }
        # PayFast supports custom_str1..custom_str5.
        if len(merged_metadata) > 5:
            merged_metadata = dict(list(merged_metadata.items())[:5])
        metadata = merged_metadata

    session = service.create_checkout_session(
        settings=settings,
        db=db,
        amount=amount,
        item_name=item_name,
        item_description=item_description,
        customer_email=customer_email,
        customer_first_name=payload.customer_first_name or current_user.first_name,
        customer_last_name=payload.customer_last_name or current_user.last_name,
        metadata=metadata,
    )

    return schemas.PayFastCheckoutResponse(**session)


@router.post("/payfast/itn", response_class=PlainTextResponse)
async def handle_itn(
    request: Request,
    settings: PayFastSettings = Depends(get_payfast_settings),
    db: Session = Depends(get_session),
) -> PlainTextResponse:
    """Handle Instant Transaction Notifications from PayFast."""

    body = await request.body()
    try:
        decoded = body.decode("utf-8")
    except UnicodeDecodeError as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=400, detail="Invalid encoding") from exc

    payload = dict(parse_qsl(decoded, keep_blank_values=True))

    if not payload:
        log.warning("ITN received with empty payload")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Empty ITN payload"
        )

    log.info("ITN payload received: %s", {k: v for k, v in payload.items() if k != "signature"})

    if not service.verify_itn_signature(payload, settings=settings):
        log.warning("ITN signature verification failed")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid PayFast signature",
        )

    # Server-to-server validation
    if not await service.validate_itn_with_server(payload, settings=settings):
        log.warning("ITN server-to-server validation failed")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PayFast server validation failed",
        )

    # Process and persist
    service.process_itn(payload, db)

    return PlainTextResponse("OK", status_code=status.HTTP_200_OK)
