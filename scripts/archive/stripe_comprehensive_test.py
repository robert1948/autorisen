#!/usr/bin/env python3
"""
Stripe Test Cards Validator for CapeControl
Tests Stripe integration with various test payment scenarios
"""

import requests
import json
import time
from datetime import datetime

class StripeTestCards:
    """Stripe test card numbers for various scenarios"""
    
    # Successful payments
    VISA = "4242424242424242"
    VISA_DEBIT = "4000056655665556" 
    MASTERCARD = "5555555555554444"
    AMEX = "378282246310005"
    DISCOVER = "6011111111111117"
    
    # Payment failures
    GENERIC_DECLINE = "4000000000000002"
    INSUFFICIENT_FUNDS = "4000000000009995"
    LOST_CARD = "4000000000009987"
    STOLEN_CARD = "4000000000009979"
    EXPIRED_CARD = "4000000000000069"
    INCORRECT_CVC = "4000000000000127"
    PROCESSING_ERROR = "4000000000000119"
    
    # Authentication required
    AUTH_REQUIRED = "4000002500003155"
    AUTH_3DS2 = "4000002760003184"
    
    # International
    UK_CARD = "4000008260003178"
    CANADA_CARD = "4000001240000000"

def test_pricing_structure():
    """Test the pricing endpoint and validate structure"""
    print("🔍 Testing Pricing Structure")
    
    try:
        response = requests.get("https://cape-control.com/api/payment/pricing")
        
        if response.status_code != 200:
            print(f"❌ Pricing API failed: {response.status_code}")
            return False
        
        data = response.json()
        print(f"✅ Pricing API responds: {response.status_code}")
        
        # Validate structure
        if isinstance(data, dict):
            print(f"📋 Pricing data structure:")
            for key, value in data.items():
                print(f"   - {key}: {type(value).__name__}")
                
        elif isinstance(data, list):
            print(f"📋 Found {len(data)} pricing plans")
            for i, plan in enumerate(data):
                if isinstance(plan, dict):
                    print(f"   Plan {i+1}: {plan.get('name', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pricing test error: {e}")
        return False

def test_api_endpoints():
    """Test all payment API endpoints"""
    print("\n🔗 Testing API Endpoints")
    
    endpoints = [
        ("GET", "/api/payment/pricing", "Pricing Plans"),
        ("GET", "/api/payment/customer", "Customer Info"),
        ("POST", "/api/payment/customer", "Create Customer"),
        ("GET", "/api/payment/subscriptions", "Subscriptions"),
        ("GET", "/api/payment/credits", "Credit Balance"),
        ("GET", "/api/payment/analytics", "Payment Analytics"),
        ("POST", "/api/payment/webhook", "Webhook Handler"),
    ]
    
    results = []
    
    for method, endpoint, description in endpoints:
        try:
            url = f"https://cape-control.com{endpoint}"
            
            if method == "GET":
                response = requests.get(url, timeout=10)
            else:
                response = requests.post(url, json={}, timeout=10)
            
            # Endpoint exists if not 404
            exists = response.status_code != 404
            
            status_info = ""
            if response.status_code == 401:
                status_info = "(requires auth)"
            elif response.status_code == 405:
                status_info = "(method not allowed)"
            elif response.status_code == 200:
                status_info = "(success)"
            
            if exists:
                print(f"✅ {description}: Endpoint exists {status_info}")
            else:
                print(f"❌ {description}: Endpoint not found")
            
            results.append((description, exists))
            
        except Exception as e:
            print(f"❌ {description}: Error - {e}")
            results.append((description, False))
    
    return results

def test_frontend_pages():
    """Test frontend pages related to payments"""
    print("\n🌐 Testing Frontend Pages")
    
    pages = [
        ("/", "Landing Page"),
        ("/subscribe", "Subscribe Page"), 
        ("/credits", "Credits Page"),
        ("/privacy", "Privacy Policy"),
        ("/terms", "Terms of Service"),
        ("/about", "About Page"),
    ]
    
    results = []
    
    for path, name in pages:
        try:
            response = requests.get(f"https://cape-control.com{path}", timeout=10)
            
            success = (response.status_code == 200 and 
                      "<!DOCTYPE html>" in response.text and
                      "<html" in response.text)
            
            if success:
                # Check for payment-related content
                content_checks = []
                if "subscribe" in path.lower():
                    content_checks = ["stripe", "payment", "subscription", "plan"]
                elif "credit" in path.lower():
                    content_checks = ["credit", "purchase", "pack"]
                
                content_found = any(check in response.text.lower() for check in content_checks)
                
                if content_checks and content_found:
                    print(f"✅ {name}: SUCCESS (payment content found)")
                elif content_checks:
                    print(f"⚠️  {name}: SUCCESS (no payment content)")
                else:
                    print(f"✅ {name}: SUCCESS")
            else:
                print(f"❌ {name}: FAILED ({response.status_code})")
            
            results.append((name, success))
            
        except Exception as e:
            print(f"❌ {name}: ERROR - {e}")
            results.append((name, False))
    
    return results

