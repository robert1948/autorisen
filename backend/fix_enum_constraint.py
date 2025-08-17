#!/usr/bin/env python3
"""
Fix Database Enum Constraint
============================

This script updates the users_v2 table role constraint to accept uppercase enum values.
"""

import os
import psycopg2
from urllib.parse import urlparse

def fix_enum_constraint():
    """Update the role check constraint to use uppercase values"""
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    try:
        # Parse the database URL
        url = urlparse(database_url)
        
        # Connect to database
        conn = psycopg2.connect(
            host=url.hostname,
            port=url.port,
            user=url.username,
            password=url.password,
            database=url.path[1:]  # Remove leading slash
        )
        
        cursor = conn.cursor()
        
        print("🔄 Updating users_v2 role constraint...")
        
        # Drop the old constraint
        cursor.execute("""
            ALTER TABLE users_v2 DROP CONSTRAINT IF EXISTS users_v2_role_check;
        """)
        
        # Add new constraint with uppercase values
        cursor.execute("""
            ALTER TABLE users_v2 ADD CONSTRAINT users_v2_role_check 
            CHECK (role IN ('CUSTOMER', 'DEVELOPER', 'ADMIN'));
        """)
        
        # Commit the changes
        conn.commit()
        
        print("✅ Successfully updated role constraint to accept uppercase values")
        
        # Verify the constraint
        cursor.execute("""
            SELECT conname, pg_get_constraintdef(oid) 
            FROM pg_constraint 
            WHERE conrelid = 'users_v2'::regclass 
            AND conname = 'users_v2_role_check';
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"✅ New constraint: {result[1]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating constraint: {e}")
        return False

if __name__ == "__main__":
    success = fix_enum_constraint()
    exit(0 if success else 1)
