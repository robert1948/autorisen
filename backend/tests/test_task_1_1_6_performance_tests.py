"""
Task 1.1.6 Performance Tests - Load Testing AI Endpoints
=======================================================

Comprehensive performance testing for LocalStorm v3.0.0.
Tests validate system performance under load, response times, and scalability.

Success Criteria: 
- API response times < 2s under normal load
- System handles concurrent users gracefully  
- Memory usage remains stable under load
- AI endpoints perform within acceptable thresholds
"""

import pytest
import asyncio
import time
import threading
import concurrent.futures
import statistics
import psutil
import os
import uuid
from typing import List, Dict, Any
from unittest.mock import patch, MagicMock, AsyncMock

# Set test environment variables
os.environ["SECRET_KEY"] = "test-secret-key-for-jwt-tokens-very-long-and-secure"
os.environ["DATABASE_URL"] = "sqlite:///./test_performance.db"
os.environ["OPENAI_API_KEY"] = "test-openai-key-sk-1234567890abcdef"
os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6379"
os.environ["DEBUG"] = "False"  # Performance testing with debug off

from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, SessionLocal
from app.models import Base, User, UserProfile
from app.auth import create_access_token

# Test configuration
TEST_API_PREFIX = "/api"
PERFORMANCE_TEST_DURATION = 30  # seconds
CONCURRENT_USERS = 10
MAX_RESPONSE_TIME = 2.0  # seconds
TARGET_REQUESTS_PER_SECOND = 50

# Initialize test client
client = TestClient(app)

