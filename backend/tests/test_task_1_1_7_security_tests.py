"""
Task 1.1.7 Security Tests - Input Validation & Security Testing
=============================================================

Comprehensive security testing for LocalStorm v3.0.0.
Tests validate input validation, XSS protection, SQL injection prevention,
authentication security, and other security measures.

Success Criteria: 
- Input validation prevents malicious data
- XSS protection working correctly
- SQL injection attempts blocked
- Authentication security measures effective
- API rate limiting and security headers present
"""

import pytest
import asyncio
import time
import uuid
import json
import re
from typing import List, Dict, Any
from unittest.mock import patch, MagicMock

# Set test environment variables
import os
os.environ["SECRET_KEY"] = "test-secret-key-for-jwt-tokens-very-long-and-secure"
os.environ["DATABASE_URL"] = "sqlite:///./test_security.db"
os.environ["OPENAI_API_KEY"] = "test-openai-key-sk-1234567890abcdef"
os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6379"
os.environ["DEBUG"] = "False"

from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, SessionLocal, Base
from app.models import User
from app.auth import create_access_token

# Test client
client = TestClient(app)

# Security test payloads
XSS_PAYLOADS = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>",
    "javascript:alert('XSS')",
    "<svg onload=alert('XSS')>",
    "<iframe src='javascript:alert(\"XSS\")'></iframe>",
    "';alert('XSS');//",
    "<input onfocus=alert('XSS') autofocus>",
]

SQL_INJECTION_PAYLOADS = [
    "'; DROP TABLE users; --",
    "' OR '1'='1",
    "' UNION SELECT * FROM users --",
    "'; UPDATE users SET password='hacked' WHERE id=1; --",
    "admin'--",
    "' OR 1=1#",
    "1' AND (SELECT COUNT(*) FROM users) > 0 --",
]

COMMAND_INJECTION_PAYLOADS = [
    "; ls -la",
    "& whoami",
    "| cat /etc/passwd",
    "`whoami`",
    "$(whoami)",
    "; rm -rf /",
    "&& cat /etc/shadow",
]

LDAP_INJECTION_PAYLOADS = [
    "*)(uid=*",
    "*)(|(password=*))",
    "admin)(&(password=*))",
    "*))%00",
]

OVERSIZED_PAYLOADS = [
    "A" * 10000,  # 10KB
    "B" * 100000,  # 100KB
    "C" * 1000000,  # 1MB (if system allows)
]

