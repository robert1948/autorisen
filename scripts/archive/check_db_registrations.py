#!/usr/bin/env python3
"""
Check database registrations
"""
import sys
import os
sys.path.append('/home/robert/Documents/localstorm2/backend')

try:
    from app.database import SessionLocal
    from app import models
    from app.config import settings
    from datetime import datetime, timedelta
    
    print(f"Database URL: {settings.database_url}")
    print(f"Environment: {settings.environment}")
    
    # Get database session
    db = SessionLocal()
    
    # Query recent users (last 24 hours)
    recent_cutoff = datetime.utcnow() - timedelta(hours=24)
    
    print("\n🔍 Checking recent user registrations (last 24 hours)...")
    
    # Query all users first to see what we have
    all_users = db.query(models.User).all()
    print(f"\n📊 Total users in database: {len(all_users)}")
    
    if all_users:
        print("\n👥 All users:")
        for user in all_users:
            created_at = getattr(user, 'created_at', 'Unknown')
            print(f"  - ID: {user.id}, Email: {user.email}, Role: {getattr(user, 'user_role', 'N/A')}, Created: {created_at}")
    
    # Query recent users
    recent_users = db.query(models.User).filter(
        models.User.created_at >= recent_cutoff
    ).order_by(models.User.created_at.desc()).all()
    
    print(f"\n🕐 Recent registrations (last 24h): {len(recent_users)}")
    
    if recent_users:
        print("\n📋 Recent user details:")
        for user in recent_users:
            print(f"  📧 Email: {user.email}")
            print(f"  👤 Full Name: {getattr(user, 'full_name', 'N/A')}")
            print(f"  🏢 Role: {getattr(user, 'user_role', 'N/A')}")
            print(f"  🏭 Company: {getattr(user, 'company_name', 'N/A')}")
            print(f"  🏭 Industry: {getattr(user, 'industry', 'N/A')}")
            print(f"  💰 Budget: {getattr(user, 'project_budget', 'N/A')}")
            print(f"  🛠️ Skills: {getattr(user, 'skills', 'N/A')}")
            print(f"  🗓️ Created: {user.created_at}")
            print("  " + "─" * 50)
    else:
        print("  No recent registrations found")
    
    # Close database session
    db.close()
    
    print("\n✅ Database check completed")
    
except Exception as e:
    print(f"❌ Error checking database: {e}")
    import traceback
    traceback.print_exc()
