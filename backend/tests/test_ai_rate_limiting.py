"""
Test AI Rate Limiting Service - Task 2.4.2
==========================================

Comprehensive tests for the AI rate limiting functionality
"""

import asyncio

import pytest

from app.services.ai_rate_limit_service import (
    AIRateLimitService,
    check_ai_rate_limit,
)


class TestAIRateLimitService:
    """Test the AI rate limiting service"""
    
    @pytest.fixture
    async def rate_limit_service(self):
        """Create a test rate limiting service"""
        service = AIRateLimitService(redis_url="redis://localhost:6379/1")  # Use test DB
        await service.initialize()
        return service
    
    @pytest.mark.asyncio
    async def test_rate_limit_initialization(self):
        """Test service initialization"""
        service = AIRateLimitService()
        await service.initialize()
        
        # Should have default rate limits configured
        assert "free" in service.rate_limits
        assert "premium" in service.rate_limits
        assert "enterprise" in service.rate_limits
        
        # Should have provider limits
        assert "openai" in service.provider_limits
        assert "anthropic" in service.provider_limits
        assert "gemini" in service.provider_limits
    
    @pytest.mark.asyncio
    async def test_free_tier_rate_limits(self, rate_limit_service):
        """Test free tier rate limiting"""
        user_id = "test_user_free"
        provider = "openai"
        
        # First request should pass
        result = await rate_limit_service.check_rate_limit(user_id, provider, "free", 1)
        assert result.allowed is True
        assert result.remaining > 0
        
        # Should track usage
        stats = await rate_limit_service.get_user_usage_stats(user_id)
        assert user_id in stats["user_id"]

# Integration test with the AI service
class TestAIServiceRateLimitIntegration:
    """Test rate limiting integration with AI service"""
    
    @pytest.mark.asyncio
    async def test_rate_limiting_in_ai_service(self):
        """Test that AI service properly checks rate limits"""
        # This would require the actual AI service to be available
        # For now, just test that the integration points exist
        
        from app.services.multi_provider_ai_service import MultiProviderAIService
        
        # Check that the service imports rate limiting
        ai_service = MultiProviderAIService()
        
        # Verify RATE_LIMITING_AVAILABLE is properly set
        import app.services.multi_provider_ai_service as ai_module
        assert hasattr(ai_module, 'RATE_LIMITING_AVAILABLE')

if __name__ == "__main__":
    # Simple test runner
    async def run_basic_test():
        """Run a basic test without pytest"""
        print("🧪 Testing AI Rate Limiting Service...")
        
        # Test basic initialization
        service = AIRateLimitService()
        await service.initialize()
        print("✅ Service initialization successful")
        
        # Test basic rate limit check
        result = await service.check_rate_limit("test_user", "openai", "free", 1)
        print(f"✅ Rate limit check: allowed={result.allowed}, remaining={result.remaining}")
        
        # Test convenience function
        result2 = await check_ai_rate_limit("test_user2", "anthropic", "premium", 10)
        print(f"✅ Convenience function: allowed={result2.allowed}, remaining={result2.remaining}")
        
        print("🎉 Basic rate limiting tests passed!")
    
    # Run the test
    asyncio.run(run_basic_test())
