import os
import uuid
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

## In-memory SQLite handles isolation, remove file cleanup

# sqlalchemy imports

## Use in-memory SQLite for isolated tests with shared StaticPool
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import app and database objects
from app.database import Base, get_db
from app.main import app
from app.models import Conversation, ConversationMessage

# Create only the tables needed for FAQ agent tests
Conversation.__table__.drop(bind=engine, checkfirst=True)
ConversationMessage.__table__.drop(bind=engine, checkfirst=True)
Conversation.__table__.create(bind=engine, checkfirst=True)
ConversationMessage.__table__.create(bind=engine, checkfirst=True)

# Override dependency


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_faq_creates_conversation_and_persists_messages():
    payload = {"user_id": 42, "question": "What is CapeControl?"}
    response = client.post("/api/agents/faq", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert data["answer"]
    assert "timestamp" in data

    # Verify records in DB
    db = TestingSessionLocal()
    conv = db.query(Conversation).filter_by(id=data["conversation_id"]).first()
    assert conv is not None
    # Should have two messages: question and answer
    msgs = db.query(ConversationMessage).filter_by(conversation_id=conv.id).all()
    assert len(msgs) == 2
    assert msgs[0].content == payload["question"]
    assert msgs[1].content == data["answer"]
    db.close()


def test_faq_with_existing_conversation_id():
    # Create initial conversation
    first = client.post("/api/agents/faq", json={"question": "Hi!"})
    conv_id = first.json()["conversation_id"]

    # Send follow-up using existing conv_id
    second_payload = {"conversation_id": conv_id, "question": "How does this work?"}
    second = client.post("/api/agents/faq", json=second_payload)
    assert second.status_code == 200
    data2 = second.json()
    assert data2["conversation_id"] == conv_id

    # Verify total messages count in DB increased
    db = TestingSessionLocal()
    msgs = db.query(ConversationMessage).filter_by(conversation_id=conv_id).all()
    assert len(msgs) == 4  # two from first, two from second
    db.close()
