#!/usr/bin/env python3
"""
Quick Stripe API Test for CapeControl
Tests basic API endpoints without authentication
"""

import requests
import json
import sys

def test_stripe_endpoints():
    """Test Stripe endpoints that don't require authentication"""
    
    base_url = "https://cape-control.com"
    
    print("🧪 Quick Stripe API Test")
    print(f"📍 Testing: {base_url}")
    print("=" * 50)
    
    tests = []
    
    # Test 1: Pricing endpoint
    try:
        response = requests.get(f"{base_url}/api/payment/pricing", timeout=10)
        pricing_success = response.status_code == 200
        
        if pricing_success:
            try:
                data = response.json()
                print("✅ Pricing endpoint: SUCCESS")
                print(f"   - Status: {response.status_code}")
                print(f"   - Response type: {type(data)}")
                if isinstance(data, list):
                    print(f"   - Plans available: {len(data)}")
            except json.JSONDecodeError:
                print("⚠️  Pricing endpoint: JSON parse error")
                pricing_success = False
        else:
            print(f"❌ Pricing endpoint: FAILED ({response.status_code})")
            
    except Exception as e:
        print(f"❌ Pricing endpoint: ERROR - {e}")
        pricing_success = False
    
    tests.append(("Pricing Endpoint", pricing_success))
    
    # Test 2: Customer endpoint (should return 401/403 without auth)
    try:
        response = requests.get(f"{base_url}/api/payment/customer", timeout=10)
        customer_success = response.status_code in [401, 403]  # Expected without auth
        
        if customer_success:
            print("✅ Customer endpoint: SUCCESS (proper auth required)")
        else:
            print(f"⚠️  Customer endpoint: Unexpected status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Customer endpoint: ERROR - {e}")
        customer_success = False
    
    tests.append(("Customer Auth Check", customer_success))
    
    # Test 3: Webhook endpoint
    try:
        test_payload = {"type": "test", "data": {}}
        response = requests.post(f"{base_url}/api/payment/webhook", 
                               json=test_payload, timeout=10)
        
        # Webhook should exist (even if it rejects the payload)
        webhook_success = response.status_code != 404
        
        if webhook_success:
            print(f"✅ Webhook endpoint: SUCCESS (exists, status {response.status_code})")
        else:
            print(f"❌ Webhook endpoint: NOT FOUND")
            
    except Exception as e:
        print(f"❌ Webhook endpoint: ERROR - {e}")
        webhook_success = False
    
    tests.append(("Webhook Endpoint", webhook_success))
    
    # Test 4: Frontend pages
    frontend_tests = [
        ("/", "Landing Page"),
        ("/subscribe", "Subscribe Page"),
        ("/privacy", "Privacy Page"),
        ("/terms", "Terms Page")
    ]
    
    for path, name in frontend_tests:
        try:
            response = requests.get(f"{base_url}{path}", timeout=10)
            page_success = response.status_code == 200 and "<!DOCTYPE html>" in response.text
            
            if page_success:
                print(f"✅ {name}: SUCCESS")
            else:
                print(f"❌ {name}: FAILED ({response.status_code})")
                
        except Exception as e:
            print(f"❌ {name}: ERROR - {e}")
            page_success = False
        
        tests.append((name, page_success))
    
    # Summary
    total_tests = len(tests)
    passed_tests = sum(1 for _, success in tests if success)
    
    print("\n" + "=" * 50)
    print(f"📊 SUMMARY")
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    if passed_tests < total_tests:
        print(f"\n❌ Failed Tests:")
        for name, success in tests:
            if not success:
                print(f"   - {name}")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = test_stripe_endpoints()
    sys.exit(0 if success else 1)
