#!/usr/bin/env python3
"""
Stripe Webhook Test Script
This script helps you test your Stripe webhook configuration.
"""

import os

import requests


def test_webhook_endpoint():
    """Test if the webhook endpoint is accessible."""

    print("🧪 Testing Stripe Webhook Configuration...")
    print("=" * 50)

    # Test 1: Check environment variables
    print("1. 🔑 Checking Environment Variables:")

    stripe_secret = os.getenv("STRIPE_SECRET_KEY")
    stripe_public = os.getenv("STRIPE_PUBLISHABLE_KEY")
    stripe_webhook = os.getenv("STRIPE_WEBHOOK_SECRET")

    if stripe_secret and stripe_secret.startswith("sk_test_"):
        print(f"   ✅ STRIPE_SECRET_KEY: sk_test_***{stripe_secret[-10:]}")
    else:
        print("   ❌ STRIPE_SECRET_KEY: Missing or invalid")

    if stripe_public and stripe_public.startswith("pk_test_"):
        print(f"   ✅ STRIPE_PUBLISHABLE_KEY: pk_test_***{stripe_public[-10:]}")
    else:
        print("   ❌ STRIPE_PUBLISHABLE_KEY: Missing or invalid")

    if stripe_webhook and stripe_webhook.startswith("whsec_"):
        print(f"   ✅ STRIPE_WEBHOOK_SECRET: whsec_***{stripe_webhook[-10:]}")
    else:
        print(
            "   ⚠️  STRIPE_WEBHOOK_SECRET: Update this with your actual webhook secret"
        )

    print()

    # Test 2: Check if server is running
    print("2. 🌐 Testing Server Connectivity:")

    server_url = "http://localhost:8000"

    try:
        # Test health endpoint
        response = requests.get(f"{server_url}/api/status", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Server running at {server_url}")
            print(f"   ✅ API Status: {response.json().get('message', 'OK')}")
        else:
            print(f"   ⚠️  Server responding but with status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Server not running at {server_url}")
        print("      Run: ./start_stripe_server.sh")
        return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False

    print()

    # Test 3: Check Stripe endpoints
    print("3. 🔗 Testing Stripe Endpoints:")

    stripe_endpoints = [
        "/api/stripe/status",
        "/api/stripe/prices",
        "/api/stripe/customer",
    ]

    for endpoint in stripe_endpoints:
        try:
            response = requests.get(f"{server_url}{endpoint}", timeout=5)
            if response.status_code in [
                200,
                401,
            ]:  # 401 is expected for auth-required endpoints
                print(f"   ✅ {endpoint}: Accessible")
            else:
                print(f"   ⚠️  {endpoint}: Status {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint}: {e}")

    print()

    # Test 4: Webhook endpoint test
    print("4. 🪝 Testing Webhook Endpoint:")

    webhook_url = f"{server_url}/api/stripe/webhook"

    try:
        # Test POST to webhook (should return method not allowed or require proper headers)
        response = requests.post(
            webhook_url,
            json={"test": "webhook"},
            headers={"Content-Type": "application/json"},
            timeout=5,
        )

        if response.status_code in [
            200,
            400,
            401,
            405,
        ]:  # These are all acceptable responses
            print(f"   ✅ Webhook endpoint accessible at {webhook_url}")
            print("   📋 Use this URL in your Stripe Dashboard")
        else:
            print(f"   ⚠️  Webhook endpoint status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Webhook endpoint error: {e}")

    print()
    print("🎉 Configuration Summary:")
    print("📋 Next Steps:")
    print("   1. Update STRIPE_WEBHOOK_SECRET in .env file")
    print("   2. Add webhook endpoint in Stripe Dashboard:")
    print(f"      URL: {webhook_url}")
    print("   3. Test payment flow from your frontend")
    print("   4. Monitor webhook events in Stripe Dashboard")

    return True


if __name__ == "__main__":
    test_webhook_endpoint()
