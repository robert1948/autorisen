from sqlalchemy import create_engine
from sqlalchemy.schema import CreateTable
from backend.src.db.models import AuditEvent

engine = create_engine("sqlite:///:memory:")
print(CreateTable(AuditEvent.__table__).compile(engine))
