"""
Initialize Analytics Tables for Performance Dashboard
This script creates the analytics tables in the database.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging

from app.database import Base, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_analytics_tables():
    """Create analytics tables in the database"""
    try:
        logger.info("Creating analytics tables...")

        # Create all tables
        Base.metadata.create_all(bind=engine)

        logger.info("✅ Analytics tables created successfully!")
        logger.info("Tables created:")
        logger.info("  - analytics_events")
        logger.info("  - system_metrics")
        logger.info("  - user_sessions")
        logger.info("  - api_usage_stats")

        return True

    except Exception as e:
        logger.error(f"❌ Error creating analytics tables: {e}")
        return False


if __name__ == "__main__":
    success = create_analytics_tables()
    if success:
        print("\n🎉 Analytics database setup complete!")
        print("You can now use the Performance Analytics Dashboard.")
    else:
        print("\n❌ Analytics database setup failed!")
        sys.exit(1)
