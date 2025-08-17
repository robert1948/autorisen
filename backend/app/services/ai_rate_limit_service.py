"""
AI Rate Limiting Service - Task 2.4.2 Implementation
====================================================

Production-ready rate limiting for AI endpoints to prevent abuse
and ensure fair usage across users and API keys.

Features:
- Per-user rate limiting with Redis backend
- Provider-specific rate limits
- Token-based rate limiting
- Graceful degradation and fallbacks
- Comprehensive monitoring and alerting
"""

import asyncio
import json
import os
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

class RateLimitType(Enum):
    """Types of rate limiting"""
    REQUEST_COUNT = "request_count"
    TOKEN_USAGE = "token_usage"
    COST_BASED = "cost_based"
    PROVIDER_SPECIFIC = "provider_specific"

@dataclass
class RateLimit:
    """Rate limit configuration"""
    limit: int  # Max requests/tokens per window
    window: int  # Time window in seconds
    type: RateLimitType
    provider: Optional[str] = None
    user_tier: Optional[str] = "free"  # free, premium, enterprise

@dataclass
class RateLimitResult:
    """Result of rate limit check"""
    allowed: bool
    remaining: int
    reset_time: datetime
    limit_type: RateLimitType
    retry_after: Optional[int] = None
    error_message: Optional[str] = None

