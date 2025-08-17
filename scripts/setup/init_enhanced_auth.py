#!/usr/bin/env python3
"""
Initialize Enhanced Authentication System
========================================

This script sets up the enhanced authentication system with:
- Creates all necessary tables
- Adds sample users for testing
- Verifies the system is working
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

# Set environment variables
os.environ.setdefault("DATABASE_URL", "sqlite:///./capecontrol.db")
os.environ.setdefault("SECRET_KEY", "dev-secret-key-change-in-production")

from backend.app.database import engine, Base
from backend.app.models_enhanced import UserV2, UserRole, Token, DeveloperEarning, PasswordReset, AuditLog
from backend.app.auth_enhanced import auth_service
from sqlalchemy.orm import sessionmaker
from datetime import datetime

def init_enhanced_auth():
    """Initialize the enhanced authentication system"""
    print("🚀 Initializing Enhanced Authentication System...")
    
    # Create all tables
    print("📋 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if users already exist
        existing_users = session.query(UserV2).count()
        if existing_users > 0:
            print(f"✅ Found {existing_users} existing users")
            return
        
        # Create sample users
        print("👤 Creating sample users...")
        
        # Admin user
        admin_user = UserV2(
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
        
        # Developer user
        developer_user = UserV2(
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
        
        # Customer user
        customer_user = UserV2(
            email="customer@capecontrol.com",
            password_hash=auth_service.get_password_hash("CustomerPassword123!"),
            role=UserRole.CUSTOMER,
            first_name="John",
            last_name="Customer",
            experience="beginner",
            is_active=True,
            is_verified=True,
            email_verified_at=datetime.utcnow(),
            terms_accepted_at=datetime.utcnow(),
            privacy_accepted_at=datetime.utcnow()
        )
        session.add(customer_user)
        
        # Commit the users first to get their IDs
        session.commit()
        
        # Add sample developer earnings
        print("💰 Creating sample developer earnings...")
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
        
        # Add another agent for the developer
        earnings2 = DeveloperEarning(
            user_id=developer_user.id,
            agent_id="code_helper_v2",
            agent_name="Code Helper Assistant",
            revenue_share=875.50,
            total_sales=2918.33,
            commission_rate=0.3000,
            last_payout_amount=500.00,
            total_paid_out=500.00,
            is_active=True
        )
        session.add(earnings2)
        
        session.commit()
        
        print("✅ Enhanced authentication system initialized successfully!")
        print("\n📝 Sample Users Created:")
        print("  🔑 Admin: admin@capecontrol.com / AdminPassword123!")
        print("  🔧 Developer: developer@capecontrol.com / DevPassword123!")
        print("  👤 Customer: customer@capecontrol.com / CustomerPassword123!")
        print("\n🎯 You can now test the enhanced authentication endpoints!")
        
    except Exception as e:
        print(f"❌ Error initializing system: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    init_enhanced_auth()
