#!/usr/bin/env python3
import os
import sys

# Set up all required environment variables
os.environ['DATABASE_URL'] = 'sqlite:///./capecontrol.db'
os.environ['PROJECT_NAME'] = 'CapeControl'
os.environ['POSTGRES_DB'] = 'capecontrol'
os.environ['POSTGRES_USER'] = 'capecontrol_user'
os.environ['POSTGRES_PASSWORD'] = 'dev-password-123'
os.environ['SECRET_KEY'] = 'dev-secret-key-change-in-production'
os.environ['ENV'] = 'development'
os.environ['DEBUG'] = 'true'
os.environ['ALLOWED_HOSTS'] = 'localhost,127.0.0.1'
os.environ['CORS_ORIGINS'] = 'http://localhost:3000'
os.environ['API_URL'] = 'http://localhost:8000'

print("Starting enhanced auth initialization...")
sys.path.insert(0, './backend')

try:
    print("Testing database connection...")
    from app.database import engine, Base
    print("✅ Database imported")
    
    # Test database connection
    connection = engine.connect()
    connection.close()
    print("✅ Database connection successful")
    
    print("Importing models...")
    from app.models_enhanced import UserV2, UserRole, Token, DeveloperEarning, PasswordReset, AuditLog
    print("✅ Models imported")
    
    print("Importing auth service...")
    from app.auth_enhanced import auth_service
    print("✅ Auth service imported")
    
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")
    
    # Test creating a user
    from sqlalchemy.orm import sessionmaker
    from datetime import datetime
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        existing_users = session.query(UserV2).count()
        print(f"Found {existing_users} existing users")
        
        if existing_users == 0:
            print("Creating sample admin user...")
            admin_user = UserV2(
                email="admin@capecontrol.com",
                password_hash=auth_service.get_password_hash("AdminPassword123!"),
                role=UserRole.ADMIN,
                first_name="System",
                last_name="Administrator",
                is_active=True,
                is_verified=True,
                email_verified_at=datetime.utcnow(),
                terms_accepted_at=datetime.utcnow(),
                privacy_accepted_at=datetime.utcnow()
            )
            session.add(admin_user)
            session.commit()
            print("✅ Sample admin user created")
        
        print("🎯 Enhanced authentication system is ready!")
        
    except Exception as e:
        print(f"❌ Error with users: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
