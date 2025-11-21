"""
Initialize Analytics Tables for Performance Dashboard
This script creates the analytics tables in the database.
"""

import logging
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.join(PROJECT_ROOT, "backend")
# Ensure backend package is importable when running as a script
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

try:
    from backend.src.db.base import Base
    from backend.src.db.session import engine
except ImportError as exc:  # pragma: no cover - defensive guard
    raise RuntimeError(
        "Unable to import database session; is backend installed?"
    ) from exc

# Import models for side effects so SQLAlchemy metadata is populated
try:
    from backend.src.db import models  # noqa: F401
except ImportError:
    # When backend package isn't installed, attempt relative path import
    sys.path.insert(0, PROJECT_ROOT)
    from backend.src.db import models  # type: ignore  # noqa: F401

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
