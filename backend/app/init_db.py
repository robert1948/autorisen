# backend/app/init_db.py

from app.database import engine
from app.models import Base

# Import modules that declare additional tables so they're registered in Base.metadata
# Optional integrations tables (CRMLead, POSOrder)
try:
    import app.models.integrations  # noqa: F401
except Exception as e:  # pragma: no cover
    print(f"Warning: failed to import integrations models: {e}")

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
