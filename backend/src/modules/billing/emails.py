"""Billing-specific email templates and dispatch.

Each ``send_*`` function is designed to be called directly by the billing
scheduler OR by the email worker when processing queued jobs. All functions
soft-fail with logging so a single email failure never crashes the billing
cycle.
"""

from __future__ import annotations

import logging
from typing import Optional

from backend.src.core.mailer import MailerError, send_email

log = logging.getLogger("billing.emails")

# ---------------------------------------------------------------------------
# Brand constants
# ---------------------------------------------------------------------------
SUPPORT_EMAIL = "bobby@cape-control.com"
BILLING_URL = "https://cape-control.com/app/billing"
PRICING_URL = "https://cape-control.com/app/pricing"


# ---------------------------------------------------------------------------
# Shared HTML wrapper
# ---------------------------------------------------------------------------

def _wrap_html(body: str) -> str:
    return f"""\
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
             color: #1a1a2e; max-width: 600px; margin: 0 auto; padding: 24px;">
  <div style="border-bottom: 3px solid #2563eb; padding-bottom: 16px; margin-bottom: 24px;">
    <h2 style="margin: 0; color: #2563eb;">CapeControl</h2>
  </div>
  {body}
  <div style="margin-top: 32px; padding-top: 16px; border-top: 1px solid #e5e7eb;
              color: #6b7280; font-size: 12px;">
    <p>CapeControl &middot; Cape Town, South Africa</p>
    <p>Questions? Reply to this email or contact <a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a></p>
  </div>
</body>
</html>"""


# ---------------------------------------------------------------------------
# 1. Payment overdue reminder
# ---------------------------------------------------------------------------

def send_payment_overdue_email(
    *,
    to_email: str,
    first_name: str = "there",
    plan_name: str = "Pro",
    amount: str = "529.00",
    currency: str = "ZAR",
    due_date: str = "",
    reminder_count: int = 1,
) -> bool:
    """Send a payment overdue / missed payment reminder. Returns True on success."""

    urgency = ""
    if reminder_count == 1:
        urgency = "Action required"
        subject = f"[CapeControl] Payment overdue for your {plan_name} plan"
    elif reminder_count == 2:
        urgency = "Second notice"
        subject = f"[CapeControl] Reminder: Payment overdue – {plan_name} plan"
    else:
        urgency = "Final notice"
        subject = f"[CapeControl] Final notice: Your {plan_name} plan will be cancelled"

    text_body = (
        f"Hi {first_name},\n\n"
        f"{urgency}: Your CapeControl {plan_name} plan payment of {currency} {amount} "
        f"{'was due on ' + due_date if due_date else 'is overdue'}.\n\n"
        f"Please update your payment method or complete payment to keep your plan active:\n"
        f"{BILLING_URL}\n\n"
    )
    if reminder_count >= 3:
        text_body += (
            "This is your final reminder. If payment is not received within the next "
            "few days, your subscription will be cancelled and you'll be moved to the Free plan.\n\n"
        )
    text_body += "— CapeControl Team\n"

    html_body = _wrap_html(f"""\
  <p>Hi {first_name},</p>
  <p><strong>{urgency}:</strong> Your CapeControl <strong>{plan_name}</strong> plan payment of
     <strong>{currency} {amount}</strong>
     {"was due on <strong>" + due_date + "</strong>" if due_date else "is overdue"}.</p>
  <p>Please update your payment method or complete payment to keep your plan active:</p>
  <p style="text-align: center; margin: 24px 0;">
    <a href="{BILLING_URL}"
       style="display: inline-block; padding: 12px 28px; background: #2563eb; color: #fff;
              border-radius: 8px; text-decoration: none; font-weight: 600;">
      Go to Billing
    </a>
  </p>
  {"<p style='color:#dc2626; font-weight:600;'>This is your final reminder. If payment is not received within the next few days, your subscription will be cancelled and you will be moved to the Free plan.</p>" if reminder_count >= 3 else ""}
  <p style="color: #6b7280; font-size: 13px;">
    If you've already made this payment, please disregard this email. It may take a few minutes
    for payments to reflect.
  </p>""")

    try:
        send_email(subject=subject, to=[to_email], text_body=text_body, html_body=html_body)
        log.info("Payment overdue email #%d sent to %s", reminder_count, to_email)
        return True
    except MailerError:
        log.exception("Failed to send payment overdue email to %s", to_email)
        return False


