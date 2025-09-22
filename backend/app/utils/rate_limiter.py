"""Redis-backed rate limiter helper.

Usage:
    from app.utils.rate_limiter import rate_limit

    @rate_limit(key_prefix='login', limit=5, period=60)
    def login(...):
        ...

This implementation uses Redis INCR with expiry to count requests.
"""
import os
import functools
import redis
from fastapi import HTTPException, Request

REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379')
_r = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def _key(prefix: str, identifier: str) -> str:
    return f"rl:{prefix}:{identifier}"


def rate_limit(key_prefix: str, limit: int = 5, period: int = 60):
    """Decorator for simple per-identifier rate limiting.

    identifier is resolved from kwargs: if 'email' in kwargs use that, else use client_ip if provided.
    The route should accept an 'email' parameter (for request-reset) or we pass client_ip in kwargs.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Resolve identifier from kwargs
            identifier = None
            if 'email' in kwargs:
                identifier = kwargs.get('email')
            elif 'client_ip' in kwargs:
                identifier = kwargs.get('client_ip')
            else:
                # Inspect positional args: look for object/dict with 'email' attribute/key
                for a in args:
                    try:
                        if hasattr(a, 'email') and getattr(a, 'email'):
                            identifier = getattr(a, 'email')
                            break
                        if isinstance(a, dict) and 'email' in a:
                            identifier = a['email']
                            break
                        # FastAPI Request object: extract client host
                        if isinstance(a, Request):
                            client_host = a.client.host if a.client else None
                            if client_host:
                                identifier = client_host
                                break
                    except Exception:
                        continue
            if not identifier:
                identifier = 'anon'
            k = _key(key_prefix, identifier)
            try:
                cur = _r.incr(k)
                if cur == 1:
                    _r.expire(k, period)
                if cur > limit:
                    raise HTTPException(status_code=429, detail='Too many requests')
            except redis.RedisError:
                # On Redis failure, allow request (fail-open) but log
                print('[RATE LIMIT] Redis error, failing open')
            return func(*args, **kwargs)

        return wrapper

    return decorator


def check_rate_limit(key_prefix: str, identifier: str, limit: int = 5, period: int = 60):
    """Programmatic check to be called from inside route handlers.
    Raises HTTPException(429) when limit exceeded.
    """
    k = _key(key_prefix, identifier or 'anon')
    try:
        cur = _r.incr(k)
        if cur == 1:
            _r.expire(k, period)
        if cur > limit:
            raise HTTPException(status_code=429, detail='Too many requests')
    except redis.RedisError:
        print('[RATE LIMIT] Redis error, failing open')
