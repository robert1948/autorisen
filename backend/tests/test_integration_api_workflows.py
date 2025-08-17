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
- Performance and reliability

Success Criteria: All end-to-end API tests pass with proper authentication and data flow.
"""

import pytest
import asyncio
import httpx
import json
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os
import sys

# Add the backend directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, SessionLocal
from app.models import Base, User, UserProfile
from app.auth import create_access_token
from sqlalchemy import text

# Test configuration
TEST_BASE_URL = "http://localhost:8000"
TEST_API_PREFIX = "/api"

# Test data templates
TEST_USER_DATA = {
    "email": "integration_test@example.com",
    "password": "TestPassword123!",
    "firstName": "Integration",
    "lastName": "Test",
    "phone": "+1-555-0123",
    "company": "Test Corp",
    "experience": "intermediate"
}

TEST_AI_DATA = {
    "message": "Hello CapeAI, this is an integration test",
    "context": {
        "page": "/test",
        "user_intent": "testing",
        "previous_interactions": []
    }
}

class IntegrationTestHelper:
    """Helper class for integration test utilities"""
    
    def __init__(self):
        self.client = None
        self.test_users = []
        self.test_sessions = []
        
    async def setup_client(self):
        """Initialize HTTP client for API testing"""
        self.client = TestClient(app)
        
    async def cleanup_client(self):
        """Cleanup HTTP client"""
        if self.client:
            self.client.close()
            
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
        
    async def register_test_user(self, user_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Register a test user and return response data"""
        if user_data is None:
            user_data = self.create_test_user_data()
            
        response = self.client.post(
            f"{TEST_API_PREFIX}/auth/v2/register",
            json=user_data
        )
        
        if response.status_code == 201:
            result = response.json()
            self.test_users.append(user_data["email"])
            return result
        else:
            raise Exception(f"User registration failed: {response.status_code} - {response.text}")
            
    async def login_test_user(self, email: str, password: str) -> Dict[str, Any]:
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
        
    async def cleanup_test_data(self):
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

# Global test helper instance
test_helper = IntegrationTestHelper()

@pytest.fixture(scope="session", autouse=True)
async def setup_integration_tests():
    """Setup integration test environment"""
    print("\n🚀 Setting up integration test environment...")
    
    # Ensure database tables exist
    Base.metadata.create_all(bind=engine)
    
    # Setup HTTP client
    await test_helper.setup_client()
    
    yield
    
    # Cleanup
    print("\n🧹 Cleaning up integration test environment...")
    await test_helper.cleanup_test_data()
    await test_helper.cleanup_client()

@pytest.fixture(autouse=True)
async def setup_test():
    """Setup for each individual test"""
    # Clear any previous test sessions
    test_helper.test_sessions.clear()
    yield
    # Individual test cleanup happens here if needed

