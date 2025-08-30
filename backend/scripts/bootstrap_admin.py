import os
import asyncio

from app.services.auth_service import AuthService
from app.database import SessionLocal


async def main():
    db = SessionLocal()
    try:
        auth = AuthService()
        try:
            await auth.register_user(db, {
                "email": os.environ.get("BOOTSTRAP_ADMIN_EMAIL") or "admin@autorisen.dev",
                "password": os.environ.get("BOOTSTRAP_ADMIN_PASSWORD") or "admin123",
                "full_name": "Autorisen Admin",
                "user_role": "admin",
            })
            print("✅ Admin bootstrapped or already exists")
        except Exception as e:
            print("ℹ️ Admin may already exist:", e)
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
