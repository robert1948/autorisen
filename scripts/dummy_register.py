import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import smtplib
from email.mime.text import MIMEText

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./capecontrol.db")
NOTIFY_EMAIL = "info@cape-control.com"
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "noreply@cape-control.com")
SMTP_SERVER = os.getenv("SMTP_SERVER", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT") or "25")

# --- DUMMY USER DATA ---
dummy_user = {
    "email": "dummyuser@example.com",
    "password_hash": "dummy1234",  # In production, this should be hashed
    "role": "CUSTOMER",
    "first_name": "Dummy",
    "last_name": "User",
    "is_active": True,
    "is_verified": False,
}


# --- DB LOGIC ---
def register_user():
    engine = create_engine(DATABASE_URL)
    try:
        with engine.connect() as conn:
            # Insert into users_v2 table with new schema
            conn.execute(
                text(
                    """
                INSERT INTO users_v2 (email, password_hash, role, first_name, last_name, is_active, is_verified)
                VALUES (:email, :password_hash, :role, :first_name, :last_name, :is_active, :is_verified)
            """
                ),
                dummy_user,
            )
            conn.commit()
        print("User registered successfully.")
        return True
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return False


# --- EMAIL LOGIC ---
def send_notification():
    msg = MIMEText(
        f"Dummy registration completed for {dummy_user['first_name']} {dummy_user['last_name']} ({dummy_user['email']})."
    )
    msg["Subject"] = "Dummy Registration Notification"
    msg["From"] = SENDER_EMAIL
    msg["To"] = NOTIFY_EMAIL
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.sendmail(SENDER_EMAIL, [NOTIFY_EMAIL], msg.as_string())
        print(f"Notification sent to {NOTIFY_EMAIL}.")
    except Exception as e:
        print(f"Email error: {e}")


if __name__ == "__main__":
    if register_user():
        send_notification()
    else:
        print("Registration failed; notification not sent.")