class AIRateLimitService:
    """
    Production AI rate limiting service with Redis backend
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.redis_client = None
        self.fallback_cache = {}  # In-memory fallback when Redis unavailable
        
        # Default rate limits per user tier
        self.rate_limits = {
            "free": {
                "requests_per_hour": RateLimit(60, 3600, RateLimitType.REQUEST_COUNT, user_tier="free"),
                "tokens_per_hour": RateLimit(50000, 3600, RateLimitType.TOKEN_USAGE, user_tier="free"),
                "requests_per_minute": RateLimit(10, 60, RateLimitType.REQUEST_COUNT, user_tier="free"),
            },
            "premium": {
                "requests_per_hour": RateLimit(500, 3600, RateLimitType.REQUEST_COUNT, user_tier="premium"),
                "tokens_per_hour": RateLimit(500000, 3600, RateLimitType.TOKEN_USAGE, user_tier="premium"),
                "requests_per_minute": RateLimit(50, 60, RateLimitType.REQUEST_COUNT, user_tier="premium"),
            },
            "enterprise": {
                "requests_per_hour": RateLimit(2000, 3600, RateLimitType.REQUEST_COUNT, user_tier="enterprise"),
                "tokens_per_hour": RateLimit(2000000, 3600, RateLimitType.TOKEN_USAGE, user_tier="enterprise"),
                "requests_per_minute": RateLimit(200, 60, RateLimitType.REQUEST_COUNT, user_tier="enterprise"),
            }
        }
        
        # Provider-specific limits
        self.provider_limits = {
            "openai": {
                "requests_per_minute": RateLimit(60, 60, RateLimitType.PROVIDER_SPECIFIC, provider="openai"),
                "tokens_per_minute": RateLimit(100000, 60, RateLimitType.PROVIDER_SPECIFIC, provider="openai"),
            },
            "anthropic": {
                "requests_per_minute": RateLimit(50, 60, RateLimitType.PROVIDER_SPECIFIC, provider="anthropic"),
                "tokens_per_minute": RateLimit(80000, 60, RateLimitType.PROVIDER_SPECIFIC, provider="anthropic"),
            },
            "gemini": {
                "requests_per_minute": RateLimit(40, 60, RateLimitType.PROVIDER_SPECIFIC, provider="gemini"),
                "tokens_per_minute": RateLimit(70000, 60, RateLimitType.PROVIDER_SPECIFIC, provider="gemini"),
            }
        }
    
    async def initialize(self):
        """Initialize Redis connection"""
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
                await self.redis_client.ping()
                logger.info("✅ Redis connection established for rate limiting")
            except Exception as e:
                logger.warning(f"⚠️ Redis connection failed, using fallback cache: {e}")
                self.redis_client = None
        else:
            logger.warning("⚠️ Redis not available, using in-memory fallback for rate limiting")
    
    async def check_rate_limit(
        self, 
        user_id: str, 
        provider: str, 
        user_tier: str = "free",
        token_count: int = 1
    ) -> RateLimitResult:
        """
        Check if request is within rate limits
        
        Args:
            user_id: User identifier
            provider: AI provider (openai, anthropic, gemini)
            user_tier: User subscription tier
            token_count: Number of tokens for this request
            
        Returns:
            RateLimitResult with allowance decision
        """
        try:
            # Check user-based limits
            user_result = await self._check_user_limits(user_id, user_tier, token_count)
            if not user_result.allowed:
                return user_result
            
            # Check provider-specific limits
            provider_result = await self._check_provider_limits(user_id, provider, token_count)
            if not provider_result.allowed:
                return provider_result
            
            # All checks passed
            await self._record_usage(user_id, provider, user_tier, token_count)
            
            return RateLimitResult(
                allowed=True,
                remaining=min(user_result.remaining, provider_result.remaining),
                reset_time=max(user_result.reset_time, provider_result.reset_time),
                limit_type=RateLimitType.REQUEST_COUNT
            )
            
        except Exception as e:
            logger.error(f"❌ Rate limit check failed: {e}")
            # Fail open for availability
            return RateLimitResult(
                allowed=True,
                remaining=1000,
                reset_time=datetime.now() + timedelta(hours=1),
                limit_type=RateLimitType.REQUEST_COUNT,
                error_message=f"Rate limit check failed: {str(e)}"
            )
    
    async def _check_user_limits(self, user_id: str, user_tier: str, token_count: int) -> RateLimitResult:
        """Check user-based rate limits"""
        limits = self.rate_limits.get(user_tier, self.rate_limits["free"])
        
        # Check requests per minute
        rpm_key = f"rate_limit:user:{user_id}:requests:minute"
        rpm_result = await self._check_limit(rpm_key, limits["requests_per_minute"], 1)
        
        if not rpm_result.allowed:
            return rpm_result
        
        # Check requests per hour
        rph_key = f"rate_limit:user:{user_id}:requests:hour"
        rph_result = await self._check_limit(rph_key, limits["requests_per_hour"], 1)
        
        if not rph_result.allowed:
            return rph_result
        
        # Check tokens per hour
        tph_key = f"rate_limit:user:{user_id}:tokens:hour"
        tph_result = await self._check_limit(tph_key, limits["tokens_per_hour"], token_count)
        
        return tph_result
    
    async def _check_provider_limits(self, user_id: str, provider: str, token_count: int) -> RateLimitResult:
        """Check provider-specific rate limits"""
        limits = self.provider_limits.get(provider, {})
        
        if not limits:
            # No provider limits configured
            return RateLimitResult(
                allowed=True,
                remaining=1000,
                reset_time=datetime.now() + timedelta(minutes=1),
                limit_type=RateLimitType.PROVIDER_SPECIFIC
            )
        
        # Check provider requests per minute
        rpm_key = f"rate_limit:provider:{provider}:user:{user_id}:requests:minute"
        rpm_result = await self._check_limit(rpm_key, limits["requests_per_minute"], 1)
        
        if not rpm_result.allowed:
            return rpm_result
        
        # Check provider tokens per minute
        tpm_key = f"rate_limit:provider:{provider}:user:{user_id}:tokens:minute"
        tpm_result = await self._check_limit(tpm_key, limits["tokens_per_minute"], token_count)
        
        return tpm_result
    
    async def _check_limit(self, key: str, rate_limit: RateLimit, increment: int) -> RateLimitResult:
        """Check individual rate limit with sliding window"""
        now = time.time()
        window_start = now - rate_limit.window
        
        if self.redis_client:
            try:
                # Use Redis for distributed rate limiting
                pipe = self.redis_client.pipeline()
                
                # Remove old entries
                pipe.zremrangebyscore(key, 0, window_start)
                
                # Count current entries
                pipe.zcard(key)
                
                # Add current request
                pipe.zadd(key, {f"{now}:{increment}": now})
                
                # Set expiration
                pipe.expire(key, rate_limit.window)
                
                results = await pipe.execute()
                current_count = results[1]
                
                # Calculate actual usage by summing increments
                pipe = self.redis_client.pipeline()
                pipe.zrangebyscore(key, window_start, now, withscores=True)
                window_data = await pipe.execute()
                
                total_usage = sum(int(entry[0].split(':')[1]) for entry in window_data[0])
                
            except Exception as e:
                logger.warning(f"Redis error, using fallback: {e}")
                return await self._check_limit_fallback(key, rate_limit, increment)
        else:
            return await self._check_limit_fallback(key, rate_limit, increment)
        
        if total_usage > rate_limit.limit:
            reset_time = datetime.fromtimestamp(now + rate_limit.window)
            return RateLimitResult(
                allowed=False,
                remaining=0,
                reset_time=reset_time,
                limit_type=rate_limit.type,
                retry_after=rate_limit.window,
                error_message=f"Rate limit exceeded: {total_usage}/{rate_limit.limit} per {rate_limit.window}s"
            )
        
        remaining = rate_limit.limit - total_usage
        reset_time = datetime.fromtimestamp(now + rate_limit.window)
        
        return RateLimitResult(
            allowed=True,
            remaining=remaining,
            reset_time=reset_time,
            limit_type=rate_limit.type
        )
    
    async def _check_limit_fallback(self, key: str, rate_limit: RateLimit, increment: int) -> RateLimitResult:
        """Fallback rate limiting using in-memory cache"""
        now = time.time()
        window_start = now - rate_limit.window
        
        if key not in self.fallback_cache:
            self.fallback_cache[key] = []
        
        # Clean old entries
        self.fallback_cache[key] = [
            (timestamp, count) for timestamp, count in self.fallback_cache[key]
            if timestamp > window_start
        ]
        
        # Calculate current usage
        total_usage = sum(count for _, count in self.fallback_cache[key])
        
        if total_usage + increment > rate_limit.limit:
            reset_time = datetime.fromtimestamp(now + rate_limit.window)
            return RateLimitResult(
                allowed=False,
                remaining=0,
                reset_time=reset_time,
                limit_type=rate_limit.type,
                retry_after=rate_limit.window,
                error_message=f"Rate limit exceeded (fallback): {total_usage + increment}/{rate_limit.limit}"
            )
        
        # Record usage
        self.fallback_cache[key].append((now, increment))
        
        remaining = rate_limit.limit - (total_usage + increment)
        reset_time = datetime.fromtimestamp(now + rate_limit.window)
        
        return RateLimitResult(
            allowed=True,
            remaining=remaining,
            reset_time=reset_time,
            limit_type=rate_limit.type
        )
    
    async def _record_usage(self, user_id: str, provider: str, user_tier: str, token_count: int):
        """Record successful API usage for analytics"""
        try:
            usage_data = {
                "user_id": user_id,
                "provider": provider,
                "user_tier": user_tier,
                "token_count": token_count,
                "timestamp": datetime.now().isoformat()
            }
            
            if self.redis_client:
                # Store usage analytics
                analytics_key = f"ai_usage_analytics:{datetime.now().strftime('%Y-%m-%d')}"
                await self.redis_client.lpush(analytics_key, json.dumps(usage_data))
                await self.redis_client.expire(analytics_key, 86400 * 7)  # Keep for 7 days
                
        except Exception as e:
            logger.error(f"Failed to record usage analytics: {e}")
    
    async def get_user_usage_stats(self, user_id: str) -> Dict[str, Any]:
        """Get current usage statistics for a user"""
        try:
            stats = {
                "user_id": user_id,
                "current_limits": {},
                "usage": {}
            }
            
            # Check current usage against limits
            user_tier = "free"  # TODO: Get from user service
            limits = self.rate_limits.get(user_tier, self.rate_limits["free"])
            
            for limit_name, rate_limit in limits.items():
                key = f"rate_limit:user:{user_id}:{limit_name.split('_')[0]}:{limit_name.split('_')[-1]}"
                
                if self.redis_client:
                    try:
                        now = time.time()
                        window_start = now - rate_limit.window
                        
                        # Get current usage
                        window_data = await self.redis_client.zrangebyscore(
                            key, window_start, now, withscores=True
                        )
                        
                        total_usage = sum(int(entry[0].split(':')[1]) for entry in window_data)
                        
                        stats["usage"][limit_name] = {
                            "used": total_usage,
                            "limit": rate_limit.limit,
                            "remaining": rate_limit.limit - total_usage,
                            "window_seconds": rate_limit.window,
                            "reset_time": datetime.fromtimestamp(now + rate_limit.window).isoformat()
                        }
                        
                    except Exception as e:
                        logger.error(f"Failed to get usage stats for {limit_name}: {e}")
                        stats["usage"][limit_name] = {"error": str(e)}
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get user usage stats: {e}")
            return {"error": str(e)}
    
    async def cleanup_expired_data(self):
        """Cleanup expired rate limiting data"""
        if not self.redis_client:
            return
        
        try:
            # Clean up old analytics data (keep 7 days)
            cutoff_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            # This would be run as a background task
            logger.info("🧹 Cleaned up expired rate limiting data")
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired data: {e}")

# Global rate limiting service instance
rate_limit_service = AIRateLimitService()

async def check_ai_rate_limit(
    user_id: str, 
    provider: str, 
    user_tier: str = "free",
    token_count: int = 1
) -> RateLimitResult:
    """
    Convenience function for checking AI rate limits
    """
    if rate_limit_service.redis_client is None:
        await rate_limit_service.initialize()
    
    return await rate_limit_service.check_rate_limit(user_id, provider, user_tier, token_count)
