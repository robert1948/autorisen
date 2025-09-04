# backend/app/models/agent.py
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.db import Base  # your declarative Base


class AgentSession(Base):
    __tablename__ = "agent_sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    channel = Column(String(64), nullable=False, default="faq", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    messages = relationship(
        "AgentMessage", back_populates="session", cascade="all, delete-orphan"
    )


class AgentMessage(Base):
    __tablename__ = "agent_messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("agent_sessions.id", ondelete="CASCADE"),
        index=True,
    )
    role = Column(String(16), nullable=False)  # "user" | "assistant" | "system"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("AgentSession", back_populates="messages")


Index(
    "ix_agent_messages_session_created_at",
    AgentMessage.session_id,
    AgentMessage.created_at.desc(),
)
