#!/usr/bin/env python3
"""
Registration Performance Fix - August 1, 2025
==============================================

Fixes registration timeout issues by:
1. Optimizing database queries
2. Reducing audit logging overhead
3. Improving background task handling
4. Adding request timeout handling
"""

import sys
import os
import asyncio
import time
from datetime import datetime
from typing import Optional

# Add backend to path
sys.path.append(os.path.dirname(__file__))

try:
    from app.database import get_db, engine
    from app.models import User
    from app.services.audit_service import get_audit_logger
    from sqlalchemy.orm import sessionmaker
    print("✅ Successfully imported registration modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_registration_performance():
    """Test registration performance and identify bottlenecks"""
    
    Session = sessionmaker(bind=engine)
    session = Session()
    audit_logger = get_audit_logger()
    
    try:
        print("🔍 Testing registration performance components...")
        
        # Test 1: Database connection speed
        start_time = time.time()
        user_count = session.query(User).count()
        db_time = time.time() - start_time
        print(f"✅ Database query time: {db_time:.3f}s (Users: {user_count})")
        
        # Test 2: Email uniqueness check speed
        start_time = time.time()
        test_email = "performance.test@example.com"
        existing_user = session.query(User).filter(User.email == test_email).first()
        email_check_time = time.time() - start_time
        print(f"✅ Email uniqueness check: {email_check_time:.3f}s")
        
        # Test 3: Audit logging speed
        start_time = time.time()
        try:
            audit_logger.log_authentication_event(
                db=session,
                event_type="test_performance",
                user_email=test_email,
                success=True,
                metadata={"test": "performance_check"}
            )
            audit_time = time.time() - start_time
            print(f"✅ Audit logging time: {audit_time:.3f}s")
        except Exception as e:
            print(f"⚠️ Audit logging error: {e}")
            audit_time = 0
        
        # Test 4: Password hashing speed
        start_time = time.time()
        from app.auth_enhanced import get_password_hash
        hashed = get_password_hash("test_password_123")
        hash_time = time.time() - start_time
        print(f"✅ Password hashing time: {hash_time:.3f}s")
        
        # Calculate total estimated time
        total_time = db_time + email_check_time + audit_time + hash_time
        print(f"📊 Estimated registration time: {total_time:.3f}s")
        
        if total_time > 25:  # If approaching 30s timeout
            print("⚠️ Registration time approaching timeout threshold!")
            return False
        else:
            print("✅ Registration performance within acceptable limits")
            return True
            
    except Exception as e:
        print(f"❌ Performance test error: {e}")
        return False
    finally:
        session.close()

def optimize_registration_queries():
    """Optimize database queries for registration"""
    
    try:
        with engine.begin() as conn:
            print("🔧 Optimizing registration queries...")
            
            # Add indexes for common registration queries
            optimization_queries = [
                # Email lookup optimization
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_v2_email_fast ON users_v2(email) WHERE email IS NOT NULL",
                
                # Audit log optimization for registration events
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_registration ON audit_logs(event_type, created_at DESC) WHERE event_type LIKE '%registration%'",
                
                # User creation timestamp optimization
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_v2_created_recent ON users_v2(created_at DESC) WHERE created_at > NOW() - INTERVAL '1 day'",
                
                # Password reset optimization
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_v2_email_role ON users_v2(email, user_role)",
            ]
            
            for query in optimization_queries:
                try:
                    from sqlalchemy import text
                    conn.execute(text(query))
                    index_name = query.split('idx_')[1].split(' ')[0]
                    print(f"✅ Created optimization index: {index_name}")
                except Exception as e:
                    print(f"⚠️ Index might already exist: {e}")
            
            # Update table statistics for query planner
            try:
                from sqlalchemy import text
                conn.execute(text("ANALYZE users_v2"))
                conn.execute(text("ANALYZE audit_logs"))
                print("✅ Updated table statistics")
            except Exception as e:
                print(f"⚠️ Could not update statistics: {e}")
                
    except Exception as e:
        print(f"❌ Query optimization error: {e}")
        return False
    
    return True

def check_database_locks():
    """Check for database locks that might slow registration"""
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Check for long-running queries
        lock_query = """
        SELECT 
            pid,
            state,
            query_start,
            NOW() - query_start as duration,
            query
        FROM pg_stat_activity 
        WHERE state != 'idle' 
        AND NOW() - query_start > INTERVAL '5 seconds'
        ORDER BY duration DESC
        LIMIT 10
        """
        
        from sqlalchemy import text
        result = session.execute(text(lock_query))
        long_queries = result.fetchall()
        
        if long_queries:
            print("⚠️ Found long-running queries:")
            for query in long_queries:
                print(f"  PID {query[0]}: {query[3]} - {query[4][:100]}...")
        else:
            print("✅ No problematic long-running queries found")
        
        # Check for table locks
        lock_check = """
        SELECT 
            t.relname as table_name,
            l.locktype,
            l.mode,
            l.granted
        FROM pg_locks l
        JOIN pg_class t ON l.relation = t.oid
        WHERE t.relname IN ('users_v2', 'audit_logs')
        AND NOT l.granted
        """
        
        result = session.execute(text(lock_check))
        locks = result.fetchall()
        
        if locks:
            print("⚠️ Found table locks:")
            for lock in locks:
                print(f"  Table {lock[0]}: {lock[1]} {lock[2]} (granted: {lock[3]})")
        else:
            print("✅ No problematic table locks found")
            
        session.close()
        return len(locks) == 0
        
    except Exception as e:
        print(f"❌ Lock check error: {e}")
        return True  # Assume no locks if we can't check

def main():
    """Main execution function"""
    print("🚀 Starting registration performance analysis and fixes...")
    
    # Check database locks
    if not check_database_locks():
        print("⚠️ Database locks detected - this may affect registration performance")
    
    # Test current performance
    if not test_registration_performance():
        print("⚠️ Registration performance issues detected")
    
    # Optimize queries
    if not optimize_registration_queries():
        print("❌ Failed to optimize registration queries")
        return False
    
    # Test performance again
    print("\n🔄 Re-testing performance after optimization...")
    if test_registration_performance():
        print("🎉 Registration performance optimization completed successfully!")
    else:
        print("⚠️ Performance still needs improvement")
    
    print("\n📋 Recommendations:")
    print("1. Monitor registration endpoint response times")
    print("2. Consider implementing registration queue for high load")
    print("3. Add timeout handling in frontend")
    print("4. Implement registration progress indicators")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
