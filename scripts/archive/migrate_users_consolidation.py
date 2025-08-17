#!/usr/bin/env python3
"""
Migration script to consolidate users from 'users' table to 'users_v2' table
and then drop the old 'users' table.
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from urllib.parse import urlparse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment or Heroku"""
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        logger.error("DATABASE_URL environment variable not found")
        sys.exit(1)
    
    # Handle Heroku postgres URL format
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    return db_url

def migrate_users():
    """Migrate users from 'users' table to 'users_v2' table"""
    db_url = get_database_url()
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Check existing users in both tables
                old_count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
                new_count = conn.execute(text("SELECT COUNT(*) FROM users_v2")).scalar()
                
                logger.info(f"Found {old_count} users in 'users' table")
                logger.info(f"Found {new_count} users in 'users_v2' table")
                
                # Get users from old table that don't exist in new table
                migration_query = text("""
                    SELECT u.email, u.password_hash, u.user_role, u.full_name, 
                           u.created_at, u.company_name, u.tos_accepted_at
                    FROM users u
                    WHERE u.email NOT IN (SELECT email FROM users_v2)
                """)
                
                users_to_migrate = conn.execute(migration_query).fetchall()
                logger.info(f"Found {len(users_to_migrate)} users to migrate")
                
                # Migrate each user
                migrated_count = 0
                for user in users_to_migrate:
                    # Map user_role from old format to new format
                    role_mapping = {
                        'client': 'CUSTOMER',
                        'developer': 'DEVELOPER', 
                        'admin': 'ADMIN'
                    }
                    
                    new_role = role_mapping.get(user.user_role, 'CUSTOMER')
                    
                    # Split full_name into first_name and last_name
                    full_name = user.full_name or ""
                    name_parts = full_name.split(' ', 1)
                    first_name = name_parts[0] if name_parts else ""
                    last_name = name_parts[1] if len(name_parts) > 1 else ""
                    
                    # Insert into users_v2
                    insert_query = text("""
                        INSERT INTO users_v2 (
                            email, password_hash, role, first_name, last_name,
                            company, created_at, terms_accepted_at, is_active, is_verified
                        ) VALUES (
                            :email, :password_hash, :role, :first_name, :last_name,
                            :company, :created_at, :terms_accepted_at, true, false
                        )
                    """)
                    
                    conn.execute(insert_query, {
                        'email': user.email,
                        'password_hash': user.password_hash,
                        'role': new_role,
                        'first_name': first_name,
                        'last_name': last_name,
                        'company': user.company_name,
                        'created_at': user.created_at,
                        'terms_accepted_at': user.tos_accepted_at
                    })
                    
                    migrated_count += 1
                    logger.info(f"Migrated user: {user.email} as {new_role}")
                
                # Verify migration
                final_count = conn.execute(text("SELECT COUNT(*) FROM users_v2")).scalar()
                logger.info(f"Migration complete. users_v2 now has {final_count} users")
                
                # Commit the transaction
                trans.commit()
                logger.info(f"✅ Successfully migrated {migrated_count} users")
                
                return migrated_count
                
            except Exception as e:
                trans.rollback()
                logger.error(f"Migration failed, rolling back: {e}")
                raise
                
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

def drop_old_table():
    """Drop the old 'users' table after migration"""
    db_url = get_database_url()
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            # Check if there are any foreign key constraints pointing to users table
            fk_check = text("""
                SELECT tc.constraint_name, tc.table_name, kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu 
                    ON tc.constraint_name = kcu.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                AND kcu.referenced_table_name = 'users'
            """)
            
            constraints = conn.execute(fk_check).fetchall()
            
            if constraints:
                logger.warning("Found foreign key constraints pointing to 'users' table:")
                for constraint in constraints:
                    logger.warning(f"  {constraint.table_name}.{constraint.column_name} -> {constraint.constraint_name}")
                
                # Drop foreign key constraints first
                for constraint in constraints:
                    drop_fk = text(f"ALTER TABLE {constraint.table_name} DROP CONSTRAINT {constraint.constraint_name}")
                    conn.execute(drop_fk)
                    logger.info(f"Dropped constraint: {constraint.constraint_name}")
            
            # Now drop the table
            conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
            conn.commit()
            logger.info("✅ Successfully dropped old 'users' table")
            
    except Exception as e:
        logger.error(f"Failed to drop old table: {e}")
        raise

def main():
    """Main migration process"""
    logger.info("Starting user table consolidation...")
    
    try:
        # Step 1: Migrate users
        migrated_count = migrate_users()
        
        if migrated_count > 0:
            logger.info(f"Migration successful! {migrated_count} users moved to users_v2")
        
        # Step 2: Ask for confirmation before dropping old table
        response = input("\nDo you want to drop the old 'users' table? (yes/no): ")
        if response.lower() in ['yes', 'y']:
            drop_old_table()
            logger.info("✅ Table consolidation complete!")
        else:
            logger.info("Old 'users' table kept. You can drop it manually later.")
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
