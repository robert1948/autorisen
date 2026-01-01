"""REST routes for PayFast payments integration."""

from __future__ import annotations

from urllib.parse import parse_qsl

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from backend.src.db.session import get_session
from .config import PayFastSettings, get_payfast_settings
from . import schemas, service

router = APIRouter(prefix="/payments/payfast", tags=["payments"])


@router.post("/checkout", response_model=schemas.PayFastCheckoutResponse)
def create_checkout_session(
    payload: schemas.PayFastCheckoutRequest,
    settings: PayFastSettings = Depends(get_payfast_settings),
) -> schemas.PayFastCheckoutResponse:
    """Generate a signed set of form fields for the PayFast hosted checkout."""

    session = service.create_checkout_session(
        settings=settings,
        amount=payload.amount,
        item_name=payload.item_name,
        item_description=payload.item_description,
        customer_email=payload.customer_email,
        customer_first_name=payload.customer_first_name,
        customer_last_name=payload.customer_last_name,
        metadata=payload.metadata,
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