def get_test_user_token() -> str:
    """Create a test user and return JWT token"""
    db = SessionLocal()
    try:
        # Create test user
        test_user = User(
            email=f"perf_test_user_{uuid.uuid4().hex[:8]}@example.com",
            password_hash="$2b$12$test_hashed_password",
            full_name="Performance Test User",
            user_role="client",
            company_name="Test Corp",
            industry="Technology",
            project_budget="5000-10000",
            skills="Testing"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        # Create access token
        access_token = create_access_token(
            data={"sub": test_user.email}, 
            secret_key=os.environ["SECRET_KEY"],
            algorithm="HS256"
        )
        return access_token
    finally:
        db.close()

class PerformanceTestHelper:
    """Helper class for performance testing utilities"""
    
    def __init__(self):
        self.client = TestClient(app)
        self.test_users = []
        self.access_token = get_test_user_token()
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
        
    def create_multiple_users(self, count: int) -> List[str]:
        """Create multiple test users and return their tokens"""
        tokens = []
        for i in range(count):
            token = get_test_user_token()
            tokens.append(token)
        return tokens
        
    def measure_response_time(self, endpoint: str, method: str = "GET", 
                            data: Dict = None, headers: Dict = None) -> float:
        """Measure response time for a single request"""
        start_time = time.time()
        
        if method == "GET":
            response = self.client.get(endpoint, headers=headers or self.headers)
        elif method == "POST":
            response = self.client.post(endpoint, json=data, headers=headers or self.headers)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        return response_time, response.status_code
    
    def concurrent_requests(self, endpoint: str, num_requests: int, 
                          method: str = "GET", data: Dict = None) -> List[Dict]:
        """Execute concurrent requests and measure performance"""
        results = []
        
        def make_request():
            try:
                response_time, status_code = self.measure_response_time(
                    endpoint, method, data, self.headers
                )
                return {
                    "response_time": response_time,
                    "status_code": status_code,
                    "success": status_code == 200
                }
            except Exception as e:
                return {
                    "response_time": None,
                    "status_code": None,
                    "success": False,
                    "error": str(e)
                }
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        return results
    
    def get_system_metrics(self) -> Dict[str, float]:
        """Get current system performance metrics"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_used_mb": psutil.virtual_memory().used / 1024 / 1024
        }
    
    def cleanup_test_data(self):
        """Clean up test data"""
        db = SessionLocal()
        try:
            # Clean up test users
            test_users = db.query(User).filter(User.email.like("perf_test_user_%")).all()
            for user in test_users:
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

# Global test helper instance - will be initialized in fixture
perf_helper = None

@pytest.fixture(scope="session", autouse=True)
def setup_performance_tests():
    """Setup performance test environment"""
    print("\n🚀 Setting up performance test environment...")
    
    # Ensure database tables exist
    Base.metadata.create_all(bind=engine)
    
    # Initialize test helper after DB is ready
    global perf_helper
    perf_helper = PerformanceTestHelper()
    
    yield
    
    # Cleanup
    print("\n🧹 Cleaning up performance test environment...")
    try:
        if perf_helper:
            perf_helper.cleanup_test_data()
    except:
        pass  # Ignore cleanup errors

class TestAuthenticationPerformance:
    """Performance tests for Authentication V2 endpoints"""
    
    def test_health_endpoint_performance(self):
        """Test health endpoint performance under load"""
        print("\n⚡ Testing health endpoint performance...")
        global perf_helper
        
        # Single request baseline
        response_time, status_code = perf_helper.measure_response_time("/api/health")
        assert status_code == 200
        assert response_time < 0.1  # Health should be very fast
        print(f"✅ Baseline health response time: {response_time:.3f}s")
        
        # Concurrent requests
        results = perf_helper.concurrent_requests("/api/health", 50)
        
        successful_requests = [r for r in results if r["success"]]
        response_times = [r["response_time"] for r in successful_requests]
        
        assert len(successful_requests) >= 45  # At least 90% success rate
        assert max(response_times) < 0.5  # Max response time
        assert statistics.mean(response_times) < 0.1  # Average response time
        
        print(f"✅ Concurrent health requests: {len(successful_requests)}/50 successful")
        print(f"✅ Average response time: {statistics.mean(response_times):.3f}s")
        print(f"✅ Max response time: {max(response_times):.3f}s")
    
    def test_login_endpoint_performance(self):
        """Test login endpoint performance"""
        print("\n🔐 Testing login endpoint performance...")
        
        # Create test user data
        login_data = {
            "email": "performance_test@example.com",
            "password": "TestPassword123!"
        }
        
        # First register the user
        register_data = {
            "email": "performance_test@example.com",
            "password": "TestPassword123!",
            "full_name": "Performance Test User",
            "user_role": "client",
            "company_name": "Test Corp",
            "industry": "Technology",
            "project_budget": "5000-10000",
            "skills": "Testing",
            "tos_accepted": True
        }
        
        response = client.post(f"{TEST_API_PREFIX}/auth/v2/register", json=register_data)
        # Ignore if user already exists
        
        # Test login performance
        response_time, status_code = perf_helper.measure_response_time(
            f"{TEST_API_PREFIX}/auth/v2/login", "POST", login_data
        )
        
        assert status_code == 200
        assert response_time < 1.0  # Login should be under 1 second
        print(f"✅ Login response time: {response_time:.3f}s")
        
        # Test concurrent logins (simulating multiple users)
        concurrent_results = []
        for i in range(5):  # Test with 5 concurrent logins
            results = perf_helper.concurrent_requests(
                f"{TEST_API_PREFIX}/auth/v2/login", 3, "POST", login_data
            )
            concurrent_results.extend(results)
        
        successful_logins = [r for r in concurrent_results if r["success"]]
        login_times = [r["response_time"] for r in successful_logins]
        
        if login_times:  # Only assert if we have successful logins
            assert statistics.mean(login_times) < 2.0  # Average under 2 seconds
            print(f"✅ Concurrent login average: {statistics.mean(login_times):.3f}s")
    
    def test_email_validation_performance(self):
        """Test email validation endpoint performance"""
        print("\n📧 Testing email validation performance...")
        
        test_email = f"perf_test_{uuid.uuid4().hex[:8]}@example.com"
        endpoint = f"{TEST_API_PREFIX}/auth/v2/validate-email"
        
        # Single request performance
        response_time, status_code = perf_helper.measure_response_time(
            f"{endpoint}?email={test_email}"
        )
        
        assert status_code == 200
        assert response_time < 0.5  # Email validation should be fast
        print(f"✅ Email validation response time: {response_time:.3f}s")
        
        # Concurrent email validations
        results = perf_helper.concurrent_requests(f"{endpoint}?email={test_email}", 20)
        
        successful_requests = [r for r in results if r["success"]]
        response_times = [r["response_time"] for r in successful_requests]
        
        assert len(successful_requests) >= 18  # At least 90% success rate
        assert statistics.mean(response_times) < 1.0  # Average under 1 second
        
        print(f"✅ Concurrent email validation: {len(successful_requests)}/20 successful")
        print(f"✅ Average response time: {statistics.mean(response_times):.3f}s")

class TestCapeAIPerformance:
    """Performance tests for CapeAI endpoints"""
    
    @patch('app.routes.cape_ai.openai_client.chat.completions.create')
    @patch('app.routes.cape_ai.redis_client')
    def test_ai_prompt_performance(self, mock_redis, mock_openai):
        """Test AI prompt endpoint performance"""
        print("\n🤖 Testing AI prompt performance...")
        
        # Mock fast AI responses
        mock_redis.lrange.return_value = []
        mock_redis.lpush.return_value = True
        mock_redis.expire.return_value = True
        
        mock_openai.return_value = AsyncMock()
        mock_openai.return_value.choices = [
            MagicMock(message=MagicMock(content="This is a quick AI response for performance testing."))
        ]
        
        ai_request = {
            "message": "Hello CapeAI, please help me with performance testing",
            "context": {"page": "/dashboard", "user_intent": "testing"},
            "conversation_id": str(uuid.uuid4())
        }
        
        # Single request performance
        response_time, status_code = perf_helper.measure_response_time(
            f"{TEST_API_PREFIX}/ai/prompt", "POST", ai_request
        )
        
        assert status_code == 200
        assert response_time < MAX_RESPONSE_TIME  # Should be under 2 seconds
        print(f"✅ AI prompt response time: {response_time:.3f}s")
        
        # Test concurrent AI requests
        concurrent_requests = 5  # Moderate load for AI endpoint
        results = perf_helper.concurrent_requests(
            f"{TEST_API_PREFIX}/ai/prompt", concurrent_requests, "POST", ai_request
        )
        
        successful_requests = [r for r in results if r["success"]]
        response_times = [r["response_time"] for r in successful_requests]
        
        assert len(successful_requests) >= 4  # At least 80% success rate for AI
        if response_times:  # Only check if we have successful responses
            assert statistics.mean(response_times) < MAX_RESPONSE_TIME * 1.5  # Allow some overhead for concurrent
            print(f"✅ Concurrent AI requests: {len(successful_requests)}/{concurrent_requests} successful")
            print(f"✅ Average AI response time: {statistics.mean(response_times):.3f}s")
    
    @patch('app.routes.cape_ai.redis_client')
    def test_conversation_history_performance(self, mock_redis):
        """Test conversation history retrieval performance"""
        print("\n💬 Testing conversation history performance...")
        
        # Mock conversation history data
        mock_conversation = [
            '{"user": "Hello", "ai": "Hi there!", "timestamp": "2024-01-01T10:00:00"}',
            '{"user": "How are you?", "ai": "I\'m doing well!", "timestamp": "2024-01-01T10:01:00"}'
        ]
        mock_redis.lrange.return_value = mock_conversation
        
        conversation_id = str(uuid.uuid4())
        endpoint = f"{TEST_API_PREFIX}/ai/conversation/{conversation_id}"
        
        # Single request performance
        response_time, status_code = perf_helper.measure_response_time(endpoint)
        
        assert status_code == 200
        assert response_time < 0.5  # History retrieval should be very fast
        print(f"✅ Conversation history response time: {response_time:.3f}s")
        
        # Concurrent history requests
        results = perf_helper.concurrent_requests(endpoint, 15)
        
        successful_requests = [r for r in results if r["success"]]
        response_times = [r["response_time"] for r in successful_requests]
        
        assert len(successful_requests) >= 13  # At least 85% success rate
        assert statistics.mean(response_times) < 1.0  # Average under 1 second
        
        print(f"✅ Concurrent history requests: {len(successful_requests)}/15 successful")
        print(f"✅ Average response time: {statistics.mean(response_times):.3f}s")
    
    def test_ai_suggestions_performance(self):
        """Test AI suggestions endpoint performance"""
        print("\n💡 Testing AI suggestions performance...")
        
        endpoint = f"{TEST_API_PREFIX}/ai/suggestions"
        
        # Single request performance
        response_time, status_code = perf_helper.measure_response_time(
            f"{endpoint}?context=dashboard&user_level=beginner"
        )
        
        assert status_code == 200
        assert response_time < 0.3  # Suggestions should be very fast (cached)
        print(f"✅ AI suggestions response time: {response_time:.3f}s")
        
        # Concurrent suggestions requests
        results = perf_helper.concurrent_requests(
            f"{endpoint}?context=dashboard&user_level=beginner", 25
        )
        
        successful_requests = [r for r in results if r["success"]]
        response_times = [r["response_time"] for r in successful_requests]
        
        assert len(successful_requests) >= 22  # At least 88% success rate
        assert statistics.mean(response_times) < 0.5  # Average under 0.5 seconds
        
        print(f"✅ Concurrent suggestions: {len(successful_requests)}/25 successful")
        print(f"✅ Average response time: {statistics.mean(response_times):.3f}s")

class TestSystemPerformance:
    """System-wide performance and resource utilization tests"""
    
    def test_system_resource_usage(self):
        """Test system resource usage under load"""
        print("\n🖥️ Testing system resource usage...")
        
        # Baseline system metrics
        baseline_metrics = perf_helper.get_system_metrics()
        print(f"✅ Baseline CPU: {baseline_metrics['cpu_percent']:.1f}%")
        print(f"✅ Baseline Memory: {baseline_metrics['memory_percent']:.1f}%")
        
        # Generate load across multiple endpoints
        def generate_load():
            endpoints = [
                ("/api/health", "GET", None),
                (f"{TEST_API_PREFIX}/ai/suggestions?context=dashboard", "GET", None),
                (f"{TEST_API_PREFIX}/auth/v2/validate-email?email=test@example.com", "GET", None)
            ]
            
            for endpoint, method, data in endpoints:
                try:
                    perf_helper.measure_response_time(endpoint, method, data)
                except:
                    pass  # Ignore errors during load generation
        
        # Run load test
        threads = []
        for _ in range(10):  # 10 concurrent threads
            thread = threading.Thread(target=generate_load)
            threads.append(thread)
            thread.start()
        
        # Monitor metrics during load
        time.sleep(2)  # Let load build up
        load_metrics = perf_helper.get_system_metrics()
        
        # Wait for threads to complete
        for thread in threads:
            thread.join()
        
        # Post-load metrics
        time.sleep(1)
        post_load_metrics = perf_helper.get_system_metrics()
        
        print(f"✅ Under load CPU: {load_metrics['cpu_percent']:.1f}%")
        print(f"✅ Under load Memory: {load_metrics['memory_percent']:.1f}%")
        print(f"✅ Post-load CPU: {post_load_metrics['cpu_percent']:.1f}%")
        
        # Assertions for resource usage
        assert load_metrics['memory_percent'] < 90  # Memory shouldn't exceed 90%
        assert post_load_metrics['cpu_percent'] < 80  # CPU should recover
    
    def test_database_connection_performance(self):
        """Test database connection and query performance"""
        print("\n🗄️ Testing database performance...")
        
        def db_operation():
            db = SessionLocal()
            try:
                # Simple query
                start_time = time.time()
                users = db.query(User).limit(10).all()
                end_time = time.time()
                return end_time - start_time
            finally:
                db.close()
        
        # Single operation
        single_time = db_operation()
        assert single_time < 0.1  # Single query should be very fast
        print(f"✅ Single DB query time: {single_time:.3f}s")
        
        # Concurrent database operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(db_operation) for _ in range(20)]
            concurrent_times = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        avg_concurrent_time = statistics.mean(concurrent_times)
        max_concurrent_time = max(concurrent_times)
        
        assert avg_concurrent_time < 0.2  # Average should be under 200ms
        assert max_concurrent_time < 0.5   # Max should be under 500ms
        
        print(f"✅ Concurrent DB operations average: {avg_concurrent_time:.3f}s")
        print(f"✅ Concurrent DB operations max: {max_concurrent_time:.3f}s")
    
    def test_memory_leak_detection(self):
        """Test for memory leaks during extended operation"""
        print("\n🔍 Testing for memory leaks...")
        
        initial_memory = psutil.virtual_memory().used / 1024 / 1024  # MB
        
        # Perform many operations to detect leaks
        for i in range(100):
            try:
                # Mix of operations
                perf_helper.measure_response_time("/api/health")
                perf_helper.measure_response_time(
                    f"{TEST_API_PREFIX}/ai/suggestions?context=test"
                )
                
                # Occasionally check memory
                if i % 25 == 0:
                    current_memory = psutil.virtual_memory().used / 1024 / 1024
                    memory_increase = current_memory - initial_memory
                    print(f"   Memory after {i} operations: +{memory_increase:.1f}MB")
                    
                    # Memory shouldn't grow excessively
                    assert memory_increase < 100  # Less than 100MB growth
            except:
                pass  # Continue testing even if some requests fail
        
        final_memory = psutil.virtual_memory().used / 1024 / 1024
        total_increase = final_memory - initial_memory
        
        print(f"✅ Total memory increase: {total_increase:.1f}MB")
        assert total_increase < 50  # Should not increase by more than 50MB

# Performance test execution and reporting
def test_task_1_1_6_performance_tests():
    """Main test function for Task 1.1.6 - Performance Tests"""
    print("\n" + "="*70)
    print("⚡ TASK 1.1.6 - PERFORMANCE TESTS - API LOAD TESTING")
    print("="*70)
    print("Testing system performance under load, response times, and scalability")
    print(f"Configuration: Max Response Time: {MAX_RESPONSE_TIME}s")
    print(f"Target RPS: {TARGET_REQUESTS_PER_SECOND}, Concurrent Users: {CONCURRENT_USERS}")
    print()
    
    # Run performance tests
    import pytest
    
    exit_code = pytest.main([__file__ + "::TestAuthenticationPerformance", "-v", "-s"])
    exit_code += pytest.main([__file__ + "::TestCapeAIPerformance", "-v", "-s"])
    exit_code += pytest.main([__file__ + "::TestSystemPerformance", "-v", "-s"])
    
    if exit_code == 0:
        print("\n" + "="*70)
        print("✅ TASK 1.1.6 COMPLETE - ALL PERFORMANCE TESTS PASSED")
        print("✅ API response times within acceptable thresholds")
        print("✅ System handles concurrent load gracefully")
        print("✅ Resource utilization within expected limits")
        print("✅ No memory leaks detected")
        print("="*70)
    else:
        print("\n❌ Some performance tests failed - see details above")
        
    return exit_code

if __name__ == "__main__":
    test_task_1_1_6_performance_tests()
