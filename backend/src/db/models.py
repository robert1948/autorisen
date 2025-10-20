"""Database ORM models."""

from __future__ import annotations

import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
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
    token_version = Column(Integer, nullable=False, default=1, server_default="1")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(func.length(first_name) <= 50, name="ck_users_first_name_length"),
        CheckConstraint(func.length(last_name) <= 50, name="ck_users_last_name_length"),
        CheckConstraint(func.length(company_name) <= 100, name="ck_users_company_name_length"),
    )

    credentials = relationship("Credential", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    password_reset_tokens = relationship(
        "PasswordResetToken", back_populates="user", cascade="all, delete-orphan"
    )


class Credential(Base):
    """Authentication credential per provider (password, oauth, etc.)."""

    __tablename__ = "credentials"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(32), nullable=False)
    provider_uid = Column(String(255), nullable=False)
    secret_hash = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (UniqueConstraint("provider", "provider_uid", name="uq_credentials_provider"),)

    user = relationship("User", back_populates="credentials")


class Role(Base):
    """Role aggregate grouping permissions."""

    __tablename__ = "roles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(64), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    users = relationship("User", secondary="user_roles", back_populates="roles")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")


class Permission(Base):
    """Individual permission code (e.g., auth.user.read)."""

    __tablename__ = "permissions"

    code = Column(String(128), primary_key=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")


class UserRole(Base):
    """Association between users and roles."""

    __tablename__ = "user_roles"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(String(36), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    assigned_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class RolePermission(Base):
    """Join table linking roles to permissions."""

    __tablename__ = "role_permissions"

    role_id = Column(String(36), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permission_code = Column(
        String(128), ForeignKey("permissions.code", ondelete="CASCADE"), primary_key=True
    )
    granted_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class Session(Base):
    """Persistent session / refresh token tracking."""

    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), unique=True, nullable=False)
    user_agent = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="sessions")


class PasswordResetToken(Base):
    """One-time password reset token issued to a user."""

    __tablename__ = "password_reset_tokens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), unique=True, nullable=False)
    purpose = Column(String(32), nullable=False, server_default="password_reset")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="password_reset_tokens")


class LoginAudit(Base):
    """Track authentication attempts for auditing and monitoring."""

    __tablename__ = "login_audits"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(320), nullable=False)
    success = Column(Boolean, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    details = Column(Text, nullable=True)


class ChatThread(Base):
    """Persisted ChatKit thread metadata per user and placement."""

    __tablename__ = "app_chat_threads"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    placement = Column(String(64), nullable=False)
    context = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User")
    events = relationship("ChatEvent", back_populates="thread", cascade="all, delete-orphan")


class ChatEvent(Base):
    """Individual ChatKit messages or tool invocations stored per thread."""

    __tablename__ = "app_chat_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    thread_id = Column(
        String(36), ForeignKey("app_chat_threads.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role = Column(String(32), nullable=False)
    content = Column(Text, nullable=False)
    tool_name = Column(String(64), nullable=True)
    event_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    thread = relationship("ChatThread", back_populates="events")


class Agent(Base):
    """Registered agent metadata owned by an organization or developer."""

    __tablename__ = "agents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    slug = Column(String(100), unique=True, nullable=False)
    name = Column(String(160), nullable=False)
    description = Column(Text, nullable=True)
    visibility = Column(String(32), nullable=False, server_default="private")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    owner = relationship("User")
    versions = relationship(
        "AgentVersion",
        back_populates="agent",
        cascade="all, delete-orphan",
        order_by="AgentVersion.created_at.desc()",
    )


class AgentVersion(Base):
    """Versioned manifest entries for an agent."""

    __tablename__ = "agent_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(String(20), nullable=False)
    manifest = Column(JSON, nullable=False)
    changelog = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, server_default="draft")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (UniqueConstraint("agent_id", "version", name="uq_agent_versions_version"),)

    agent = relationship("Agent", back_populates="versions")


class FlowRun(Base):
    """Recorded orchestrator runs for auditing and UI history."""

    __tablename__ = "flow_runs"
    __table_args__ = (
        UniqueConstraint("user_id", "idempotency_key", name="uq_flow_runs_user_idempotency"),
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
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class OnboardingChecklist(Base):
    """Per-user onboarding checklist state."""

    __tablename__ = "onboarding_checklists"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    thread_id = Column(String(36), nullable=False, index=True)
    tasks = Column(JSON, nullable=False, default=dict)
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class UserProfile(Base):
    """Flexible registration profile payload per role."""

    __tablename__ = "user_profiles"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    profile = Column(JSON, nullable=False, server_default="{}")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
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
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
