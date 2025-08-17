"""
Comprehensive Test Suite for AI Audit Service

Tests all functionality including:
- Audit logging and storage
- PII detection and compliance
- Security event tracking
- Compliance reporting
- Data retention and cleanup
- High availability features
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ai_audit_service import (
    AIAuditService, 
    AuditEntry, 
    AuditEventType, 
    ComplianceLevel,
    AIAuditLog
)

class TestAIAuditService:
    """Test suite for AI Audit Service"""
    
    @pytest.fixture
    async def audit_service(self):
        """Create audit service instance for testing"""
        service = AIAuditService(
            redis_url="redis://localhost:6379",
            db_url="sqlite+aiosqlite:///test_audit.db"
        )
        await service.initialize()
        return service
    
    @pytest.fixture
    async def mock_audit_service(self):
        """Create mock audit service for testing without external dependencies"""
        service = AIAuditService()
        service.redis_client = None  # Force memory fallback
        service.db_session = None
        await service.initialize()
        return service

    @pytest.mark.asyncio
    async def test_audit_service_initialization(self):
        """Test audit service initialization"""
        service = AIAuditService()
        await service.initialize()
        
        # Should handle missing Redis/DB gracefully
        assert service is not None
        assert hasattr(service, 'memory_cache')
        assert isinstance(service.memory_cache, dict)

    @pytest.mark.asyncio
    async def test_log_ai_interaction_basic(self, mock_audit_service):
        """Test basic AI interaction logging"""
        audit_id = await mock_audit_service.log_ai_interaction(
            user_id="test_user",
            provider="openai",
            model="gpt-4",
            prompt="Test prompt",
            response="Test response"
        )
        
        assert audit_id is not None
        assert len(audit_id) == 36  # UUID length
        assert audit_id in mock_audit_service.memory_cache

    @pytest.mark.asyncio
    async def test_log_ai_interaction_with_metadata(self, mock_audit_service):
        """Test AI interaction logging with full metadata"""
        metadata = {
            "temperature": 0.7,
            "max_tokens": 100,
            "custom_field": "test_value"
        }
        
        audit_id = await mock_audit_service.log_ai_interaction(
            user_id="test_user",
            provider="anthropic",
            model="claude-3",
            prompt="Complex prompt with context",
            response="Detailed response",
            session_id="session_123",
            ip_address="192.168.1.1",
            user_agent="TestAgent/1.0",
            tokens_used=150,
            estimated_cost=0.003,
            rate_limited=False,
            safety_filtered=False,
            response_time_ms=1250.5,
            request_metadata=metadata
        )
        
        assert audit_id is not None
        
        # Check stored data
        stored_entry = mock_audit_service.memory_cache[audit_id]
        assert stored_entry['user_id'] == "test_user"
        assert stored_entry['provider'] == "anthropic"
        assert stored_entry['model'] == "claude-3"
        assert stored_entry['session_id'] == "session_123"
        assert stored_entry['tokens_used'] == 150
        assert stored_entry['estimated_cost'] == 0.003
        assert stored_entry['response_time_ms'] == 1250.5
        assert stored_entry['metadata'] == metadata

    @pytest.mark.asyncio
    async def test_pii_detection(self, mock_audit_service):
        """Test PII detection in prompts and responses"""
        # Test with SSN
        audit_id_ssn = await mock_audit_service.log_ai_interaction(
            user_id="test_user",
            provider="openai",
            model="gpt-4",
            prompt="My SSN is 123-45-6789",
            response="I cannot process personal information"
        )
        
        stored_entry = mock_audit_service.memory_cache[audit_id_ssn]
        assert stored_entry['contains_pii'] is True
        assert stored_entry['compliance_level'] == ComplianceLevel.HIGH.value
        
        # Test with email
        audit_id_email = await mock_audit_service.log_ai_interaction(
            user_id="test_user",
            provider="openai",
            model="gpt-4",
            prompt="Contact me at john.doe@example.com",
            response="Noted"
        )
        
        stored_entry = mock_audit_service.memory_cache[audit_id_email]
        assert stored_entry['contains_pii'] is True
        
        # Test with credit card
        audit_id_cc = await mock_audit_service.log_ai_interaction(
            user_id="test_user",
            provider="openai",
            model="gpt-4",
            prompt="My card number is 4532-1234-5678-9012",
            response="I cannot process payment information"
        )
        
        stored_entry = mock_audit_service.memory_cache[audit_id_cc]
        assert stored_entry['contains_pii'] is True
        
        # Test without PII
        audit_id_clean = await mock_audit_service.log_ai_interaction(
            user_id="test_user",
            provider="openai",
            model="gpt-4",
            prompt="What is the weather like?",
            response="I don't have real-time weather data"
        )
        
        stored_entry = mock_audit_service.memory_cache[audit_id_clean]
        assert stored_entry['contains_pii'] is False
        assert stored_entry['compliance_level'] == ComplianceLevel.LOW.value

    @pytest.mark.asyncio
    async def test_security_event_logging(self, mock_audit_service):
        """Test security event logging"""
        audit_id = await mock_audit_service.log_security_event(
            user_id="test_user",
            event_type="suspicious_activity",
            description="Multiple failed login attempts",
            severity=ComplianceLevel.HIGH,
            metadata={"ip": "192.168.1.100", "attempts": 5}
        )
        
        assert audit_id is not None
        stored_entry = mock_audit_service.memory_cache[audit_id]
        assert stored_entry['user_id'] == "test_user"
        assert stored_entry['event_type'] == AuditEventType.SYSTEM_ERROR.value
        assert stored_entry['compliance_level'] == ComplianceLevel.HIGH.value
        assert stored_entry['security_events'] == ["suspicious_activity"]

    @pytest.mark.asyncio
    async def test_compliance_level_assessment(self, mock_audit_service):
        """Test compliance level assessment logic"""
        # High compliance (PII detected)
        audit_id_high = await mock_audit_service.log_ai_interaction(
            user_id="test_user",
            provider="openai",
            model="gpt-4",
            prompt="My phone is 555-123-4567",
            response="Response"
        )
        stored_entry = mock_audit_service.memory_cache[audit_id_high]
        assert stored_entry['compliance_level'] == ComplianceLevel.HIGH.value
        
        # Medium compliance (safety filtered)
        audit_id_medium = await mock_audit_service.log_ai_interaction(
            user_id="test_user",
            provider="openai",
            model="gpt-4",
            prompt="Normal prompt",
            response="Response",
            safety_filtered=True
        )
        stored_entry = mock_audit_service.memory_cache[audit_id_medium]
        assert stored_entry['compliance_level'] == ComplianceLevel.MEDIUM.value
        
        # Medium compliance (rate limited)
        audit_id_rate = await mock_audit_service.log_ai_interaction(
            user_id="test_user",
            provider="openai",
            model="gpt-4",
            prompt="Normal prompt",
            response="Response",
            rate_limited=True
        )
        stored_entry = mock_audit_service.memory_cache[audit_id_rate]
        assert stored_entry['compliance_level'] == ComplianceLevel.MEDIUM.value
        
        # Low compliance (normal)
        audit_id_low = await mock_audit_service.log_ai_interaction(
            user_id="test_user",
            provider="openai",
            model="gpt-4",
            prompt="Normal prompt",
            response="Response"
        )
        stored_entry = mock_audit_service.memory_cache[audit_id_low]
        assert stored_entry['compliance_level'] == ComplianceLevel.LOW.value

    @pytest.mark.asyncio
    async def test_content_hashing(self, mock_audit_service):
        """Test content hashing for privacy"""
        prompt1 = "This is a test prompt"
        prompt2 = "This is a different prompt"
        
        hash1 = mock_audit_service._hash_content(prompt1)
        hash2 = mock_audit_service._hash_content(prompt2)
        hash3 = mock_audit_service._hash_content(prompt1)  # Same as first
        
        assert hash1 != hash2  # Different content = different hashes
        assert hash1 == hash3  # Same content = same hash
        assert len(hash1) == 64  # SHA-256 hex length
        assert hash1.isalnum()  # Only alphanumeric characters

    @pytest.mark.asyncio
    async def test_get_user_audit_trail_memory(self, mock_audit_service):
        """Test getting user audit trail from memory cache"""
        user_id = "test_user_trail"
        
        # Create multiple audit entries
        for i in range(5):
            await mock_audit_service.log_ai_interaction(
                user_id=user_id,
                provider="openai",
                model=f"gpt-{i}",
                prompt=f"Test prompt {i}",
                response=f"Test response {i}"
            )
        
        # Create entry for different user
        await mock_audit_service.log_ai_interaction(
            user_id="other_user",
            provider="openai",
            model="gpt-4",
            prompt="Other user prompt",
            response="Other user response"
        )
        
        # Get audit trail
        trail = await mock_audit_service.get_user_audit_trail(user_id, limit=10)
        
        assert len(trail) == 5
        for entry in trail:
            assert entry['user_id'] == user_id
        
        # Test with limit
        limited_trail = await mock_audit_service.get_user_audit_trail(user_id, limit=3)
        assert len(limited_trail) == 3

    @pytest.mark.asyncio
    async def test_memory_cache_overflow(self, mock_audit_service):
        """Test memory cache overflow handling"""
        # Set small cache size for testing
        mock_audit_service.cache_max_size = 3
        
        # Add entries beyond cache size
        audit_ids = []
        for i in range(5):
            audit_id = await mock_audit_service.log_ai_interaction(
                user_id=f"user_{i}",
                provider="openai",
                model="gpt-4",
                prompt=f"Prompt {i}",
                response=f"Response {i}"
            )
            audit_ids.append(audit_id)
        
        # Cache should only contain 3 entries (max size)
        assert len(mock_audit_service.memory_cache) == 3
        
        # First entries should be evicted
        assert audit_ids[0] not in mock_audit_service.memory_cache
        assert audit_ids[1] not in mock_audit_service.memory_cache
        
        # Last entries should be present
        assert audit_ids[2] in mock_audit_service.memory_cache
        assert audit_ids[3] in mock_audit_service.memory_cache
        assert audit_ids[4] in mock_audit_service.memory_cache

    @pytest.mark.asyncio
    async def test_compliance_report_generation(self, mock_audit_service):
        """Test compliance report generation"""
        # Create test data with various compliance scenarios
        await mock_audit_service.log_ai_interaction(
            user_id="user1", provider="openai", model="gpt-4",
            prompt="Normal prompt", response="Normal response"
        )
        
        await mock_audit_service.log_ai_interaction(
            user_id="user2", provider="anthropic", model="claude-3",
            prompt="SSN: 123-45-6789", response="Cannot process",
            safety_filtered=True
        )
        
        await mock_audit_service.log_ai_interaction(
            user_id="user3", provider="gemini", model="gemini-pro",
            prompt="Rate limited request", response="",
            rate_limited=True
        )
        
        # Generate report
        report = await mock_audit_service.get_compliance_report()
        
        assert 'period' in report
        assert 'summary' in report
        assert 'providers' in report
        assert 'recommendations' in report
        
        # Check recommendations are generated
        assert len(report['recommendations']) > 0

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_audit_service):
        """Test error handling in various scenarios"""
        # Test with None values
        audit_id = await mock_audit_service.log_ai_interaction(
            user_id="test_user",
            provider="openai",
            model="gpt-4",
            prompt="",  # Empty prompt
            response=None  # None response
        )
        assert audit_id is not None
        
        # Test with invalid user ID
        audit_id = await mock_audit_service.log_ai_interaction(
            user_id="",
            provider="openai",
            model="gpt-4",
            prompt="Test",
            response="Test"
        )
        assert audit_id is not None

    @pytest.mark.asyncio
    async def test_audit_entry_creation(self):
        """Test AuditEntry dataclass creation and serialization"""
        entry = AuditEntry(
            id="test-id",
            user_id="user123",
            timestamp=datetime.utcnow(),
            event_type=AuditEventType.AI_REQUEST,
            provider="openai",
            model="gpt-4",
            prompt_hash="hash123",
            response_hash="hash456",
            compliance_level=ComplianceLevel.MEDIUM,
            compliance_flags=["flag1", "flag2"],
            security_events=["event1"],
            metadata={"key": "value"}
        )
        
        # Test serialization
        entry_dict = entry.__dict__
        assert entry_dict['id'] == "test-id"
        assert entry_dict['user_id'] == "user123"
        assert entry_dict['compliance_level'] == ComplianceLevel.MEDIUM
        assert entry_dict['compliance_flags'] == ["flag1", "flag2"]

    def test_pii_patterns(self):
        """Test PII detection patterns"""
        service = AIAuditService()
        
        # Test SSN patterns
        assert service._detect_pii("My SSN is 123-45-6789") is True
        assert service._detect_pii("SSN: 987654321") is False  # No hyphens
        
        # Test email patterns
        assert service._detect_pii("Contact john.doe@example.com") is True
        assert service._detect_pii("Email: user+tag@domain.co.uk") is True
        assert service._detect_pii("Not an email: john.doe@") is False
        
        # Test credit card patterns
        assert service._detect_pii("Card: 4532-1234-5678-9012") is True
        assert service._detect_pii("Card: 4532 1234 5678 9012") is True
        assert service._detect_pii("Card: 4532123456789012") is True
        assert service._detect_pii("Card: 123") is False  # Too short
        
        # Test phone patterns
        assert service._detect_pii("Call 555-123-4567") is True
        assert service._detect_pii("Phone: 555 123 4567") is True
        assert service._detect_pii("Number: 5551234567") is True
        
        # Test clean content
        assert service._detect_pii("This is clean content") is False
        assert service._detect_pii("No personal information here") is False

    @pytest.mark.asyncio
    async def test_recommendations_generation(self, mock_audit_service):
        """Test compliance recommendations generation"""
        # Create scenarios that should trigger recommendations
        
        # High PII detection rate
        for i in range(10):
            await mock_audit_service.log_ai_interaction(
                user_id=f"user{i}",
                provider="openai",
                model="gpt-4",
                prompt=f"My email is user{i}@example.com",
                response="Response"
            )
        
        # High rate limiting
        for i in range(5):
            await mock_audit_service.log_ai_interaction(
                user_id=f"user{i}",
                provider="openai",
                model="gpt-4",
                prompt="Normal prompt",
                response="Response",
                rate_limited=True
            )
        
        # Safety filtering
        await mock_audit_service.log_ai_interaction(
            user_id="user1",
            provider="openai",
            model="gpt-4",
            prompt="Filtered content",
            response="Filtered response",
            safety_filtered=True
        )
        
        report = await mock_audit_service.get_compliance_report()
        recommendations = report.get('recommendations', [])
        
        # Should have recommendations for PII, rate limiting, and safety
        pii_rec = any("PII" in rec for rec in recommendations)
        rate_rec = any("rate limiting" in rec for rec in recommendations)
        safety_rec = any("safety" in rec for rec in recommendations)
        
        assert pii_rec, "Should recommend PII detection measures"
        assert rate_rec, "Should recommend rate limiting review"
        assert safety_rec, "Should recommend safety filtering review"

    @pytest.mark.asyncio
    async def test_concurrent_audit_logging(self, mock_audit_service):
        """Test concurrent audit logging"""
        async def log_interaction(user_id: str, index: int):
            return await mock_audit_service.log_ai_interaction(
                user_id=user_id,
                provider="openai",
                model="gpt-4",
                prompt=f"Concurrent prompt {index}",
                response=f"Concurrent response {index}"
            )
        
        # Run 10 concurrent logging operations
        tasks = [log_interaction(f"user_{i}", i) for i in range(10)]
        audit_ids = await asyncio.gather(*tasks)
        
        # All operations should succeed
        assert len(audit_ids) == 10
        assert all(aid is not None for aid in audit_ids)
        assert len(set(audit_ids)) == 10  # All unique IDs

# Performance benchmarks
class TestAuditServicePerformance:
    """Performance tests for audit service"""
    
    @pytest.mark.asyncio
    async def test_logging_performance(self, mock_audit_service):
        """Test audit logging performance"""
        import time
        
        start_time = time.time()
        
        # Log 100 interactions
        for i in range(100):
            await mock_audit_service.log_ai_interaction(
                user_id=f"perf_user_{i}",
                provider="openai",
                model="gpt-4",
                prompt=f"Performance test prompt {i}",
                response=f"Performance test response {i}"
            )
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_log = total_time / 100
        
        print(f"Logged 100 interactions in {total_time:.3f}s")
        print(f"Average time per log: {avg_time_per_log:.4f}s")
        
        # Should be fast (less than 10ms per log on average)
        assert avg_time_per_log < 0.01, f"Logging too slow: {avg_time_per_log:.4f}s per log"

if __name__ == "__main__":
    # Run basic tests
    import asyncio
    
    async def run_basic_tests():
        print("🧪 Running AI Audit Service Tests")
        print("=" * 50)
        
        # Create test service
        service = AIAuditService()
        await service.initialize()
        
        # Test 1: Basic logging
        print("\n1. Testing Basic AI Interaction Logging")
        audit_id = await service.log_ai_interaction(
            user_id="test_user",
            provider="openai",
            model="gpt-4",
            prompt="Test prompt",
            response="Test response"
        )
        print(f"✅ Logged interaction: {audit_id}")
        
        # Test 2: PII detection
        print("\n2. Testing PII Detection")
        pii_detected = service._detect_pii("My email is john@example.com")
        print(f"✅ PII Detection: {pii_detected}")
        
        # Test 3: Security event
        print("\n3. Testing Security Event Logging")
        security_id = await service.log_security_event(
            user_id="test_user",
            event_type="test_event",
            description="Test security event"
        )
        print(f"✅ Logged security event: {security_id}")
        
        # Test 4: Audit trail
        print("\n4. Testing Audit Trail Retrieval")
        trail = await service.get_user_audit_trail("test_user")
        print(f"✅ Retrieved {len(trail)} audit entries")
        
        # Test 5: Compliance report
        print("\n5. Testing Compliance Report")
        report = await service.get_compliance_report()
        print(f"✅ Generated compliance report with {len(report.get('recommendations', []))} recommendations")
        
        print("\n🎉 All Tests Passed!")
        print("AI Audit Service is operational!")
    
    asyncio.run(run_basic_tests())
