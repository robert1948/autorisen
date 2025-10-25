"""
Payment System Database Migration
Creates all payment-related tables for Cape Control
"""

import os
import sys

from sqlalchemy import text

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import DATABASE_URL, Base, engine
from app.models.payment import (
    AnalyticsEvent,
    Credits,
    CreditTransaction,
    CustomRequest,
    PaymentMethod,
    Subscription,
    SupportTicket,
)


def run_payment_migration():
    """Create payment system tables"""
    try:
        print(f"📊 Connecting to database: {DATABASE_URL}")

        # Create all payment tables
        print("🔧 Creating payment system tables...")
        Base.metadata.create_all(
            bind=engine,
            tables=[
                Subscription.__table__,
                Credits.__table__,
                CreditTransaction.__table__,
                CustomRequest.__table__,
                SupportTicket.__table__,
                AnalyticsEvent.__table__,
                PaymentMethod.__table__,
            ],
        )

        # Test connection
        with engine.connect() as conn:
            if DATABASE_URL.startswith("postgresql://"):
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                print(f"✅ Connected to PostgreSQL: {version}")
            else:
                result = conn.execute(text("SELECT sqlite_version()"))
                version = result.fetchone()[0]
                print(f"✅ Connected to SQLite: {version}")

        print("✅ Payment system tables created successfully!")

        # Verify tables exist
        with engine.connect() as conn:
            # Check if tables were created
            tables_to_check = [
                "subscriptions",
                "credits",
                "credit_transactions",
                "custom_requests",
                "support_tickets",
                "analytics_events",
                "payment_methods",
            ]

            for table in tables_to_check:
                if DATABASE_URL.startswith("postgresql://"):
                    result = conn.execute(
                        text(
                            f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = '{table}'
                        )
                    """
                        )
                    )
                else:
                    result = conn.execute(
                        text(
                            f"""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name='{table}'
                    """
                        )
                    )

                if DATABASE_URL.startswith("postgresql://"):
                    exists = result.fetchone()[0]
                else:
                    exists = result.fetchone() is not None

                if exists:
                    print(f"✅ Table '{table}' created successfully")
                else:
                    print(f"❌ Table '{table}' not found")

        print("\n🎉 Payment system migration completed!")
        print("\n📋 Available payment endpoints:")
        print("   • POST /api/payment/subscription/subscribe")
        print("   • GET  /api/payment/subscription/status")
        print("   • POST /api/payment/subscription/cancel")
        print("   • POST /api/payment/credits/purchase")
        print("   • GET  /api/payment/credits/balance")
        print("   • POST /api/payment/credits/deduct")
        print("   • POST /api/payment/custom-agent/request")
        print("   • GET  /api/payment/custom-agent/requests")
        print("   • POST /api/payment/support/ticket")
        print("   • GET  /api/payment/pricing")
        print("   • POST /api/payment/webhooks/stripe")

        print("\n⚙️  Next steps:")
        print(
            "   1. Set STRIPE_SECRET_KEY and STRIPE_WEBHOOK_SECRET environment variables"
        )
        print("   2. Create Stripe products for subscription tiers")
        print("   3. Configure webhook endpoint in Stripe dashboard")
        print("   4. Test payment flow with Stripe test mode")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

    return True


if __name__ == "__main__":
    print("🚀 Starting Payment System Migration...")
    success = run_payment_migration()

    if success:
        print("\n✅ Migration completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
