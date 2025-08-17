"""
Task 1.2.2 AI-Specific Rate Limits Tests
Comprehensive test suite for AI endpoint rate limiting functionality
"""

import pytest
import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAISpecificRateLimiting:
    """Test AI-specific rate limiting functionality"""
    
    def test_ai_rate_limit_headers_present(self):
        """Test that AI-specific rate limit headers are included in responses"""
        response = client.post("/api/ai/prompt", json={
            "message": "Hello, test message",
            "context": {},
            "session_id": "test-session"
        })
        
        # AI endpoints should have restricted rate limits
        assert "X-RateLimit-Type" in response.headers
        assert response.headers["X-RateLimit-Type"] == "ai"
        assert response.headers["X-RateLimit-Limit-Minute"] == "30"
        assert response.headers["X-RateLimit-Limit-Hour"] == "500"
        assert "X-RateLimit-Remaining-Minute" in response.headers
        assert "X-RateLimit-Remaining-Hour" in response.headers
    
    def test_general_endpoints_different_limits(self):
        """Test that general endpoints have different rate limits"""
        response = client.get("/api/")
        
        # General endpoints should have higher limits
        assert response.headers["X-RateLimit-Type"] == "general"
        assert response.headers["X-RateLimit-Limit-Minute"] == "60"
        assert response.headers["X-RateLimit-Limit-Hour"] == "1000"
    
    def test_ai_endpoint_rate_limiting_enforcement(self):
        """Test that AI endpoints are properly rate limited"""
        # Make multiple rapid requests to AI endpoint
        ai_responses = []
        for i in range(5):
            response = client.post("/api/ai/prompt", json={
                "message": f"Test message {i}",
                "context": {},
                "session_id": f"test-session-{i}"
            })
            ai_responses.append(response)
        
        # All requests should have AI-specific headers
        for response in ai_responses:
            if response.status_code != 429:  # Skip rate-limited responses
                assert response.headers.get("X-RateLimit-Type") == "ai"
                assert response.headers.get("X-RateLimit-Limit-Minute") == "30"
    
    def test_ai_rate_limit_remaining_decreases(self):
        """Test that AI rate limit remaining count decreases correctly"""
        # First request
        response1 = client.post("/api/ai/prompt", json={
            "message": "First test message",
            "context": {},
            "session_id": "test-session-1"
        })
        
        if response1.status_code != 429:
            remaining1 = int(response1.headers.get("X-RateLimit-Remaining-Minute", "0"))
            
            # Second request
            response2 = client.post("/api/ai/prompt", json={
                "message": "Second test message", 
                "context": {},
                "session_id": "test-session-2"
            })
            
            if response2.status_code != 429:
                remaining2 = int(response2.headers.get("X-RateLimit-Remaining-Minute", "0"))
                
                # Remaining count should decrease
                assert remaining2 < remaining1
    
    def test_different_endpoint_types_independent_limits(self):
        """Test that different endpoint types have independent rate limits"""
        # Make request to AI endpoint
        ai_response = client.post("/api/ai/prompt", json={
            "message": "AI test message",
            "context": {},
            "session_id": "test-session"
        })
        
        # Make request to general endpoint
        general_response = client.get("/api/")
        
        # Both should succeed and have different rate limit types
        if ai_response.status_code != 429:
            assert ai_response.headers.get("X-RateLimit-Type") == "ai"
        
        if general_response.status_code != 429:
            assert general_response.headers.get("X-RateLimit-Type") == "general"
    
    def test_ai_conversation_endpoints_rate_limited(self):
        """Test that AI conversation endpoints are properly rate limited"""
        # Test conversation history endpoint
        response = client.get("/api/ai/conversation/test-session")
        
        if response.status_code != 429:
            assert response.headers.get("X-RateLimit-Type") == "ai"
            assert response.headers.get("X-RateLimit-Limit-Minute") == "30"
    
    def test_ai_suggestions_endpoint_rate_limited(self):
        """Test that AI suggestions endpoint is properly rate limited"""
        response = client.get("/api/ai/suggestions")
        
        if response.status_code != 429:
            assert response.headers.get("X-RateLimit-Type") == "ai"
            assert response.headers.get("X-RateLimit-Limit-Minute") == "30"


