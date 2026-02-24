"""RAG module — Evidence export for compliance review.

Generates exportable evidence packs (JSON) containing full provenance
records: queries, citations, document metadata, and actor identity.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.src.db import models as app_models
from .models import ApprovedDocument, RAGQueryLog

log = logging.getLogger(__name__)


class EvidencePackEntry(BaseModel):
    """A single query record in an evidence pack."""

    query_id: str
    query_text: str
    timestamp: datetime
    model_used: Optional[str]
    grounded: bool
    refused: bool
    similarity_threshold: float
    unsupported_policy: str
    retrieval_count: int
    cited_document_ids: Optional[List[str]]
    response_text: Optional[str]
    processing_time_ms: Optional[int]


class EvidencePackDocument(BaseModel):
    """Document metadata in the evidence pack."""

    document_id: str
    title: str
    doc_type: str
    status: str
    chunk_count: int
    created_at: datetime
    metadata: Optional[Dict[str, Any]]


class EvidencePack(BaseModel):
    """Complete evidence export bundle."""

    export_id: str
    exported_at: datetime
    exported_by_id: str
    exported_by_email: str
    period_start: Optional[datetime]
    period_end: Optional[datetime]
    total_queries: int
    grounded_queries: int
    refused_queries: int
    documents: List[EvidencePackDocument]
    queries: List[EvidencePackEntry]
    summary: Dict[str, Any]


def generate_evidence_pack(
    db: Session,
    user: app_models.User,
    *,
    period_start: Optional[datetime] = None,
    period_end: Optional[datetime] = None,
) -> EvidencePack:
    """Build a full evidence pack for the user's RAG activity.

    Includes:
    - All approved documents (metadata only, not content)
    - All RAG queries with provenance
    - Summary statistics
    """
    import uuid

    now = datetime.now(timezone.utc)

    # Fetch documents
    doc_q = select(ApprovedDocument).where(
        ApprovedDocument.owner_id == user.id
    )
    docs = db.scalars(doc_q).all()
    doc_entries = [
        EvidencePackDocument(
            document_id=d.id,
            title=d.title,
            doc_type=d.doc_type,
            status=d.status,
            chunk_count=d.chunk_count or 0,
            created_at=d.created_at,
            metadata=d.doc_metadata,
        )
        for d in docs
    ]

    # Fetch query logs
    log_q = select(RAGQueryLog).where(RAGQueryLog.user_id == user.id)
    if period_start:
        log_q = log_q.where(RAGQueryLog.created_at >= period_start)
    if period_end:
        log_q = log_q.where(RAGQueryLog.created_at <= period_end)
    log_q = log_q.order_by(RAGQueryLog.created_at.asc())

    logs = db.scalars(log_q).all()
    query_entries = [
        EvidencePackEntry(
            query_id=entry.id,
            query_text=entry.query_text,
            timestamp=entry.created_at,
            model_used=entry.model_used,
            grounded=bool(entry.grounded),
            refused=bool(entry.refused),
            similarity_threshold=entry.similarity_threshold,
            unsupported_policy=entry.unsupported_policy,
            retrieval_count=entry.retrieval_count,
            cited_document_ids=entry.cited_document_ids,
            response_text=entry.response_text,
            processing_time_ms=entry.processing_time_ms,
        )
        for entry in logs
    ]

    grounded_count = sum(1 for q in query_entries if q.grounded)
    refused_count = sum(1 for q in query_entries if q.refused)

    summary = {
        "total_documents": len(doc_entries),
        "approved_documents": sum(1 for d in doc_entries if d.status == "approved"),
        "total_queries": len(query_entries),
        "grounded_percentage": (
            round(grounded_count / len(query_entries) * 100, 1)
            if query_entries
            else 0.0
        ),
        "refused_percentage": (
            round(refused_count / len(query_entries) * 100, 1)
            if query_entries
            else 0.0
        ),
        "avg_processing_time_ms": (
            round(
                sum(q.processing_time_ms or 0 for q in query_entries) / len(query_entries),
                0,
            )
            if query_entries
            else 0
        ),
        "document_types": list({d.doc_type for d in doc_entries}),
        "period": {
            "start": period_start.isoformat() if period_start else None,
            "end": period_end.isoformat() if period_end else None,
        },
    }

    return EvidencePack(
        export_id=str(uuid.uuid4()),
        exported_at=now,
        exported_by_id=user.id,
        exported_by_email=user.email,
        period_start=period_start,
        period_end=period_end,
        total_queries=len(query_entries),
        grounded_queries=grounded_count,
        refused_queries=refused_count,
        documents=doc_entries,
        queries=query_entries,
        summary=summary,
    )
