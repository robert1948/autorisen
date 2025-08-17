"""
Enhanced Authentication System Test Suite
=========================================

Comprehensive testing for the CapeControl authentication system including:
- API endpoint testing
- Authentication flow validation
- Security feature verification
- Developer revenue system testing
"""

import asyncio
import httpx
import json
import pytest
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthTestSuite:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url)
        self.test_users = {}
        self.tokens = {}
    
    async def test_user_registration(self):
        """Test user registration endpoint"""
        logger.info("🧪 Testing user registration...")
        
        # Test customer registration
        customer_data = {
            "email": "test_customer@example.com",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "Customer",
            "role": "customer",
            "experience": "intermediate"
        }
        
        response = await self.client.post("/api/auth/register", json=customer_data)
        assert response.status_code == 201, f"Registration failed: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        assert "tokens" in data["data"]
        assert "user" in data["data"]
        
        self.test_users["customer"] = data["data"]["user"]
        self.tokens["customer"] = data["data"]["tokens"]
        
        logger.info("✅ Customer registration successful")
        
        # Test developer registration
        developer_data = {
            "email": "test_developer@example.com",
            "password": "DevPassword123!",
            "first_name": "Test",
            "last_name": "Developer",
            "role": "developer",
            "company": "Test Corp",
            "website": "https://testcorp.com",
            "experience": "expert"
        }
        
        response = await self.client.post("/api/auth/register", json=developer_data)
        assert response.status_code == 201, f"Developer registration failed: {response.text}"
        
        data = response.json()
        self.test_users["developer"] = data["data"]["user"]
        self.tokens["developer"] = data["data"]["tokens"]
        
        logger.info("✅ Developer registration successful")
        
        # Test duplicate email (should fail)
        response = await self.client.post("/api/auth/register", json=customer_data)
        assert response.status_code == 409, "Duplicate email should be rejected"
        
        logger.info("✅ Duplicate email properly rejected")
    
    async def test_user_login(self):
        """Test user login endpoint"""
        logger.info("🧪 Testing user login...")
        
        # Test valid login
        login_data = {
            "email": "test_customer@example.com",
            "password": "TestPassword123!"
        }
        
        response = await self.client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        assert "tokens" in data["data"]
        
        # Update tokens
        self.tokens["customer"] = data["data"]["tokens"]
        
        logger.info("✅ Valid login successful")
        
        # Test invalid login
        invalid_login = {
            "email": "test_customer@example.com",
            "password": "WrongPassword"
        }
        
        response = await self.client.post("/api/auth/login", json=invalid_login)
        assert response.status_code == 401, "Invalid login should be rejected"
        
        logger.info("✅ Invalid login properly rejected")
    
    async def test_protected_endpoints(self):
        """Test JWT-protected endpoints"""
        logger.info("🧪 Testing protected endpoints...")
        
        # Test accessing profile without token (should fail)
        response = await self.client.get("/api/auth/me")
        assert response.status_code == 401, "Unauthenticated access should be rejected"
        
        # Test accessing profile with valid token
        headers = {"Authorization": f"Bearer {self.tokens['customer']['access_token']}"}
        response = await self.client.get("/api/auth/me", headers=headers)
        assert response.status_code == 200, f"Authenticated access failed: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        assert data["data"]["email"] == "test_customer@example.com"
        
        logger.info("✅ JWT authentication working correctly")
    
    async def test_token_refresh(self):
        """Test token refresh functionality"""
        logger.info("🧪 Testing token refresh...")
        
        refresh_data = {
            "refresh_token": self.tokens["customer"]["refresh_token"]
        }
        
        response = await self.client.post("/api/auth/refresh", json=refresh_data)
        assert response.status_code == 200, f"Token refresh failed: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        assert "access_token" in data["data"]
        
        # Update access token
        self.tokens["customer"]["access_token"] = data["data"]["access_token"]
        
        logger.info("✅ Token refresh successful")
    
    async def test_profile_update(self):
        """Test profile update functionality"""
        logger.info("🧪 Testing profile update...")
        
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone": "+1-555-0123",
            "experience": "advanced"
        }
        
        headers = {"Authorization": f"Bearer {self.tokens['customer']['access_token']}"}
        response = await self.client.put("/api/auth/me", json=update_data, headers=headers)
        assert response.status_code == 200, f"Profile update failed: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        assert data["data"]["first_name"] == "Updated"
        assert data["data"]["phone"] == "+1-555-0123"
        
        logger.info("✅ Profile update successful")
    
    async def test_password_change(self):
        """Test password change functionality"""
        logger.info("🧪 Testing password change...")
        
        change_data = {
            "current_password": "TestPassword123!",
            "new_password": "NewTestPassword456!"
        }
        
        headers = {"Authorization": f"Bearer {self.tokens['customer']['access_token']}"}
        response = await self.client.post("/api/auth/change-password", json=change_data, headers=headers)
        assert response.status_code == 200, f"Password change failed: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        
        # Test login with new password
        login_data = {
            "email": "test_customer@example.com",
            "password": "NewTestPassword456!"
        }
        
        response = await self.client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200, "Login with new password failed"
        
        logger.info("✅ Password change successful")
    
    async def test_developer_earnings(self):
        """Test developer earnings endpoint"""
        logger.info("🧪 Testing developer earnings...")
        
        # Test access with customer role (should fail)
        headers = {"Authorization": f"Bearer {self.tokens['customer']['access_token']}"}
        response = await self.client.get("/api/auth/developer/earnings", headers=headers)
        assert response.status_code == 403, "Customer should not access developer earnings"
        
        # Test access with developer role
        headers = {"Authorization": f"Bearer {self.tokens['developer']['access_token']}"}
        response = await self.client.get("/api/auth/developer/earnings", headers=headers)
        assert response.status_code == 200, f"Developer earnings access failed: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        assert "summary" in data["data"]
        assert "earnings" in data["data"]
        
        logger.info("✅ Developer earnings access control working")
    
    async def test_password_reset_flow(self):
        """Test password reset functionality"""
        logger.info("🧪 Testing password reset flow...")
        
        # Request password reset
        reset_request = {
            "email": "test_customer@example.com"
        }
        
        response = await self.client.post("/api/auth/reset-password", json=reset_request)
        assert response.status_code == 200, f"Password reset request failed: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        
        logger.info("✅ Password reset request successful")
        # Note: In a real test, you'd verify the email was sent and get the token
    
    async def test_logout(self):
        """Test logout functionality"""
        logger.info("🧪 Testing logout...")
        
        headers = {"Authorization": f"Bearer {self.tokens['customer']['access_token']}"}
        response = await self.client.post("/api/auth/logout", headers=headers)
        assert response.status_code == 200, f"Logout failed: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        
        # Test that token is invalidated
        response = await self.client.get("/api/auth/me", headers=headers)
        assert response.status_code == 401, "Token should be invalidated after logout"
        
        logger.info("✅ Logout and token invalidation successful")
    
    async def run_all_tests(self):
        """Run the complete test suite"""
        logger.info("🚀 Starting Enhanced Authentication Test Suite...")
        
        try:
            await self.test_user_registration()
            await self.test_user_login()
            await self.test_protected_endpoints()
            await self.test_token_refresh()
            await self.test_profile_update()
            await self.test_password_change()
            await self.test_developer_earnings()
            await self.test_password_reset_flow()
            await self.test_logout()
            
            logger.info("🎉 All tests passed successfully!")
            return True
            
        except AssertionError as e:
            logger.error(f"❌ Test failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False
        finally:
            await self.client.aclose()

async def main():
    """Run the test suite"""
    test_suite = AuthTestSuite()
    success = await test_suite.run_all_tests()
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    print("\n" + "="*60)
    if result:
        print("🎉 Enhanced Authentication System: ALL TESTS PASSED")
        print("✅ System is ready for production deployment!")
    else:
        print("❌ Some tests failed. Please review the logs above.")
    print("="*60)
