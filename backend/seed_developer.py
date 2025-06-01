# backend/seed_developer.py

from src.database import SessionLocal
from src.models import Developer
from src.utils import hash_password
from src.config.settings import settings
print("Using DATABASE_URL:", settings.DATABASE_URL)


db = SessionLocal()

# Check if developer already exists
existing = db.query(Developer).filter_by(email="dev@example.com").first()
if existing:
    print("Developer already exists.")
else:
    onboarding_template = {
        "upload_portfolio": False,
        "complete_profile": False,
        "connect_github": False,
        "start_agent_task": False
    }

    dev = Developer(
        full_name="Test Developer",
        company="Cape Craft",
        email="dev@example.com",
        portfolio="https://example.com",
        password=hash_password("test123"),
        onboarding=onboarding_template
    )
    db.add(dev)
    db.commit()
    print("Developer seeded successfully.")
