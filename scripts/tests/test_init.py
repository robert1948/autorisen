#!/usr/bin/env python3
import os
import sys

print("Starting enhanced auth initialization...")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")

# Set up environment
os.environ['DATABASE_URL'] = 'sqlite:///./capecontrol.db'
print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")

# Add paths
sys.path.insert(0, './backend')
print(f"Python path: {sys.path[:3]}")

try:
    print("Importing modules...")
    from app.database import engine, Base
    print("✅ Database imported")
    
    from app.models_enhanced import UserV2, UserRole, Token, DeveloperEarning, PasswordReset, AuditLog
    print("✅ Models imported")
    
    from app.auth_enhanced import auth_service
    print("✅ Auth service imported")
    
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")
    
    print("✅ Enhanced authentication system initialized successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
