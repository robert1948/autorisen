"""
Simple integration test for CapeControl API
"""
import os
import requests
import time

# Set environment variables
os.environ["SECRET_KEY"] = "test-secret-key-for-jwt-tokens"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["DEBUG"] = "True"

def test_api_health():
    """Test the health endpoint while the server is running"""
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ Health endpoint test passed")
        return True
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

def test_email_validation():
    """Test email validation endpoint"""
    try:
        response = requests.get("http://localhost:8000/api/auth/v2/validate-email?email=test@example.com", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert "available" in data
        print("✅ Email validation test passed")
        return True
    except Exception as e:
        print(f"❌ Email validation test failed: {e}")
        return False

def test_password_validation():
    """Test password validation endpoint"""
    try:
        response = requests.post("http://localhost:8000/api/auth/v2/validate-password", 
                               json={"password": "StrongPassword123!"}, timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert "valid" in data
        print("✅ Password validation test passed")
        return True
    except Exception as e:
        print(f"❌ Password validation test failed: {e}")
        return False

def run_integration_tests():
    """Run all integration tests"""
    print("🚀 Running CapeControl Integration Tests...")
    print("🔗 Testing against: http://localhost:8000")
    
    tests = [
        test_api_health,
        test_email_validation,
        test_password_validation,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(0.5)  # Brief pause between tests
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1)
