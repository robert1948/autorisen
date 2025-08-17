#!/usr/bin/env python3
import os
import sys

# Set environment variables
os.environ['DATABASE_URL'] = 'sqlite:///./capecontrol.db'
os.environ['SECRET_KEY'] = 'dev-secret-key-change-in-production'

print("Testing config...")
sys.path.insert(0, './backend')

try:
    # Try to import without using the config
    print("Testing database import...")
    from app.database import engine, Base
    print("✅ Database imported")
    
    print("Testing models import...")
    from app.models_enhanced import UserV2, UserRole
    print("✅ Models imported")
    
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")
    
    print("Testing auth service...")
    from app.auth_enhanced import auth_service
    print("✅ Auth service imported")
    
    print("✅ All imports successful!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
