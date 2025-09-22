import os
import pytest
import redis


@pytest.fixture(autouse=True, scope="module")
def clear_rate_limiter_keys():
    """Clear Redis keys starting with `rl:` for the duration of the test module.

    This fixture runs automatically for every test module (autouse=True). It deletes
    keys at the start and end of the module to avoid leftover counters affecting
    rate-limiter tests.
    """
    url = os.getenv("REDIS_URL", "redis://redis:6379")
    r = redis.Redis.from_url(url, decode_responses=True)

    try:
        keys = r.keys("rl:*")
        if keys:
            r.delete(*keys)
    except Exception:
        # If Redis is unavailable, do not fail tests here; caller may expect fail-open behavior.
        pass

    yield

    # teardown: remove any rl keys created during tests
    try:
        keys = r.keys("rl:*")
        if keys:
            r.delete(*keys)
    except Exception:
        pass
