#! /usr/bin/env python
# backend/scripts/build_knowledge_base.py
import os
import sys

# Add backend directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.settings import settings
from app.services.knowledge import KnowledgeManager


def main():
    """
    Builds and persists the knowledge base vectorstore.
    This script should be run whenever the documentation in /docs changes.
    """
    print("--- Building Knowledge Base ---")

    if not settings.OPENAI_API_KEY:
        print("❌ ERROR: OPENAI_API_KEY environment variable not set.")
        print("Please set it in your .env file or export it.")
        sys.exit(1)

    try:
        kb_manager = KnowledgeManager(openai_api_key=settings.OPENAI_API_KEY)

        # Force reload to rebuild from scratch
        retriever = kb_manager.get_retriever(force_reload=True)

        if retriever:
            print("\n✅ Knowledge Base built successfully.")

            # --- Perform a test query ---
            print("\n--- Running a test query ---")
            test_query = "What is the MVP for AI agents?"
            print(f"🔍 Query: {test_query}")

            try:
                results = retriever.invoke(test_query)
                if results:
                    print("\n📚 Top search results:")
                    for i, doc in enumerate(results):
                        print(f"\n--- Result {i+1} ---")
                        print(doc.page_content)
                        source = doc.metadata.get("source", "N/A")
                        print(f"\nSource: {source}")
                else:
                    print("⚠️ Test query returned no results.")
            except Exception as e:
                print(f"❌ Test query failed: {e}")

        else:
            print("\n❌ Knowledge Base could not be initialized.")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
