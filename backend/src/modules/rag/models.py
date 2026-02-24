"""RAG module — SQLAlchemy ORM models for approved documents and chunks."""

from __future__ import annotations

import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from backend.src.db.base import Base


class ApprovedDocument(Base):
    """An uploaded, approved business document (SOP, policy, checklist, etc.)."""

    __tablename__ = "rag_approved_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(String(512), nullable=False)
    content = Column(Text, nullable=False)
    doc_type = Column(String(64), nullable=False, server_default="sop")
    status = Column(String(32), nullable=False, server_default="pending")
    chunk_count = Column(Integer, nullable=False, server_default="0")
    doc_metadata = Column(JSON, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    __table_args__ = (
        Index("ix_rag_docs_owner_status", "owner_id", "status"),
        Index("ix_rag_docs_doc_type", "doc_type"),
    )


class DocumentChunk(Base):
    """An embedded chunk of an approved document for vector retrieval."""

    __tablename__ = "rag_document_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(
        String(36),
        ForeignKey("rag_approved_documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=False)  # stored as JSON array of floats
    token_count = Column(Integer, nullable=False, server_default="0")
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    document = relationship("ApprovedDocument", back_populates="chunks")

    __table_args__ = (
        Index("ix_rag_chunks_document", "document_id", "chunk_index"),
    )


class RAGQueryLog(Base):
    """Audit log entry for every RAG query — evidence-first."""

    __tablename__ = "rag_query_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    query_text = Column(Text, nullable=False)
    model_used = Column(String(128), nullable=True)
    similarity_threshold = Column(Float, nullable=False)
    unsupported_policy = Column(String(32), nullable=False)
    retrieval_count = Column(Integer, nullable=False, server_default="0")
    grounded = Column(Integer, nullable=False, server_default="0")  # bool as int for SQLite compat
    refused = Column(Integer, nullable=False, server_default="0")
    cited_document_ids = Column(JSON, nullable=True)  # list of document IDs
    response_text = Column(Text, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("ix_rag_query_user", "user_id"),
        Index("ix_rag_query_created", "created_at"),
    )
