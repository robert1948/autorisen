"""PAY-010: Test full ITN ingestion → Transaction + Invoice persistence.

Simulates a complete PayFast ITN lifecycle: pending invoice → ITN callback
→ transaction record created → invoice marked paid with invoice_number.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from backend.src.db import models


def _seed_user_and_invoice(db):
    """Create a test user and pending invoice, return (user, invoice)."""
    user_id = str(uuid.uuid4())
    user = models.User(
        id=user_id,
        email=f"itn-test-{user_id[:8]}@example.test",
        hashed_password="not-used",
        first_name="Test",
        last_name="ITN",
        role="user",
        is_active=True,
    )
    db.add(user)

    invoice_id = str(uuid.uuid4())
    invoice = models.Invoice(
        id=invoice_id,
        user_id=user_id,
        amount=Decimal("99.00"),
        currency="ZAR",
        status="pending",
        item_name="Pro Plan Monthly",
        item_description="CapeControl Pro subscription",
        customer_email=user.email,
        customer_first_name="Test",
        customer_last_name="ITN",
        payment_provider="payfast",
        external_reference=invoice_id,
    )
    db.add(invoice)
    db.commit()
    return user, invoice


def test_process_itn_creates_transaction_and_marks_invoice_paid(app):
    """Simulate a COMPLETE ITN → verify Transaction created, Invoice paid, invoice_number assigned."""
    from backend.src.db.session import SessionLocal
    from backend.src.modules.payments.service import process_itn

    db = SessionLocal()
    try:
        user, invoice = _seed_user_and_invoice(db)

        pf_payment_id = f"pf-{uuid.uuid4().hex[:12]}"
        itn_payload = {
            "m_payment_id": invoice.external_reference,
            "pf_payment_id": pf_payment_id,
            "payment_status": "COMPLETE",
            "amount_gross": "99.00",
            "amount_fee": "2.28",
            "amount_net": "96.72",
            "item_name": "Pro Plan Monthly",
            "signature": "not-checked-here",
        }

        process_itn(itn_payload, db)

        # Reload from DB
        db.expire_all()

        txn = (
            db.query(models.Transaction)
            .filter(models.Transaction.provider_transaction_id == pf_payment_id)
            .first()
        )
        assert txn is not None, "Transaction should be created"
        assert txn.status == "completed"
        assert txn.transaction_type == "payment"
        assert txn.amount == Decimal("99.00")
        assert txn.amount_fee == Decimal("2.28")
        assert txn.amount_net == Decimal("96.72")
        assert txn.itn_data is not None
        assert txn.itn_data["pf_payment_id"] == pf_payment_id
        assert txn.processed_at is not None

        # Invoice should be paid with a sequential invoice number
        inv = db.query(models.Invoice).filter(models.Invoice.id == invoice.id).first()
        assert inv.status == "paid"
        assert inv.invoice_number is not None
        assert inv.invoice_number.startswith("INV-")

    finally:
        # Cleanup
        db.query(models.Transaction).filter(
            models.Transaction.invoice_id == invoice.id
        ).delete()
        db.query(models.Invoice).filter(models.Invoice.id == invoice.id).delete()
        db.query(models.User).filter(models.User.id == user.id).delete()
        db.commit()
        db.close()


def test_process_itn_duplicate_is_idempotent(app):
    """Sending the same ITN twice should update existing Transaction, not create a duplicate."""
    from backend.src.db.session import SessionLocal
    from backend.src.modules.payments.service import process_itn

    db = SessionLocal()
    try:
        user, invoice = _seed_user_and_invoice(db)
        pf_payment_id = f"pf-{uuid.uuid4().hex[:12]}"

        itn_payload = {
            "m_payment_id": invoice.external_reference,
            "pf_payment_id": pf_payment_id,
            "payment_status": "COMPLETE",
            "amount_gross": "99.00",
            "amount_fee": "2.28",
            "amount_net": "96.72",
        }

        # Process twice
        process_itn(itn_payload, db)
        process_itn(itn_payload, db)

        txns = (
            db.query(models.Transaction)
            .filter(models.Transaction.provider_transaction_id == pf_payment_id)
            .all()
        )
        assert len(txns) == 1, "Duplicate ITN should not create a second Transaction"

    finally:
        db.query(models.Transaction).filter(
            models.Transaction.invoice_id == invoice.id
        ).delete()
        db.query(models.Invoice).filter(models.Invoice.id == invoice.id).delete()
        db.query(models.User).filter(models.User.id == user.id).delete()
        db.commit()
        db.close()


def test_create_checkout_session_reuses_recent_pending_invoice(app):
    """Repeated checkout creation for same user/item/amount should reuse recent pending invoice."""
    from backend.src.db.session import SessionLocal
    from backend.src.modules.payments.config import PayFastSettings
    from backend.src.modules.payments.service import create_checkout_session

    db = SessionLocal()
    try:
        user, invoice = _seed_user_and_invoice(db)
        settings = PayFastSettings(
            merchant_id="10000100",
            merchant_key="46f0cd694581a",
            return_url="https://example.test/return",
            cancel_url="https://example.test/cancel",
            notify_url="https://example.test/itn",
            mode="sandbox",
            passphrase="test-passphrase",
        )

        checkout_1 = create_checkout_session(
            settings=settings,
            db=db,
            amount="99.00",
            item_name="Pro Plan Monthly",
            item_description="CapeControl Pro subscription",
            customer_email=user.email,
            customer_first_name="Test",
            customer_last_name="ITN",
            metadata={"product_code": "PRO_MONTHLY"},
        )

        checkout_2 = create_checkout_session(
            settings=settings,
            db=db,
            amount="99.00",
            item_name="Pro Plan Monthly",
            item_description="CapeControl Pro subscription",
            customer_email=user.email,
            customer_first_name="Test",
            customer_last_name="ITN",
            metadata={"product_code": "PRO_MONTHLY"},
        )

        assert (
            checkout_1["fields"]["m_payment_id"] == checkout_2["fields"]["m_payment_id"]
        )

        pending = (
            db.query(models.Invoice)
            .filter(
                models.Invoice.user_id == user.id, models.Invoice.status == "pending"
            )
            .all()
        )
        assert len(pending) == 1
    finally:
        db.query(models.Transaction).filter(
            models.Transaction.invoice_id == invoice.id
        ).delete()
        db.query(models.Invoice).filter(models.Invoice.id == invoice.id).delete()
        db.query(models.User).filter(models.User.id == user.id).delete()
        db.commit()
        db.close()


def test_process_itn_complete_cancels_duplicate_pending_invoices(app):
    """Once one invoice is paid, same-day duplicate pending invoices should be auto-cancelled."""
    from backend.src.db.session import SessionLocal
    from backend.src.modules.payments.service import process_itn

    db = SessionLocal()
    try:
        user, paid_target = _seed_user_and_invoice(db)

        duplicate = models.Invoice(
            id=str(uuid.uuid4()),
            user_id=user.id,
            amount=Decimal("99.00"),
            currency="ZAR",
            status="pending",
            item_name="Pro Plan Monthly",
            item_description="CapeControl Pro subscription",
            customer_email=user.email,
            customer_first_name="Test",
            customer_last_name="ITN",
            payment_provider="payfast",
            external_reference=str(uuid.uuid4()),
        )
        db.add(duplicate)
        db.commit()

        pf_payment_id = f"pf-{uuid.uuid4().hex[:12]}"
        itn_payload = {
            "m_payment_id": paid_target.external_reference,
            "pf_payment_id": pf_payment_id,
            "payment_status": "COMPLETE",
            "amount_gross": "99.00",
            "amount_fee": "2.28",
            "amount_net": "96.72",
        }

        process_itn(itn_payload, db)
        db.expire_all()

        paid = (
            db.query(models.Invoice).filter(models.Invoice.id == paid_target.id).first()
        )
        dup = db.query(models.Invoice).filter(models.Invoice.id == duplicate.id).first()

        assert paid is not None and paid.status == "paid"
        assert dup is not None and dup.status == "cancelled"
    finally:
        db.query(models.Transaction).filter(
            models.Transaction.invoice_id.in_([paid_target.id, duplicate.id])
        ).delete(synchronize_session=False)
        db.query(models.Invoice).filter(
            models.Invoice.id.in_([paid_target.id, duplicate.id])
        ).delete(synchronize_session=False)
        db.query(models.User).filter(models.User.id == user.id).delete()
        db.commit()
        db.close()


def test_process_itn_failed_status(app):
    """FAILED ITN should create a failed transaction and mark invoice failed."""
    from backend.src.db.session import SessionLocal
    from backend.src.modules.payments.service import process_itn

    db = SessionLocal()
    try:
        user, invoice = _seed_user_and_invoice(db)
        pf_payment_id = f"pf-{uuid.uuid4().hex[:12]}"

        itn_payload = {
            "m_payment_id": invoice.external_reference,
            "pf_payment_id": pf_payment_id,
            "payment_status": "FAILED",
            "amount_gross": "99.00",
        }

        process_itn(itn_payload, db)
        db.expire_all()

        txn = (
            db.query(models.Transaction)
            .filter(models.Transaction.provider_transaction_id == pf_payment_id)
            .first()
        )
        assert txn is not None
        assert txn.status == "failed"
        assert txn.amount_fee is None  # No fee on failed payment

        inv = db.query(models.Invoice).filter(models.Invoice.id == invoice.id).first()
        assert inv.status == "failed"
        assert inv.invoice_number is None  # No invoice number for failed payments

    finally:
        db.query(models.Transaction).filter(
            models.Transaction.invoice_id == invoice.id
        ).delete()
        db.query(models.Invoice).filter(models.Invoice.id == invoice.id).delete()
        db.query(models.User).filter(models.User.id == user.id).delete()
        db.commit()
        db.close()
