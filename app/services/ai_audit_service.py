"""
AI Audit Trail Service - Comprehensive AI interaction tracking and compliance system.

This service provides enterprise-grade audit trail capabilities for all AI interactions,
ensuring transparency, compliance, and security monitoring across the platform.
"""

import asyncio
import hashlib
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import redis.asyncio as redis
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
    and_,
    func,
    or_,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database Models
Base = declarative_base()

class AIAuditLog(Base):
    __tablename__ = "ai_audit_logs"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    session_id = Column(String(36), nullable=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Request Details
    provider = Column(String(50), nullable=False, index=True)
    model = Column(String(100), nullable=False)
    endpoint = Column(String(200), nullable=False)
    request_hash = Column(String(64), nullable=False, index=True)
    
    # Response Details
    response_hash = Column(String(64), nullable=True)
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Float, nullable=False)
    
    # Content & Privacy
    prompt_length = Column(Integer, nullable=False)
    response_length = Column(Integer, nullable=True)
    contains_pii = Column(Boolean, default=False)
    safety_filtered = Column(Boolean, default=False)
    
    # Usage & Cost
    tokens_used = Column(Integer, nullable=True)
    estimated_cost = Column(Float, nullable=True)
    rate_limited = Column(Boolean, default=False)
    
    # Compliance & Security
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    compliance_flags = Column(Text, nullable=True)  # JSON
    security_events = Column(Text, nullable=True)  # JSON
    
    # Metadata
    audit_metadata = Column(Text, nullable=True)  # JSON
    retention_until = Column(DateTime, nullable=True)

    # Indexes for performance
    __table_args__ = (
        Index('idx_audit_user_time', 'user_id', 'timestamp'),
        Index('idx_audit_provider_time', 'provider', 'timestamp'),
        Index('idx_audit_session_time', 'session_id', 'timestamp'),
        Index('idx_audit_compliance', 'contains_pii', 'safety_filtered'),
    )

# Enums and Data Classes
class AuditEventType(Enum):
    AI_REQUEST = "ai_request"
    AI_RESPONSE = "ai_response"
    RATE_LIMIT_HIT = "rate_limit_hit"
    SAFETY_FILTER = "safety_filter"
    PII_DETECTION = "pii_detection"
    COMPLIANCE_VIOLATION = "compliance_violation"
    SYSTEM_ERROR = "system_error"

class ComplianceLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AuditEntry:
    """Structured audit entry for AI interactions"""
    id: str
    user_id: str
    timestamp: datetime
    event_type: AuditEventType
    provider: str
    model: str
    
    # Request/Response
    prompt_hash: str
    response_hash: str | None = None
    status_code: int = 200
    response_time_ms: float = 0.0
    
    # Content analysis
    prompt_length: int = 0
    response_length: int = 0
    contains_pii: bool = False
    safety_filtered: bool = False
    
    # Usage tracking
    tokens_used: int | None = None
    estimated_cost: float | None = None
    rate_limited: bool = False
    
    # Security context
    session_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    
    # Compliance
    compliance_level: ComplianceLevel = ComplianceLevel.LOW
    compliance_flags: list[str] = None
    security_events: list[str] = None
    
    # Additional metadata
    metadata: dict[str, Any] = None

