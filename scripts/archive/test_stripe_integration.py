#!/usr/bin/env python3
"""
Automated Stripe Integration Tests for CapeControl
Tests all payment endpoints, subscription flows, and webhook handling
"""

import asyncio
import aiohttp
import json
import sys
import os
from typing import Dict, List, Optional
from datetime import datetime
import argparse

class StripeIntegrationTester:
    def __init__(self, base_url: str = "https://cape-control.com", jwt_token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.jwt_token = jwt_token
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def get_headers(self, include_auth: bool = False) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if include_auth and self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"
        return headers
    
    async def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                          include_auth: bool = False) -> Dict:
        """Make HTTP request and return response data"""
        url = f"{self.base_url}{endpoint}"
        headers = self.get_headers(include_auth)
        
        try:
            async with self.session.request(method, url, headers=headers, 
                                          json=data if data else None) as response:
                response_text = await response.text()
                
                # Try to parse as JSON
                try:
                    response_data = json.loads(response_text)
                except json.JSONDecodeError:
                    response_data = {"raw_response": response_text}
                
                return {
                    "status_code": response.status,
                    "headers": dict(response.headers),
                    "data": response_data,
                    "success": 200 <= response.status < 300
                }
        except Exception as e:
            return {
                "status_code": 0,
                "error": str(e),
                "success": False
            }
    
    def record_test_result(self, test_name: str, success: bool, details: Dict):
        """Record test result for reporting"""
        self.test_results.append({
            "test_name": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details
        })
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")
        if not success and "error" in details:
            print(f"      Error: {details['error']}")
    
    # Test Methods
    
    async def test_pricing_endpoint(self):
        """Test GET /api/payment/pricing"""
        response = await self.make_request("GET", "/api/payment/pricing")
        
        success = (response["success"] and 
                  "data" in response and 
                  isinstance(response["data"], (list, dict)))
        
        self.record_test_result("Pricing Endpoint", success, response)
        return success
    
    async def test_customer_endpoints(self):
        """Test customer-related endpoints (requires auth)"""
        if not self.jwt_token:
            self.record_test_result("Customer Endpoints", False, 
                                  {"error": "No JWT token provided"})
            return False
        
        # Test GET customer
        get_response = await self.make_request("GET", "/api/payment/customer", 
                                             include_auth=True)
        
        # Test POST customer  
        post_response = await self.make_request("POST", "/api/payment/customer", 
                                              include_auth=True)
        
        success = get_response["success"] or post_response["success"]
        
        self.record_test_result("Customer Endpoints", success, {
            "get_response": get_response,
            "post_response": post_response
        })
        return success
    
    async def test_subscriptions_endpoint(self):
        """Test GET /api/payment/subscriptions"""
        if not self.jwt_token:
            self.record_test_result("Subscriptions Endpoint", False, 
                                  {"error": "No JWT token provided"})
            return False
        
        response = await self.make_request("GET", "/api/payment/subscriptions", 
                                         include_auth=True)
        
        success = response["success"]
        self.record_test_result("Subscriptions Endpoint", success, response)
        return success
    
    async def test_credits_endpoint(self):
        """Test GET /api/payment/credits"""
        if not self.jwt_token:
            self.record_test_result("Credits Endpoint", False, 
                                  {"error": "No JWT token provided"})
            return False
        
        response = await self.make_request("GET", "/api/payment/credits", 
                                         include_auth=True)
        
        success = response["success"]
        self.record_test_result("Credits Endpoint", success, response)
        return success
    
    async def test_analytics_endpoint(self):
        """Test GET /api/payment/analytics"""
        if not self.jwt_token:
            self.record_test_result("Analytics Endpoint", False, 
                                  {"error": "No JWT token provided"})
            return False
        
        response = await self.make_request("GET", "/api/payment/analytics", 
                                         include_auth=True)
        
        success = response["success"]
        self.record_test_result("Analytics Endpoint", success, response)
        return success
    
    async def test_webhook_endpoint(self):
        """Test POST /api/payment/webhook"""
        test_payload = {
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_test_123",
                    "amount": 2999,
                    "currency": "usd"
                }
            }
        }
        
        response = await self.make_request("POST", "/api/payment/webhook", 
                                         data=test_payload)
        
        # Webhook might return 400 due to signature verification, but should not return HTML
        success = (response["status_code"] != 0 and 
                  "<!DOCTYPE" not in str(response.get("data", "")))
        
        self.record_test_result("Webhook Endpoint", success, response)
        return success
    
    async def test_subscription_creation(self):
        """Test subscription creation with test payment method"""
        if not self.jwt_token:
            self.record_test_result("Subscription Creation", False, 
                                  {"error": "No JWT token provided"})
            return False
        
        test_data = {
            "tier": "Pro",
            "payment_method_id": "pm_card_visa"  # Stripe test payment method
        }
        
        response = await self.make_request("POST", "/api/payment/subscribe", 
                                         data=test_data, include_auth=True)
        
        success = response["success"] and "subscription_id" in response.get("data", {})
        
        self.record_test_result("Subscription Creation", success, response)
        return success
    
    async def test_credit_purchase(self):
        """Test credit purchase with test payment method"""
        if not self.jwt_token:
            self.record_test_result("Credit Purchase", False, 
                                  {"error": "No JWT token provided"})
            return False
        
        test_data = {
            "pack_size": "small",
            "payment_method_id": "pm_card_visa"  # Stripe test payment method
        }
        
        response = await self.make_request("POST", "/api/payment/credits/purchase", 
                                         data=test_data, include_auth=True)
        
        success = response["success"] and "payment_intent_id" in response.get("data", {})
        
        self.record_test_result("Credit Purchase", success, response)
        return success
    
    async def test_payment_methods_endpoint(self):
        """Test payment methods endpoint if available"""
        if not self.jwt_token:
            return False
        
        response = await self.make_request("GET", "/api/payment/methods", 
                                         include_auth=True)
        
        success = response["success"]
        self.record_test_result("Payment Methods Endpoint", success, response)
        return success
    
    # Main test runner
    
    async def run_all_tests(self) -> Dict:
        """Run all Stripe integration tests"""
        print("🧪 Starting Stripe Integration Tests")
        print(f"📍 Testing against: {self.base_url}")
        print(f"🔑 JWT Token: {'✅ Provided' if self.jwt_token else '❌ Not provided'}")
        print("=" * 60)
        
        # Run tests
        await self.test_pricing_endpoint()
        await self.test_customer_endpoints() 
        await self.test_subscriptions_endpoint()
        await self.test_credits_endpoint()
        await self.test_analytics_endpoint()
        await self.test_webhook_endpoint()
        await self.test_payment_methods_endpoint()
        
        # Test actual payment flows (be careful with these)
        if self.jwt_token:
            print("\n🔄 Testing Payment Flows (use with caution)")
            # await self.test_subscription_creation()  # Uncomment to test actual payments
            # await self.test_credit_purchase()       # Uncomment to test actual payments
        
        # Generate report
        return self.generate_report()
    
    def generate_report(self) -> Dict:
        """Generate test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 60)
        print(f"📊 TEST SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   - {result['test_name']}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests/total_tests) if total_tests > 0 else 0,
            "results": self.test_results
        }

async def main():
    parser = argparse.ArgumentParser(description="Test Stripe integration for CapeControl")
    parser.add_argument("--url", default="https://cape-control.com", 
                       help="Base URL to test against")
    parser.add_argument("--token", help="JWT token for authenticated requests")
    parser.add_argument("--local", action="store_true", 
                       help="Test against local development server")
    parser.add_argument("--output", help="Save results to JSON file")
    
    args = parser.parse_args()
    
    # Set URL based on local flag
    if args.local:
        base_url = "http://localhost:8000"
    else:
        base_url = args.url
    
    # Run tests
    async with StripeIntegrationTester(base_url, args.token) as tester:
        report = await tester.run_all_tests()
        
        # Save results if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n💾 Results saved to: {args.output}")
        
        # Exit with appropriate code
        sys.exit(0 if report["failed_tests"] == 0 else 1)

if __name__ == "__main__":
    asyncio.run(main())
