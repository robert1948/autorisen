"""Database ORM models."""

from __future__ import annotations

import uuid

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    """Minimal user model used for authentication flows."""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(320), unique=True, nullable=False, index=True)
    first_name = Column(String(50), nullable=False, server_default="")
    last_name = Column(String(50), nullable=False, server_default="")
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(32), nullable=False, server_default="Customer")
    company_name = Column(String(100), nullable=False, server_default="")
    is_email_verified = Column(Boolean, nullable=False, server_default="0")
    is_active = Column(Boolean, nullable=False, server_default="1")
    token_version = Column(Integer, nullable=False, default=0, server_default="0")
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    terms_accepted_at = Column(DateTime(timezone=True), nullable=True)
    terms_version = Column(String(32), nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(
            func.length(first_name) <= 50, name="ck_users_first_name_length"
        ),
        CheckConstraint(func.length(last_name) <= 50, name="ck_users_last_name_length"),
        CheckConstraint(
            func.length(company_name) <= 100, name="ck_users_company_name_length"
        ),
    )

    credentials = relationship(
        "Credential", back_populates="user", cascade="all, delete-orphan"
    )
    sessions = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan"
    )
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    password_reset_tokens = relationship(
        "PasswordResetToken", back_populates="user", cascade="all, delete-orphan"
    )
    invoices = relationship(
        "Invoice", back_populates="user", cascade="all, delete-orphan"
    )
    payment_methods = relationship(
        "PaymentMethod", back_populates="user", cascade="all, delete-orphan"
    )
    tasks = relationship("Task", back_populates="user")
    audit_events = relationship("AuditEvent", back_populates="user")


class Credential(Base):
    """Authentication credential per provider (password, oauth, etc.)."""

    __tablename__ = "credentials"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider = Column(String(32), nullable=False)
    provider_uid = Column(String(255), nullable=False)
    secret_hash = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("provider", "provider_uid", name="uq_credentials_provider"),
    )

    user = relationship("User", back_populates="credentials")


class Role(Base):
    """Role aggregate grouping permissions."""

    __tablename__ = "roles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(64), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    users = relationship("User", secondary="user_roles", back_populates="roles")
    permissions = relationship(
        "Permission", secondary="role_permissions", back_populates="roles"
    )


class Permission(Base):
    """Individual permission code (e.g., auth.user.read)."""

    __tablename__ = "permissions"

    code = Column(String(128), primary_key=True)
    description = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    roles = relationship(
        "Role", secondary="role_permissions", back_populates="permissions"
    )


class UserRole(Base):
    """Association between users and roles."""

    __tablename__ = "user_roles"

    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role_id = Column(
        String(36), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    assigned_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class RolePermission(Base):
    """Join table linking roles to permissions."""

    __tablename__ = "role_permissions"

    role_id = Column(
        String(36), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    permission_code = Column(
        String(128),
        ForeignKey("permissions.code", ondelete="CASCADE"),
        primary_key=True,
    )
    granted_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class Session(Base):
    """Persistent session / refresh token tracking."""

    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash = Column(String(255), unique=True, nullable=False)
    user_agent = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="sessions")


class PasswordResetToken(Base):
    """One-time password reset token issued to a user."""

    __tablename__ = "password_reset_tokens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash = Column(String(255), unique=True, nullable=False)
    purpose = Column(String(32), nullable=False, server_default="password_reset")
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="password_reset_tokens")


class EmailEvent(Base):
    """Record outbound email delivery attempts."""

    __tablename__ = "email_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    to_email = Column(String(320), nullable=False, index=True)
    template = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False)
    error = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class EmailJob(Base):
    """Queued email job payloads for background processing."""

    __tablename__ = "email_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_type = Column(String(64), nullable=False)
    payload = Column(JSON, nullable=False)
    status = Column(String(32), nullable=False, index=True)
    attempts = Column(Integer, nullable=False, server_default="0")
    max_attempts = Column(Integer, nullable=False, server_default="3")
    run_after = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
    last_error = Column(Text, nullable=True)
    idempotency_key = Column(String(128), nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index("ix_email_jobs_status_run_after", "status", "run_after"),
    )


class AppBuild(Base):
    """Recorded build metadata for runtime version display."""

    __tablename__ = "app_builds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    app_name = Column(String(64), nullable=False, server_default="autorisen")
    version_label = Column(String(128), nullable=False)
    build_number = Column(Integer, nullable=True)
    git_sha = Column(String(64), nullable=False)
    build_epoch = Column(BigInteger, nullable=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "app_name",
            "git_sha",
            "build_epoch",
            name="uq_app_builds_identity",
        ),
        Index("ix_app_builds_app_name_created_at", "app_name", "created_at"),
    )


