"""REST routes for PayFast payments integration."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import parse_qsl

from backend.src.db import models
from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_verified_user
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from . import schemas, service
from .config import PayFastSettings, get_payfast_settings
from .constants import PLANS, get_payfast_product_by_code, get_plan_by_id

log = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])


def _serialize_payment_method(m: models.PaymentMethod) -> dict[str, Any]:
    def _iso(dt: datetime | None) -> str:
        if dt is None:
            return datetime.now(timezone.utc).isoformat()
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()

    return {
        "id": m.id,
        "userId": m.user_id,
        "provider": m.provider,
        "methodType": m.method_type,
        "isDefault": bool(m.is_default),
        "isActive": bool(m.is_active),
        "providerToken": m.provider_token or "",
        "lastFour": m.last_four,
        "cardBrand": m.card_brand,
        "expiryMonth": m.expiry_month,
        "expiryYear": m.expiry_year,
        "metadata": m.metadata_json or {},
        "createdAt": _iso(m.created_at),
        "updatedAt": _iso(m.updated_at),
    }


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
# Payment methods (authenticated)
# ---------------------------------------------------------------------------


@router.get("/methods")
def list_payment_methods(
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> list[dict[str, Any]]:
    """List stored payment methods for the current user."""
    methods = (
        db.query(models.PaymentMethod)
        .filter(models.PaymentMethod.user_id == current_user.id)
        .order_by(
            models.PaymentMethod.is_default.desc(),
            models.PaymentMethod.created_at.desc(),
        )
        .all()
    )

    return [_serialize_payment_method(m) for m in methods]


@router.post("/methods")
def create_payment_method(
    payload: schemas.PaymentMethodCreateRequest,
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> dict[str, Any]:
    """Create a new stored payment method for the current user."""
    if payload.is_default:
        (
            db.query(models.PaymentMethod)
            .filter(models.PaymentMethod.user_id == current_user.id)
            .update({models.PaymentMethod.is_default: False}, synchronize_session=False)
        )

    method = models.PaymentMethod(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        provider="payfast",
        method_type=payload.method_type,
        is_default=payload.is_default,
        is_active=True,
        provider_token=str(uuid.uuid4()),
        last_four=payload.last_four,
        card_brand=payload.card_brand,
        expiry_month=payload.expiry_month,
        expiry_year=payload.expiry_year,
        metadata_json=dict(payload.metadata_json),
    )
    db.add(method)
    db.commit()
    db.refresh(method)
    return _serialize_payment_method(method)


@router.patch("/methods/{method_id}")
def update_payment_method(
    method_id: str,
    payload: schemas.PaymentMethodUpdateRequest,
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> dict[str, Any]:
    """Update an existing payment method for the current user."""
    method = (
        db.query(models.PaymentMethod)
        .filter(
            models.PaymentMethod.id == method_id,
            models.PaymentMethod.user_id == current_user.id,
        )
        .first()
    )
    if not method:
        raise HTTPException(status_code=404, detail="Payment method not found")

    if payload.is_default is True:
        (
            db.query(models.PaymentMethod)
            .filter(models.PaymentMethod.user_id == current_user.id)
            .update({models.PaymentMethod.is_default: False}, synchronize_session=False)
        )

    updates = payload.model_dump(exclude_unset=True)
    if "method_type" in updates:
        method.method_type = updates["method_type"]
    if "is_default" in updates:
        method.is_default = bool(updates["is_default"])
    if "is_active" in updates:
        method.is_active = bool(updates["is_active"])
    if "last_four" in updates:
        method.last_four = updates["last_four"]
    if "card_brand" in updates:
        method.card_brand = updates["card_brand"]
    if "expiry_month" in updates:
        method.expiry_month = updates["expiry_month"]
    if "expiry_year" in updates:
        method.expiry_year = updates["expiry_year"]

    db.commit()
    db.refresh(method)
    return _serialize_payment_method(method)


@router.delete("/methods/{method_id}")
def delete_payment_method(
    method_id: str,
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> dict[str, str]:
    """Delete a stored payment method for the current user."""
    method = (
        db.query(models.PaymentMethod)
        .filter(
            models.PaymentMethod.id == method_id,
            models.PaymentMethod.user_id == current_user.id,
        )
        .first()
    )
    if not method:
        raise HTTPException(status_code=404, detail="Payment method not found")

    db.delete(method)
    db.commit()
    return {"status": "deleted"}


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

    log.info(
        "subscription_created user=%s plan=%s cycle=%s",
        current_user.id,
        payload.plan_id,
        payload.billing_cycle,
    )

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

    all_invoices = query.all()

    paid_invoices = [inv for inv in all_invoices if inv.status == "paid"]
    latest_pending_by_key: dict[tuple[str, str, str], datetime] = {}
    deduped_invoices: list[models.Invoice] = []
    for inv in all_invoices:
        if inv.status != "pending":
            deduped_invoices.append(inv)
            continue

        # Suppress stale duplicate pending records when a matching paid invoice exists
        # around the same checkout window.
        has_matching_paid = any(
            paid.item_name == inv.item_name
            and paid.amount == inv.amount
            and abs((paid.created_at - inv.created_at).total_seconds()) <= 86400
            for paid in paid_invoices
        )
        if has_matching_paid:
            continue

        # Also suppress duplicate pending entries created in quick succession
        # for the same invoice item/amount combination.
        pending_key = (
            inv.item_name or "",
            str(inv.amount),
            inv.currency or "ZAR",
        )
        latest_pending_created_at = latest_pending_by_key.get(pending_key)
        if latest_pending_created_at is not None:
            within_duplicate_window = (
                abs((latest_pending_created_at - inv.created_at).total_seconds())
                <= 86400
            )
            if within_duplicate_window:
                continue

        latest_pending_by_key[pending_key] = inv.created_at
        deduped_invoices.append(inv)

    total = len(deduped_invoices)
    invoices = deduped_invoices[offset : offset + min(limit, 100)]

    return schemas.InvoiceListResponse(
        invoices=[
            schemas.InvoiceOut(
                id=inv.id,
                invoice_number=inv.invoice_number,
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


@router.get("/invoices/{invoice_id}", response_model=schemas.InvoiceDetailOut)
def get_invoice_detail(
    invoice_id: str,
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> schemas.InvoiceDetailOut:
    """Get full invoice detail including transaction history."""
    invoice = (
        db.query(models.Invoice)
        .filter(
            models.Invoice.id == invoice_id,
            models.Invoice.user_id == current_user.id,
        )
        .first()
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    transactions = (
        db.query(models.Transaction)
        .filter(models.Transaction.invoice_id == invoice.id)
        .order_by(models.Transaction.created_at.desc())
        .all()
    )

    return schemas.InvoiceDetailOut(
        id=invoice.id,
        invoice_number=invoice.invoice_number,
        amount=str(invoice.amount),
        currency=invoice.currency,
        status=invoice.status,
        item_name=invoice.item_name,
        item_description=invoice.item_description,
        customer_email=invoice.customer_email,
        customer_first_name=invoice.customer_first_name,
        customer_last_name=invoice.customer_last_name,
        payment_provider=invoice.payment_provider,
        external_reference=invoice.external_reference,
        transactions=[
            schemas.TransactionOut(
                id=txn.id,
                amount=str(txn.amount),
                currency=txn.currency,
                status=txn.status,
                transaction_type=txn.transaction_type,
                amount_fee=str(txn.amount_fee) if txn.amount_fee else None,
                amount_net=str(txn.amount_net) if txn.amount_net else None,
                payment_provider=txn.payment_provider,
                provider_transaction_id=txn.provider_transaction_id,
                processed_at=txn.processed_at,
                created_at=txn.created_at,
            )
            for txn in transactions
        ],
        created_at=invoice.created_at,
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
    log.info(
        "Checkout initiated by user %s for %s",
        current_user.id,
        payload.product_code or payload.item_name,
    )

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

    log.info(
        "ITN payload received: %s",
        {k: v for k, v in payload.items() if k != "signature"},
    )

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


# ---------------------------------------------------------------------------
# Payment status lookup (for return pages)
# ---------------------------------------------------------------------------


@router.get("/status/latest", response_model=schemas.InvoiceOut)
def get_latest_payment_status(
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> schemas.InvoiceOut:
    """Return the user's most recent invoice — used by the checkout return page
    to verify whether the payment actually completed."""
    invoice = (
        db.query(models.Invoice)
        .filter(models.Invoice.user_id == current_user.id)
        .order_by(models.Invoice.created_at.desc())
        .first()
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="No invoices found")

    return schemas.InvoiceOut(
        id=invoice.id,
        invoice_number=invoice.invoice_number,
        amount=str(invoice.amount),
        currency=invoice.currency,
        status=invoice.status,
        item_name=invoice.item_name,
        item_description=invoice.item_description,
        payment_provider=invoice.payment_provider,
        created_at=invoice.created_at,
    )