class TestAuthenticationV2Workflows:
    """Test Authentication V2 API workflows"""
    
    async def test_email_validation_workflow(self):
        """Test complete email validation workflow"""
        print("\n📧 Testing email validation workflow...")
        
        # Test 1: Valid available email
        valid_email = test_helper.create_unique_email()
        response = await test_helper.client.get(
            f"{TEST_API_PREFIX}/auth/v2/validate-email",
            params={"email": valid_email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["available"] is True
        assert "available" in data["message"]
        print(f"✅ Valid email validation: {valid_email}")
        
        # Test 2: Invalid email format
        response = await test_helper.client.get(
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
        await test_helper.register_test_user(user_data)
        
        response = await test_helper.client.get(
            f"{TEST_API_PREFIX}/auth/v2/validate-email",
            params={"email": user_data["email"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["available"] is False
        assert data["reason"] == "already_exists"
        print("✅ Existing email validation")
        
    async def test_password_validation_workflow(self):
        """Test password strength validation workflow"""
        print("\n🔐 Testing password validation workflow...")
        
        # Test 1: Weak password
        response = await test_helper.client.post(
            f"{TEST_API_PREFIX}/auth/v2/validate-password",
            json={"password": "weak"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert data["score"] < 100
        print(f"✅ Weak password validation: score={data['score']}")
        
        # Test 2: Strong password
        response = await test_helper.client.post(
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
        
    async def test_user_registration_workflow(self):
        """Test complete user registration workflow"""
        print("\n👤 Testing user registration workflow...")
        
        # Test 1: Successful registration
        user_data = test_helper.create_test_user_data()
        response = await test_helper.client.post(
            f"{TEST_API_PREFIX}/auth/v2/register",
            json=user_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["email"] == user_data["email"]
        assert data["firstName"] == user_data["firstName"]
        assert data["lastName"] == user_data["lastName"]
        assert "created_at" in data
        print(f"✅ Successful registration: {user_data['email']}")
        
        # Test 2: Duplicate email registration
        response = await test_helper.client.post(
            f"{TEST_API_PREFIX}/auth/v2/register",
            json=user_data
        )
        
        assert response.status_code == 409
        error_data = response.json()
        assert "already exists" in error_data["detail"].lower()
        print("✅ Duplicate email rejection")
        
        # Test 3: Invalid data registration
        invalid_data = user_data.copy()
        invalid_data["email"] = "invalid-email"
        
        response = await test_helper.client.post(
            f"{TEST_API_PREFIX}/auth/v2/register",
            json=invalid_data
        )
        
        assert response.status_code in [400, 422]
        print("✅ Invalid data rejection")
        
    async def test_user_login_workflow(self):
        """Test complete user login workflow"""
        print("\n🔓 Testing user login workflow...")
        
        # Setup: Register a test user
        user_data = test_helper.create_test_user_data()
        await test_helper.register_test_user(user_data)
        
        # Test 1: Successful login
        response = await test_helper.client.post(
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
        
        # Store token for other tests
        access_token = data["access_token"]
        
        # Test 2: Invalid credentials
        response = await test_helper.client.post(
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
        response = await test_helper.client.post(
            f"{TEST_API_PREFIX}/auth/v2/login",
            json={
                "email": "nonexistent@example.com", 
                "password": "password123"
            }
        )
        
        assert response.status_code == 401
        print("✅ Non-existent user rejection")
        
        return access_token  # Return for use in other tests

class TestCapeAIWorkflows:
    """Test CapeAI service API workflows"""
    
    async def test_ai_prompt_workflow(self):
        """Test AI prompt conversation workflow"""
        print("\n🤖 Testing AI prompt workflow...")
        
        # Setup: Get authenticated user token
        user_data = test_helper.create_test_user_data()
        await test_helper.register_test_user(user_data)
        login_response = await test_helper.login_test_user(
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
        
        response = await test_helper.client.post(
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
        
        # Test 2: Follow-up message in same conversation 
        followup_request = {
            "message": "Can you tell me more about the features?",
            "context": {
                "page": "/dashboard", 
                "user_intent": "feature_inquiry"
            },
            "conversation_id": conversation_id
        }
        
        response = await test_helper.client.post(
            f"{TEST_API_PREFIX}/ai/prompt",
            json=followup_request,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == conversation_id
        print("✅ Follow-up AI prompt successful")
        
        # Test 3: Unauthenticated request
        response = await test_helper.client.post(
            f"{TEST_API_PREFIX}/ai/prompt",
            json=ai_request
        )
        
        assert response.status_code == 401
        print("✅ Unauthenticated AI request rejected")
        
        return conversation_id, headers
        
    async def test_conversation_history_workflow(self):
        """Test conversation history retrieval workflow"""
        print("\n💬 Testing conversation history workflow...")
        
        # Setup: Create conversation with multiple messages
        conversation_id, headers = await self.test_ai_prompt_workflow()
        
        # Test 1: Retrieve conversation history
        response = await test_helper.client.get(
            f"{TEST_API_PREFIX}/ai/conversation/{conversation_id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert len(data["messages"]) >= 2  # At least 2 messages from previous test
        print(f"✅ Conversation history retrieved: {len(data['messages'])} messages")
        
        # Test 2: Non-existent conversation
        fake_id = str(uuid.uuid4())
        response = await test_helper.client.get(
            f"{TEST_API_PREFIX}/ai/conversation/{fake_id}",
            headers=headers
        )
        
        assert response.status_code == 200  # Empty conversation returns 200 with empty messages
        data = response.json()
        assert data["messages"] == []
        print("✅ Non-existent conversation handled")
        
        # Test 3: Unauthenticated history request
        response = await test_helper.client.get(
            f"{TEST_API_PREFIX}/ai/conversation/{conversation_id}"
        )
        
        assert response.status_code == 401
        print("✅ Unauthenticated history request rejected")
        
    async def test_conversation_management_workflow(self):
        """Test conversation deletion and management workflow"""
        print("\n🗑️ Testing conversation management workflow...")
        
        # Setup: Create a conversation
        conversation_id, headers = await self.test_ai_prompt_workflow()
        
        # Test 1: Delete conversation
        response = await test_helper.client.delete(
            f"{TEST_API_PREFIX}/ai/conversation/{conversation_id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        print("✅ Conversation deleted successfully")
        
        # Test 2: Verify conversation is cleared
        response = await test_helper.client.get(
            f"{TEST_API_PREFIX}/ai/conversation/{conversation_id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["messages"] == []
        print("✅ Conversation deletion verified")
        
        # Test 3: Delete non-existent conversation
        fake_id = str(uuid.uuid4())
        response = await test_helper.client.delete(
            f"{TEST_API_PREFIX}/ai/conversation/{fake_id}",
            headers=headers
        )
        
        assert response.status_code == 200  # Should still return success
        print("✅ Non-existent conversation deletion handled")
        
    async def test_ai_suggestions_workflow(self):
        """Test AI suggestions API workflow"""
        print("\n💡 Testing AI suggestions workflow...")
        
        # Setup: Get authenticated user
        user_data = test_helper.create_test_user_data()
        await test_helper.register_test_user(user_data)
        login_response = await test_helper.login_test_user(
            user_data["email"],
            user_data["password"]
        )
        headers = test_helper.get_auth_headers(login_response["access_token"])
        
        # Test 1: Get contextual suggestions
        response = await test_helper.client.get(
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
        
        # Test 2: Get suggestions without context
        response = await test_helper.client.get(
            f"{TEST_API_PREFIX}/ai/suggestions",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data
        print("✅ Default suggestions retrieved")
        
        # Test 3: Unauthenticated suggestions request
        response = await test_helper.client.get(
            f"{TEST_API_PREFIX}/ai/suggestions"
        )
        
        assert response.status_code == 401  
        print("✅ Unauthenticated suggestions request rejected")

class TestEndToEndIntegration:
    """Test complete end-to-end integration workflows"""
    
    async def test_complete_user_journey_workflow(self):
        """Test complete user journey from registration to AI interaction"""
        print("\n🚀 Testing complete user journey workflow...")
        
        # Step 1: Email validation
        email = test_helper.create_unique_email()
        response = await test_helper.client.get(
            f"{TEST_API_PREFIX}/auth/v2/validate-email",
            params={"email": email}
        )
        assert response.status_code == 200
        assert response.json()["available"] is True
        print("✅ Step 1: Email validation successful")
        
        # Step 2: Password validation
        password = "SecurePassword123!@#"
        response = await test_helper.client.post(
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
        
        response = await test_helper.client.post(
            f"{TEST_API_PREFIX}/auth/v2/register",
            json=user_data
        )
        assert response.status_code == 201
        user_info = response.json()
        print(f"✅ Step 3: User registration successful - ID: {user_info['id']}")
        
        # Step 4: User login
        response = await test_helper.client.post(
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
        
        response = await test_helper.client.post(
            f"{TEST_API_PREFIX}/ai/prompt",
            json=ai_request,
            headers=headers
        )
        assert response.status_code == 200
        ai_data = response.json()
        assert len(ai_data["response"]) > 0
        print("✅ Step 5: AI interaction successful")
        
        # Step 6: Get contextual suggestions
        response = await test_helper.client.get(
            f"{TEST_API_PREFIX}/ai/suggestions",
            params={"context": "onboarding", "user_level": "beginner"},
            headers=headers
        )
        assert response.status_code == 200
        suggestions_data = response.json()
        assert len(suggestions_data["suggestions"]) > 0
        print("✅ Step 6: AI suggestions successful")
        
        # Step 7: Continue conversation
        followup_request = {
            "message": "That's helpful! Can you show me the main features?",
            "context": {
                "page": "/features",
                "user_intent": "feature_exploration"
            },
            "conversation_id": conversation_id
        }
        
        response = await test_helper.client.post(
            f"{TEST_API_PREFIX}/ai/prompt",
            json=followup_request,
            headers=headers
        )
        assert response.status_code == 200
        print("✅ Step 7: Conversation continuation successful")
        
        # Step 8: Check conversation history
        response = await test_helper.client.get(
            f"{TEST_API_PREFIX}/ai/conversation/{conversation_id}",
            headers=headers
        )
        assert response.status_code == 200
        history_data = response.json()
        assert len(history_data["messages"]) >= 2
        print(f"✅ Step 8: Conversation history verified - {len(history_data['messages'])} messages")
        
        print("🎉 Complete user journey workflow successful!")
        return {
            "user_info": user_info,
            "token": token,
            "conversation_id": conversation_id
        }
        
    async def test_concurrent_user_workflows(self):
        """Test multiple concurrent user workflows"""
        print("\n👥 Testing concurrent user workflows...")
        
        async def single_user_workflow(user_index: int):
            """Single user workflow for concurrent testing"""
            # Create unique user
            user_data = test_helper.create_test_user_data()
            user_data["email"] = f"concurrent_user_{user_index}_{int(time.time())}@example.com"
            
            # Register and login
            await test_helper.register_test_user(user_data)
            login_response = await test_helper.login_test_user(
                user_data["email"], 
                user_data["password"]
            )
            
            headers = test_helper.get_auth_headers(login_response["access_token"])
            
            # AI interaction
            ai_request = {
                "message": f"Hello from user {user_index}!",
                "context": {"page": f"/test_{user_index}"},
                "conversation_id": str(uuid.uuid4())
            }
            
            response = await test_helper.client.post(
                f"{TEST_API_PREFIX}/ai/prompt",
                json=ai_request,
                headers=headers
            )
            
            assert response.status_code == 200
            return f"User {user_index} workflow completed"
        
        # Run 3 concurrent user workflows
        tasks = [single_user_workflow(i) for i in range(1, 4)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        for result in results:
            assert "completed" in result
            print(f"✅ {result}")
            
        print("✅ Concurrent user workflows successful")
        
    async def test_error_handling_workflows(self):
        """Test error handling across all API workflows"""
        print("\n🔥 Testing error handling workflows...")
        
        # Test 1: Invalid authentication token
        invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
        
        response = await test_helper.client.post(
            f"{TEST_API_PREFIX}/ai/prompt",
            json={"message": "test", "conversation_id": str(uuid.uuid4())},
            headers=invalid_headers
        )
        assert response.status_code == 401
        print("✅ Invalid token rejection")
        
        # Test 2: Malformed requests
        response = await test_helper.client.post(
            f"{TEST_API_PREFIX}/auth/v2/register",
            json={"invalid": "data"}
        )
        assert response.status_code in [400, 422]
        print("✅ Malformed request rejection")
        
        # Test 3: Missing required fields
        response = await test_helper.client.post(
            f"{TEST_API_PREFIX}/auth/v2/login",
            json={"email": "test@example.com"}  # Missing password
        )
        assert response.status_code in [400, 422]
        print("✅ Missing fields rejection")
        
        # Test 4: Server error simulation (invalid AI request)
        user_data = test_helper.create_test_user_data()
        await test_helper.register_test_user(user_data)
        login_response = await test_helper.login_test_user(
            user_data["email"],
            user_data["password"]
        )
        headers = test_helper.get_auth_headers(login_response["access_token"])
        
        # Send malformed AI request
        response = await test_helper.client.post(
            f"{TEST_API_PREFIX}/ai/prompt",
            json={
                "message": "",  # Empty message
                "conversation_id": "invalid_id_format"
            },
            headers=headers
        )
        
        # Should handle gracefully (either 400 or return error response)
        assert response.status_code in [200, 400, 422]
        print("✅ Malformed AI request handled")
        
        print("✅ Error handling workflows complete")

# Performance and reliability tests
class TestPerformanceAndReliability:
    """Test performance and reliability of API workflows"""
    
    async def test_api_response_times(self):
        """Test API response time performance"""
        print("\n⚡ Testing API response times...")
        
        # Setup authenticated user
        user_data = test_helper.create_test_user_data()
        await test_helper.register_test_user(user_data)
        login_response = await test_helper.login_test_user(
            user_data["email"],
            user_data["password"]
        )
        headers = test_helper.get_auth_headers(login_response["access_token"])
        
        # Test response times for different endpoints
        endpoints_to_test = [
            ("GET", f"{TEST_API_PREFIX}/auth/v2/validate-email", {"params": {"email": "test@example.com"}}),
            ("POST", f"{TEST_API_PREFIX}/auth/v2/validate-password", {"json": {"password": "TestPass123!"}}),
            ("GET", f"{TEST_API_PREFIX}/ai/suggestions", {"headers": headers}),
        ]
        
        response_times = {}
        
        for method, endpoint, kwargs in endpoints_to_test:
            start_time = time.time()
            
            if method == "GET":
                response = await test_helper.client.get(endpoint, **kwargs)
            else:
                response = await test_helper.client.post(endpoint, **kwargs)
                
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            response_times[endpoint] = response_time
            assert response.status_code in [200, 201]
            assert response_time < 5000  # Should respond within 5 seconds
            
            print(f"✅ {method} {endpoint}: {response_time:.2f}ms")
        
        # Average response time should be reasonable
        avg_response_time = sum(response_times.values()) / len(response_times)
        assert avg_response_time < 2000  # Average under 2 seconds
        print(f"✅ Average response time: {avg_response_time:.2f}ms")
        
    async def test_rate_limiting_behavior(self):
        """Test API behavior under rapid requests"""
        print("\n🚦 Testing rate limiting behavior...")
        
        # Setup authenticated user
        user_data = test_helper.create_test_user_data()
        await test_helper.register_test_user(user_data)
        login_response = await test_helper.login_test_user(
            user_data["email"],
            user_data["password"]
        )
        headers = test_helper.get_auth_headers(login_response["access_token"])
        
        # Make rapid consecutive requests
        rapid_requests = []
        for i in range(10):
            request_coro = test_helper.client.get(
                f"{TEST_API_PREFIX}/ai/suggestions",
                headers=headers
            )
            rapid_requests.append(request_coro)
        
        # Execute all requests concurrently
        responses = await asyncio.gather(*rapid_requests, return_exceptions=True)
        
        # Count successful responses
        success_count = 0
        rate_limited_count = 0
        
        for response in responses:
            if isinstance(response, Exception):
                continue
            elif response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:  # Too Many Requests
                rate_limited_count += 1
        
        print(f"✅ Rapid requests: {success_count} successful, {rate_limited_count} rate-limited")
        assert success_count > 0  # At least some should succeed
        
    async def test_data_consistency_workflow(self):
        """Test data consistency across API operations"""
        print("\n🔄 Testing data consistency workflow...")
        
        # Create user and verify data consistency
        user_data = test_helper.create_test_user_data()
        register_response = await test_helper.register_test_user(user_data)
        
        # Login and verify user data matches
        login_response = await test_helper.login_test_user(
            user_data["email"],
            user_data["password"]
        )
        
        # Data should be consistent
        assert register_response["email"] == user_data["email"]
        assert "access_token" in login_response
        print("✅ User data consistency verified")
        
        # Test conversation data consistency
        headers = test_helper.get_auth_headers(login_response["access_token"])
        conversation_id = str(uuid.uuid4())
        
        # Send multiple messages in same conversation
        messages = [
            "First message in conversation",
            "Second message for testing",
            "Third message to verify consistency"
        ]
        
        for i, message in enumerate(messages):
            ai_request = {
                "message": message,
                "context": {"page": f"/test_{i}"},
                "conversation_id": conversation_id
            }
            
            response = await test_helper.client.post(
                f"{TEST_API_PREFIX}/ai/prompt",
                json=ai_request,
                headers=headers
            )
            
            assert response.status_code == 200
            assert response.json()["conversation_id"] == conversation_id
        
        # Verify conversation history consistency
        response = await test_helper.client.get(
            f"{TEST_API_PREFIX}/ai/conversation/{conversation_id}",
            headers=headers
        )
        
        assert response.status_code == 200
        history = response.json()
        assert len(history["messages"]) >= len(messages)
        print(f"✅ Conversation consistency verified: {len(history['messages'])} messages")

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
        "--asyncio-mode=auto",
        "-s"  # Show print statements
    ])
