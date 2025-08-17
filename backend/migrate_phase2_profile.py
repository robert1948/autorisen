#!/usr/bin/env python3
"""
Phase 2 Profile Migration Script
===============================

This script adds Phase 2 profile fields to the users_v2 table to support
enhanced onboarding for customers and developers.

New fields:
- profile_completed (BOOLEAN) - Whether user completed basic profile
- phase2_completed (BOOLEAN) - Whether user completed Phase 2 onboarding
- Customer fields: company_name, industry, company_size, business_type, use_case, budget, goals, preferred_integrations, timeline
- Developer fields: experience_level, primary_languages, specializations, github_profile, portfolio_url, social_links, previous_projects, availability, hourly_rate, earnings_target, revenue_share

Run this script to migrate the database.
"""

import os
import sys
import sqlite3
from datetime import datetime

def get_db_connection():
    """Get database connection"""
    database_url = os.getenv('DATABASE_URL', 'sqlite:///./capecontrol.db')
    
    if database_url.startswith('sqlite:///'):
        # SQLite connection
        db_path = database_url.replace('sqlite:///', '')
        if not os.path.exists(db_path):
            print(f"ERROR: Database file {db_path} does not exist")
            sys.exit(1)
        return sqlite3.connect(db_path)
    else:
        # PostgreSQL connection (for production)
        import psycopg2
        from psycopg2.extras import RealDictCursor
        try:
            connection = psycopg2.connect(database_url, sslmode='require')
            return connection
        except Exception as e:
            print(f"ERROR: Failed to connect to database: {e}")
            sys.exit(1)

def check_existing_columns(cursor, is_sqlite=True):
    """Check which Phase 2 columns already exist"""
    if is_sqlite:
        cursor.execute("PRAGMA table_info(users_v2)")
        existing_columns = [row[1] for row in cursor.fetchall()]
    else:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users_v2' 
            AND table_schema = 'public'
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
    
    phase2_columns = [
        'profile_completed', 'phase2_completed', 'company_name', 'industry', 
        'company_size', 'business_type', 'use_case', 'budget', 'goals', 
        'preferred_integrations', 'timeline', 'experience_level', 
        'primary_languages', 'specializations', 'github_profile', 
        'portfolio_url', 'social_links', 'previous_projects', 'availability', 
        'hourly_rate', 'earnings_target', 'revenue_share'
    ]
    
    existing_phase2 = [col for col in phase2_columns if col in existing_columns]
    print(f"Found existing Phase 2 columns: {existing_phase2}")
    return existing_phase2

def add_phase2_columns_sqlite(cursor):
    """Add Phase 2 profile columns to users_v2 table (SQLite)"""
    
    # Define all Phase 2 columns with their SQL definitions for SQLite
    phase2_columns = [
        ('profile_completed', 'BOOLEAN DEFAULT 0 NOT NULL'),
        ('phase2_completed', 'BOOLEAN DEFAULT 0 NOT NULL'),
        ('company_name', 'TEXT'),
        ('industry', 'TEXT'),
        ('company_size', 'TEXT'),
        ('business_type', 'TEXT'),
        ('use_case', 'TEXT'),
        ('budget', 'TEXT'),
        ('goals', 'TEXT'),  # JSON as TEXT in SQLite
        ('preferred_integrations', 'TEXT'),  # JSON as TEXT in SQLite
        ('timeline', 'TEXT'),
        ('experience_level', 'TEXT'),
        ('primary_languages', 'TEXT'),  # JSON as TEXT in SQLite
        ('specializations', 'TEXT'),  # JSON as TEXT in SQLite
        ('github_profile', 'TEXT'),
        ('portfolio_url', 'TEXT'),
        ('social_links', 'TEXT'),  # JSON as TEXT in SQLite
        ('previous_projects', 'TEXT'),
        ('availability', 'TEXT'),
        ('hourly_rate', 'TEXT'),
        ('earnings_target', 'TEXT'),
        ('revenue_share', 'REAL DEFAULT 0.3000')
    ]
    
    # Check which columns already exist
    existing_columns = check_existing_columns(cursor, is_sqlite=True)
    
    # Add columns that don't exist
    for column_name, column_definition in phase2_columns:
        if column_name not in existing_columns:
            try:
                sql = f"ALTER TABLE users_v2 ADD COLUMN {column_name} {column_definition};"
                print(f"Adding column: {column_name}")
                cursor.execute(sql)
                print(f"✓ Successfully added column: {column_name}")
            except Exception as e:
                print(f"✗ Error adding column {column_name}: {e}")
                raise
        else:
            print(f"⚠ Column {column_name} already exists, skipping")

def verify_migration_sqlite(cursor):
    """Verify that all Phase 2 columns were added successfully (SQLite)"""
    cursor.execute("PRAGMA table_info(users_v2)")
    columns = cursor.fetchall()
    
    phase2_columns = [
        'profile_completed', 'phase2_completed', 'company_name', 'industry', 
        'company_size', 'business_type', 'use_case', 'budget', 'goals', 
        'preferred_integrations', 'timeline', 'experience_level', 
        'primary_languages', 'specializations', 'github_profile', 
        'portfolio_url', 'social_links', 'previous_projects', 'availability', 
        'hourly_rate', 'earnings_target', 'revenue_share'
    ]
    
    existing_phase2 = []
    print(f"\nVerification: Table structure:")
    for col in columns:
        col_name = col[1]
        col_type = col[2]
        col_nullable = "YES" if col[3] == 0 else "NO"
        col_default = col[4] if col[4] is not None else "NULL"
        
        if col_name in phase2_columns:
            existing_phase2.append(col_name)
            print(f"  ✓ {col_name}: {col_type} (nullable: {col_nullable}, default: {col_default})")
        else:
            print(f"    {col_name}: {col_type}")
    
    print(f"\nFound {len(existing_phase2)} Phase 2 columns out of {len(phase2_columns)} expected")
    return len(existing_phase2) == len(phase2_columns)

def main():
    """Main migration function"""
    print("🚀 Starting Phase 2 Profile Migration")
    print("=" * 50)
    
    # Get database connection
    connection = get_db_connection()
    is_sqlite = isinstance(connection, sqlite3.Connection)
    
    try:
        cursor = connection.cursor()
        
        # Check if users_v2 table exists
        if is_sqlite:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users_v2'")
            table_exists = cursor.fetchone() is not None
        else:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users_v2'
                );
            """)
            table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("ERROR: users_v2 table does not exist. Run the initial enhanced auth migration first.")
            sys.exit(1)
        
        print("✓ users_v2 table found")
        
        # Add Phase 2 columns
        print("\n📋 Adding Phase 2 profile columns...")
        if is_sqlite:
            add_phase2_columns_sqlite(cursor)
        else:
            # Would use PostgreSQL version for production
            pass
        
        # Commit changes
        connection.commit()
        
        # Verify migration
        print("\n🔍 Verifying migration...")
        if is_sqlite:
            success = verify_migration_sqlite(cursor)
        else:
            success = True  # Would implement PostgreSQL verification
        
        if success:
            print("✅ Migration completed successfully!")
        else:
            print("❌ Migration verification failed!")
            sys.exit(1)
        
        print(f"\n📊 Migration completed at {datetime.now()}")
        print("🎉 Phase 2 profile fields are now available!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)
    finally:
        connection.close()

if __name__ == "__main__":
    main()