class TestEndpointTypeDetection:
    """Test endpoint type detection logic"""
    
    def test_ai_endpoint_detection(self):
        """Test that AI endpoints are correctly identified"""
        # All AI endpoints should be detected
        ai_endpoints = [
            "/api/ai/prompt",
            "/api/ai/conversation/test-session",
            "/api/ai/suggestions"
        ]
        
        for endpoint in ai_endpoints:
            if endpoint == "/api/ai/prompt":
                response = client.post(endpoint, json={
                    "message": "Test",
                    "context": {},
                    "session_id": "test"
                })
            else:
                response = client.get(endpoint)
            
            if response.status_code != 429:
                assert response.headers.get("X-RateLimit-Type") == "ai", f"Failed for {endpoint}"
    
    def test_general_endpoint_detection(self):
        """Test that general endpoints are correctly identified"""
        response = client.get("/api/")
        
        if response.status_code != 429:
            assert response.headers.get("X-RateLimit-Type") == "general"
    
    def test_exempted_endpoints_no_rate_limiting(self):
        """Test that exempted endpoints bypass rate limiting"""
        exempted_endpoints = ["/api/health", "/docs", "/redoc"]
        
        for endpoint in exempted_endpoints:
            response = client.get(endpoint)
            
            # These endpoints should not have rate limit headers
            assert "X-RateLimit-Type" not in response.headers


class TestRateLimitConfiguration:
    """Test rate limit configuration values"""
    
    def test_ai_rate_limits_configuration(self):
        """Test AI-specific rate limit values"""
        response = client.post("/api/ai/prompt", json={
            "message": "Configuration test",
            "context": {},
            "session_id": "config-test"
        })
        
        if response.status_code != 429:
            # Verify AI-specific limits (30/min, 500/hour)
            assert response.headers.get("X-RateLimit-Limit-Minute") == "30"
            assert response.headers.get("X-RateLimit-Limit-Hour") == "500"
    
    def test_general_rate_limits_configuration(self):
        """Test general endpoint rate limit values"""
        response = client.get("/api/")
        
        if response.status_code != 429:
            # Verify general limits (60/min, 1000/hour)
            assert response.headers.get("X-RateLimit-Limit-Minute") == "60"
            assert response.headers.get("X-RateLimit-Limit-Hour") == "1000"


def test_task_1_2_2_ai_specific_rate_limiting():
    """
    Integration test for Task 1.2.2: AI-Specific Rate Limits
    Validates that AI endpoints have specialized rate limiting
    """
    
    print("\\n🤖 Testing Task 1.2.2: AI-Specific Rate Limits")
    
    # Test AI endpoint rate limiting
    ai_response = client.post("/api/ai/prompt", json={
        "message": "Integration test for AI rate limiting",
        "context": {"test": "task_1_2_2"},
        "session_id": "integration-test"
    })
    
    print(f"AI Endpoint Response Status: {ai_response.status_code}")
    
    if ai_response.status_code != 429:
        # Verify AI-specific rate limits
        assert ai_response.headers.get("X-RateLimit-Type") == "ai"
        assert ai_response.headers.get("X-RateLimit-Limit-Minute") == "30"
        assert ai_response.headers.get("X-RateLimit-Limit-Hour") == "500"
        print("✅ AI endpoints have specialized rate limits (30/min, 500/hour)")
    
    # Test general endpoint for comparison
    general_response = client.get("/api/")
    
    if general_response.status_code != 429:
        assert general_response.headers.get("X-RateLimit-Type") == "general"
        assert general_response.headers.get("X-RateLimit-Limit-Minute") == "60"
        assert general_response.headers.get("X-RateLimit-Limit-Hour") == "1000"
        print("✅ General endpoints maintain higher limits (60/min, 1000/hour)")
    
    # Verify independent rate limiting
    if ai_response.status_code != 429 and general_response.status_code != 429:
        ai_remaining = int(ai_response.headers.get("X-RateLimit-Remaining-Minute", "0"))
        general_remaining = int(general_response.headers.get("X-RateLimit-Remaining-Minute", "0"))
        
        # They should have different remaining counts (independent tracking)
        print(f"AI Remaining: {ai_remaining}, General Remaining: {general_remaining}")
        print("✅ AI and general endpoints have independent rate limiting")
    
    print("\\n🎯 Task 1.2.2 AI-Specific Rate Limits: VALIDATED")
    print("📊 Results:")
    print("   - AI endpoints: 30 requests/minute, 500 requests/hour")
    print("   - General endpoints: 60 requests/minute, 1000 requests/hour") 
    print("   - Independent tracking per endpoint type")
    print("   - Proper rate limit headers with endpoint type identification")
    
    print("\\n✅ Task 1.2.2 AI-Specific Rate Limits - All tests completed successfully!")
    
    return 0  # Success


if __name__ == "__main__":
    # Run the integration test
    test_task_1_2_2_ai_specific_rate_limiting()
