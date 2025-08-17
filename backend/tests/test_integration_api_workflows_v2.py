"""
Integration Tests - API Workflows
================================

This module provides comprehensive end-to-end API integration tests for LocalStorm v3.0.0.
Tests cover the complete integration between Authentication V2 and CapeAI services.

Test Coverage:
- Authentication V2 API workflows
- CapeAI service API workflows  
- End-to-end integration scenarios
- Error handling and edge cases

Success Criteria: All end-to-end API tests pass with proper authentication and data flow.
"""

import pytest
import json
import uuid
import time
from typing import Dict, Any, Optional
import os
import sys

# Add the backend directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, SessionLocal
from app.models import Base, User, UserProfile
from sqlalchemy import text

# Test configuration
TEST_API_PREFIX = "/api"

# Test data templates
TEST_USER_DATA = {
    "email": "integration_test@example.com",
    "password": "TestPassword123!",
    "full_name": "Integration Test User",
    "user_role": "client",
    "company_name": "Test Corp",
    "industry": "Technology",
    "project_budget": "5000-10000",
    "skills": "Testing, Integration",
    "tos_accepted": True
}

class IntegrationTestHelper:
    """Helper class for integration test utilities"""
    
    def __init__(self):
        self.client = TestClient(app)
        self.test_users = []
        self.test_sessions = []
        
    def create_unique_email(self) -> str:
        """Generate unique email for testing"""
        timestamp = int(time.time())
        return f"test_{timestamp}_{uuid.uuid4().hex[:8]}@example.com"
        
    def create_test_user_data(self, **overrides) -> Dict[str, Any]:
        """Create test user data with unique email"""
        data = TEST_USER_DATA.copy()
        data["email"] = self.create_unique_email()
        data.update(overrides)
        return data
        
    def register_test_user(self, user_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Register a test user and return response data"""
        if user_data is None:
            user_data = self.create_test_user_data()
            
        response = self.client.post(
            f"{TEST_API_PREFIX}/auth/v2/register",
            json=user_data
        )
        
        if response.status_code in [200, 201]:  # Accept both 200 and 201
            result = response.json()
            self.test_users.append(user_data["email"])
            return result
        else:
            raise Exception(f"User registration failed: {response.status_code} - {response.text}")
            
    def login_test_user(self, email: str, password: str) -> Dict[str, Any]:
        """Login test user and return tokens"""
        response = self.client.post(
            f"{TEST_API_PREFIX}/auth/v2/login",
            json={"email": email, "password": password}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"User login failed: {response.status_code} - {response.text}")

    def get_auth_headers(self, token: str) -> Dict[str, str]:
        """Get authentication headers for API requests"""
        return {"Authorization": f"Bearer {token}"}
        
    def cleanup_test_data(self):
        """Clean up test data from database"""
        db = SessionLocal()
        try:
            # Clean up test users
            for email in self.test_users:
                user = db.query(User).filter(User.email == email).first()
                if user:
                    # Delete related profile
                    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
                    if profile:
                        db.delete(profile)
                    db.delete(user)
            
            db.commit()
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")
            db.rollback()
        finally:
            db.close()
            self.client.close()

# Global test helper instance
test_helper = IntegrationTestHelper()

@pytest.fixture(scope="session", autouse=True)
def setup_integration_tests():
    """Setup integration test environment"""
    print("\n🚀 Setting up integration test environment...")
    
    # Ensure database tables exist
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Cleanup
    print("\n🧹 Cleaning up integration test environment...")
    test_helper.cleanup_test_data()

@pytest.fixture(autouse=True)
def setup_test():
    """Setup for each individual test"""
    # Clear any previous test sessions
    test_helper.test_sessions.clear()
    yield

class TestAuthenticationV2Workflows:
    """Test Authentication V2 API workflows"""
    
    def test_email_validation_workflow(self):
        """Test complete email validation workflow"""
        print("\n📧 Testing email validation workflow...")
        
        # Test 1: Valid available email
        valid_email = test_helper.create_unique_email()
        response = test_helper.client.get(
            f"{TEST_API_PREFIX}/auth/v2/validate-email",
            params={"email": valid_email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["available"] is True
        assert "available" in data["message"]
        print(f"✅ Valid email validation: {valid_email}")
        
        # Test 2: Invalid email format
        response = test_helper.client.get(
            f"{TEST_API_PREFIX}/auth/v2/validate-email",
            params={"email": "invalid-email"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["available"] is False
        assert data["reason"] == "invalid_format"
        print("✅ Invalid email format validation")
        
        # Test 3: Register user then check email unavailable
        user_data = test_helper.create_test_user_data()
        test_helper.register_test_user(user_data)
        
        response = test_helper.client.get(
            f"{TEST_API_PREFIX}/auth/v2/validate-email",
            params={"email": user_data["email"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["available"] is False
        assert data["reason"] == "already_exists"
        print("✅ Existing email validation")
        
    def test_password_validation_workflow(self):
        """Test password strength validation workflow"""
        print("\n🔐 Testing password validation workflow...")
        
        # Test 1: Weak password
        response = test_helper.client.post(
            f"{TEST_API_PREFIX}/auth/v2/validate-password",
            json={"password": "weak"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert data["score"] < 100
        print(f"✅ Weak password validation: score={data['score']}")
        
        # Test 2: Strong password
        response = test_helper.client.post(
            f"{TEST_API_PREFIX}/auth/v2/validate-password", 
            json={"password": "StrongPassword123!@#"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["score"] == 100
        print(f"✅ Strong password validation: score={data['score']}")
        
        # Test 3: Check all requirements
        requirements = data["requirements"]
        assert requirements["minLength"] is True
        assert requirements["hasUpper"] is True
        assert requirements["hasLower"] is True
        assert requirements["hasNumber"] is True  
        assert requirements["hasSpecial"] is True
        print("✅ All password requirements met")
        
    def test_user_registration_workflow(self):
        """Test complete user registration workflow"""
        print("\n👤 Testing user registration workflow...")
        
        # Test 1: Successful registration
        user_data = test_helper.create_test_user_data()
        response = test_helper.client.post(
            f"{TEST_API_PREFIX}/auth/v2/register",
            json=user_data
        )
        
        assert response.status_code in [200, 201]  # API returns 200
        data = response.json()
        assert "id" in data
        assert data["email"] == user_data["email"]
        # Note: API returns some fields as null, which is expected behavior
        test_helper.test_users.append(user_data["email"])
        print(f"✅ Successful registration: {user_data['email']}")
        
        # Test 2: Duplicate email registration
        response = test_helper.client.post(
            f"{TEST_API_PREFIX}/auth/v2/register",
            json=user_data
        )
        
        assert response.status_code == 409
        error_data = response.json()
        assert "already registered" in error_data["detail"].lower()
        print("✅ Duplicate email rejection")
        
        # Test 3: Invalid data registration
        invalid_data = user_data.copy()
        invalid_data["email"] = "invalid-email"
        
        response = test_helper.client.post(
            f"{TEST_API_PREFIX}/auth/v2/register",
            json=invalid_data
        )
        
        assert response.status_code in [400, 422]
        print("✅ Invalid data rejection")
        
    def test_user_login_workflow(self):
        """Test complete user login workflow"""
        print("\n🔓 Testing user login workflow...")
        
        # Setup: Register a test user
        user_data = test_helper.create_test_user_data()
        test_helper.register_test_user(user_data)
        
        # Test 1: Successful login
        response = test_helper.client.post(
            f"{TEST_API_PREFIX}/auth/v2/login",
            json={
                "email": user_data["email"],
                "password": user_data["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        print(f"✅ Successful login: {user_data['email']}")
        
        # Test 2: Invalid credentials
        response = test_helper.client.post(
            f"{TEST_API_PREFIX}/auth/v2/login", 
            json={
                "email": user_data["email"],
                "password": "wrong_password"
            }
        )
        
        assert response.status_code == 401
        error_data = response.json()
        assert "incorrect" in error_data["detail"].lower()
        print("✅ Invalid credentials rejection")
        
        # Test 3: Non-existent user
        response = test_helper.client.post(
            f"{TEST_API_PREFIX}/auth/v2/login",
            json={
                "email": "nonexistent@example.com", 
                "password": "password123"
            }
        )
        
        assert response.status_code == 401
        print("✅ Non-existent user rejection")
        
        return data["access_token"]  # Return for use in other tests

class TestCapeAIWorkflows:
    """Test CapeAI service API workflows"""
    
    def test_ai_prompt_workflow(self):
        """Test AI prompt conversation workflow"""
        print("\n🤖 Testing AI prompt workflow...")
        
        # Setup: Get authenticated user token
        user_data = test_helper.create_test_user_data()
        test_helper.register_test_user(user_data)
        login_response = test_helper.login_test_user(
            user_data["email"], 
            user_data["password"]
        )
        token = login_response["access_token"]
        headers = test_helper.get_auth_headers(token)
        
        # Test 1: Successful AI prompt
        ai_request = {
            "message": "Hello CapeAI, please help me understand the platform",
            "context": {
                "page": "/dashboard",
                "user_intent": "onboarding",
                "platform_section": "getting_started"
            },
            "conversation_id": str(uuid.uuid4())
        }
        
        response = test_helper.client.post(
            f"{TEST_API_PREFIX}/ai/prompt",
            json=ai_request,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "conversation_id" in data
        assert len(data["response"]) > 0
        print(f"✅ AI prompt successful: {len(data['response'])} chars")
        
        # Store conversation ID for later tests
        conversation_id = data["conversation_id"]
        test_helper.test_sessions.append(conversation_id)
        
        # Test 2: Unauthenticated request
        response = test_helper.client.post(
            f"{TEST_API_PREFIX}/ai/prompt",
            json=ai_request
        )
        
        assert response.status_code == 401
        print("✅ Unauthenticated AI request rejected")
        
        return conversation_id, headers
        
    def test_conversation_history_workflow(self):
        """Test conversation history retrieval workflow"""
        print("\n💬 Testing conversation history workflow...")
        
        # Setup: Create conversation with multiple messages
        conversation_id, headers = self.test_ai_prompt_workflow()
        
        # Test 1: Retrieve conversation history
        response = test_helper.client.get(
            f"{TEST_API_PREFIX}/ai/conversation/{conversation_id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        print(f"✅ Conversation history retrieved: {len(data['messages'])} messages")
        
        # Test 2: Non-existent conversation
        fake_id = str(uuid.uuid4())
        response = test_helper.client.get(
            f"{TEST_API_PREFIX}/ai/conversation/{fake_id}",
            headers=headers
        )
        
        assert response.status_code == 200  # Empty conversation returns 200 with empty messages
        data = response.json()
        assert data["messages"] == []
        print("✅ Non-existent conversation handled")
        
        # Test 3: Unauthenticated history request
        response = test_helper.client.get(
            f"{TEST_API_PREFIX}/ai/conversation/{conversation_id}"
        )
        
        assert response.status_code == 401
        print("✅ Unauthenticated history request rejected")
        
    def test_conversation_management_workflow(self):
        """Test conversation deletion and management workflow"""
        print("\n🗑️ Testing conversation management workflow...")
        
        # Setup: Create a conversation
        conversation_id, headers = self.test_ai_prompt_workflow()
        
        # Test 1: Delete conversation
        response = test_helper.client.delete(
            f"{TEST_API_PREFIX}/ai/conversation/{conversation_id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        print("✅ Conversation deleted successfully")
        
        # Test 2: Verify conversation is cleared
        response = test_helper.client.get(
            f"{TEST_API_PREFIX}/ai/conversation/{conversation_id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["messages"] == []
        print("✅ Conversation deletion verified")
        
    def test_ai_suggestions_workflow(self):
        """Test AI suggestions API workflow"""
        print("\n💡 Testing AI suggestions workflow...")
        
        # Setup: Get authenticated user
        user_data = test_helper.create_test_user_data()
        test_helper.register_test_user(user_data)
        login_response = test_helper.login_test_user(
            user_data["email"],
            user_data["password"]
        )
        headers = test_helper.get_auth_headers(login_response["access_token"])
        
        # Test 1: Get contextual suggestions
        response = test_helper.client.get(
            f"{TEST_API_PREFIX}/ai/suggestions",
            params={
                "context": "dashboard",
                "user_level": "beginner"
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data
        assert len(data["suggestions"]) > 0
        print(f"✅ AI suggestions retrieved: {len(data['suggestions'])} suggestions")
        
        # Test 2: Unauthenticated suggestions request
        response = test_helper.client.get(
            f"{TEST_API_PREFIX}/ai/suggestions"
        )
        
        assert response.status_code == 401  
        print("✅ Unauthenticated suggestions request rejected")

class TestEndToEndIntegration:
    """Test complete end-to-end integration workflows"""
    
    def test_complete_user_journey_workflow(self):
        """Test complete user journey from registration to AI interaction"""
        print("\n🚀 Testing complete user journey workflow...")
        
        # Step 1: Email validation
        email = test_helper.create_unique_email()
        response = test_helper.client.get(
            f"{TEST_API_PREFIX}/auth/v2/validate-email",
            params={"email": email}
        )
        assert response.status_code == 200
        assert response.json()["available"] is True
        print("✅ Step 1: Email validation successful")
        
        # Step 2: Password validation
        password = "SecurePassword123!@#"
        response = test_helper.client.post(
            f"{TEST_API_PREFIX}/auth/v2/validate-password",
            json={"password": password}
        )
        assert response.status_code == 200
        assert response.json()["valid"] is True
        print("✅ Step 2: Password validation successful")
        
        # Step 3: User registration
        user_data = test_helper.create_test_user_data()
        user_data["email"] = email
        user_data["password"] = password
        
        response = test_helper.client.post(
            f"{TEST_API_PREFIX}/auth/v2/register",
            json=user_data
        )
        assert response.status_code in [200, 201]  # API returns 200
        user_info = response.json()
        test_helper.test_users.append(user_data["email"])
        print(f"✅ Step 3: User registration successful - ID: {user_info['id']}")
        
        # Step 4: User login
        response = test_helper.client.post(
            f"{TEST_API_PREFIX}/auth/v2/login",
            json={"email": email, "password": password}
        )
        assert response.status_code == 200
        login_data = response.json()
        token = login_data["access_token"]
        headers = test_helper.get_auth_headers(token)
        print("✅ Step 4: User login successful")
        
        # Step 5: AI interaction
        conversation_id = str(uuid.uuid4())
        ai_request = {
            "message": "Hello CapeAI! I'm a new user, can you help me get started?",
            "context": {
                "page": "/onboarding",
                "user_intent": "getting_started",
                "user_level": "beginner"
            },
            "conversation_id": conversation_id
        }
        
        response = test_helper.client.post(
            f"{TEST_API_PREFIX}/ai/prompt",
            json=ai_request,
            headers=headers
        )
        assert response.status_code == 200
        ai_data = response.json()
        assert len(ai_data["response"]) > 0
        print("✅ Step 5: AI interaction successful")
        
        # Step 6: Get contextual suggestions
        response = test_helper.client.get(
            f"{TEST_API_PREFIX}/ai/suggestions",
            params={"context": "onboarding", "user_level": "beginner"},
            headers=headers
        )
        assert response.status_code == 200
        suggestions_data = response.json()
        assert len(suggestions_data["suggestions"]) > 0
        print("✅ Step 6: AI suggestions successful")
        
        # Step 7: Check conversation history
        response = test_helper.client.get(
            f"{TEST_API_PREFIX}/ai/conversation/{conversation_id}",
            headers=headers
        )
        assert response.status_code == 200
        history_data = response.json()
        assert len(history_data["messages"]) >= 1
        print(f"✅ Step 7: Conversation history verified - {len(history_data['messages'])} messages")
        
        print("🎉 Complete user journey workflow successful!")
        return {
            "user_info": user_info,
            "token": token,
            "conversation_id": conversation_id
        }
        
    def test_error_handling_workflows(self):
        """Test error handling across all API workflows"""
        print("\n🔥 Testing error handling workflows...")
        
        # Test 1: Invalid authentication token
        invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
        
        response = test_helper.client.post(
            f"{TEST_API_PREFIX}/ai/prompt",
            json={"message": "test", "conversation_id": str(uuid.uuid4())},
            headers=invalid_headers
        )
        assert response.status_code == 401
        print("✅ Invalid token rejection")
        
        # Test 2: Malformed requests
        response = test_helper.client.post(
            f"{TEST_API_PREFIX}/auth/v2/register",
            json={"invalid": "data"}
        )
        assert response.status_code in [400, 422]
        print("✅ Malformed request rejection")
        
        # Test 3: Missing required fields
        response = test_helper.client.post(
            f"{TEST_API_PREFIX}/auth/v2/login",
            json={"email": "test@example.com"}  # Missing password
        )
        assert response.status_code in [400, 422]
        print("✅ Missing fields rejection")
        
        print("✅ Error handling workflows complete")

# Test execution and reporting
if __name__ == "__main__":
    print("🧪 LocalStorm v3.0.0 - Integration Tests - API Workflows")
    print("=" * 60)
    print("Testing end-to-end API integration between Authentication V2 and CapeAI services")
    print()
    
    # Run tests with pytest
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s"  # Show print statements
    ])
