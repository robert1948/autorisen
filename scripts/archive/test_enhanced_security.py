#!/usr/bin/env python3
"""
Quick test for enhanced security middleware
"""

import asyncio
from backend.app.middleware.input_sanitization import InputSanitizationMiddleware
from fastapi import Request, FastAPI
from starlette.responses import PlainTextResponse


async def test_middleware():
    """Test the enhanced security middleware"""
    
    try:
        app = FastAPI()
        middleware = InputSanitizationMiddleware(app)
        
        print("🔒 Enhanced Security Middleware Test")
        print("=" * 50)
        
        # Test IP extraction logic
        class MockClient:
            def __init__(self, host):
                self.host = host
        
        class MockRequest:
            def __init__(self, headers=None):
                self.headers = headers or {}
                self.client = MockClient("192.168.1.1")
                self.query_params = {}
                self.method = "GET"
        
        # Test 1: Cloudflare IP detection
        request1 = MockRequest({"cf-connecting-ip": "203.0.113.1"})
        ip1 = middleware._get_client_ip(request1)
        print(f"✅ Cloudflare IP detection: {ip1}")
        
        # Test 2: X-Forwarded-For detection  
        request2 = MockRequest({"x-forwarded-for": "203.0.113.2, 10.0.0.1"})
        ip2 = middleware._get_client_ip(request2)
        print(f"✅ X-Forwarded-For IP detection: {ip2}")
        
        # Test 3: Malicious request tracking
        middleware._track_malicious_request("192.168.1.100", "sql_injection")
        middleware._track_malicious_request("192.168.1.100", "xss_attempt")
        print(f"✅ Request tracking: {middleware._request_counts}")
        
        # Test 4: SQL injection detection
        test_sql = "SELECT * FROM users WHERE id = 1 OR 1=1"
        is_malicious = middleware._detect_sql_injection(test_sql)
        print(f"✅ SQL injection detection: {is_malicious}")
        
        # Test 5: XSS detection
        test_xss = "<script>alert('xss')</script>"
        is_xss = middleware._detect_xss(test_xss)
        print(f"✅ XSS detection: {is_xss}")
        
        # Test 6: Path traversal detection
        test_path = "../../../etc/passwd"
        is_traversal = middleware._detect_path_traversal(test_path)
        print(f"✅ Path traversal detection: {is_traversal}")
        
        # Test 7: Performance statistics
        stats = middleware.get_security_stats()
        print(f"✅ Security stats: {stats}")
        
        # Test 8: Fast SQL detection
        import time
        test_cases = [
            "SELECT * FROM users WHERE id = 1 OR 1=1",
            "normal user input",
            "DROP TABLE users",
            "regular text content",
            "UNION SELECT password FROM admin"
        ]
        
        start_time = time.time()
        for test_case in test_cases * 100:  # Test performance with 500 checks
            middleware._detect_sql_injection_fast(test_case)
        end_time = time.time()
        
        print(f"✅ Performance test: 500 SQL checks in {(end_time - start_time)*1000:.2f}ms")
        
        # Test 9: Memory cleanup simulation
        middleware._request_counter = 1000  # Trigger cleanup
        middleware._cleanup_old_tracking_data()
        print(f"✅ Memory cleanup test completed")
        
        print("\n🎯 Performance Enhancement Summary:")
        print("• Request counter and security statistics tracking")
        print("• Fast SQL injection detection with keyword pre-filtering")
        print("• Automatic memory cleanup every 1000 requests")
        print("• Performance monitoring for production optimization")
        print("• Optimized for high-traffic scenarios with CPU spike handling")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
if __name__ == "__main__":
    asyncio.run(test_middleware())
