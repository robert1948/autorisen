"""
RAG (Retrieval-Augmented Generation) module.

Controlled document retrieval pipeline for approved business documents.
Evidence-oriented: every retrieval carries provenance metadata.
"""

from .router import router
from .schemas import (
    DocumentUpload,
    DocumentResponse,
    RAGQueryRequest,
    RAGQueryResponse,
    Citation,
)
from .service import RAGService

__all__ = [
    "router",
    "DocumentUpload",
    "DocumentResponse",
    "RAGQueryRequest",
    "RAGQueryResponse",
    "Citation",
    "RAGService",
]
