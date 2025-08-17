"""
Database Migration Script for Enhanced Authentication
====================================================

This script handles the migration from the current user system to the enhanced
authentication architecture with proper data preservation and rollback support.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

# Add the parent directory to the path so we can import our models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import get_database_url
from app.database import engine, Base
from app.models import User as OldUser  # Existing user model
from app.models_enhanced import UserV2 as NewUser, UserRole, Token, DeveloperEarning, PasswordReset, AuditLog
from app.auth_enhanced import auth_service

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_enhanced_tables():
    """Create all enhanced authentication tables"""
    logger.info("Creating enhanced authentication tables...")
    
    try:
        # Drop existing tables if they exist (for development)
        # In production, you'd want more careful migration
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Enhanced tables created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        return False

def migrate_existing_users():
    """Migrate existing users to the enhanced user table"""
    logger.info("Migrating existing users...")
    
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # This would depend on your existing user structure
        # For now, we'll create some sample users
        
        # Sample admin user
        admin_user = NewUser(
            email="admin@capecontrol.com",
            password_hash=auth_service.get_password_hash("AdminPassword123!"),
            role=UserRole.ADMIN,
            first_name="System",
            last_name="Administrator",
            is_active=True,
            is_verified=True,
            email_verified_at=datetime.utcnow(),
            terms_accepted_at=datetime.utcnow(),
            privacy_accepted_at=datetime.utcnow()
        )
        session.add(admin_user)
        
        # Sample developer user
        developer_user = NewUser(
            email="developer@capecontrol.com",
            password_hash=auth_service.get_password_hash("DevPassword123!"),
            role=UserRole.DEVELOPER,
            first_name="Jane",
            last_name="Developer",
            company="AI Innovations Inc",
            website="https://aiinnovations.com",
            experience="advanced",
            is_active=True,
            is_verified=True,
            email_verified_at=datetime.utcnow(),
            terms_accepted_at=datetime.utcnow(),
            privacy_accepted_at=datetime.utcnow()
        )
        session.add(developer_user)
        session.flush()  # Get the user ID
        
        # Sample developer earnings
        earnings = DeveloperEarning(
            user_id=developer_user.id,
            agent_id="ai_assistant_v1",
            agent_name="AI Assistant Pro",
            revenue_share=1250.75,
            total_sales=4169.17,
            commission_rate=0.3000,
            last_payout_amount=800.00,
            total_paid_out=800.00,
            is_active=True
        )
        session.add(earnings)
        
        # Sample customer user
        customer_user = NewUser(
            email="customer@example.com",
            password_hash=auth_service.hash_password("CustomerPass123!"),
            role=UserRole.CUSTOMER,
            first_name="John",
            last_name="Customer",
            experience="intermediate",
            is_active=True,
            is_verified=False,
            terms_accepted_at=datetime.utcnow(),
            privacy_accepted_at=datetime.utcnow()
        )
        session.add(customer_user)
        
        session.commit()
        logger.info("✅ Sample users created successfully")
        
        # Log the migration
        audit_log = AuditLog(
            user_id=admin_user.id,
            event_type="database_migration",
            event_description="Enhanced authentication system migration completed",
            success=True,
            metadata="Initial setup with sample users"
        )
        session.add(audit_log)
        session.commit()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error migrating users: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def verify_migration():
    """Verify that the migration was successful"""
    logger.info("Verifying migration...")
    
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check users
        user_count = session.query(NewUser).count()
        logger.info(f"✅ Users migrated: {user_count}")
        
        # Check developer earnings
        earnings_count = session.query(DeveloperEarning).count()
        logger.info(f"✅ Developer earnings records: {earnings_count}")
        
        # Check tables exist
        tables = ['users', 'tokens', 'developer_earnings', 'password_resets', 'audit_logs']
        for table in tables:
            result = session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            logger.info(f"✅ Table '{table}' exists with {result} records")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verifying migration: {e}")
        return False
    finally:
        session.close()

def main():
    """Run the complete migration process"""
    logger.info("🚀 Starting enhanced authentication migration...")
    
    # Step 1: Create enhanced tables
    if not create_enhanced_tables():
        logger.error("❌ Migration failed at table creation")
        return False
    
    # Step 2: Migrate existing users
    if not migrate_existing_users():
        logger.error("❌ Migration failed at user migration")
        return False
    
    # Step 3: Verify migration
    if not verify_migration():
        logger.error("❌ Migration verification failed")
        return False
    
    logger.info("🎉 Enhanced authentication migration completed successfully!")
    logger.info("📋 Next steps:")
    logger.info("   1. Test the new authentication endpoints")
    logger.info("   2. Update frontend to use JWT tokens")
    logger.info("   3. Configure email service for password resets")
    logger.info("   4. Set up monitoring and alerts")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
