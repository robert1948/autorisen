# backend/app/services/knowledge/manager.py
import os
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# --- Constants ---
# Use a subdirectory in /tmp for persistent but non-critical data
CACHE_DIR = Path("/tmp/autorisen_cache")
VECTORSTORE_PATH = CACHE_DIR / "faiss_vectorstore"
DOCS_PATH = Path("./docs")  # Relative to project root


class KnowledgeManager:
    """
    Manages the vectorstore for the knowledge base.
    Handles loading, embedding, and persisting documents.
    """

    def __init__(self, openai_api_key: str):
        if not openai_api_key:
            raise ValueError("OpenAI API key is required for KnowledgeManager")

        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.vectorstore = None

        # Ensure cache directory exists
        CACHE_DIR.mkdir(exist_ok=True)

    def _load_and_split_docs(self):
        """Load documents from the specified directory and split them."""
        # Use DirectoryLoader to load all .md files
        loader = DirectoryLoader(
            DOCS_PATH,
            glob="**/*.md",
            loader_cls=TextLoader,
            show_progress=True,
            use_multithreading=True,
        )
        docs = loader.load()

        # Split documents into smaller chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True,
        )
        return text_splitter.split_documents(docs)

    def _create_vectorstore(self):
        """Create and persist the FAISS vectorstore from documents."""
        print(f"📚 Loading documents from: {DOCS_PATH.resolve()}")
        all_splits = self._load_and_split_docs()

        if not all_splits:
            print("⚠️ No documents found to create a vectorstore.")
            return

        print(f"🧠 Creating vectorstore with {len(all_splits)} document splits...")
        self.vectorstore = FAISS.from_documents(
            documents=all_splits, embedding=self.embeddings
        )

        # Persist the vectorstore to disk
        self.vectorstore.save_local(str(VECTORSTORE_PATH))
        print(f"✅ Vectorstore created and saved to: {VECTORSTORE_PATH}")

    def get_retriever(self, force_reload: bool = False):
        """
        Get a retriever for the knowledge base.
        Loads from disk if available, otherwise creates it.
        """
        if not self.vectorstore or force_reload:
            if VECTORSTORE_PATH.exists() and not force_reload:
                print(f"💾 Loading existing vectorstore from: {VECTORSTORE_PATH}")
                self.vectorstore = FAISS.load_local(
                    str(VECTORSTORE_PATH),
                    self.embeddings,
                    allow_dangerous_deserialization=True,
                )
            else:
                self._create_vectorstore()

        if not self.vectorstore:
            return None

        return self.vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 5}
        )


# Example usage (can be run as a script to pre-build the store)
if __name__ == "__main__":
    from app.core.settings import settings

    if not settings.OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY must be set in your environment to build the knowledge base."
        )

    print("🛠️  Initializing Knowledge Base...")
    kb_manager = KnowledgeManager(openai_api_key=settings.OPENAI_API_KEY)
    retriever = kb_manager.get_retriever(force_reload=True)

    if retriever:
        print("\n✅ Knowledge Base is ready.")
        query = "What is the MVP for AI agents?"
        results = retriever.invoke(query)
        print(f"\n🔍 Test query: '{query}'")
        for i, doc in enumerate(results):
            print(f"\n--- Result {i+1} ---\n")
            print(doc.page_content)
            print(f"\nSource: {doc.metadata.get('source', 'N/A')}")
    else:
        print("\n❌ Knowledge Base could not be initialized.")
