#!/usr/bin/env python3
"""
Migration script to add Stripe-related fields to the users_v2 table.
Run this script to update the database schema for Stripe integration.
"""

import os
import sys
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Add the app directory to the path to import database module
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def migrate_stripe_fields():
    """Add Stripe-related columns to users_v2 table."""
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    # Convert postgres:// to postgresql:// for async support
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    print(f"🔗 Connecting to database...")
    
    try:
        # Create async engine
        engine = create_async_engine(database_url)
        
        # SQL commands to add new columns
        migration_commands = [
            "ALTER TABLE users_v2 ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(255);",
            "ALTER TABLE users_v2 ADD COLUMN IF NOT EXISTS subscription_status VARCHAR(50);",
            "ALTER TABLE users_v2 ADD COLUMN IF NOT EXISTS subscription_id VARCHAR(255);",
            "ALTER TABLE users_v2 ADD COLUMN IF NOT EXISTS plan_id VARCHAR(100);",
            "ALTER TABLE users_v2 ADD COLUMN IF NOT EXISTS subscription_ends_at TIMESTAMP WITH TIME ZONE;",
            "CREATE INDEX IF NOT EXISTS idx_users_v2_stripe_customer_id ON users_v2(stripe_customer_id);"
        ]
        
        async with engine.begin() as conn:
            for command in migration_commands:
                print(f"📝 Executing: {command}")
                await conn.execute(text(command))
        
        print("✅ Successfully added Stripe fields to users_v2 table")
        print("🔍 Added columns:")
        print("   - stripe_customer_id VARCHAR(255) with index")
        print("   - subscription_status VARCHAR(50)")
        print("   - subscription_id VARCHAR(255)")
        print("   - plan_id VARCHAR(100)")
        print("   - subscription_ends_at TIMESTAMP WITH TIME ZONE")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Stripe fields migration...")
    success = asyncio.run(migrate_stripe_fields())
    if success:
        print("✅ Migration completed successfully!")
        sys.exit(0)
    else:
        print("❌ Migration failed!")
        sys.exit(1)