def validate_stripe_configuration():
    """Validate Stripe configuration indicators"""
    print("\n⚙️  Validating Stripe Configuration")
    
    try:
        # Check if subscribe page loads and contains Stripe references
        response = requests.get("https://cape-control.com/subscribe", timeout=10)
        
        if response.status_code == 200:
            content = response.text.lower()
            
            stripe_indicators = [
                ("stripe.js", "js.stripe.com" in content),
                ("publishable key", "pk_test_" in content or "pk_live_" in content),
                ("payment elements", "stripe" in content and "payment" in content),
                ("subscription tiers", any(tier in content for tier in ["basic", "pro", "enterprise"])),
            ]
            
            print("🔧 Stripe Configuration Indicators:")
            for indicator, found in stripe_indicators:
                status = "✅" if found else "❌"
                print(f"   {status} {indicator}: {'Found' if found else 'Not found'}")
            
            return any(found for _, found in stripe_indicators)
        else:
            print(f"❌ Could not load subscribe page: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Configuration validation error: {e}")
        return False

def test_payment_flow_simulation():
    """Simulate payment flow (without actual payments)"""
    print("\n💳 Payment Flow Simulation")
    
    # Test card data structure
    test_scenarios = [
        ("Valid Visa", StripeTestCards.VISA),
        ("Valid Mastercard", StripeTestCards.MASTERCARD), 
        ("Declined Card", StripeTestCards.GENERIC_DECLINE),
        ("Insufficient Funds", StripeTestCards.INSUFFICIENT_FUNDS),
    ]
    
    print("🧪 Test Card Scenarios Available:")
    for scenario, card in test_scenarios:
        print(f"   - {scenario}: {card[:4]}****{card[-4:]}")
    
    print("\n⚠️  Note: Actual payment testing requires:")
    print("   1. Valid JWT authentication token")
    print("   2. Stripe Elements integration on frontend")
    print("   3. Careful testing to avoid unintended charges")

def generate_test_report():
    """Generate comprehensive test report"""
    print("\n" + "="*60)
    print(f"📊 STRIPE INTEGRATION TEST REPORT")
    print(f"🕐 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Target: https://cape-control.com")
    print("="*60)
    
    # Run all tests
    pricing_ok = test_pricing_structure()
    api_results = test_api_endpoints()
    frontend_results = test_frontend_pages()
    config_ok = validate_stripe_configuration()
    
    test_payment_flow_simulation()
    
    # Calculate totals
    all_results = [("Pricing Structure", pricing_ok), ("Stripe Configuration", config_ok)]
    all_results.extend(api_results)
    all_results.extend(frontend_results)
    
    total_tests = len(all_results)
    passed_tests = sum(1 for _, success in all_results if success)
    
    print(f"\n📈 FINAL SUMMARY")
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    if passed_tests < total_tests:
        print(f"\n❌ Issues Found:")
        for name, success in all_results:
            if not success:
                print(f"   - {name}")
        
        print(f"\n🔧 Recommendations:")
        print(f"   1. Check Heroku config for Stripe keys")
        print(f"   2. Verify frontend Stripe Elements integration") 
        print(f"   3. Test with valid JWT token for authenticated endpoints")
        print(f"   4. Review API routing configuration")
    else:
        print(f"\n🎉 All tests passed! Stripe integration looks good.")
    
    print(f"\n📚 Next Steps:")
    print(f"   - Run authenticated tests with JWT token")
    print(f"   - Test actual payment flows in Stripe Dashboard")
    print(f"   - Verify webhook delivery and processing")
    print(f"   - Test subscription lifecycle (create/update/cancel)")

if __name__ == "__main__":
    generate_test_report()
