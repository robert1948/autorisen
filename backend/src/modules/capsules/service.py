"""Capsule module — Core workflow engine for template-driven RAG tasks."""

from __future__ import annotations

import logging
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from backend.src.core.config import get_settings
from backend.src.db import models as app_models

from .schemas import (
    CapsuleCategory,
    CapsuleCitation,
    CapsuleDefinition,
    CapsuleListResponse,
    CapsuleRunRequest,
    CapsuleRunResponse,
)

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Built-in capsule registry
# ---------------------------------------------------------------------------

_BUILTIN_CAPSULES: Dict[str, CapsuleDefinition] = {}


def _register(capsule: CapsuleDefinition) -> None:
    _BUILTIN_CAPSULES[capsule.id] = capsule


_register(
    CapsuleDefinition(
        id="sop-answering",
        name="SOP Answering",
        description=(
            "Answer questions about Standard Operating Procedures by "
            "retrieving relevant SOP documents and providing precise, "
            "citation-backed answers."
        ),
        category=CapsuleCategory.SOP_ANSWERING,
        system_prompt=(
            "You are an SOP assistant. Answer the user's question using ONLY "
            "the provided SOP document excerpts. Cite every claim with the "
            "document title and chunk index. If no SOP covers the question, "
            "state that clearly."
        ),
        doc_types=["sop", "procedure", "policy"],
        top_k=5,
        similarity_threshold=0.3,
        output_format="markdown",
    )
)

_register(
    CapsuleDefinition(
        id="audit-summary",
        name="Audit Summary",
        description=(
            "Generate a compliance audit summary from uploaded audit "
            "reports, policies, and evidence packs."
        ),
        category=CapsuleCategory.AUDIT_SUMMARY,
        system_prompt=(
            "You are an audit analyst. Synthesise a concise executive audit "
            "summary from the provided document excerpts. Include: key "
            "findings, compliance status, gaps identified, and recommended "
            "actions. Cite each finding."
        ),
        doc_types=["audit", "compliance", "report"],
        top_k=8,
        similarity_threshold=0.25,
        output_format="markdown",
    )
)

_register(
    CapsuleDefinition(
        id="clause-finding",
        name="Clause Finder",
        description=(
            "Locate specific clauses or provisions across legal and "
            "regulatory documents."
        ),
        category=CapsuleCategory.CLAUSE_FINDING,
        system_prompt=(
            "You are a legal clause finder. Identify and extract the exact "
            "clauses that match the user's query. Return each clause with its "
            "source document, section number (if available), and verbatim "
            "text. Do not paraphrase clauses."
        ),
        doc_types=["legal", "contract", "regulation", "policy"],
        top_k=10,
        similarity_threshold=0.2,
        output_format="markdown",
    )
)

_register(
    CapsuleDefinition(
        id="compliance-check",
        name="Compliance Checklist",
        description=(
            "Run a compliance checklist against uploaded policies and "
            "standards. Returns a structured pass/fail report."
        ),
        category=CapsuleCategory.COMPLIANCE_CHECK,
        system_prompt=(
            "You are a compliance checker. Given the user's query describing "
            "the compliance requirement, evaluate the provided document "
            "excerpts and produce a structured checklist:\n"
            "- For each requirement, output: Requirement | Status "
            "(PASS/FAIL/PARTIAL) | Evidence (cite source)\n"
            "Summarise overall compliance at the end."
        ),
        doc_types=None,  # all doc types
        top_k=10,
        similarity_threshold=0.2,
        output_format="checklist",
    )
)

_register(
    CapsuleDefinition(
        id="incident-report",
        name="Incident Report Builder",
        description=(
            "Generate structured incident reports from uploaded incident "
            "records, logs, and procedures."
        ),
        category=CapsuleCategory.INCIDENT_REPORT,
        system_prompt=(
            "You are an incident report writer. Using the provided document "
            "excerpts, generate a structured incident report with: "
            "1) Incident summary, 2) Timeline, 3) Root cause analysis, "
            "4) Impact assessment, 5) Corrective actions. Cite all sources."
        ),
        doc_types=["incident", "log", "report", "procedure"],
        top_k=8,
        similarity_threshold=0.25,
        output_format="markdown",
    )
)


