"""RAG module — FastAPI router with evidence-first endpoints."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_verified_user
from backend.src.db import models

from .evidence import EvidencePack, generate_evidence_pack
from .schemas import (
    DocumentListResponse,
    DocumentResponse,
    DocumentUpload,
    RAGHealthResponse,
    RAGQueryRequest,
    RAGQueryResponse,
)
from .service import RAGService

log = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["rag"])

# Module-level singleton (lazy init)
_service: Optional[RAGService] = None


def _get_service() -> RAGService:
    global _service
    if _service is None:
        from backend.src.core.config import get_settings

        settings = get_settings()
        _service = RAGService(
            openai_api_key=settings.openai_api_key,
            anthropic_api_key=settings.anthropic_api_key,
        )
    return _service


# ------------------------------------------------------------------
# Document management endpoints
# ------------------------------------------------------------------


@router.post("/documents", response_model=DocumentResponse, status_code=201)
async def upload_document(
    payload: DocumentUpload,
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
):
    """Upload and ingest a new approved document.

    The document is chunked, embedded, and marked as approved for retrieval.
    """
    service = _get_service()
    return await service.upload_document(db, current_user, payload)


@router.get("/documents", response_model=DocumentListResponse)
def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    doc_type: Optional[str] = Query(None),
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
):
    """List approved documents for the current user."""
    service = _get_service()
    return service.list_documents(
        db,
        current_user,
        page=page,
        page_size=page_size,
        status=status,
        doc_type=doc_type,
    )


@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
):
    """Get a single approved document by ID."""
    service = _get_service()
    doc = service.get_document(db, current_user, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/documents/{document_id}", status_code=204)
def delete_document(
    document_id: str,
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
):
    """Archive (soft-delete) a document. Removes it from future retrievals."""
    service = _get_service()
    found = service.delete_document(db, current_user, document_id)
    if not found:
        raise HTTPException(status_code=404, detail="Document not found")
    return None


# ------------------------------------------------------------------
# RAG query endpoint
# ------------------------------------------------------------------


@router.post("/query", response_model=RAGQueryResponse)
async def rag_query(
    request: RAGQueryRequest,
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
):
    """Execute a RAG query against approved documents.

    Returns an LLM response grounded in approved documents, with a full
    evidence trace including citations, similarity scores, and provenance.

    When no approved documents match and the unsupported policy is 'refuse',
    the response will be withheld and ``refused=True``.
    """
    service = _get_service()
    return await service.query(db, current_user, request)


# ------------------------------------------------------------------
# Health
# ------------------------------------------------------------------


@router.get("/health", response_model=RAGHealthResponse)
def rag_health(
    db: Session = Depends(get_session),
):
    """RAG subsystem health check."""
    service = _get_service()
    return service.health(db)


# ------------------------------------------------------------------
# Evidence export
# ------------------------------------------------------------------


@router.get("/evidence/export", response_model=EvidencePack)
def export_evidence_pack(
    period_start: Optional[datetime] = Query(None, description="ISO datetime filter start"),
    period_end: Optional[datetime] = Query(None, description="ISO datetime filter end"),
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
):
    """Export a full evidence pack for compliance review.

    Returns all approved documents (metadata), RAG query logs with
    full provenance, and summary statistics. Filterable by time period.
    """
    return generate_evidence_pack(
        db,
        current_user,
        period_start=period_start,
        period_end=period_end,
    )
