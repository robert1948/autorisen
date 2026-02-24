"""add RAG tables (approved_documents, chunks, query_logs)

Revision ID: a1b2c3d4e5f6
Revises: None (attach to current head)
Create Date: 2026-02-24
"""

from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = "20260219_plan_align"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Approved documents
    op.create_table(
        "rag_approved_documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "owner_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("doc_type", sa.String(64), nullable=False, server_default="sop"),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("chunk_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("doc_metadata", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_rag_docs_owner_status",
        "rag_approved_documents",
        ["owner_id", "status"],
    )
    op.create_index(
        "ix_rag_docs_doc_type",
        "rag_approved_documents",
        ["doc_type"],
    )

    # Document chunks with embeddings
    op.create_table(
        "rag_document_chunks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "document_id",
            sa.String(36),
            sa.ForeignKey("rag_approved_documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("embedding", sa.JSON(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_rag_chunks_document",
        "rag_document_chunks",
        ["document_id", "chunk_index"],
    )

    # Query audit log
    op.create_table(
        "rag_query_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("query_text", sa.Text(), nullable=False),
        sa.Column("model_used", sa.String(128), nullable=True),
        sa.Column("similarity_threshold", sa.Float(), nullable=False),
        sa.Column("unsupported_policy", sa.String(32), nullable=False),
        sa.Column("retrieval_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("grounded", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("refused", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cited_document_ids", sa.JSON(), nullable=True),
        sa.Column("response_text", sa.Text(), nullable=True),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_rag_query_user", "rag_query_logs", ["user_id"])
    op.create_index("ix_rag_query_created", "rag_query_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("rag_query_logs")
    op.drop_table("rag_document_chunks")
    op.drop_table("rag_approved_documents")
