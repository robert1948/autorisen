"""Simple mailer service: logs in development, sends via SMTP in production."""
import os
import smtplib
from email.message import EmailMessage


def send_verification_email(to_email: str, link: str):
    env = os.getenv('ENVIRONMENT', 'development')
    subject = "Please verify your account"
    body = f"Click the link to verify your account: {link}"
    if env == 'development':
        print(f"[DEV MAIL] to={to_email} subject={subject} body={body}")
        return True

    # Production: send via SMTP using env config
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')
    email_from = os.getenv('EMAIL_FROM', 'noreply@example.com')

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = email_from
    msg['To'] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as s:
            s.starttls()
            if smtp_user and smtp_pass:
                s.login(smtp_user, smtp_pass)
            s.send_message(msg)
        return True
    except Exception as exc:
        # Log and swallow to avoid failing user flows; in production, integrate with retry/backoff
        print(f"[MAIL ERROR] {exc}")
        return False
