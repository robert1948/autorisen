# backend/app/init_db.py

from app.models import Base
from app.database import engine

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