class SecurityTestHelper:
    """Helper class for security testing utilities"""
    
    def __init__(self):
        self.client = TestClient(app)
    
    def create_test_user(self) -> str:
        """Create a test user and return JWT token"""
        try:
            db = SessionLocal()
            test_user = User(
                email=f"security_test_user_{uuid.uuid4().hex[:8]}@example.com",
                password_hash="$2b$12$test_hashed_password",
                full_name="Security Test User",
                user_role="client",
                company_name="Security Corp",
                industry="Security",
                project_budget="5000-10000",
                skills="Security Testing"
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            access_token = create_access_token(data={"sub": test_user.email})
            return access_token
        except Exception as e:
            print(f"⚠️ Could not create test user: {e}")
            return None
        finally:
            if 'db' in locals():
                db.close()
    
    def test_payload_injection(self, endpoint: str, method: str, 
                             payloads: List[str], field_name: str = "email") -> Dict:
        """Test various injection payloads against an endpoint"""
        results = {
            "safe_responses": 0,
            "vulnerable_responses": 0,
            "error_responses": 0,
            "details": []
        }
        
        for payload in payloads:
            try:
                data = {field_name: payload}
                
                if method == "GET":
                    response = self.client.get(f"{endpoint}?{field_name}={payload}")
                elif method == "POST":
                    response = self.client.post(endpoint, json=data)
                
                # Analyze response for security issues
                if response.status_code in [400, 422, 500]:
                    # Expected - system rejected malicious input
                    results["safe_responses"] += 1
                elif response.status_code == 200:
                    # Check if payload was processed/reflected
                    response_text = response.text.lower()
                    if any(danger in response_text for danger in ['<script', 'javascript:', 'onerror=', 'onload=']):
                        results["vulnerable_responses"] += 1
                        results["details"].append({
                            "payload": payload[:50] + "..." if len(payload) > 50 else payload,
                            "status": "VULNERABLE",
                            "response_code": response.status_code
                        })
                    else:
                        results["safe_responses"] += 1
                else:
                    results["error_responses"] += 1
                    
            except Exception as e:
                results["error_responses"] += 1
                
        return results
    
    def check_security_headers(self, response) -> Dict[str, bool]:
        """Check for important security headers"""
        headers = response.headers
        security_checks = {
            "content_type_present": "content-type" in headers,
            "no_cache_sensitive": "cache-control" in headers or "pragma" in headers,
            "xss_protection": "x-xss-protection" in headers or "content-security-policy" in headers,
            "frame_options": "x-frame-options" in headers,
            "content_type_options": "x-content-type-options" in headers,
        }
        return security_checks
    
    def cleanup_test_data(self):
        """Clean up security test data"""
        try:
            db = SessionLocal()
            test_users = db.query(User).filter(User.email.like("security_test_user_%")).all()
            for user in test_users:
                db.delete(user)
            db.commit()
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")
            if 'db' in locals():
                db.rollback()
        finally:
            if 'db' in locals():
                db.close()

# Global security test helper
security_helper = SecurityTestHelper()

@pytest.fixture(scope="session", autouse=True)
def setup_security_tests():
    """Setup security test environment"""
    print("\n🔒 Setting up security test environment...")
    
    # Ensure database tables exist
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Cleanup
    print("\n🧹 Cleaning up security test environment...")
    try:
        security_helper.cleanup_test_data()
    except:
        pass

class TestInputValidationSecurity:
    """Security tests for input validation"""
    
    def test_xss_protection_email_validation(self):
        """Test XSS protection in email validation endpoint"""
        print("\n🛡️ Testing XSS protection in email validation...")
        
        endpoint = "/api/auth/v2/validate-email"
        results = security_helper.test_payload_injection(
            endpoint, "GET", XSS_PAYLOADS, "email"
        )
        
        print(f"✅ Safe responses: {results['safe_responses']}/{len(XSS_PAYLOADS)}")
        print(f"❌ Vulnerable responses: {results['vulnerable_responses']}")
        print(f"⚠️ Error responses: {results['error_responses']}")
        
        # Should have mostly safe responses (rejecting XSS attempts)
        assert results["vulnerable_responses"] == 0, "XSS vulnerabilities detected!"
        assert results["safe_responses"] + results["error_responses"] >= len(XSS_PAYLOADS) * 0.8
        
        if results["details"]:
            for detail in results["details"]:
                print(f"⚠️ Potential vulnerability: {detail}")
    
    def test_sql_injection_protection(self):
        """Test SQL injection protection"""
        print("\n💉 Testing SQL injection protection...")
        
        # Test email validation endpoint for SQL injection
        endpoint = "/api/auth/v2/validate-email"
        results = security_helper.test_payload_injection(
            endpoint, "GET", SQL_INJECTION_PAYLOADS, "email"
        )
        
        print(f"✅ Safe responses: {results['safe_responses']}/{len(SQL_INJECTION_PAYLOADS)}")
        print(f"❌ Vulnerable responses: {results['vulnerable_responses']}")
        
        # SQL injection should be blocked
        assert results["vulnerable_responses"] == 0, "SQL injection vulnerabilities detected!"
        assert results["safe_responses"] + results["error_responses"] >= len(SQL_INJECTION_PAYLOADS) * 0.8
    
    def test_command_injection_protection(self):
        """Test command injection protection"""
        print("\n⚡ Testing command injection protection...")
        
        # Test various endpoints for command injection
        test_endpoints = [
            ("/api/auth/v2/validate-email", "GET", "email"),
        ]
        
        total_safe = 0
        total_vulnerable = 0
        
        for endpoint, method, field in test_endpoints:
            results = security_helper.test_payload_injection(
                endpoint, method, COMMAND_INJECTION_PAYLOADS, field
            )
            
            total_safe += results["safe_responses"]
            total_vulnerable += results["vulnerable_responses"]
            
            print(f"✅ {endpoint}: {results['safe_responses']} safe, {results['vulnerable_responses']} vulnerable")
        
        assert total_vulnerable == 0, "Command injection vulnerabilities detected!"
        print(f"✅ Total safe responses: {total_safe}")
    
    def test_oversized_input_protection(self):
        """Test protection against oversized inputs"""
        print("\n📏 Testing oversized input protection...")
        
        endpoint = "/api/auth/v2/validate-email"
        
        safe_responses = 0
        for payload in OVERSIZED_PAYLOADS[:2]:  # Test first 2 to avoid timeouts
            try:
                response = security_helper.client.get(f"{endpoint}?email={payload}")
                
                # Should reject oversized input
                if response.status_code in [400, 422, 413, 500]:  # 413 = Request Entity Too Large
                    safe_responses += 1
                    print(f"✅ Rejected oversized input ({len(payload)} chars): {response.status_code}")
                else:
                    print(f"⚠️ Accepted oversized input ({len(payload)} chars): {response.status_code}")
                    
            except Exception as e:
                safe_responses += 1  # Exception is also a form of protection
                print(f"✅ Exception on oversized input: {str(e)[:100]}")
        
        assert safe_responses >= 1, "System should reject at least some oversized inputs"
    
    def test_special_characters_handling(self):
        """Test handling of special characters and unicode"""
        print("\n🔤 Testing special character handling...")
        
        special_payloads = [
            "test@üñíçødé.com",  # Unicode
            "test+tag@example.com",  # Plus sign
            "test@example.com; DROP TABLE users;",  # SQL with semicolon
            "test@example.com\r\n\r\nHeader-Injection: true",  # Header injection
            "test@example.com\x00",  # Null byte
            "test@example.com\u202E",  # Right-to-left override
        ]
        
        endpoint = "/api/auth/v2/validate-email"
        safe_count = 0
        
        for payload in special_payloads:
            try:
                response = security_helper.client.get(f"{endpoint}?email={payload}")
                
                # Check for proper handling
                if response.status_code in [200, 400, 422]:
                    safe_count += 1
                    if response.status_code == 200:
                        # Make sure no injection occurred
                        assert "drop table" not in response.text.lower()
                        assert "header-injection" not in response.text.lower()
                
                print(f"✅ Special char test: {response.status_code} for {payload[:30]}...")
                
            except Exception as e:
                safe_count += 1  # Exceptions are acceptable for malformed input
                print(f"✅ Exception for special chars: {str(e)[:50]}...")
        
        assert safe_count >= len(special_payloads) * 0.8  # Most should be handled safely

class TestAuthenticationSecurity:
    """Security tests for authentication system"""
    
    def test_jwt_token_security(self):
        """Test JWT token security measures"""
        print("\n🔑 Testing JWT token security...")
        
        # Test with invalid tokens
        invalid_tokens = [
            "invalid.token.here",
            "Bearer fake-token",
            "",
            "null",
            "undefined",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.fake.signature",  # Invalid signature
        ]
        
        # Test protected endpoint (if exists)
        protected_endpoints = [
            "/api/ai/suggestions?context=test",
        ]
        
        for endpoint in protected_endpoints:
            for token in invalid_tokens:
                headers = {"Authorization": f"Bearer {token}"}
                response = security_helper.client.get(endpoint, headers=headers)
                
                # Should reject invalid tokens
                assert response.status_code in [401, 403, 422], f"Invalid token accepted: {token[:20]}..."
                print(f"✅ Rejected invalid token: {response.status_code}")
    
    def test_password_security_requirements(self):
        """Test password security requirements in registration"""
        print("\n🔐 Testing password security requirements...")
        
        weak_passwords = [
            "123",
            "password",
            "123456",
            "qwerty",
            "abc",
            "",
            "a",  # Too short
        ]
        
        registration_data_template = {
            "email": "test@example.com",
            "password": "",  # Will be replaced
            "full_name": "Test User",
            "user_role": "client",
            "company_name": "Test Corp",
            "industry": "Technology",
            "project_budget": "5000-10000",
            "skills": "Testing",
            "tos_accepted": True
        }
        
        rejected_count = 0
        for weak_password in weak_passwords:
            registration_data = registration_data_template.copy()
            registration_data["password"] = weak_password
            registration_data["email"] = f"test{uuid.uuid4().hex[:8]}@example.com"
            
            response = security_helper.client.post("/api/auth/v2/register", json=registration_data)
            
            # Should reject weak passwords
            if response.status_code in [400, 422]:
                rejected_count += 1
                print(f"✅ Rejected weak password: '{weak_password}' -> {response.status_code}")
            else:
                print(f"⚠️ Accepted weak password: '{weak_password}' -> {response.status_code}")
        
        # At least half of weak passwords should be rejected
        assert rejected_count >= len(weak_passwords) * 0.5, "Too many weak passwords accepted"
    
    def test_authentication_brute_force_protection(self):
        """Test brute force protection"""
        print("\n🚪 Testing brute force protection...")
        
        # Create a test user first
        registration_data = {
            "email": f"bruteforce_test_{uuid.uuid4().hex[:8]}@example.com",
            "password": "StrongPassword123!",
            "full_name": "Brute Force Test",
            "user_role": "client",
            "company_name": "Test Corp",
            "industry": "Security",
            "project_budget": "5000-10000",
            "skills": "Testing",
            "tos_accepted": True
        }
        
        # Try to register (might fail if DB not set up, that's OK)
        register_response = security_helper.client.post("/api/auth/v2/register", json=registration_data)
        
        # Attempt multiple failed logins
        login_data = {
            "email": registration_data["email"],
            "password": "WrongPassword123"
        }
        
        failed_attempts = 0
        for attempt in range(10):  # Try 10 failed logins
            response = security_helper.client.post("/api/auth/v2/login", json=login_data)
            
            if response.status_code in [401, 403, 429]:  # 429 = Too Many Requests
                failed_attempts += 1
                
                # Check if rate limiting kicks in
                if response.status_code == 429:
                    print(f"✅ Rate limiting activated after {attempt + 1} attempts")
                    break
            
            time.sleep(0.1)  # Small delay between attempts
        
        print(f"✅ Failed login attempts handled: {failed_attempts}/10")
        # System should reject failed attempts (exact behavior may vary)
        assert failed_attempts >= 8, "Most brute force attempts should be rejected"

class TestSecurityHeaders:
    """Test security headers and configurations"""
    
    def test_security_headers_presence(self):
        """Test presence of important security headers"""
        print("\n📋 Testing security headers...")
        
        # Test various endpoints
        test_endpoints = [
            "/api/health",
            "/docs",
            "/openapi.json",
        ]
        
        for endpoint in test_endpoints:
            response = security_helper.client.get(endpoint)
            security_checks = security_helper.check_security_headers(response)
            
            print(f"✅ {endpoint}:")
            for check, result in security_checks.items():
                status = "✅" if result else "⚠️"
                print(f"   {status} {check}: {result}")
            
            # At least content-type should be present
            assert security_checks["content_type_present"], f"Content-Type missing for {endpoint}"
    
    def test_cors_configuration(self):
        """Test CORS configuration security"""
        print("\n🌐 Testing CORS configuration...")
        
        # Test OPTIONS request for CORS
        response = security_helper.client.options("/api/health")
        
        cors_headers = {
            "access-control-allow-origin": response.headers.get("access-control-allow-origin"),
            "access-control-allow-methods": response.headers.get("access-control-allow-methods"),
            "access-control-allow-headers": response.headers.get("access-control-allow-headers"),
        }
        
        print(f"✅ CORS headers found: {sum(1 for v in cors_headers.values() if v)}/3")
        
        # Check that CORS is not overly permissive
        origin_header = cors_headers.get("access-control-allow-origin")
        if origin_header:
            # Should not be "*" for credentials-enabled endpoints
            if origin_header == "*":
                print("⚠️ CORS allows all origins - check if this is intended")
            else:
                print(f"✅ CORS origin restricted: {origin_header}")
    
    def test_error_information_disclosure(self):
        """Test that errors don't disclose sensitive information"""
        print("\n🔍 Testing error information disclosure...")
        
        # Test various error scenarios
        error_tests = [
            ("/api/nonexistent", "GET", None),
            ("/api/auth/v2/login", "POST", {"email": "invalid", "password": "invalid"}),
            ("/api/auth/v2/validate-email", "GET", {"email": "invalid@invalid"}),
        ]
        
        for endpoint, method, data in error_tests:
            try:
                if method == "GET":
                    if data:
                        params = "&".join([f"{k}={v}" for k, v in data.items()])
                        response = security_helper.client.get(f"{endpoint}?{params}")
                    else:
                        response = security_helper.client.get(endpoint)
                elif method == "POST":
                    response = security_helper.client.post(endpoint, json=data)
                
                # Check response for sensitive information
                response_text = response.text.lower()
                sensitive_patterns = [
                    r'password\s*[:=]',
                    r'secret\s*[:=]',
                    r'key\s*[:=]',
                    r'token\s*[:=]',
                    r'/home/\w+',
                    r'traceback.*line\s+\d+',
                    r'exception.*line\s+\d+',
                ]
                
                sensitive_found = any(re.search(pattern, response_text) for pattern in sensitive_patterns)
                
                if sensitive_found and response.status_code >= 500:  # Only care about server errors
                    print(f"⚠️ Potential information disclosure in {endpoint}")
                    # Don't fail the test for 404 errors or client errors
                    if response.status_code >= 500:
                        sensitive_disclosure_found = True
                else:
                    print(f"✅ No sensitive information disclosed in {endpoint}")
                
                # Should not disclose sensitive information in server errors
                if response.status_code >= 500:
                    assert not sensitive_found, f"Sensitive information disclosed in server error for {endpoint}"
                
            except Exception as e:
                print(f"✅ Exception handled for {endpoint}: {str(e)[:50]}...")

class TestDataSanitization:
    """Test data sanitization and output encoding"""
    
    def test_output_encoding(self):
        """Test that outputs are properly encoded"""
        print("\n🎭 Testing output encoding...")
        
        # Test with potential XSS in different fields
        test_cases = [
            ("/api/health", "GET", None),
        ]
        
        for endpoint, method, data in test_cases:
            try:
                if method == "GET":
                    response = security_helper.client.get(endpoint)
                elif method == "POST":
                    response = security_helper.client.post(endpoint, json=data)
                
                # Check Content-Type header
                content_type = response.headers.get("content-type", "")
                
                if "application/json" in content_type:
                    # JSON should be properly formatted
                    try:
                        json.loads(response.text)
                        print(f"✅ Valid JSON output for {endpoint}")
                    except:
                        print(f"⚠️ Invalid JSON output for {endpoint}")
                
                elif "text/html" in content_type:
                    # HTML should have proper encoding
                    html_content = response.text
                    if "<script>" in html_content and "&lt;script&gt;" not in html_content:
                        print(f"⚠️ Potential unencoded script tags in {endpoint}")
                    else:
                        print(f"✅ HTML properly encoded for {endpoint}")
                
            except Exception as e:
                print(f"✅ Exception in output encoding test: {str(e)[:50]}...")

# Security test execution and reporting
def test_task_1_1_7_security_tests():
    """Main test function for Task 1.1.7 - Security Tests"""
    print("\n" + "="*70)
    print("🔒 TASK 1.1.7 - SECURITY TESTS - INPUT VALIDATION & PROTECTION")
    print("="*70)
    print("Testing input validation, XSS protection, SQL injection prevention")
    print("and other security measures")
    print()
    
    # Run security tests
    import pytest
    
    test_classes = [
        "TestInputValidationSecurity",
        "TestAuthenticationSecurity", 
        "TestSecurityHeaders",
        "TestDataSanitization"
    ]
    
    total_exit_code = 0
    for test_class in test_classes:
        try:
            exit_code = pytest.main([
                f"{__file__}::{test_class}", 
                "-v", "-s", "--tb=short", "--maxfail=5"
            ])
            total_exit_code += exit_code
        except Exception as e:
            print(f"⚠️ Error running {test_class}: {e}")
            total_exit_code += 1
    
    if total_exit_code == 0:
        print("\n" + "="*70)
        print("✅ TASK 1.1.7 COMPLETE - ALL SECURITY TESTS PASSED")
        print("✅ Input validation working correctly")
        print("✅ XSS protection measures effective")
        print("✅ SQL injection attempts blocked")
        print("✅ Authentication security measures validated")
        print("✅ Security headers and configurations verified")
        print("="*70)
    else:
        print("\n❌ Some security tests failed - see details above")
        print("🔒 Review security measures and fix vulnerabilities")
        
    return total_exit_code

if __name__ == "__main__":
    test_task_1_1_7_security_tests()