class AIAuditService:
    """
    Comprehensive AI Audit Trail Service
    
    Features:
    - Real-time audit logging for all AI interactions
    - Content analysis and PII detection
    - Compliance monitoring and reporting
    - Security event tracking
    - Data retention management
    - Analytics and insights
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379", db_url: str = None):
        self.redis_url = redis_url
        self.db_url = db_url
        self.redis_client = None
        self.db_session = None
        
        # Configuration
        self.max_content_length = 10000  # Max chars to store
        self.default_retention_days = 90
        self.pii_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',  # Credit card
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}[- ]?\d{3}[- ]?\d{4}\b',  # Phone
        ]
        
        # In-memory fallback for high availability
        self.memory_cache = {}
        self.cache_max_size = 10000

    async def initialize(self):
        """Initialize Redis connection and database"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            await self.redis_client.ping()
            print("✅ AI Audit Service: Redis connected")
        except Exception as e:
            print(f"⚠️ AI Audit Service: Redis connection failed, using memory fallback: {e}")
            self.redis_client = None

        if self.db_url:
            try:
                engine = create_async_engine(self.db_url)
                self.db_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
                print("✅ AI Audit Service: Database connected")
            except Exception as e:
                print(f"⚠️ AI Audit Service: Database connection failed: {e}")

    async def log_ai_interaction(
        self,
        user_id: str,
        provider: str,
        model: str,
        prompt: str,
        response: str | None = None,
        request_metadata: dict[str, Any] | None = None,
        **kwargs
    ) -> str:
        """
        Log an AI interaction with comprehensive audit trail
        
        Args:
            user_id: User identifier
            provider: AI provider (openai, anthropic, gemini)
            model: Specific model used
            prompt: User prompt/input
            response: AI response (optional)
            request_metadata: Additional request context
            **kwargs: Additional audit parameters
            
        Returns:
            Audit entry ID
        """
        try:
            # Generate unique audit ID
            audit_id = str(uuid.uuid4())
            timestamp = datetime.utcnow()
            
            # Content analysis
            prompt_hash = self._hash_content(prompt)
            response_hash = self._hash_content(response) if response else None
            contains_pii = self._detect_pii(prompt) or (response and self._detect_pii(response))
            
            # Create audit entry
            entry = AuditEntry(
                id=audit_id,
                user_id=user_id,
                timestamp=timestamp,
                event_type=AuditEventType.AI_REQUEST,
                provider=provider,
                model=model,
                prompt_hash=prompt_hash,
                response_hash=response_hash,
                prompt_length=len(prompt),
                response_length=len(response) if response else 0,
                contains_pii=contains_pii,
                session_id=kwargs.get('session_id'),
                ip_address=kwargs.get('ip_address'),
                user_agent=kwargs.get('user_agent'),
                tokens_used=kwargs.get('tokens_used'),
                estimated_cost=kwargs.get('estimated_cost'),
                rate_limited=kwargs.get('rate_limited', False),
                safety_filtered=kwargs.get('safety_filtered', False),
                response_time_ms=kwargs.get('response_time_ms', 0.0),
                metadata=request_metadata or {}
            )
            
            # Determine compliance level
            entry.compliance_level = self._assess_compliance_level(entry)
            
            # Store audit entry
            await self._store_audit_entry(entry)
            
            # Store content securely if needed
            if kwargs.get('store_content', False):
                await self._store_content(audit_id, prompt, response)
            
            return audit_id
            
        except Exception as e:
            print(f"❌ AI Audit Service: Failed to log interaction: {e}")
            return None

    async def log_security_event(
        self,
        user_id: str,
        event_type: str,
        description: str,
        severity: ComplianceLevel = ComplianceLevel.MEDIUM,
        metadata: dict[str, Any] | None = None
    ) -> str:
        """Log a security event"""
        try:
            audit_id = str(uuid.uuid4())
            
            entry = AuditEntry(
                id=audit_id,
                user_id=user_id,
                timestamp=datetime.utcnow(),
                event_type=AuditEventType.SYSTEM_ERROR,
                provider="security",
                model="event",
                prompt_hash="",
                compliance_level=severity,
                security_events=[event_type],
                metadata=metadata or {}
            )
            
            await self._store_audit_entry(entry)
            return audit_id
            
        except Exception as e:
            print(f"❌ AI Audit Service: Failed to log security event: {e}")
            return None

    async def get_user_audit_trail(
        self,
        user_id: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get audit trail for a specific user"""
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Try database first
            if self.db_session:
                async with self.db_session() as session:
                    result = await session.execute(
                        select(AIAuditLog)
                        .where(and_(
                            AIAuditLog.user_id == user_id,
                            AIAuditLog.timestamp >= start_date,
                            AIAuditLog.timestamp <= end_date
                        ))
                        .order_by(AIAuditLog.timestamp.desc())
                        .limit(limit)
                    )
                    logs = result.scalars().all()
                    return [self._log_to_dict(log) for log in logs]
            
            # Fallback to Redis/memory
            return await self._get_cached_audit_trail(user_id, start_date, end_date, limit)
            
        except Exception as e:
            print(f"❌ AI Audit Service: Failed to get audit trail: {e}")
            return []

    async def get_compliance_report(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None
    ) -> dict[str, Any]:
        """Generate compliance report"""
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=7)
            if not end_date:
                end_date = datetime.utcnow()
            
            report = {
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "summary": {
                    "total_interactions": 0,
                    "pii_detected": 0,
                    "safety_filtered": 0,
                    "rate_limited": 0,
                    "compliance_violations": 0
                },
                "providers": {},
                "security_events": [],
                "recommendations": []
            }
            
            if self.db_session:
                async with self.db_session() as session:
                    # Total interactions
                    result = await session.execute(
                        select(func.count(AIAuditLog.id))
                        .where(and_(
                            AIAuditLog.timestamp >= start_date,
                            AIAuditLog.timestamp <= end_date
                        ))
                    )
                    report["summary"]["total_interactions"] = result.scalar()
                    
                    # PII detection
                    result = await session.execute(
                        select(func.count(AIAuditLog.id))
                        .where(and_(
                            AIAuditLog.timestamp >= start_date,
                            AIAuditLog.timestamp <= end_date,
                            AIAuditLog.contains_pii == True
                        ))
                    )
                    report["summary"]["pii_detected"] = result.scalar()
                    
                    # Provider breakdown
                    result = await session.execute(
                        select(AIAuditLog.provider, func.count(AIAuditLog.id))
                        .where(and_(
                            AIAuditLog.timestamp >= start_date,
                            AIAuditLog.timestamp <= end_date
                        ))
                        .group_by(AIAuditLog.provider)
                    )
                    for provider, count in result.all():
                        report["providers"][provider] = count
            
            # Add recommendations
            report["recommendations"] = self._generate_compliance_recommendations(report)
            
            return report
            
        except Exception as e:
            print(f"❌ AI Audit Service: Failed to generate compliance report: {e}")
            return {"error": str(e)}

    async def cleanup_expired_logs(self) -> int:
        """Clean up expired audit logs based on retention policy"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.default_retention_days)
            deleted_count = 0
            
            if self.db_session:
                async with self.db_session() as session:
                    result = await session.execute(
                        select(AIAuditLog)
                        .where(or_(
                            AIAuditLog.retention_until < datetime.utcnow(),
                            and_(
                                AIAuditLog.retention_until.is_(None),
                                AIAuditLog.timestamp < cutoff_date
                            )
                        ))
                    )
                    expired_logs = result.scalars().all()
                    
                    for log in expired_logs:
                        await session.delete(log)
                        deleted_count += 1
                    
                    await session.commit()
            
            print(f"✅ AI Audit Service: Cleaned up {deleted_count} expired logs")
            return deleted_count
            
        except Exception as e:
            print(f"❌ AI Audit Service: Failed to cleanup logs: {e}")
            return 0

    def _hash_content(self, content: str) -> str:
        """Create SHA-256 hash of content for privacy"""
        if not content:
            return ""
        return hashlib.sha256(content.encode()).hexdigest()

    def _detect_pii(self, content: str) -> bool:
        """Detect potential PII in content"""
        if not content:
            return False
        
        import re
        for pattern in self.pii_patterns:
            if re.search(pattern, content):
                return True
        return False

    def _assess_compliance_level(self, entry: AuditEntry) -> ComplianceLevel:
        """Assess compliance level based on entry characteristics"""
        if entry.contains_pii:
            return ComplianceLevel.HIGH
        elif entry.safety_filtered or entry.rate_limited:
            return ComplianceLevel.MEDIUM
        else:
            return ComplianceLevel.LOW

    async def _store_audit_entry(self, entry: AuditEntry):
        """Store audit entry to database and cache"""
        try:
            # Store to database
            if self.db_session:
                async with self.db_session() as session:
                    log = AIAuditLog(
                        id=entry.id,
                        user_id=entry.user_id,
                        session_id=entry.session_id,
                        timestamp=entry.timestamp,
                        provider=entry.provider,
                        model=entry.model,
                        endpoint=f"{entry.provider}/{entry.model}",
                        request_hash=entry.prompt_hash,
                        response_hash=entry.response_hash,
                        status_code=entry.status_code,
                        response_time_ms=entry.response_time_ms,
                        prompt_length=entry.prompt_length,
                        response_length=entry.response_length,
                        contains_pii=entry.contains_pii,
                        safety_filtered=entry.safety_filtered,
                        tokens_used=entry.tokens_used,
                        estimated_cost=entry.estimated_cost,
                        rate_limited=entry.rate_limited,
                        ip_address=entry.ip_address,
                        user_agent=entry.user_agent,
                        compliance_flags=json.dumps(entry.compliance_flags or []),
                        security_events=json.dumps(entry.security_events or []),
                        audit_metadata=json.dumps(entry.metadata or {}),
                        retention_until=entry.timestamp + timedelta(days=self.default_retention_days)
                    )
                    session.add(log)
                    await session.commit()
            
            # Store to Redis cache
            if self.redis_client:
                await self.redis_client.setex(
                    f"audit:{entry.id}",
                    3600,  # 1 hour cache
                    json.dumps(asdict(entry), default=str)
                )
            else:
                # Memory fallback
                if len(self.memory_cache) >= self.cache_max_size:
                    # Remove oldest entry
                    oldest_key = min(self.memory_cache.keys())
                    del self.memory_cache[oldest_key]
                self.memory_cache[entry.id] = asdict(entry)
            
        except Exception as e:
            print(f"❌ AI Audit Service: Failed to store audit entry: {e}")

    async def _store_content(self, audit_id: str, prompt: str, response: str | None):
        """Store content securely with encryption"""
        try:
            # Truncate long content
            prompt_truncated = prompt[:self.max_content_length] if prompt else ""
            response_truncated = response[:self.max_content_length] if response else ""
            
            content_data = {
                "prompt": prompt_truncated,
                "response": response_truncated,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if self.redis_client:
                await self.redis_client.setex(
                    f"content:{audit_id}",
                    86400,  # 24 hours
                    json.dumps(content_data)
                )
            
        except Exception as e:
            print(f"❌ AI Audit Service: Failed to store content: {e}")

    async def _get_cached_audit_trail(self, user_id: str, start_date: datetime, end_date: datetime, limit: int) -> list[dict[str, Any]]:
        """Get audit trail from cache"""
        try:
            results = []
            
            if self.redis_client:
                # Scan for user audit entries
                cursor = 0
                while cursor != '0':
                    cursor, keys = await self.redis_client.scan(
                        cursor, match="audit:*", count=100
                    )
                    for key in keys:
                        data = await self.redis_client.get(key)
                        if data:
                            entry = json.loads(data)
                            if entry.get('user_id') == user_id:
                                results.append(entry)
            else:
                # Memory fallback
                for entry_data in self.memory_cache.values():
                    if entry_data.get('user_id') == user_id:
                        results.append(entry_data)
            
            # Filter by date and sort
            filtered_results = [
                r for r in results
                if start_date <= datetime.fromisoformat(r['timestamp']) <= end_date
            ]
            filtered_results.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return filtered_results[:limit]
            
        except Exception as e:
            print(f"❌ AI Audit Service: Failed to get cached audit trail: {e}")
            return []

    def _log_to_dict(self, log: AIAuditLog) -> dict[str, Any]:
        """Convert database log to dictionary"""
        return {
            "id": log.id,
            "user_id": log.user_id,
            "timestamp": log.timestamp.isoformat(),
            "provider": log.provider,
            "model": log.model,
            "status_code": log.status_code,
            "response_time_ms": log.response_time_ms,
            "contains_pii": log.contains_pii,
            "safety_filtered": log.safety_filtered,
            "tokens_used": log.tokens_used,
            "estimated_cost": log.estimated_cost,
            "rate_limited": log.rate_limited,
            "compliance_flags": json.loads(log.compliance_flags or "[]"),
            "security_events": json.loads(log.security_events or "[]"),
            "metadata": json.loads(log.audit_metadata or "{}")
        }

    def _generate_compliance_recommendations(self, report: dict[str, Any]) -> list[str]:
        """Generate compliance recommendations based on report data"""
        recommendations = []
        
        if report["summary"]["pii_detected"] > 0:
            recommendations.append("Consider implementing additional PII detection and masking")
        
        if report["summary"]["rate_limited"] > report["summary"]["total_interactions"] * 0.1:
            recommendations.append("High rate limiting detected - consider capacity planning")
        
        if report["summary"]["safety_filtered"] > 0:
            recommendations.append("Review safety filtering events for policy compliance")
        
        return recommendations

# Example usage and testing
if __name__ == "__main__":
    async def demo_audit_service():
        """Demonstrate AI audit service functionality"""
        print("🔍 AI Audit Service Demo")
        print("=" * 50)
        
        # Initialize service
        audit_service = AIAuditService()
        await audit_service.initialize()
        
        # Demo 1: Log AI interaction
        print("\n1. Logging AI Interaction")
        audit_id = await audit_service.log_ai_interaction(
            user_id="user123",
            provider="openai",
            model="gpt-4",
            prompt="What is machine learning?",
            response="Machine learning is a subset of AI...",
            session_id="session456",
            tokens_used=150,
            estimated_cost=0.003,
            response_time_ms=1200
        )
        print(f"✅ Logged interaction with ID: {audit_id}")
        
        # Demo 2: Log PII detection
        print("\n2. Logging PII Detection")
        pii_audit_id = await audit_service.log_ai_interaction(
            user_id="user123",
            provider="anthropic",
            model="claude-3",
            prompt="My SSN is 123-45-6789",
            response="I cannot process personal information.",
            safety_filtered=True
        )
        print(f"✅ Logged PII interaction with ID: {pii_audit_id}")
        
        # Demo 3: Log security event
        print("\n3. Logging Security Event")
        security_audit_id = await audit_service.log_security_event(
            user_id="user123",
            event_type="suspicious_activity",
            description="Multiple failed authentication attempts",
            severity=ComplianceLevel.HIGH
        )
        print(f"✅ Logged security event with ID: {security_audit_id}")
        
        # Demo 4: Get user audit trail
        print("\n4. Retrieving User Audit Trail")
        trail = await audit_service.get_user_audit_trail("user123", limit=10)
        print(f"✅ Retrieved {len(trail)} audit entries")
        
        # Demo 5: Generate compliance report
        print("\n5. Generating Compliance Report")
        report = await audit_service.get_compliance_report()
        print("✅ Compliance Report Generated:")
        print(f"   Total Interactions: {report['summary']['total_interactions']}")
        print(f"   PII Detected: {report['summary']['pii_detected']}")
        print(f"   Recommendations: {len(report['recommendations'])}")
        
        print("\n🎉 AI Audit Service Demo Complete!")
        print("All audit trail functionality operational!")

    # Run demo
    asyncio.run(demo_audit_service())