class CapsuleService:
    """Workflow capsule execution engine.

    Uses the RAG pipeline under the hood but wraps each run in a
    capsule-specific prompt, retrieval scope, and output format.
    """

    def __init__(self) -> None:
        # Capsule registry: built-in + user-defined (future)
        self._registry: Dict[str, CapsuleDefinition] = dict(_BUILTIN_CAPSULES)

    # ------------------------------------------------------------------
    # Registry operations
    # ------------------------------------------------------------------

    def list_capsules(self, *, enabled_only: bool = True) -> CapsuleListResponse:
        """Return all registered capsules."""
        caps = list(self._registry.values())
        if enabled_only:
            caps = [c for c in caps if c.enabled]
        return CapsuleListResponse(capsules=caps, total=len(caps))

    def get_capsule(self, capsule_id: str) -> Optional[CapsuleDefinition]:
        """Get a single capsule definition."""
        return self._registry.get(capsule_id)

    def register(self, capsule: CapsuleDefinition) -> None:
        """Register a custom capsule definition at runtime."""
        self._registry[capsule.id] = capsule
        log.info("Registered capsule %s (%s)", capsule.id, capsule.name)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def run(
        self,
        db: Session,
        user: app_models.User,
        request: CapsuleRunRequest,
    ) -> CapsuleRunResponse:
        """Execute a capsule run.

        Pipeline:
        1. Look up capsule definition
        2. Embed the user query
        3. Retrieve chunks scoped to capsule doc_types
        4. Augment with capsule system prompt
        5. Generate LLM response
        6. Return structured result with citations
        """
        t0 = time.time()
        capsule = self.get_capsule(request.capsule_id)
        if capsule is None:
            return CapsuleRunResponse(
                capsule_id=request.capsule_id,
                capsule_name="unknown",
                category="unknown",
                response=None,
                output_format="markdown",
                grounded=False,
                refused=True,
                refusal_reason=f"Capsule '{request.capsule_id}' not found.",
                query=request.query,
                actor_id=user.id,
                actor_email=user.email,
                timestamp=datetime.now(timezone.utc),
                capsule_version="0",
            )

        # Use the RAG service for retrieval + LLM generation
        from backend.src.modules.rag.service import RAGService
        from backend.src.modules.rag.schemas import (
            RAGQueryRequest,
            UnsupportedPolicy,
        )

        settings_obj = get_settings()
        rag = RAGService(
            openai_api_key=settings_obj.openai_api_key,
            anthropic_api_key=settings_obj.anthropic_api_key,
        )

        # Map capsule policy string to UnsupportedPolicy enum
        policy_map = {
            "refuse": UnsupportedPolicy.REFUSE,
            "flag": UnsupportedPolicy.FLAG,
            "allow": UnsupportedPolicy.ALLOW,
        }
        policy = policy_map.get(
            request.unsupported_policy.lower(), UnsupportedPolicy.FLAG
        )

        rag_request = RAGQueryRequest(
            query=request.query,
            doc_types=capsule.doc_types,
            top_k=capsule.top_k,
            similarity_threshold=capsule.similarity_threshold,
            unsupported_policy=policy,
            include_response=True,
        )

        rag_result = await rag.query(db, user, rag_request)

        # Build capsule-specific LLM response if we have citations
        capsule_response = rag_result.response
        grounded = rag_result.grounded
        refused = rag_result.refused
        refusal_reason = rag_result.refusal_reason

        if grounded and rag_result.evidence and rag_result.evidence.citations:
            # Re-generate with capsule-specific system prompt
            capsule_response = await self._generate_capsule_response(
                capsule=capsule,
                query=request.query,
                citations=rag_result.evidence.citations,
                context=request.context,
            )

        # Map RAG citations → CapsuleCitations
        capsule_citations: List[CapsuleCitation] = []
        if rag_result.evidence:
            for c in rag_result.evidence.citations:
                capsule_citations.append(
                    CapsuleCitation(
                        document_id=c.document_id,
                        document_title=c.document_title,
                        chunk_text=c.chunk_text,
                        similarity_score=c.similarity_score,
                        doc_type=c.doc_type,
                    )
                )

        elapsed_ms = int((time.time() - t0) * 1000)

        return CapsuleRunResponse(
            capsule_id=capsule.id,
            capsule_name=capsule.name,
            category=capsule.category.value,
            response=capsule_response,
            output_format=capsule.output_format,
            grounded=grounded,
            refused=refused,
            refusal_reason=refusal_reason,
            citations=capsule_citations,
            query=request.query,
            actor_id=user.id,
            actor_email=user.email,
            timestamp=datetime.now(timezone.utc),
            processing_time_ms=elapsed_ms,
            capsule_version=capsule.version,
        )

    # ------------------------------------------------------------------
    # Capsule-specific LLM call
    # ------------------------------------------------------------------

    async def _generate_capsule_response(
        self,
        *,
        capsule: CapsuleDefinition,
        query: str,
        citations: list,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate LLM response using the capsule's system prompt."""
        settings_obj = get_settings()

        # Build context from retrieved citations
        context_parts: List[str] = []
        for i, c in enumerate(citations, 1):
            context_parts.append(
                f"[Source {i}] {c.document_title} (chunk {c.chunk_index}):\n"
                f"{c.chunk_text}"
            )
        doc_context = "\n\n---\n\n".join(context_parts)

        # Append any extra context fields
        extra = ""
        if context:
            extra = "\n\nAdditional context:\n" + "\n".join(
                f"- {k}: {v}" for k, v in context.items()
            )

        user_message = f"{query}{extra}\n\n---\nRetrieved Documents:\n\n{doc_context}"

        # Use Anthropic (preferred) or OpenAI
        anthropic_key = settings_obj.anthropic_api_key
        openai_key = settings_obj.openai_api_key
        model = os.getenv("RAG_LLM_MODEL", "claude-3-5-haiku-20241022")

        if anthropic_key:
            try:
                import anthropic

                client = anthropic.Anthropic(api_key=anthropic_key)
                msg = client.messages.create(
                    model=model,
                    max_tokens=2048,
                    system=capsule.system_prompt,
                    messages=[{"role": "user", "content": user_message}],
                )
                return msg.content[0].text  # type: ignore[union-attr]
            except Exception as exc:
                log.warning("Anthropic call failed for capsule %s: %s", capsule.id, exc)

        if openai_key:
            try:
                import openai

                client = openai.OpenAI(api_key=openai_key)
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": capsule.system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    max_tokens=2048,
                )
                return resp.choices[0].message.content or ""
            except Exception as exc:
                log.warning("OpenAI call failed for capsule %s: %s", capsule.id, exc)

        return (
            f"[Capsule {capsule.name}] Retrieved {len(citations)} relevant "
            f"excerpts but LLM generation unavailable (no API keys configured)."
        )
