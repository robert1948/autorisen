"""
Analytics models for performance tracking and user behavior analysis.
Created for Performance Analytics Dashboard implementation.
"""
import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text

from app.database import Base


class AnalyticsEvent(Base):
    """Track user events and system interactions"""
    __tablename__ = "analytics_events"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users_v2.id"), nullable=True)
    event_type = Column(String(100), nullable=False, index=True)  # api_call, login, payment, etc.
    event_category = Column(String(50), nullable=False, index=True)  # system, user, payment, api
    event_data = Column(JSON, nullable=True)  # Additional event details
    endpoint = Column(String(200), nullable=True)  # API endpoint if applicable
    method = Column(String(10), nullable=True)  # HTTP method
    status_code = Column(Integer, nullable=True)  # Response status
    duration_ms = Column(Float, nullable=True)  # Request duration
    ip_address = Column(String(45), nullable=True)  # Client IP
    user_agent = Column(Text, nullable=True)  # Client user agent
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship to user - TEMPORARILY COMMENTED OUT FOR REGISTRATION FIX
    # user = relationship("User", back_populates="analytics_events")

class SystemMetrics(Base):
    """Track system performance metrics"""
    __tablename__ = "system_metrics"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_type = Column(String(50), nullable=False, index=True)  # cpu, memory, response_time, etc.
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20), nullable=False)  # percent, ms, bytes, etc.
    source = Column(String(50), nullable=False, default="localhost")  # localhost, heroku, etc.
    metric_metadata = Column(JSON, nullable=True)  # Additional metric details (renamed from metadata)
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)

class UserSession(Base):
    """Track user sessions for analytics"""
    __tablename__ = "user_sessions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users_v2.id"), nullable=True)
    session_id = Column(String(100), nullable=False, unique=True, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    page_views = Column(Integer, default=0)
    api_calls = Column(Integer, default=0)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationship to user - TEMPORARILY COMMENTED OUT FOR REGISTRATION FIX
    # user = relationship("User", back_populates="sessions")

class APIUsageStats(Base):
    """Track API usage statistics"""
    __tablename__ = "api_usage_stats"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users_v2.id"), nullable=True)
    endpoint = Column(String(200), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    calls_count = Column(Integer, default=1)
    total_duration_ms = Column(Float, default=0.0)
    avg_duration_ms = Column(Float, default=0.0)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship to user - TEMPORARILY COMMENTED OUT FOR REGISTRATION FIX
    # user = relationship("User", back_populates="api_usage_stats")
