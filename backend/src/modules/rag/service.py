"""RAG module — Core business logic: document ingestion, retrieval, evidence generation."""

from __future__ import annotations

import logging
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.src.core.config import get_settings
from backend.src.db import models as app_models

from . import embeddings
from .models import ApprovedDocument, DocumentChunk, RAGQueryLog
from .schemas import (
    Citation,
    DocumentListResponse,
    DocumentResponse,
    DocumentStatus,
    DocumentUpload,
    EvidenceTrace,
    RAGHealthResponse,
    RAGQueryRequest,
    RAGQueryResponse,
    UnsupportedPolicy,
)

log = logging.getLogger(__name__)


class RAGService:
    """Approved-document RAG pipeline with evidence-first design.

    Every query produces an ``EvidenceTrace`` recording:
    - which documents were retrieved and at what similarity
    - whether the answer was grounded
    - the policy applied for ungrounded answers
    - actor identity and timestamps
    """

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self._openai_key = openai_api_key
        self._anthropic_key = anthropic_api_key
        self._model = model or os.getenv(
            "RAG_LLM_MODEL", "claude-3-5-haiku-20241022"
        )

    # ------------------------------------------------------------------
    # Document CRUD
    # ------------------------------------------------------------------

    async def upload_document(
        self,
        db: Session,
        user: app_models.User,
        payload: DocumentUpload,
    ) -> DocumentResponse:
        """Ingest a new document: store → chunk → embed → approve."""
        doc = ApprovedDocument(
            id=str(uuid.uuid4()),
            owner_id=user.id,
            title=payload.title,
            content=payload.content,
            doc_type=payload.doc_type,
            status=DocumentStatus.PROCESSING.value,
            doc_metadata=payload.metadata,
        )
        db.add(doc)
        db.flush()

        # Chunk
        chunks_text = embeddings.chunk_text(payload.content)
        if not chunks_text:
            doc.status = DocumentStatus.APPROVED.value
            doc.chunk_count = 0
            db.commit()
            return self._doc_to_response(doc)

        # Embed
        settings = get_settings()
        api_key = self._openai_key or settings.openai_api_key
        vectors = await embeddings.generate_embeddings(chunks_text, api_key=api_key)

        # Store chunks
        for idx, (text, vec) in enumerate(zip(chunks_text, vectors)):
            chunk = DocumentChunk(
                id=str(uuid.uuid4()),
                document_id=doc.id,
                chunk_index=idx,
                chunk_text=text,
                embedding=vec,
                token_count=len(text.split()),
            )
            db.add(chunk)

        doc.chunk_count = len(chunks_text)
        doc.status = DocumentStatus.APPROVED.value
        db.commit()
        db.refresh(doc)
        log.info("Document %s ingested: %d chunks", doc.id, doc.chunk_count)
        return self._doc_to_response(doc)

    def list_documents(
        self,
        db: Session,
        user: app_models.User,
        *,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        doc_type: Optional[str] = None,
    ) -> DocumentListResponse:
        """List documents belonging to the user."""
        q = select(ApprovedDocument).where(ApprovedDocument.owner_id == user.id)
        if status:
            q = q.where(ApprovedDocument.status == status)
        if doc_type:
            q = q.where(ApprovedDocument.doc_type == doc_type)

        total = db.scalar(
            select(func.count()).select_from(q.subquery())
        ) or 0

        rows = (
            db.scalars(
                q.order_by(ApprovedDocument.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            .all()
        )
        return DocumentListResponse(
            documents=[self._doc_to_response(r) for r in rows],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_document(
        self, db: Session, user: app_models.User, document_id: str
    ) -> Optional[DocumentResponse]:
        """Get a single document owned by the user."""
        doc = db.scalar(
            select(ApprovedDocument).where(
                ApprovedDocument.id == document_id,
                ApprovedDocument.owner_id == user.id,
            )
        )
        return self._doc_to_response(doc) if doc else None

    def delete_document(
        self, db: Session, user: app_models.User, document_id: str
    ) -> bool:
        """Archive (soft-delete) a document. Returns True if found."""
        doc = db.scalar(
            select(ApprovedDocument).where(
                ApprovedDocument.id == document_id,
                ApprovedDocument.owner_id == user.id,
            )
        )
        if not doc:
            return False
        doc.status = DocumentStatus.ARCHIVED.value
        db.commit()
        return True

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    async def query(
        self,
        db: Session,
        user: app_models.User,
        request: RAGQueryRequest,
    ) -> RAGQueryResponse:
        """Execute a RAG query against approved documents.

        Returns a response with full evidence trace regardless of whether
        an LLM answer is generated.
        """
        t0 = time.time()
        query_id = str(uuid.uuid4())
        settings = get_settings()

        # 1. Embed the query
        api_key = self._openai_key or settings.openai_api_key
        query_vectors = await embeddings.generate_embeddings(
            [request.query], api_key=api_key
        )
        query_vec = query_vectors[0]

        # 2. Retrieve candidate chunks (approved docs owned by user)
        candidates = self._retrieve_chunks(
            db,
            user=user,
            query_vec=query_vec,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            doc_types=request.doc_types,
        )

        # 3. Build citations
        citations: List[Citation] = []
        for chunk, score, doc in candidates:
            citations.append(
                Citation(
                    document_id=doc.id,
                    document_title=doc.title,
                    chunk_index=chunk.chunk_index,
                    chunk_text=chunk.chunk_text,
                    similarity_score=round(score, 4),
                    doc_type=doc.doc_type,
                    doc_metadata=doc.doc_metadata,
                )
            )

        grounded = len(citations) > 0

        # 4. Apply unsupported policy
        refused = False
        refusal_reason: Optional[str] = None
        response_text: Optional[str] = None

        if not grounded and request.unsupported_policy == UnsupportedPolicy.REFUSE:
            refused = True
            refusal_reason = (
                "No approved documents match this query. Under the current "
                "unsupported policy, answers without document backing are "
                "not permitted."
            )
        elif request.include_response:
            # 5. Generate LLM response with retrieved context
            response_text = await self._generate_response(
                query=request.query,
                citations=citations,
                grounded=grounded,
                unsupported_policy=request.unsupported_policy,
            )

        # 6. Build evidence trace
        elapsed_ms = int((time.time() - t0) * 1000)
        evidence = EvidenceTrace(
            query_id=query_id,
            query_text=request.query,
            actor_id=user.id,
            actor_email=user.email,
            timestamp=datetime.now(timezone.utc),
            model_used=self._model if request.include_response else "none",
            citations=citations,
            retrieval_count=len(candidates),
            similarity_threshold=request.similarity_threshold,
            unsupported_policy=request.unsupported_policy.value,
            grounded=grounded,
        )

        # 7. Audit log
        self._log_query(
            db,
            user=user,
            query_text=request.query,
            grounded=grounded,
            refused=refused,
            citations=citations,
            response_text=response_text,
            elapsed_ms=elapsed_ms,
            request=request,
        )

        return RAGQueryResponse(
            response=response_text,
            grounded=grounded,
            refused=refused,
            refusal_reason=refusal_reason,
            evidence=evidence,
            processing_time_ms=elapsed_ms,
        )

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def health(self, db: Session) -> RAGHealthResponse:
        """Return RAG subsystem health metrics."""
        doc_count = db.scalar(
            select(func.count()).select_from(ApprovedDocument)
        ) or 0
        chunk_count = db.scalar(
            select(func.count()).select_from(DocumentChunk)
        ) or 0
        return RAGHealthResponse(
            status="ok",
            document_count=doc_count,
            chunk_count=chunk_count,
            embedding_dimensions=embeddings.embedding_dimensions(),
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _retrieve_chunks(
        self,
        db: Session,
        *,
        user: app_models.User,
        query_vec: List[float],
        top_k: int,
        similarity_threshold: float,
        doc_types: Optional[List[str]],
    ) -> List[Tuple[DocumentChunk, float, ApprovedDocument]]:
        """Retrieve top-K chunks by cosine similarity from approved documents.

        Uses in-application cosine similarity (portable across PostgreSQL
        and SQLite). Can be upgraded to pgvector ``<=>`` operator for scale.
        """
        # Build base query for approved docs owned by user
        doc_q = select(ApprovedDocument).where(
            ApprovedDocument.owner_id == user.id,
            ApprovedDocument.status == DocumentStatus.APPROVED.value,
        )
        if doc_types:
            doc_q = doc_q.where(ApprovedDocument.doc_type.in_(doc_types))

        docs = {d.id: d for d in db.scalars(doc_q).all()}
        if not docs:
            return []

        # Fetch all chunks for those documents
        chunks = db.scalars(
            select(DocumentChunk).where(
                DocumentChunk.document_id.in_(list(docs.keys()))
            )
        ).all()

        # Score every chunk
        scored: List[Tuple[DocumentChunk, float, ApprovedDocument]] = []
        for chunk in chunks:
            stored_vec = chunk.embedding
            if not stored_vec or not isinstance(stored_vec, list):
                continue
            score = embeddings.cosine_similarity(query_vec, stored_vec)
            if score >= similarity_threshold:
                scored.append((chunk, score, docs[chunk.document_id]))

        # Sort descending by score, take top_k
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    async def _generate_response(
        self,
        query: str,
        citations: List[Citation],
        grounded: bool,
        unsupported_policy: UnsupportedPolicy,
    ) -> str:
        """Generate an LLM response using retrieved context."""
        system_prompt = self._build_system_prompt(grounded, unsupported_policy)
        user_prompt = self._build_user_prompt(query, citations)

        if "claude" in self._model.lower():
            return await self._call_anthropic(system_prompt, user_prompt)
        else:
            return await self._call_openai(system_prompt, user_prompt)

    def _build_system_prompt(
        self, grounded: bool, unsupported_policy: UnsupportedPolicy
    ) -> str:
        """Construct the system prompt for the LLM."""
        base = (
            "You are CapeControl's RAG assistant. You answer questions using ONLY "
            "the approved document excerpts provided below. Your answers must be:\n"
            "- Accurate and traceable to the source documents\n"
            "- Concise and actionable\n"
            "- Written in a calm, professional tone\n\n"
        )
        if grounded:
            base += (
                "IMPORTANT: Base your answer ONLY on the provided document excerpts. "
                "If the excerpts do not fully answer the question, say what you can "
                "confirm from the documents and explicitly state what is not covered.\n"
                "Always reference which document(s) support each claim.\n"
            )
        else:
            if unsupported_policy == UnsupportedPolicy.FLAG:
                base += (
                    "WARNING: No approved documents matched this query. You may "
                    "provide a general answer, but you MUST begin your response with "
                    "the following banner:\n"
                    "⚠️ UNSUPPORTED — This answer is not backed by any approved "
                    "document in your library. Verify independently before acting.\n\n"
                )
            else:
                base += (
                    "No approved documents matched this query. Provide a helpful "
                    "general answer.\n"
                )
        return base

    def _build_user_prompt(self, query: str, citations: List[Citation]) -> str:
        """Build the user message with context from retrieved chunks."""
        parts = [f"Question: {query}\n"]

        if citations:
            parts.append("--- APPROVED DOCUMENT EXCERPTS ---\n")
            for i, c in enumerate(citations, 1):
                parts.append(
                    f"[Source {i}] {c.document_title} (type: {c.doc_type}, "
                    f"similarity: {c.similarity_score:.2f}):\n"
                    f"{c.chunk_text}\n"
                )
            parts.append("--- END EXCERPTS ---\n")
            parts.append(
                "Answer the question using ONLY the excerpts above. "
                "Reference sources by number (e.g., [Source 1])."
            )
        else:
            parts.append(
                "No approved document excerpts are available for this query."
            )

        return "\n".join(parts)

    async def _call_anthropic(self, system_prompt: str, user_prompt: str) -> str:
        """Call Anthropic Claude API."""
        from anthropic import AsyncAnthropic

        settings = get_settings()
        api_key = self._anthropic_key or settings.anthropic_api_key
        if not api_key:
            return "[Error: No Anthropic API key configured]"

        client = AsyncAnthropic(api_key=api_key)
        try:
            resp = await client.messages.create(
                model=self._model,
                max_tokens=2048,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return resp.content[0].text if resp.content else ""
        except Exception as exc:
            log.exception("Anthropic API error during RAG response")
            return f"[Error generating response: {exc}]"

    async def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenAI API."""
        from openai import AsyncOpenAI

        settings = get_settings()
        api_key = self._openai_key or settings.openai_api_key
        if not api_key:
            return "[Error: No OpenAI API key configured]"

        client = AsyncOpenAI(api_key=api_key)
        try:
            resp = await client.chat.completions.create(
                model=self._model,
                max_tokens=2048,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return resp.choices[0].message.content or ""
        except Exception as exc:
            log.exception("OpenAI API error during RAG response")
            return f"[Error generating response: {exc}]"

    def _log_query(
        self,
        db: Session,
        *,
        user: app_models.User,
        query_text: str,
        grounded: bool,
        refused: bool,
        citations: List[Citation],
        response_text: Optional[str],
        elapsed_ms: int,
        request: RAGQueryRequest,
    ) -> None:
        """Write an audit log entry for this RAG query."""
        try:
            entry = RAGQueryLog(
                id=str(uuid.uuid4()),
                user_id=user.id,
                query_text=query_text,
                model_used=self._model if request.include_response else None,
                similarity_threshold=request.similarity_threshold,
                unsupported_policy=request.unsupported_policy.value,
                retrieval_count=len(citations),
                grounded=1 if grounded else 0,
                refused=1 if refused else 0,
                cited_document_ids=[c.document_id for c in citations] if citations else None,
                response_text=response_text,
                processing_time_ms=elapsed_ms,
            )
            db.add(entry)
            db.commit()
        except Exception:
            log.exception("Failed to write RAG query audit log")
            db.rollback()

    @staticmethod
    def _doc_to_response(doc: ApprovedDocument) -> DocumentResponse:
        return DocumentResponse(
            id=doc.id,
            owner_id=doc.owner_id,
            title=doc.title,
            doc_type=doc.doc_type,
            status=doc.status,
            chunk_count=doc.chunk_count or 0,
            metadata=doc.doc_metadata,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )
