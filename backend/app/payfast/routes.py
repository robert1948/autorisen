from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from starlette.background import BackgroundTasks
from .schemas import CreateCheckoutIn, CreateCheckoutOut, ITNResult
from .config import PAYFAST_CFG
from .utils import build_signature, host, validate_itn_with_payfast
import urllib.parse

# DB + models
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.payment import CreditTransaction, Credits

router = APIRouter(prefix="/api/payfast", tags=["payfast"])

# (Optional) plug in your auth dependency for protected creation
def current_user_ok():
    return True

@router.post("/checkout", response_model=CreateCheckoutOut)
async def create_checkout(payload: CreateCheckoutIn, user_ok: bool = Depends(current_user_ok)):
    if not PAYFAST_CFG["merchant_id"] or not PAYFAST_CFG["merchant_key"]:
        raise HTTPException(500, "PayFast not configured")

    params = {
        "merchant_id": PAYFAST_CFG["merchant_id"],
        "merchant_key": PAYFAST_CFG["merchant_key"],
        "return_url": PAYFAST_CFG["return_url"],
        "cancel_url": PAYFAST_CFG["cancel_url"],
        "notify_url": PAYFAST_CFG["notify_url"],

        "m_payment_id": payload.m_payment_id,
        "amount": f"{payload.amount:.2f}",
        "item_name": payload.item_name[:100],
        "item_description": (payload.item_description or "")[:255],
        "email_address": payload.email_address or "",
    }

    signature = build_signature(params)
    params["signature"] = signature

    # Host-to-host is allowed, but easiest is to redirect the browser to PayFast
    # Build the full redirect URL
    qs = urllib.parse.urlencode(params, doseq=True)
    redirect_url = f"{host()}/eng/process?{qs}"
    return CreateCheckoutOut(redirect_url=redirect_url)


@router.post("/itn", response_model=ITNResult)
async def itn(request: Request, background: BackgroundTasks, db: Session = Depends(get_db)):
    # Raw body is required for validation with PayFast
    raw = await request.body()

    # Step 1: quick ACK validation with PayFast
    is_valid = await validate_itn_with_payfast(raw)
    if not is_valid:
        # PayFast expects 200 always, but we'll log failure and return OK
        return JSONResponse(status_code=200, content={"status": "INVALID"})

    # Step 2: parse form fields
    form = dict((await request.form()).items())

    # Step 3: our own signature verification to protect against tampering
    # Build signature from received fields (excluding `signature`)
    verify_fields = {k: v for k, v in form.items() if k != "signature"}
    if build_signature(verify_fields) != form.get("signature"):
        return JSONResponse(status_code=200, content={"status": "INVALID_SIGNATURE"})

    # Step 4: business rules (recommended)
    # - check amount matches your order
    # - check currency (PayFast ZAR)
    # - ensure receiver merchant_id == our merchant_id
    if form.get("merchant_id") != PAYFAST_CFG["merchant_id"]:
        return JSONResponse(status_code=200, content={"status": "MERCHANT_MISMATCH"})

    # Extract core fields
    m_payment_id = form.get("m_payment_id")  # our internal order id e.g., credits:{userId}:{pack}:{ts}
    pf_payment_id = form.get("pf_payment_id")
    payment_status = form.get("payment_status")  # COMPLETE/PENDING/FAILED

    # Simple convention: m_payment_id = credits:{user_id}:{pack}:{timestamp}
    # Safely parse user_id and pack from m_payment_id
    user_id = None
    pack = None
    try:
        if m_payment_id and m_payment_id.startswith("credits:"):
            _, user_str, pack, _ts = m_payment_id.split(":", 3)
            user_id = int(user_str)
    except Exception:
        pass

    # Persist credits only on COMPLETE
    if payment_status == "COMPLETE" and user_id and pack:
        # Idempotency guard: skip if transaction for this pf_payment_id already exists
        existing = db.query(CreditTransaction).filter(
            CreditTransaction.user_id == user_id,
            CreditTransaction.transaction_type == "purchase",
            CreditTransaction.description.ilike(f"%pf:{pf_payment_id}%")
        ).first() if pf_payment_id else None
        if not existing:
            # Lookup pack credits
            from app.models.payment import CREDIT_PACKS
            pack_conf = CREDIT_PACKS.get(pack)
            if pack_conf:
                credits_to_add = int(pack_conf["credits"]) + int(pack_conf.get("bonus", 0))
                # Upsert Credits row
                credits = db.query(Credits).filter(Credits.user_id == user_id).one_or_none()
                if not credits:
                    credits = Credits(user_id=user_id, balance=0, total_purchased=0, total_used=0)
                    db.add(credits)
                    db.flush()
                credits.balance += credits_to_add
                credits.total_purchased += credits_to_add

                # Log credit transaction
                ct = CreditTransaction(
                    user_id=user_id,
                    transaction_type="purchase",
                    amount=credits_to_add,
                    description=f"PayFast {pack} credits (pf:{pf_payment_id})"
                )
                db.add(ct)
                db.commit()

    return {"status": payment_status or "OK"}
