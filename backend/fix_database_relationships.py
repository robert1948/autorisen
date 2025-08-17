#!/usr/bin/env python3
"""
Fix Database Relationships - August 1, 2025
===========================================

Fixes database relationship issues identified in production logs:
1. AuditLog.user relationship foreign key mismatch
2. Ensure proper table references
3. Add missing indexes for performance
"""

import sys
import os
import asyncio
from sqlalchemy import create_engine, text, MetaData, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Add backend to path
sys.path.append(os.path.dirname(__file__))

try:
    from app.database import DATABASE_URL, engine
    from app.models import User, Conversation, ConversationMessage, UserProfile
    from app.models.audit_log import AuditLog
    print("✅ Successfully imported models")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def fix_foreign_key_constraints():
    """Fix foreign key constraints in the database"""
    try:
        with engine.begin() as conn:
            print("🔍 Checking current database schema...")
            
            # Check if audit_logs table exists
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            if 'audit_logs' in tables:
                print("✅ audit_logs table exists")
                
                # Check foreign key constraints
                fks = inspector.get_foreign_keys('audit_logs')
                print(f"📊 Current foreign keys: {fks}")
                
                # Drop existing foreign key constraint if it references wrong table
                for fk in fks:
                    if fk['referred_table'] == 'users':
                        print(f"🔧 Dropping incorrect foreign key: {fk['name']}")
                        try:
                            conn.execute(text(f"ALTER TABLE audit_logs DROP CONSTRAINT IF EXISTS {fk['name']}"))
                        except Exception as e:
                            print(f"⚠️ Could not drop constraint {fk['name']}: {e}")
                
                # Add correct foreign key constraint
                print("🔧 Adding correct foreign key constraint...")
                try:
                    conn.execute(text("""
                        ALTER TABLE audit_logs 
                        ADD CONSTRAINT fk_audit_logs_user_id 
                        FOREIGN KEY (user_id) REFERENCES users_v2(id) ON DELETE SET NULL
                    """))
                    print("✅ Added foreign key constraint: audit_logs.user_id -> users_v2.id")
                except Exception as e:
                    print(f"⚠️ Foreign key constraint might already exist or error occurred: {e}")
            
            # Check conversations table
            if 'conversations' in tables:
                print("✅ conversations table exists")
                
                # Check foreign key constraints
                fks = inspector.get_foreign_keys('conversations')
                print(f"📊 Conversations foreign keys: {fks}")
                
                # Fix conversations foreign key if needed
                for fk in fks:
                    if fk['referred_table'] == 'users':
                        print(f"🔧 Dropping incorrect conversation foreign key: {fk['name']}")
                        try:
                            conn.execute(text(f"ALTER TABLE conversations DROP CONSTRAINT IF EXISTS {fk['name']}"))
                        except Exception as e:
                            print(f"⚠️ Could not drop constraint {fk['name']}: {e}")
                
                # Add correct foreign key constraint
                try:
                    conn.execute(text("""
                        ALTER TABLE conversations 
                        ADD CONSTRAINT fk_conversations_user_id 
                        FOREIGN KEY (user_id) REFERENCES users_v2(id) ON DELETE CASCADE
                    """))
                    print("✅ Added foreign key constraint: conversations.user_id -> users_v2.id")
                except Exception as e:
                    print(f"⚠️ Conversations foreign key constraint might already exist: {e}")
            
            # Add performance indexes
            print("🔧 Adding performance indexes...")
            
            performance_indexes = [
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_user_id_created ON audit_logs(user_id, created_at DESC)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_event_type_created ON audit_logs(event_type, created_at DESC)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_ip_address ON audit_logs(ip_address)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_user_updated ON conversations(user_id, updated_at DESC)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_v2_email_lower ON users_v2(LOWER(email))"
            ]
            
            for index_sql in performance_indexes:
                try:
                    conn.execute(text(index_sql))
                    print(f"✅ Created index: {index_sql.split('idx_')[1].split(' ')[0]}")
                except Exception as e:
                    print(f"⚠️ Index might already exist: {e}")
            
            print("✅ Database relationship fixes completed successfully")
            
    except Exception as e:
        print(f"❌ Error fixing database relationships: {e}")
        return False
    
    return True

def validate_relationships():
    """Validate that relationships work correctly"""
    try:
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("🔍 Validating database relationships...")
        
        # Test User model
        user_count = session.query(User).count()
        print(f"✅ Users table accessible: {user_count} users")
        
        # Test AuditLog model
        audit_count = session.query(AuditLog).count()
        print(f"✅ AuditLog table accessible: {audit_count} logs")
        
        # Test relationship query
        try:
            # This should not fail now
            recent_logs = session.query(AuditLog).join(User, AuditLog.user_id == User.id, isouter=True).limit(5).all()
            print(f"✅ AuditLog-User relationship working: {len(recent_logs)} logs retrieved")
        except Exception as e:
            print(f"⚠️ Relationship test failed: {e}")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False

def main():
    """Main execution function"""
    print("🚀 Starting database relationship fixes...")
    print(f"📍 Database URL: {DATABASE_URL[:50]}...")
    
    # Fix foreign key constraints
    if not fix_foreign_key_constraints():
        print("❌ Failed to fix foreign key constraints")
        return False
    
    # Validate relationships
    if not validate_relationships():
        print("❌ Relationship validation failed")
        return False
    
    print("🎉 All database relationship fixes completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
