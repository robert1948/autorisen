"""REST routes for PayFast payments integration."""

from __future__ import annotations

from urllib.parse import parse_qsl

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_verified_user
from .config import PayFastSettings, get_payfast_settings
from .constants import get_payfast_product_by_code
from . import schemas, service

log = logging.getLogger(__name__)

router = APIRouter(prefix="/payments/payfast", tags=["payments"])


@router.post("/checkout", response_model=schemas.PayFastCheckoutResponse)
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


@router.post("/itn", response_class=PlainTextResponse)
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Empty ITN payload"
        )

    if not service.verify_itn_signature(payload, settings=settings):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid PayFast signature",
        )

    # Server-to-server validation
    if not await service.validate_itn_with_server(payload, settings=settings):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PayFast server validation failed",
        )

    # Process and persist
    service.process_itn(payload, db)

    return PlainTextResponse("OK", status_code=status.HTTP_200_OK)
