#!/usr/bin/env python3
"""
Test script to verify Anthropic API connectivity and feature usage.
"""

import asyncio
import os
import sys
from pathlib import Path

from anthropic import AsyncAnthropic

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed, using environment variables only")

# Load environment variables if dotenv is available


async def test_basic_completion():
    """Test basic message completion."""
    print("🔍 Testing basic message completion...")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        return False

    if api_key.startswith("sk-ant-api03-placeholder"):
        print("❌ ANTHROPIC_API_KEY is a placeholder value")
        return False

    try:
        client = AsyncAnthropic(api_key=api_key)

        response = await client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": "Say 'API test successful' and nothing else.",
                }
            ],
        )

        # Extract text from response, handling different content block types
        result_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                result_text = block.text
                break
        print(f"✅ Basic completion works! Response: {result_text}")
        print(f"   Model: {response.model}")
        print(
            f"   Usage: {response.usage.input_tokens} in, {response.usage.output_tokens} out"
        )
        return True

    except Exception as e:
        print(f"❌ Basic completion failed: {e}")
        return False


async def test_streaming():
    """Test streaming responses."""
    print("\n🔍 Testing streaming responses...")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key.startswith("sk-ant-api03-placeholder"):
        print("⏭️  Skipping (API key issue)")
        return False

    try:
        client = AsyncAnthropic(api_key=api_key)

        print("   Streaming: ", end="", flush=True)
        async with client.messages.stream(
            model="claude-3-5-haiku-20241022",
            max_tokens=50,
            messages=[{"role": "user", "content": "Count from 1 to 5."}],
        ) as stream:
            async for text in stream.text_stream:
                print(text, end="", flush=True)

        print()
        print("✅ Streaming works!")
        return True

    except Exception as e:
        print(f"❌ Streaming failed: {e}")
        return False


async def test_system_prompt():
    """Test system prompt functionality."""
    print("\n🔍 Testing system prompts...")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key.startswith("sk-ant-api03-placeholder"):
        print("⏭️  Skipping (API key issue)")
        return False

    try:
        client = AsyncAnthropic(api_key=api_key)

        response = await client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=100,
            system="You are a pirate. Always respond in pirate speak.",
            messages=[{"role": "user", "content": "What is 2+2?"}],
        )

        # Extract text from response
        result_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                result_text = block.text
                break
        print(f"✅ System prompt works! Response: {result_text}")
        return True

    except Exception as e:
        print(f"❌ System prompt test failed: {e}")
        return False


async def test_tool_use():
    """Test tool/function calling capability."""
    print("\n🔍 Testing tool use (function calling)...")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key.startswith("sk-ant-api03-placeholder"):
        print("⏭️  Skipping (API key issue)")
        return False

    try:
        client = AsyncAnthropic(api_key=api_key)

        tools = [
            {
                "name": "get_weather",
                "description": "Get the weather for a specific location",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        }
                    },
                    "required": ["location"],
                },
            }
        ]

        response = await client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=500,
            tools=tools,
            messages=[{"role": "user", "content": "What's the weather in Cape Town?"}],
        )

        # Check if Claude used the tool
        has_tool_use = any(block.type == "tool_use" for block in response.content)

        if has_tool_use:
            print("✅ Tool use works! Claude attempted to use the get_weather tool.")
            for block in response.content:
                if block.type == "tool_use":
                    print(f"   Tool: {block.name}")
                    print(f"   Input: {block.input}")
            return True
        else:
            print("⚠️  Tool use partially works but Claude didn't use the tool")
            # Extract text for error message
            text_response = ""
            for block in response.content:
                if hasattr(block, "text"):
                    text_response = block.text
                    break
            print(f"   Response: {text_response[:100]}...")
            return False

    except Exception as e:
        print(f"❌ Tool use test failed: {e}")
        return False


async def test_vision():
    """Test vision/image analysis capability."""
    print("\n🔍 Testing vision (image analysis)...")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key.startswith("sk-ant-api03-placeholder"):
        print("⏭️  Skipping (API key issue)")
        return False

    try:
        client = AsyncAnthropic(api_key=api_key)

        # Use a simple base64 encoded 1x1 red pixel PNG for testing
        test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="

        response = await client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": test_image,
                            },
                        },
                        {"type": "text", "text": "What color is this image?"},
                    ],
                }
            ],
        )

        # Extract text from response
        result_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                result_text = block.text
                break
        print(f"✅ Vision works! Response: {result_text}")
        return True

    except Exception as e:
        print(f"❌ Vision test failed: {e}")
        return False


async def check_current_usage_patterns():
    """Analyze how we're currently using Anthropic in the codebase."""
    print("\n📊 Current Anthropic Usage Analysis:")
    print("-" * 50)

    usage_patterns = {
        "Basic completions": "✅ Used in cape_ai_guide and cape_ai_domain_specialist",
        "System prompts": "✅ Used (prompts.py in both agents)",
        "Streaming": "❌ Not implemented",
        "Tool use": "❌ Not implemented",
        "Vision": "❌ Not implemented",
        "Multi-turn conversations": "❌ Limited (no conversation history)",
        "Temperature control": "✅ Used (0.6-0.7)",
        "Max tokens control": "✅ Used (700-1000)",
    }

    for feature, status in usage_patterns.items():
        print(f"  {feature:.<40} {status}")

    print("\n💡 Recommendations:")
    print("  1. Implement streaming for better UX on long responses")
    print("  2. Add tool use for agent actions (workflows, data queries)")
    print("  3. Consider conversation history for multi-turn interactions")
    print("  4. Add vision support for document/image analysis use cases")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("  ANTHROPIC API CONNECTIVITY & FEATURE TEST")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Basic Completion", await test_basic_completion()))
    results.append(("Streaming", await test_streaming()))
    results.append(("System Prompts", await test_system_prompt()))
    results.append(("Tool Use", await test_tool_use()))
    results.append(("Vision", await test_vision()))

    # Print summary
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name:.<40} {status}")

    print(f"\n  Total: {passed}/{total} tests passed")

    # Usage analysis
    await check_current_usage_patterns()

    print("\n" + "=" * 60)

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