# ---------------------------------------------------------------------------
# 2. Subscription cancelled due to non-payment
# ---------------------------------------------------------------------------

def send_subscription_cancelled_email(
    *,
    to_email: str,
    first_name: str = "there",
    plan_name: str = "Pro",
) -> bool:
    """Notify the user their subscription has been cancelled for non-payment."""

    subject = f"[CapeControl] Your {plan_name} subscription has been cancelled"
    text_body = (
        f"Hi {first_name},\n\n"
        f"Unfortunately, we were unable to collect payment for your CapeControl {plan_name} plan "
        f"after multiple reminders.\n\n"
        f"Your subscription has been cancelled and your account has been moved to the Free plan. "
        f"You can still access your projects and data, but some features may be limited.\n\n"
        f"To reactivate your {plan_name} plan at any time, visit:\n"
        f"{PRICING_URL}\n\n"
        f"— CapeControl Team\n"
    )
    html_body = _wrap_html(f"""\
  <p>Hi {first_name},</p>
  <p>Unfortunately, we were unable to collect payment for your CapeControl
     <strong>{plan_name}</strong> plan after multiple reminders.</p>
  <p>Your subscription has been cancelled and your account has been moved to the
     <strong>Free plan</strong>. You can still access your projects and data, but
     some features may be limited.</p>
  <p style="text-align: center; margin: 24px 0;">
    <a href="{PRICING_URL}"
       style="display: inline-block; padding: 12px 28px; background: #2563eb; color: #fff;
              border-radius: 8px; text-decoration: none; font-weight: 600;">
      Reactivate Plan
    </a>
  </p>
  <p style="color: #6b7280; font-size: 13px;">
    Questions? Contact us at <a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a>
  </p>""")

    try:
        send_email(subject=subject, to=[to_email], text_body=text_body, html_body=html_body)
        log.info("Subscription cancelled email sent to %s", to_email)
        return True
    except MailerError:
        log.exception("Failed to send cancellation email to %s", to_email)
        return False


# ---------------------------------------------------------------------------
# 3. Subscription ended (user-requested cancel at period end)
# ---------------------------------------------------------------------------

def send_subscription_ended_email(
    *,
    to_email: str,
    first_name: str = "there",
) -> bool:
    """Notify the user their subscription period has ended as requested."""

    subject = "[CapeControl] Your subscription has ended"
    text_body = (
        f"Hi {first_name},\n\n"
        f"As requested, your CapeControl subscription has ended and your account "
        f"has been moved to the Free plan.\n\n"
        f"You can resubscribe at any time: {PRICING_URL}\n\n"
        f"— CapeControl Team\n"
    )
    html_body = _wrap_html(f"""\
  <p>Hi {first_name},</p>
  <p>As requested, your CapeControl subscription has ended and your account
     has been moved to the <strong>Free plan</strong>.</p>
  <p>You can resubscribe at any time:</p>
  <p style="text-align: center; margin: 24px 0;">
    <a href="{PRICING_URL}"
       style="display: inline-block; padding: 12px 28px; background: #2563eb; color: #fff;
              border-radius: 8px; text-decoration: none; font-weight: 600;">
      View Plans
    </a>
  </p>
  <p>Thanks for being a CapeControl customer!</p>""")

    try:
        send_email(subject=subject, to=[to_email], text_body=text_body, html_body=html_body)
        log.info("Subscription ended email sent to %s", to_email)
        return True
    except MailerError:
        log.exception("Failed to send subscription ended email to %s", to_email)
        return False


