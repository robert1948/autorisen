"""REST routes for subscription management."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.db.session import get_session
from backend.src.modules.auth.csrf import require_csrf_token
from backend.src.modules.auth.deps import get_current_user

from . import schemas, service
from .plans import ALL_PLANS

router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"],
    dependencies=[Depends(require_csrf_token)],
)


# --- Public: list plans ---


@router.get("/plans", response_model=List[schemas.PlanOut])
def list_plans() -> list[schemas.PlanOut]:
    """Return the public pricing plans."""
    return [
        schemas.PlanOut(
            id=p.id,
            name=p.name,
            display_price=p.display_price,
            amount=p.amount,
            currency=p.currency,
            interval=p.interval,
            features=list(p.features),
            cta_label=p.cta_label,
            is_public=p.is_public,
        )
        for p in ALL_PLANS
        if p.is_public
    ]


# --- Current subscription ---


@router.get("/current", response_model=schemas.SubscriptionOut)
def get_current_subscription(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> schemas.SubscriptionOut:
    """Return the authenticated user's current subscription (auto-creates Starter if none)."""
    sub = service.ensure_subscription(db, user.id)
    return schemas.SubscriptionOut(**service._sub_to_dict(sub))


# --- Subscribe / change plan ---


@router.post(
    "/subscribe",
    response_model=schemas.SubscribeResponse,
    status_code=status.HTTP_200_OK,
)
def subscribe_to_plan(
    payload: schemas.SubscribeRequest,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> schemas.SubscribeResponse:
    """Subscribe to or change the user's plan."""
    try:
        sub, msg, checkout_url = service.subscribe(db, user, payload.plan_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        )
    return schemas.SubscribeResponse(
        subscription=schemas.SubscriptionOut(**service._sub_to_dict(sub)),
        message=msg,
        checkout_url=checkout_url,
    )


# --- Cancel ---


@router.post("/cancel", response_model=schemas.CancelResponse)
def cancel_subscription(
    payload: schemas.CancelRequest,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> schemas.CancelResponse:
    """Cancel the user's paid subscription."""
    try:
        sub, msg = service.cancel_subscription(
            db,
            user.id,
            immediate=payload.immediate,
            reason=payload.reason,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        )
    return schemas.CancelResponse(
        subscription=schemas.SubscriptionOut(**service._sub_to_dict(sub)),
        message=msg,
    )


# --- Enterprise inquiry ---


@router.post(
    "/enterprise-inquiry",
    response_model=schemas.EnterpriseInquiryResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_enterprise_inquiry(
    payload: schemas.EnterpriseInquiryRequest,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> schemas.EnterpriseInquiryResponse:
    """Submit an enterprise plan inquiry."""
    inquiry = service.create_enterprise_inquiry(
        db,
        user_id=user.id,
        company_name=payload.company_name,
        contact_name=payload.contact_name,
        contact_email=payload.contact_email,
        message=payload.message,
    )
    return schemas.EnterpriseInquiryResponse(
        id=inquiry.id,
        status=inquiry.status,
        message="Thank you! Our team will be in touch shortly.",
    )


# --- Billing history ---


@router.get("/invoices", response_model=List[schemas.InvoiceOut])
def list_invoices(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> list[schemas.InvoiceOut]:
    """Return the user's invoice history."""
    invoices = service.list_invoices(db, user.id)
    return [schemas.InvoiceOut.model_validate(inv) for inv in invoices]
