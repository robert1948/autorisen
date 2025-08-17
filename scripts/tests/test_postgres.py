#!/usr/bin/env python3
import sys
import os
sys.path.append('/workspaces/localstorm/backend')

print("Testing PostgreSQL setup...")

try:
    # Test database connection
    from app.database import engine
    connection = engine.connect()
    print("✅ Database connection successful")
    connection.close()
    
    # Test model imports
    from app.models_enhanced import UserV2, Token, DeveloperEarning, PasswordReset, AuditLog
    print("✅ Model imports successful")
    
    # Check UserV2 columns
    print(f"✅ UserV2 has {len(UserV2.__table__.columns)} columns")
    
    # Create tables
    from app.database import Base
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")
    
    # Verify tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"✅ Tables in database: {tables}")
    
    # Check users_v2 columns
    if 'users_v2' in tables:
        columns = inspector.get_columns('users_v2')
        print(f"✅ users_v2 has {len(columns)} columns in database")
        
        print("\nColumns in database:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
        
        print(f"\nColumns in UserV2 model ({len(UserV2.__table__.columns)}):")
        for col in UserV2.__table__.columns:
            print(f"  - {col.name}: {col.type}")
        
        phase2_fields = ['profile_completed', 'phase2_completed', 'company_name', 'goals']
        found = [col['name'] for col in columns if col['name'] in phase2_fields]
        print(f"\n✅ Found Phase 2 sample fields: {found}")
        
        if len(columns) != len(UserV2.__table__.columns):
            print(f"⚠️  Mismatch: DB has {len(columns)} columns, model has {len(UserV2.__table__.columns)}")
            print("This suggests the table needs to be recreated with the updated model.")
    
    print("🎉 PostgreSQL setup complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