# ---------------------------------------------------------------------------
# 4. Renewal invoice generated
# ---------------------------------------------------------------------------

def send_renewal_invoice_email(
    *,
    to_email: str,
    first_name: str = "there",
    plan_name: str = "Pro",
    amount: str = "529.00",
    currency: str = "ZAR",
    invoice_number: str = "",
) -> bool:
    """Notify the user a renewal invoice has been generated."""

    subject = f"[CapeControl] Invoice {invoice_number} – {plan_name} plan renewal"
    text_body = (
        f"Hi {first_name},\n\n"
        f"Your CapeControl {plan_name} plan renewal invoice has been generated:\n\n"
        f"  Invoice: {invoice_number}\n"
        f"  Amount:  {currency} {amount}\n\n"
        f"Please complete payment to continue your subscription:\n"
        f"{BILLING_URL}\n\n"
        f"— CapeControl Team\n"
    )
    html_body = _wrap_html(f"""\
  <p>Hi {first_name},</p>
  <p>Your CapeControl <strong>{plan_name}</strong> plan renewal invoice has been generated:</p>
  <table style="border-collapse: collapse; margin: 16px 0;">
    <tr>
      <td style="padding: 8px 16px 8px 0; font-weight: bold;">Invoice</td>
      <td style="padding: 8px 0;">{invoice_number}</td>
    </tr>
    <tr>
      <td style="padding: 8px 16px 8px 0; font-weight: bold;">Amount</td>
      <td style="padding: 8px 0;">{currency} {amount}</td>
    </tr>
  </table>
  <p style="text-align: center; margin: 24px 0;">
    <a href="{BILLING_URL}"
       style="display: inline-block; padding: 12px 28px; background: #2563eb; color: #fff;
              border-radius: 8px; text-decoration: none; font-weight: 600;">
      Pay Now
    </a>
  </p>""")

    try:
        send_email(subject=subject, to=[to_email], text_body=text_body, html_body=html_body)
        log.info("Renewal invoice email sent to %s for %s", to_email, invoice_number)
        return True
    except MailerError:
        log.exception("Failed to send renewal invoice email to %s", to_email)
        return False


# ---------------------------------------------------------------------------
# Dispatcher — called by email worker for queued billing jobs
# ---------------------------------------------------------------------------

def dispatch_billing_email(job_type: str, payload: dict) -> bool:
    """Route a queued email job to the correct sender. Returns True on success."""
    event_type = payload.get("event_type", "")

    if event_type == "payment_overdue":
        return send_payment_overdue_email(
            to_email=payload["to"],
            first_name=payload.get("first_name", "there"),
            plan_name=payload.get("plan_name", "Pro"),
            amount=payload.get("amount", "529.00"),
            currency=payload.get("currency", "ZAR"),
            due_date=payload.get("due_date", ""),
            reminder_count=payload.get("reminder_count", 1),
        )

    elif event_type == "subscription_cancelled":
        return send_subscription_cancelled_email(
            to_email=payload["to"],
            first_name=payload.get("first_name", "there"),
            plan_name=payload.get("plan_name", "Pro"),
        )

    elif event_type == "subscription_ended":
        return send_subscription_ended_email(
            to_email=payload["to"],
            first_name=payload.get("first_name", "there"),
        )

    elif event_type == "renewal_invoice_created":
        return send_renewal_invoice_email(
            to_email=payload["to"],
            first_name=payload.get("first_name", "there"),
            plan_name=payload.get("plan_name", "Pro"),
            amount=payload.get("amount", "529.00"),
            currency=payload.get("currency", "ZAR"),
            invoice_number=payload.get("invoice_number", ""),
        )

    else:
        log.warning("Unknown billing email event_type: %s", event_type)
        return False
