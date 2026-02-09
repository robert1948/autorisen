"""mvp: agent runs, support, and seed marketplace agents (MVP-PROMISES-ALIGN-001)

Revision ID: b41f0b1a5b8e
Revises: aa304231e2e8
Create Date: 2026-02-09 09:20:00.000000

"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b41f0b1a5b8e"
down_revision: Union[str, None] = "aa304231e2e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


AGENT_SEEDS = [
    {
        "slug": "onboarding-guide",
        "name": "Onboarding Guide",
        "description": "Guided onboarding with next-step tracking and blocker capture.",
        "category": "workflow",
        "placement": "onboarding",
        "permissions": ["onboarding:read", "onboarding:write"],
        "capabilities": ["next_step", "complete_step", "blocked_reason"],
    },
    {
        "slug": "cape-support-bot",
        "name": "Cape Support Bot",
        "description": "Search FAQs and open support tickets with full audit trails.",
        "category": "communication",
        "placement": "support",
        "permissions": ["support:read", "support:write"],
        "capabilities": ["faq_search", "ticket_create", "ticket_list"],
    },
    {
        "slug": "data-analyst",
        "name": "Data Analyst",
        "description": "Guided ops insights with decision-ready summaries.",
        "category": "analytics",
        "placement": "ops",
        "permissions": ["ops:read"],
        "capabilities": ["insights"],
    },
]


def upgrade() -> None:
    op.create_table(
        "agent_runs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "agent_id",
            sa.String(length=36),
            sa.ForeignKey("agents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("input_json", sa.JSON(), nullable=True),
        sa.Column("output_json", sa.JSON(), nullable=True),
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
    op.create_index("ix_agent_runs_agent_id", "agent_runs", ["agent_id"])
    op.create_index("ix_agent_runs_user_id", "agent_runs", ["user_id"])
    op.create_index("ix_agent_runs_status", "agent_runs", ["status"])
    op.create_index("ix_agent_runs_created_at", "agent_runs", ["created_at"])

    op.create_table(
        "agent_events",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "run_id",
            sa.String(length=36),
            sa.ForeignKey("agent_runs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_agent_events_run_id", "agent_events", ["run_id"])
    op.create_index("ix_agent_events_created_at", "agent_events", ["created_at"])

    op.create_table(
        "faq_articles",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("question", sa.String(length=255), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default="1"),
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
    op.create_index("ix_faq_articles_created_at", "faq_articles", ["created_at"])

    op.create_table(
        "support_tickets",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("subject", sa.String(length=160), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="open"),
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
    op.create_index("ix_support_tickets_user_id", "support_tickets", ["user_id"])
    op.create_index("ix_support_tickets_status", "support_tickets", ["status"])
    op.create_index("ix_support_tickets_created_at", "support_tickets", ["created_at"])

    _seed_agents()
    _seed_faqs()


def downgrade() -> None:
    _delete_seeded_agents()
    op.drop_index("ix_support_tickets_created_at", table_name="support_tickets")
    op.drop_index("ix_support_tickets_status", table_name="support_tickets")
    op.drop_index("ix_support_tickets_user_id", table_name="support_tickets")
    op.drop_table("support_tickets")
    op.drop_index("ix_faq_articles_created_at", table_name="faq_articles")
    op.drop_table("faq_articles")
    op.drop_index("ix_agent_events_created_at", table_name="agent_events")
    op.drop_index("ix_agent_events_run_id", table_name="agent_events")
    op.drop_table("agent_events")
    op.drop_index("ix_agent_runs_created_at", table_name="agent_runs")
    op.drop_index("ix_agent_runs_status", table_name="agent_runs")
    op.drop_index("ix_agent_runs_user_id", table_name="agent_runs")
    op.drop_index("ix_agent_runs_agent_id", table_name="agent_runs")
    op.drop_table("agent_runs")


def _seed_agents() -> None:
    conn = op.get_bind()
    now = datetime.utcnow()
    agents_table = sa.table(
        "agents",
        sa.column("id", sa.String()),
        sa.column("owner_id", sa.String()),
        sa.column("slug", sa.String()),
        sa.column("name", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("visibility", sa.String()),
        sa.column("created_at", sa.DateTime()),
        sa.column("updated_at", sa.DateTime()),
    )
    versions_table = sa.table(
        "agent_versions",
        sa.column("id", sa.String()),
        sa.column("agent_id", sa.String()),
        sa.column("version", sa.String()),
        sa.column("manifest", sa.JSON()),
        sa.column("changelog", sa.Text()),
        sa.column("status", sa.String()),
        sa.column("created_at", sa.DateTime()),
        sa.column("published_at", sa.DateTime()),
    )

    for seed in AGENT_SEEDS:
        slug = seed["slug"]
        existing = conn.execute(
            sa.select(agents_table.c.id).where(agents_table.c.slug == slug)
        ).fetchone()
        if existing:
            agent_id = existing[0]
        else:
            agent_id = str(uuid.uuid4())
            conn.execute(
                agents_table.insert().values(
                    id=agent_id,
                    owner_id=None,
                    slug=slug,
                    name=seed["name"],
                    description=seed["description"],
                    visibility="public",
                    created_at=now,
                    updated_at=now,
                )
            )

        version = "1.0.0"
        existing_version = conn.execute(
            sa.select(versions_table.c.id).where(
                sa.and_(
                    versions_table.c.agent_id == agent_id,
                    versions_table.c.version == version,
                )
            )
        ).fetchone()
        if existing_version:
            continue

        manifest = {
            "name": seed["name"],
            "description": seed["description"],
            "placement": seed["placement"],
            "tools": seed["capabilities"],
            "category": seed["category"],
            "author": "CapeControl",
            "permissions": seed["permissions"],
            "capabilities": seed["capabilities"],
            "tags": seed["capabilities"],
            "readme": f"# {seed['name']}\n\n{seed['description']}\n",
            "changelog": "Initial MVP-ready release.",
        }

        conn.execute(
            versions_table.insert().values(
                id=str(uuid.uuid4()),
                agent_id=agent_id,
                version=version,
                manifest=manifest,
                changelog="Initial published version",
                status="published",
                created_at=now,
                published_at=now,
            )
        )


def _seed_faqs() -> None:
    conn = op.get_bind()
    now = datetime.utcnow()
    faqs_table = sa.table(
        "faq_articles",
        sa.column("id", sa.String()),
        sa.column("question", sa.String()),
        sa.column("answer", sa.Text()),
        sa.column("tags", sa.JSON()),
        sa.column("is_published", sa.Boolean()),
        sa.column("created_at", sa.DateTime()),
        sa.column("updated_at", sa.DateTime()),
    )

    seeds = [
        {
            "question": "How do I update my onboarding progress?",
            "answer": "Use the Onboarding Guide agent to complete the next step or mark a step as blocked.",
            "tags": ["onboarding", "workflow"],
        },
        {
            "question": "Where can I see operational blockers?",
            "answer": "Open the Data Analyst agent and ask for Top Blockers to see aggregated friction.",
            "tags": ["ops", "insights"],
        },
        {
            "question": "How do I contact support?",
            "answer": "Use the Cape Support Bot to create a ticket; you'll get a ticket ID immediately.",
            "tags": ["support", "tickets"],
        },
    ]

    for seed in seeds:
        conn.execute(
            faqs_table.insert().values(
                id=str(uuid.uuid4()),
                question=seed["question"],
                answer=seed["answer"],
                tags=seed["tags"],
                is_published=True,
                created_at=now,
                updated_at=now,
            )
        )


def _delete_seeded_agents() -> None:
    conn = op.get_bind()
    slugs = [seed["slug"] for seed in AGENT_SEEDS]
    conn.execute(
        sa.text(
            "DELETE FROM agent_versions WHERE agent_id IN (SELECT id FROM agents WHERE slug = ANY(:slugs))"
        ),
        {"slugs": slugs},
    )
    conn.execute(sa.text("DELETE FROM agents WHERE slug = ANY(:slugs)"), {"slugs": slugs})