class LoginAudit(Base):
    """Track authentication attempts for auditing and monitoring."""

    __tablename__ = "login_audits"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(320), nullable=False)
    success = Column(Boolean, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    details = Column(Text, nullable=True)


class ChatThread(Base):
    """Persisted ChatKit thread metadata per user and placement."""

    __tablename__ = "app_chat_threads"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    placement = Column(String(64), nullable=False)
    context = Column(JSON, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User")
    events = relationship(
        "ChatEvent", back_populates="thread", cascade="all, delete-orphan"
    )


class ChatEvent(Base):
    """Individual ChatKit messages or tool invocations stored per thread."""

    __tablename__ = "app_chat_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    thread_id = Column(
        String(36),
        ForeignKey("app_chat_threads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String(32), nullable=False)
    content = Column(Text, nullable=False)
    tool_name = Column(String(64), nullable=True)
    event_metadata = Column(JSON, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    thread = relationship("ChatThread", back_populates="events")


class Agent(Base):
    """Registered agent metadata owned by an organization or developer."""

    __tablename__ = "agents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    slug = Column(String(100), unique=True, nullable=False)
    name = Column(String(160), nullable=False)
    description = Column(Text, nullable=True)
    visibility = Column(String(32), nullable=False, server_default="private")
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    owner = relationship("User")
    versions = relationship(
        "AgentVersion",
        back_populates="agent",
        cascade="all, delete-orphan",
        order_by="AgentVersion.created_at.desc()",
    )
    runs = relationship("AgentRun", back_populates="agent")
    tasks = relationship("Task", back_populates="agent")
    audit_events = relationship("AuditEvent", back_populates="agent")


class AgentVersion(Base):
    """Versioned manifest entries for an agent."""

    __tablename__ = "agent_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(
        String(36),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version = Column(String(20), nullable=False)
    manifest = Column(JSON, nullable=False)
    changelog = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, server_default="draft")
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    published_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("agent_id", "version", name="uq_agent_versions_version"),
    )

    agent = relationship("Agent", back_populates="versions")


class AgentInstallation(Base):
    """Track installed agents per user."""

    __tablename__ = "agent_installations"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "agent_id", name="uq_agent_installations_user_agent"
        ),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent_id = Column(
        String(36),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version = Column(String(20), nullable=False)
    configuration = Column(JSON, nullable=False, server_default="{}")
    status = Column(String(32), nullable=False, server_default="active")
    installed_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User")
    agent = relationship("Agent")


class Task(Base):
    """Agent task execution tracking."""

    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=False, index=True)
    goal = Column(Text, nullable=True)
    input = Column(JSON, nullable=True)
    status = Column(String(32), nullable=False, server_default="queued", index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    result = Column(JSON, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )

    user = relationship("User")
    agent = relationship("Agent")


class AgentRun(Base):
    """Track user-initiated agent runs for the marketplace UI."""

    __tablename__ = "agent_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(
        String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status = Column(String(32), nullable=False, server_default="active", index=True)
    input_json = Column(JSON, nullable=True)
    output_json = Column(JSON, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    agent = relationship("Agent", back_populates="runs")
    user = relationship("User")
    events = relationship(
        "AgentEvent", back_populates="run", cascade="all, delete-orphan"
    )


class AgentEvent(Base):
    """Event log for actions performed within an agent run."""

    __tablename__ = "agent_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(
        String(36), ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type = Column(String(64), nullable=False)
    payload_json = Column(JSON, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )

    run = relationship("AgentRun", back_populates="events")


class Run(Base):
    """Step-by-step execution details for tasks."""

    __tablename__ = "runs"
    __table_args__ = (UniqueConstraint("task_id", "step", name="uq_runs_task_step"),)

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(
        String(36),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step = Column(Integer, nullable=False)
    state = Column(JSON, nullable=True)
    status = Column(String(32), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    error_details = Column(JSON, nullable=True)

    task = relationship("Task")


class AuditEvent(Base):
    """Comprehensive audit trail for agent activities."""

    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(
        String(36), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True
    )
    agent_id = Column(
        String(36), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True
    )
    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    event_type = Column(String(64), nullable=False, index=True)
    payload = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )

    task = relationship("Task")
    agent = relationship("Agent")
    user = relationship("User")


class FlowRun(Base):
    """Recorded orchestrator runs for auditing and UI history."""

    __tablename__ = "flow_runs"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "idempotency_key", name="uq_flow_runs_user_idempotency"
        ),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True, index=True)
    agent_id = Column(String(36), nullable=True, index=True)
    agent_version_id = Column(String(36), nullable=True, index=True)
    placement = Column(String(64), nullable=False)
    thread_id = Column(String(36), nullable=False, index=True)
    steps = Column(JSON, nullable=False)
    status = Column(String(20), nullable=False, server_default="pending")
    attempt = Column(Integer, nullable=False, server_default="0")
    max_attempts = Column(Integer, nullable=False, server_default="3")
    idempotency_key = Column(String(128), nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class OnboardingChecklist(Base):
    """Per-user onboarding checklist state."""

    __tablename__ = "onboarding_checklists"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    thread_id = Column(String(36), nullable=False, index=True)
    tasks = Column(JSON, nullable=False, default=dict)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class OnboardingSession(Base):
    """Track onboarding sessions per user."""

    __tablename__ = "onboarding_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(String(32), nullable=False, server_default="active")
    onboarding_completed = Column(Boolean, nullable=False, server_default="0")
    last_step_key = Column(String(64), nullable=True)
    metadata_json = Column(JSON, nullable=True)
    started_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (Index("ix_onboarding_sessions_user_status", "user_id", "status"),)


class OnboardingStep(Base):
    """Catalog of onboarding steps."""

    __tablename__ = "onboarding_steps"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    step_key = Column(String(64), nullable=False, unique=True)
    title = Column(String(160), nullable=False)
    order_index = Column(Integer, nullable=False, default=0)
    required = Column(Boolean, nullable=False, server_default="1")
    role_scope_json = Column(JSON, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class UserOnboardingStepState(Base):
    """Per-session onboarding step state."""

    __tablename__ = "user_onboarding_step_state"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(
        String(36),
        ForeignKey("onboarding_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_key = Column(
        String(64),
        ForeignKey("onboarding_steps.step_key", ondelete="CASCADE"),
        nullable=False,
    )
    status = Column(String(32), nullable=False, server_default="pending")
    completed_at = Column(DateTime(timezone=True), nullable=True)
    skipped_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "step_key",
            name="uq_onboarding_step_state_session_step",
        ),
    )


class OnboardingMessage(Base):
    """Messages captured during onboarding."""

    __tablename__ = "onboarding_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(
        String(36),
        ForeignKey("onboarding_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String(32), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class TrustAcknowledgement(Base):
    """Record trust acknowledgements (privacy/security)."""

    __tablename__ = "trust_acknowledgements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(
        String(36),
        ForeignKey("onboarding_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    key = Column(String(64), nullable=False)
    metadata_json = Column(JSON, nullable=True)
    acknowledged_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "key",
            name="uq_trust_ack_user_key",
        ),
    )


class OnboardingEventLog(Base):
    """Audit log for onboarding events."""

    __tablename__ = "onboarding_event_log"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(
        String(36),
        ForeignKey("onboarding_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type = Column(String(64), nullable=False)
    step_key = Column(String(64), nullable=True)
    payload = Column(JSON, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class UserProfile(Base):
    """Flexible registration profile payload per role."""

    __tablename__ = "user_profiles"

    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    profile = Column(JSON, nullable=False, server_default="{}")
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", back_populates="profile")


class AnalyticsEvent(Base):
    """Minimal analytics events captured for onboarding."""

    __tablename__ = "analytics_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String(64), nullable=False)
    step = Column(String(32), nullable=True)
    role = Column(String(32), nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class FaqArticle(Base):
    """Support FAQ knowledge base entries."""

    __tablename__ = "faq_articles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question = Column(String(255), nullable=False)
    answer = Column(Text, nullable=False)
    tags = Column(JSON, nullable=True)
    is_published = Column(Boolean, nullable=False, server_default="1")
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class SupportTicket(Base):
    """User-submitted support tickets."""

    __tablename__ = "support_tickets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, nullable=False, index=True)
    stripe_payment_intent_id = Column(String(255), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(32), nullable=True)
    status = Column(String(32), nullable=True)
    assigned_to = Column(String(255), nullable=True)
    resolution = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class Invoice(Base):
    """Payment invoices/orders tracking billing requests."""

    __tablename__ = "invoices"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    # Invoice details
    amount = Column(Numeric(10, 2), nullable=False)  # Precise decimal for money
    currency = Column(String(3), nullable=False, default="ZAR")
    status = Column(String(32), nullable=False, default="pending", index=True)

    # Item details
    item_name = Column(String(255), nullable=False)
    item_description = Column(Text, nullable=True)

    # Customer details
    customer_email = Column(String(255), nullable=False)
    customer_first_name = Column(String(64), nullable=True)
    customer_last_name = Column(String(64), nullable=True)

    # PayFast integration
    payment_provider = Column(String(32), nullable=False, default="payfast")
    external_reference = Column(String(255), nullable=True, unique=True, index=True)

    # Metadata and audit
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'paid', 'cancelled', 'failed', 'refunded')",
            name="invoice_status_check",
        ),
        CheckConstraint("amount > 0", name="invoice_amount_positive"),
    )

    # Relationships
    user = relationship("User", back_populates="invoices")
    transactions = relationship(
        "Transaction", back_populates="invoice", cascade="all, delete-orphan"
    )


class Transaction(Base):
    """Individual payment transactions linked to invoices."""

    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    invoice_id = Column(
        String(36), ForeignKey("invoices.id"), nullable=False, index=True
    )

    # Transaction details
    amount = Column(Numeric(10, 2), nullable=False)  # Precise decimal for money
    currency = Column(String(3), nullable=False, default="ZAR")
    status = Column(String(32), nullable=False, default="pending", index=True)
    transaction_type = Column(String(32), nullable=False, default="payment")

    # PayFast integration
    payment_provider = Column(String(32), nullable=False, default="payfast")
    provider_transaction_id = Column(
        String(255), nullable=True, unique=True, index=True
    )
    provider_reference = Column(String(255), nullable=True, index=True)

    # ITN data
    itn_data = Column(JSON, nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata and audit
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'completed', 'failed', 'cancelled', 'refunded')",
            name="transaction_status_check",
        ),
        CheckConstraint(
            "transaction_type IN ('payment', 'refund', 'chargeback')",
            name="transaction_type_check",
        ),
        CheckConstraint("amount > 0", name="transaction_amount_positive"),
    )

    # Relationships
    invoice = relationship("Invoice", back_populates="transactions")


class PaymentMethod(Base):
    """Stored payment method information for users."""

    __tablename__ = "billing_payment_methods"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    # Payment method details
    provider = Column(String(32), nullable=False, default="payfast")
    method_type = Column(String(32), nullable=False)  # 'card', 'eft', 'instant_eft'
    is_default = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)

    # Encrypted/tokenized details (never store actual card details)
    provider_token = Column(String(255), nullable=True)
    last_four = Column(String(4), nullable=True)  # Last 4 digits for display
    card_brand = Column(String(32), nullable=True)  # 'visa', 'mastercard', etc.
    expiry_month = Column(Integer, nullable=True)
    expiry_year = Column(Integer, nullable=True)

    # Metadata and audit
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "method_type IN ('card', 'eft', 'instant_eft', 'bank_transfer')",
            name="payment_method_type_check",
        ),
        UniqueConstraint(
            "user_id", "provider_token", name="unique_user_provider_token"
        ),
    )

    # Relationships
    user = relationship("User", back_populates="payment_methods")


# ---------------------------------------------------------------------------
# Developer & Admin registration models
# ---------------------------------------------------------------------------


class DeveloperProfile(Base):
    """Extended profile data for users with the Developer role."""

    __tablename__ = "developer_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    organization = Column(String(200), nullable=True)
    use_case = Column(String(64), nullable=True)
    website_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    developer_terms_accepted_at = Column(DateTime(timezone=True), nullable=True)
    developer_terms_version = Column(String(32), nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", backref="developer_profile")


class ApiCredential(Base):
    """API key pair issued to developers."""

    __tablename__ = "api_credentials"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    client_id = Column(String(64), unique=True, nullable=False, index=True)
    client_secret_hash = Column(String(255), nullable=False)
    label = Column(String(100), nullable=True)
    is_active = Column(Boolean, nullable=False, server_default="1")
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", backref="api_credentials")


class AdminInvite(Base):
    """Invite token for admin account registration (invite-only)."""

    __tablename__ = "admin_invites"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    target_email = Column(String(320), nullable=False, index=True)
    invited_by = Column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    token_hash = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    used_by = Column(String(36), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    inviter = relationship("User", foreign_keys=[invited_by])
