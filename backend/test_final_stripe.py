#!/usr/bin/env python3
"""
Final Stripe Integration Test
Tests the complete Stripe setup with webhook secret configured.
"""

import os
import sys

def test_stripe_environment():
    """Test Stripe environment configuration."""
    print("🧪 Testing Complete Stripe Integration...")
    print("=" * 50)
    
    # Test environment variables
    print("1. 🔑 Environment Variables:")
    
    stripe_secret = os.getenv('STRIPE_SECRET_KEY')
    stripe_public = os.getenv('STRIPE_PUBLISHABLE_KEY')
    stripe_webhook = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    if stripe_secret and stripe_secret.startswith('sk_test_'):
        print(f"   ✅ STRIPE_SECRET_KEY: {stripe_secret[:15]}...")
    else:
        print("   ❌ STRIPE_SECRET_KEY: Missing or invalid")
        return False
    
    if stripe_public and stripe_public.startswith('pk_test_'):
        print(f"   ✅ STRIPE_PUBLISHABLE_KEY: {stripe_public[:15]}...")
    else:
        print("   ❌ STRIPE_PUBLISHABLE_KEY: Missing or invalid")
        return False
    
    if stripe_webhook and stripe_webhook.startswith('whsec_'):
        print(f"   ✅ STRIPE_WEBHOOK_SECRET: {stripe_webhook[:15]}...")
    else:
        print("   ❌ STRIPE_WEBHOOK_SECRET: Missing or invalid")
        return False
    
    print()
    
    # Test imports
    print("2. 📦 Package Imports:")
    
    try:
        import stripe
        print(f"   ✅ stripe: v{stripe.version.VERSION}")
    except ImportError:
        print("   ❌ stripe: Not installed")
        return False
    
    try:
        import fastapi
        print(f"   ✅ fastapi: Available")
    except ImportError:
        print("   ❌ fastapi: Not installed")
        return False
    
    try:
        import uvicorn
        print(f"   ✅ uvicorn: Available")
    except ImportError:
        print("   ❌ uvicorn: Not installed")
        return False
    
    print()
    
    # Test route imports
    print("3. 🛤️  Route Imports:")
    
    try:
        from app.routes.stripe_routes import router
        print(f"   ✅ Stripe routes: {len(router.routes)} endpoints")
    except ImportError as e:
        print(f"   ❌ Stripe routes: {e}")
        return False
    
    try:
        from app.main import app
        print("   ✅ FastAPI app: Available")
    except ImportError as e:
        print(f"   ❌ FastAPI app: {e}")
        return False
    
    print()
    print("🎉 All tests passed! Ready to start server.")
    print()
    print("🚀 Next Steps:")
    print("1. Start server: python3 -m uvicorn app.main:app --reload --port 8000")
    print("2. Visit: http://localhost:8000/docs")
    print("3. Test webhook in Stripe Dashboard: Send test events")
    print("4. Check Stripe integration at: http://localhost:8000/api/stripe/status")
    
    return True

if __name__ == "__main__":
    success = test_stripe_environment()
    sys.exit(0 if success else 1)
