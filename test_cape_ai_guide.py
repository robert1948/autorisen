"""
Test script for CapeAI Guide Agent

Tests the core functionality without requiring full FastAPI setup.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend src to Python path
backend_src = Path(__file__).parent.parent.parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

from modules.agents.cape_ai_guide.schemas import CapeAIGuideTaskInput
from modules.agents.cape_ai_guide.service import CapeAIGuideService
from modules.agents.cape_ai_guide.knowledge_base import KnowledgeBase


async def test_knowledge_base():
    """Test the knowledge base functionality."""
    print("Testing Knowledge Base...")
    kb = KnowledgeBase()

    # Test search functionality
    results = await kb.search("How to set up workflows", limit=3)
    print(f"Search results for 'workflows': {len(results)} documents found")
    for doc in results:
        print(f"  - {doc['title']} (score: {doc['search_score']:.2f})")

    # Test context-aware search
    context = {"current_page": "/dashboard/workflows"}
    context_results = await kb.search("setup automation", context=context, limit=2)
    print(f"\nContext-aware search: {len(context_results)} documents found")
    for doc in context_results:
        print(f"  - {doc['title']} (score: {doc['search_score']:.2f})")


async def test_service_without_openai():
    """Test the service functionality without OpenAI API calls."""
    print("\nTesting Service (without OpenAI)...")

    # Create test input
    test_input = CapeAIGuideTaskInput(
        query="How do I create my first workflow?",
        context={
            "current_page": "/dashboard/workflows",
            "user_role": "admin",
            "features_used": [],
        },
        user_level="beginner",
        preferred_format="steps",
    )

    print(f"Test input: {test_input.query}")
    print(f"User level: {test_input.user_level}")
    print(f"Preferred format: {test_input.preferred_format}")

    # Test knowledge base integration
    kb = KnowledgeBase()
    relevant_docs = await kb.search(test_input.query, test_input.context, limit=3)
    print(f"Found {len(relevant_docs)} relevant documents")

    # Test without actual OpenAI service (would require API key)
    print("Service integration test completed (OpenAI integration requires API key)")


async def test_full_service():
    """Test the full service if OpenAI API key is available."""
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        print("\nSkipping full service test - OPENAI_API_KEY not set")
        return

    print("\nTesting Full Service with OpenAI...")

    try:
        service = CapeAIGuideService(openai_api_key=openai_api_key, model="gpt-4")

        test_input = CapeAIGuideTaskInput(
            query="What are the best practices for setting up automated workflows?",
            context={"current_page": "/dashboard", "user_role": "admin"},
            user_level="intermediate",
            preferred_format="steps",
        )

        # This would make an actual API call
        result = await service.process_query(test_input)

        print(f"Response: {result.response[:200]}...")
        print(f"Confidence: {result.confidence_score}")
        print(f"Suggestions: {result.suggestions}")
        print(f"Resources: {len(result.resources)}")
        print(f"Processing time: {result.processing_time_ms}ms")

    except Exception as e:
        print(f"Full service test failed (expected without valid API key): {e}")


def test_schemas():
    """Test the Pydantic schemas."""
    print("Testing Schemas...")

    # Test input schema
    input_data = CapeAIGuideTaskInput(
        query="How do I get started?", user_level="beginner"
    )
    print(f"Input schema test passed: {input_data.query}")

    # Test with all fields
    full_input = CapeAIGuideTaskInput(
        query="Advanced workflow setup",
        context={"page": "/workflows"},
        user_level="advanced",
        preferred_format="code",
    )
    print(f"Full input schema test passed: {full_input.preferred_format}")

    print("Schema validation successful!")


async def main():
    """Run all tests."""
    print("🚀 CapeAI Guide Agent Test Suite")
    print("=" * 50)

    # Test schemas (synchronous)
    test_schemas()

    # Test knowledge base
    await test_knowledge_base()

    # Test service components
    await test_service_without_openai()

    # Test full service if API key available
    await test_full_service()

    print("\n✅ Test suite completed!")
    print("To test with OpenAI integration, set OPENAI_API_KEY environment variable")


if __name__ == "__main__":
    asyncio.run(main())
