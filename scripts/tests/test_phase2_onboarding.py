#!/usr/bin/env python3
"""
Complete Phase 2 Onboarding Test
================================
Tests the entire Phase 2 customer and developer onboarding flow
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_customer_registration():
    """Test customer registration and Phase 2 completion"""
    print("🧪 Testing Customer Registration & Phase 2 Onboarding")
    print("=" * 60)
    
    # Step 1: Register customer
    register_data = {
        "email": "customer@test.com",
        "password": "testpass123",
        "firstName": "John",
        "lastName": "Customer",
        "role": "CUSTOMER"
    }
    
    print("1. Registering customer...")
    try:
        response = requests.post(f"{BASE_URL}/api/enhanced/register", json=register_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ Customer registered: {user_data.get('user', {}).get('email')}")
            access_token = user_data.get('access_token')
            
            # Step 2: Complete Phase 2 profile
            phase2_data = {
                "profileCompleted": True,
                "phase2Completed": True,
                "companyName": "Test Company Inc",
                "industry": "Technology",
                "companySize": "Small team (2-10)",
                "businessType": "Startup",
                "useCase": "Customer Support",
                "budget": "$100-500/month",
                "goals": ["Increase Productivity", "Reduce Costs"],
                "preferredIntegrations": ["Slack", "HubSpot"],
                "timeline": "month",
                "experience": "intermediate"
            }
            
            print("2. Completing Phase 2 profile...")
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.post(f"{BASE_URL}/api/enhanced/complete-phase2-profile", 
                                   json=phase2_data, headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                profile = response.json()
                print(f"   ✅ Phase 2 completed for customer")
                print(f"   Company: {profile.get('company_name')}")
                print(f"   Industry: {profile.get('industry')}")
                print(f"   Goals: {profile.get('goals')}")
                return True
            else:
                print(f"   ❌ Phase 2 failed: {response.text}")
                return False
        else:
            print(f"   ❌ Registration failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_developer_registration():
    """Test developer registration and Phase 2 completion"""
    print("\n🧪 Testing Developer Registration & Phase 2 Onboarding")
    print("=" * 60)
    
    # Step 1: Register developer
    register_data = {
        "email": "developer@test.com",
        "password": "testpass123",
        "firstName": "Jane",
        "lastName": "Developer",
        "role": "DEVELOPER"
    }
    
    print("1. Registering developer...")
    try:
        response = requests.post(f"{BASE_URL}/api/enhanced/register", json=register_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ Developer registered: {user_data.get('user', {}).get('email')}")
            access_token = user_data.get('access_token')
            
            # Step 2: Complete Phase 2 profile
            phase2_data = {
                "profileCompleted": True,
                "phase2Completed": True,
                "experienceLevel": "Senior (5-10 years)",
                "primaryLanguages": ["Python", "JavaScript", "TypeScript"],
                "specializations": ["API Development", "AI/ML", "Web Applications"],
                "githubProfile": "https://github.com/janedeveloper",
                "portfolioUrl": "https://janedeveloper.dev",
                "socialLinks": {
                    "linkedin": "https://linkedin.com/in/janedeveloper",
                    "twitter": "https://twitter.com/janedeveloper"
                },
                "previousProjects": "Built multiple AI-powered applications and APIs",
                "availability": "Part-time",
                "hourlyRate": "$75-100/hour",
                "earningsTarget": "High",
                "revenueShare": 0.25
            }
            
            print("2. Completing Phase 2 profile...")
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.post(f"{BASE_URL}/api/enhanced/complete-phase2-profile", 
                                   json=phase2_data, headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                profile = response.json()
                print(f"   ✅ Phase 2 completed for developer")
                print(f"   Languages: {profile.get('primary_languages')}")
                print(f"   Specializations: {profile.get('specializations')}")
                print(f"   Revenue Share: {profile.get('revenue_share')}")
                return True
            else:
                print(f"   ❌ Phase 2 failed: {response.text}")
                return False
        else:
            print(f"   ❌ Registration failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Phase 2 Onboarding System Test")
    print("Testing against:", BASE_URL)
    print("=" * 60)
    
    # Test server connectivity
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ Backend server is running")
        else:
            print("❌ Backend server not responding")
            return
    except:
        print("❌ Cannot connect to backend server")
        return
    
    # Run tests
    customer_success = test_customer_registration()
    developer_success = test_developer_registration()
    
    # Summary
    print("\n📊 Test Results")
    print("=" * 60)
    print(f"Customer Registration & Phase 2: {'✅ PASS' if customer_success else '❌ FAIL'}")
    print(f"Developer Registration & Phase 2: {'✅ PASS' if developer_success else '❌ FAIL'}")
    
    if customer_success and developer_success:
        print("\n🎉 ALL TESTS PASSED! Phase 2 onboarding is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main()
