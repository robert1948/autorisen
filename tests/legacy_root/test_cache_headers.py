#!/usr/bin/env python3
"""
Test script to verify cache-control headers are working correctly
"""

import os
import sys
from pathlib import Path

import requests

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def test_cache_headers():
    """Test that cache headers are set correctly"""
    base_url = os.getenv("TEST_BASE_URL", "http://localhost:8000")

    print(f"🧪 Testing cache headers on {base_url}")

    test_cases = [
        {
            "path": "/",
            "expected_cache_control": "no-cache, must-revalidate",
            "description": "HTML root should not cache",
        },
        {
            "path": "/config.json",
            "expected_cache_control": "no-store, must-revalidate",
            "description": "Config should never cache",
        },
        {
            "path": "/favicon.ico",
            "expected_cache_control": "public, max-age=31536000",
            "description": "Favicon should cache for 1 year",
        },
        {
            "path": "/api/health",
            "expected_cache_control": "no-store",
            "description": "API endpoints should not cache",
        },
    ]

    results = []

    for test in test_cases:
        try:
            response = requests.get(f"{base_url}{test['path']}", timeout=10)
            cache_control = response.headers.get("Cache-Control", "")

            success = test["expected_cache_control"] in cache_control
            status = "✅ PASS" if success else "❌ FAIL"

            print(f"{status} {test['description']}")
            print(f"   Path: {test['path']}")
            print(f"   Expected: {test['expected_cache_control']}")
            print(f"   Actual: {cache_control}")
            print()

            results.append(
                {
                    "path": test["path"],
                    "success": success,
                    "expected": test["expected_cache_control"],
                    "actual": cache_control,
                }
            )

        except requests.exceptions.RequestException as e:
            print(f"❌ FAIL {test['description']} - Connection error: {e}")
            results.append({"path": test["path"], "success": False, "error": str(e)})

    # Summary
    passed = sum(1 for r in results if r["success"])
    total = len(results)

    print(f"📊 Cache Header Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All cache header tests passed!")
        return True
    else:
        print("⚠️  Some cache header tests failed.")
        return False


if __name__ == "__main__":
    success = test_cache_headers()
    sys.exit(0 if success else 1)
