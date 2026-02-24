"""RAG module — Pydantic request/response schemas with evidence metadata."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class DocumentStatus(str, Enum):
    """Lifecycle of an approved document."""

    PENDING = "pending"          # uploaded, not yet embedded
    PROCESSING = "processing"    # embedding in progress
    APPROVED = "approved"        # ready for retrieval
    REJECTED = "rejected"        # flagged / removed by admin
    ARCHIVED = "archived"        # soft-deleted


class UnsupportedPolicy(str, Enum):
    """What to do when retrieval finds no approved-doc match."""

    REFUSE = "refuse"            # return empty + flag
    FLAG = "flag"                # answer with a warning banner
    ALLOW = "allow"              # answer normally (testing only)


# ---------------------------------------------------------------------------
# Document CRUD
# ---------------------------------------------------------------------------

class DocumentUpload(BaseModel):
    """Payload for uploading a new approved document."""

    title: str = Field(..., max_length=512, description="Human-readable document title")
    content: str = Field(..., description="Plain-text document content (Markdown accepted)")
    doc_type: str = Field(
        default="sop",
        description="Document category: sop, policy, checklist, regulation, other",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Arbitrary metadata (e.g. department, version, expiry date)",
    )


class DocumentResponse(BaseModel):
    """Returned after document creation or retrieval."""

    id: str
    owner_id: str
    title: str
    doc_type: str
    status: str
    chunk_count: int = 0
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Paginated list of documents."""

    documents: List[DocumentResponse]
    total: int
    page: int
    page_size: int


# ---------------------------------------------------------------------------
# Citation / evidence
# ---------------------------------------------------------------------------

class Citation(BaseModel):
    """A single evidence reference attached to a RAG response."""

    document_id: str = Field(..., description="Source document ID")
    document_title: str = Field(..., description="Human-readable source title")
    chunk_index: int = Field(..., description="Chunk position within the document")
    chunk_text: str = Field(..., description="Exact text excerpt used as context")
    similarity_score: float = Field(
        ..., ge=0.0, le=1.0, description="Cosine similarity to the query"
    )
    doc_type: str = Field(..., description="Document category")
    doc_metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Source document metadata"
    )


class EvidenceTrace(BaseModel):
    """Full provenance record for an AI response."""

    query_id: str = Field(..., description="Unique identifier for this query")
    query_text: str = Field(..., description="The original user query")
    actor_id: str = Field(..., description="User who initiated the query")
    actor_email: str = Field(..., description="Email of the querying user")
    timestamp: datetime = Field(..., description="When the query was executed")
    model_used: str = Field(..., description="LLM model identifier")
    citations: List[Citation] = Field(default_factory=list)
    retrieval_count: int = Field(0, description="Total chunks retrieved before filtering")
    similarity_threshold: float = Field(..., description="Minimum similarity applied")
    unsupported_policy: str = Field(..., description="Policy applied for ungrounded answers")
    grounded: bool = Field(
        ..., description="True if at least one citation met the threshold"
    )


# ---------------------------------------------------------------------------
# RAG query
# ---------------------------------------------------------------------------

class RAGQueryRequest(BaseModel):
    """Input for a RAG-augmented query."""

    query: str = Field(..., min_length=1, max_length=4000)
    doc_types: Optional[List[str]] = Field(
        default=None,
        description="Filter retrieval to specific document types",
    )
    top_k: int = Field(default=5, ge=1, le=20, description="Max chunks to retrieve")
    similarity_threshold: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
        description="Minimum cosine similarity to include a chunk",
    )
    unsupported_policy: UnsupportedPolicy = Field(
        default=UnsupportedPolicy.FLAG,
        description="Behaviour when no approved document matches the query",
    )
    include_response: bool = Field(
        default=True,
        description="If True, generate an LLM response; if False, return citations only",
    )


class RAGQueryResponse(BaseModel):
    """Output of a RAG-augmented query — always includes evidence trace."""

    response: Optional[str] = Field(
        None, description="LLM-generated answer (None if include_response=False or refused)"
    )
    grounded: bool = Field(
        ..., description="True if answer is backed by at least one approved document"
    )
    refused: bool = Field(
        default=False,
        description="True if the unsupported policy caused the answer to be withheld",
    )
    refusal_reason: Optional[str] = Field(
        default=None,
        description="Explanation when the answer is refused",
    )
    evidence: EvidenceTrace = Field(..., description="Full provenance trace")
    processing_time_ms: Optional[int] = Field(
        None, description="Total processing time in milliseconds"
    )


# ---------------------------------------------------------------------------
# Health / status
# ---------------------------------------------------------------------------

class RAGHealthResponse(BaseModel):
    status: str = "ok"
    document_count: int = 0
    chunk_count: int = 0
    embedding_dimensions: int = 0
