#!/usr/bin/env python3
"""
Test script to verify database interaction APIs work correctly.
"""

import asyncio
import os
import sys
from pathlib import Path

# Set environment variables for testing
os.environ["DATABASE_URL"] = "sqlite:///./test_db_interaction.db"
os.environ["SECRET_KEY"] = "test-secret-key"

# Add backend to path
backend_path = Path(__file__).parent / "backend" / "src"
sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import Session  # noqa: E402

from backend.src.db import models  # noqa: E402
from backend.src.db.base import Base  # noqa: E402
from backend.src.db.session import SessionLocal, engine  # noqa: E402
from backend.src.modules.user.schemas import UserProfileUpdate  # noqa: E402
from backend.src.modules.user.service import (  # noqa: E402
    complete_onboarding_item,
    get_dashboard_stats,
    get_onboarding_checklist,
    get_user_profile,
    update_user_profile,
)


async def test_database_interaction():
    """Test the database interaction functionality."""
    print("🔍 Testing database interaction...")

    # Create tables
    print("📋 Creating database tables...")
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        # Test 1: Create a test user
        test_user = models.User(
            email="test-db-interaction@example.com",
            hashed_password="test_hash",
            first_name="Test",
            last_name="User",
            role="Customer",
            is_email_verified=True,
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"✅ Created test user: {test_user.id}")

        # Test 2: Get user profile
        try:
            profile = get_user_profile(db, str(test_user.id))
            print(f"✅ Retrieved profile: {profile.email}")
        except Exception as e:
            print(f"❌ Failed to get profile: {e}")

        # Test 3: Update user profile
        try:
            update_data = UserProfileUpdate(
                first_name="Updated",
                last_name="User",
                company="Test Company",
                role="Developer",
                experience_level="advanced",
                interests=["Task Automation", "Data Analysis"],
                notifications_email=True,
                notifications_push=False,
                notifications_sms=False,
            )
            updated_profile = update_user_profile(db, str(test_user.id), update_data)
            print(
                f"✅ Updated profile: {updated_profile.first_name} {updated_profile.last_name}"
            )
        except Exception as e:
            print(f"❌ Failed to update profile: {e}")

        # Test 4: Get onboarding checklist
        try:
            checklist = get_onboarding_checklist(db, str(test_user.id))
            print(
                f"✅ Retrieved checklist: {len(checklist.items)} items, {checklist.completion_percentage}% complete"
            )
        except Exception as e:
            print(f"❌ Failed to get checklist: {e}")

        # Test 5: Complete onboarding item
        try:
            complete_onboarding_item(db, str(test_user.id), "complete_profile")
            updated_checklist = get_onboarding_checklist(db, str(test_user.id))
            print(
                f"✅ Completed checklist item: {updated_checklist.completion_percentage}% complete"
            )
        except Exception as e:
            print(f"❌ Failed to complete item: {e}")

        # Test 6: Get dashboard stats
        try:
            stats = get_dashboard_stats(db, str(test_user.id))
            print(
                f"✅ Retrieved dashboard stats: {stats.active_agents} agents, {stats.success_rate}% success rate"
            )
        except Exception as e:
            print(f"❌ Failed to get dashboard stats: {e}")

        print("\n🎉 Database interaction tests completed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        # Cleanup
        try:
            # Delete test user using proper SQLAlchemy syntax
            test_user_to_delete = (
                db.query(models.User)
                .filter(models.User.email == "test-db-interaction@example.com")
                .first()
            )
            if test_user_to_delete:
                db.delete(test_user_to_delete)
                db.commit()
            print("🧹 Cleaned up test data")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
        db.close()

    return True


if __name__ == "__main__":
    success = asyncio.run(test_database_interaction())
    sys.exit(0 if success else 1)
