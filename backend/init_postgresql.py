#!/usr/bin/env python3
"""
PostgreSQL Database Initialization Script
=========================================

This script initializes the PostgreSQL database with all enhanced auth tables
including Phase 2 profile fields for customer and developer onboarding.

Tables created:
- users_v2: Enhanced users with Phase 2 profile fields
- tokens_v2: JWT and session management
- developer_earnings_v2: Developer revenue tracking
- password_resets_v2: Password reset tokens
- audit_logs_v2: Security audit logging
"""

import sys
import os
from datetime import datetime

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base
from app.models_enhanced import UserV2, Token, DeveloperEarning, PasswordReset, AuditLog
from sqlalchemy import inspect

def create_all_tables():
    """Create all database tables"""
    print("🚀 Initializing PostgreSQL Database with Enhanced Auth Tables")
    print("=" * 60)
    
    try:
        # Create all tables
        print("📋 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        print("🔍 Verifying table creation...")
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = ['users_v2', 'tokens_v2', 'developer_earnings_v2', 'password_resets_v2', 'audit_logs_v2']
        
        print(f"📊 Found {len(tables)} tables in database:")
        for table in sorted(tables):
            if table in expected_tables:
                print(f"  ✅ {table}")
            else:
                print(f"  📋 {table}")
        
        # Check for missing tables
        missing_tables = [table for table in expected_tables if table not in tables]
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            return False
        
        # Show Phase 2 fields in users_v2 table
        print(f"\n📋 Phase 2 Profile Fields in users_v2 table:")
        columns = inspector.get_columns('users_v2')
        phase2_fields = [
            'profile_completed', 'phase2_completed', 'company_name', 'industry', 
            'company_size', 'business_type', 'use_case', 'budget', 'goals', 
            'preferred_integrations', 'timeline', 'experience_level', 
            'primary_languages', 'specializations', 'github_profile', 
            'portfolio_url', 'social_links', 'previous_projects', 'availability', 
            'hourly_rate', 'earnings_target', 'revenue_share'
        ]
        
        found_phase2_fields = []
        for col in columns:
            if col['name'] in phase2_fields:
                found_phase2_fields.append(col['name'])
                print(f"  ✅ {col['name']}: {col['type']}")
        
        if len(found_phase2_fields) == len(phase2_fields):
            print(f"✅ All {len(phase2_fields)} Phase 2 fields created successfully!")
        else:
            missing_fields = [field for field in phase2_fields if field not in found_phase2_fields]
            print(f"❌ Missing Phase 2 fields: {missing_fields}")
            return False
        
        print(f"\n🎉 Database initialization completed successfully!")
        print(f"📊 Ready for Phase 2 customer and developer onboarding!")
        print(f"🕒 Completed at {datetime.now()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def main():
    """Main function"""
    success = create_all_tables()
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
