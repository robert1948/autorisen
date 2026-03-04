#!/usr/bin/env python3
"""Seed the RAG knowledge base with approved company documents.

Reads documents from docs/ and uploads them through the RAG pipeline
(chunk → embed → approve). Uses the system user as document owner.

Usage:
    python scripts/seed_rag_documents.py                       # uses OpenAI embeddings
    python scripts/seed_rag_documents.py --dry-run             # preview without writing
    python scripts/seed_rag_documents.py --fallback-embeddings # hash-based (no API needed)

Requires:
    OPENAI_API_KEY in environment (unless --fallback-embeddings is used)
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import uuid
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.src.db import models
from backend.src.db.session import DB_URL
from backend.src.modules.rag.models import ApprovedDocument
from backend.src.modules.rag.schemas import DocumentUpload
from backend.src.modules.rag.service import RAGService

# ---------------------------------------------------------------------------
# Seed documents — sourced from docs/
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SEED_DOCUMENTS = [
    {
        "title": "CapeControl Business Plan v2 — February 2026",
        "doc_type": "policy",
        "metadata": {
            "department": "management",
            "version": "2.0",
            "last_updated": "2026-02",
            "classification": "internal",
        },
        "source_file": "docs/CapeControl_Business_Plan_v2.md",
    },
    {
        "title": "Governance & Compliance Playbook",
        "doc_type": "sop",
        "metadata": {
            "department": "security",
            "version": "1.0",
            "classification": "internal",
            "scope": "access control, data handling, policy adherence",
        },
        "source_file": "docs/playbooks/governance_compliance.md",
    },
    {
        "title": "Closed Beta Pilot Playbook v1.0",
        "doc_type": "sop",
        "metadata": {
            "department": "operations",
            "version": "1.0",
            "last_updated": "2026-02-24",
            "classification": "internal",
            "target": "10-20 compliance-heavy SMBs",
        },
        "source_file": "docs/playbooks/BETA_PILOT_PLAYBOOK.md",
    },
    {
        "title": "Release & Deploy Playbook (MVP)",
        "doc_type": "sop",
        "metadata": {
            "department": "engineering",
            "version": "1.0",
            "classification": "internal",
            "scope": "staging + production deployment procedures",
        },
        "source_file": "docs/playbooks/PLAYBOOK_RELEASE_AND_DEPLOY.md",
    },
    {
        "title": "Platform Design Principles",
        "doc_type": "policy",
        "metadata": {
            "department": "product",
            "version": "1.0",
            "classification": "internal",
        },
        "source_file": "docs/DESIGN_PRINCIPLES.md",
    },
]


def get_or_create_system_user(db) -> models.User:
    """Return the system user, creating it if necessary."""
    system_email = "system@capecontrol.com"
    user = db.query(models.User).filter(models.User.email == system_email).first()
    if user:
        print(f"  Using existing system user: {user.id}")
        return user

    user = models.User(
        id=str(uuid.uuid4()),
        email=system_email,
        first_name="System",
        last_name="Admin",
        hashed_password="hashed_placeholder",
        role="Admin",
        is_active=True,
        is_email_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"  Created system user: {user.id}")
    return user


def document_already_seeded(db, owner_id: str, title: str) -> bool:
    """Check if a document with this title already exists for the owner."""
    existing = (
        db.query(ApprovedDocument)
        .filter(
            ApprovedDocument.owner_id == owner_id,
            ApprovedDocument.title == title,
            ApprovedDocument.status.in_(["approved", "processing", "pending"]),
        )
        .first()
    )
    return existing is not None


async def seed_documents(dry_run: bool = False, fallback_embeddings: bool = False):
    """Main seeding logic."""
    print(f"\n{'=' * 60}")
    print("CapeControl RAG Knowledge Base Seeder")
    print(f"{'=' * 60}")
    print(f"Database: {DB_URL[:40]}...")
    print(f"Dry run:  {dry_run}")
    print(f"Documents to seed: {len(SEED_DOCUMENTS)}")
    print()

    engine = create_engine(DB_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Get or create system user
        print("[1/3] Resolving system user...")
        system_user = get_or_create_system_user(db)

        # Initialise RAG service
        print("[2/3] Initialising RAG service...")
        openai_key = None if fallback_embeddings else os.environ.get("OPENAI_API_KEY")
        if fallback_embeddings:
            # Remove from env so RAGService.upload_document() doesn't pick it up
            # via settings.openai_api_key fallback. Also clear the cached settings.
            os.environ.pop("OPENAI_API_KEY", None)
            try:
                from backend.src.core.config import get_settings
                get_settings.cache_clear()
            except Exception:
                pass
            print("  --fallback-embeddings — using hash-based pseudo-embeddings")
        elif openai_key:
            print("  OpenAI API key found — will generate real embeddings")
        else:
            print("  No OpenAI API key — will use hash-based dev embeddings")

        service = RAGService(openai_api_key=openai_key)

        # Process each document
        print(f"[3/3] Seeding {len(SEED_DOCUMENTS)} documents...\n")
        seeded = 0
        skipped = 0
        errors = 0

        for i, doc_spec in enumerate(SEED_DOCUMENTS, 1):
            title = doc_spec["title"]
            source = PROJECT_ROOT / doc_spec["source_file"]

            print(f"  [{i}/{len(SEED_DOCUMENTS)}] {title}")
            print(f"       Source: {doc_spec['source_file']}")

            # Check source file exists
            if not source.exists():
                print(f"       ⚠ Source file not found — SKIPPED")
                errors += 1
                continue

            # Check not already seeded
            if document_already_seeded(db, system_user.id, title):
                print(f"       ✓ Already seeded — SKIPPED")
                skipped += 1
                continue

            # Read content
            content = source.read_text(encoding="utf-8")
            print(f"       Content: {len(content):,} chars")

            if dry_run:
                print(f"       → Would upload (dry run)")
                seeded += 1
                continue

            # Upload via RAG service
            payload = DocumentUpload(
                title=title,
                content=content,
                doc_type=doc_spec["doc_type"],
                metadata=doc_spec.get("metadata"),
            )
            try:
                result = await service.upload_document(db, system_user, payload)
                print(f"       ✓ Uploaded — ID: {result.id}, Chunks: {result.chunk_count}")
                seeded += 1
            except Exception as e:
                print(f"       ✗ FAILED: {e}")
                errors += 1

        # Summary
        print(f"\n{'─' * 60}")
        print(f"Done! Seeded: {seeded}  Skipped: {skipped}  Errors: {errors}")
        if dry_run:
            print("(Dry run — no changes written)")
        print(f"{'─' * 60}\n")

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description="Seed the RAG knowledge base with approved company documents."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview documents without uploading",
    )
    parser.add_argument(
        "--fallback-embeddings",
        action="store_true",
        help="Use hash-based pseudo-embeddings (no OpenAI API key needed)",
    )
    args = parser.parse_args()
    asyncio.run(seed_documents(dry_run=args.dry_run, fallback_embeddings=args.fallback_embeddings))


if __name__ == "__main__":
    main()
