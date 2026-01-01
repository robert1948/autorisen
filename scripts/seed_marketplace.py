import sys
import os
import uuid
from datetime import datetime
from sqlalchemy import create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.src.db import models
from backend.src.db.session import DB_URL


def seed_marketplace():
    """
    Seeds the database with initial marketplace agents.
    Creates a system user if it doesn't exist, and then creates or updates
    default agents (Cape Support Bot, Onboarding Guide, Data Analyst).
    """
    print(f"Connecting to database: {DB_URL}")
    engine = create_engine(DB_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # 1. Create a System User if not exists
        system_email = "system@capecontrol.com"
        system_user = (
            db.query(models.User).filter(models.User.email == system_email).first()
        )

        if not system_user:
            print("Creating System User...")
            system_user = models.User(
                id=str(uuid.uuid4()),
                email=system_email,
                first_name="System",
                last_name="Admin",
                hashed_password="hashed_placeholder",  # Not used for login
                role="Admin",
                is_active=True,
                is_email_verified=True,
            )
            db.add(system_user)
            db.commit()
            db.refresh(system_user)
        else:
            print("System User already exists.")

        # 2. Define Agents to Seed
        agents_data = [
            {
                "name": "Cape Support Bot",
                "slug": "cape-support-bot",
                "description": "Your 24/7 customer support assistant. Handles FAQs, ticket creation, and basic troubleshooting.",
                "category": "communication",
                "manifest": {
                    "name": "Cape Support Bot",
                    "description": "AI Support Agent",
                    "category": "communication",
                    "author": "CapeControl",
                    "capabilities": ["chat", "ticket_management"],
                    "placement": "support_widget",
                    "tags": ["support", "chat", "helpdesk"],
                },
            },
            {
                "name": "Onboarding Guide",
                "slug": "onboarding-guide",
                "description": "Helps new users navigate the platform and set up their first workspace.",
                "category": "productivity",
                "manifest": {
                    "name": "Onboarding Guide",
                    "description": "User Onboarding Assistant",
                    "category": "productivity",
                    "author": "CapeControl",
                    "capabilities": ["chat", "walkthrough"],
                    "placement": "dashboard",
                    "tags": ["onboarding", "tutorial", "guide"],
                },
            },
            {
                "name": "Data Analyst",
                "slug": "data-analyst",
                "description": "Analyzes your business data and generates actionable insights and reports.",
                "category": "analytics",
                "manifest": {
                    "name": "Data Analyst",
                    "description": "Business Intelligence Agent",
                    "category": "analytics",
                    "author": "CapeControl",
                    "capabilities": ["data_analysis", "reporting"],
                    "placement": "analytics",
                    "tags": ["data", "analytics", "bi"],
                },
            },
        ]

        for agent_data in agents_data:
            agent = (
                db.query(models.Agent)
                .filter(models.Agent.slug == agent_data["slug"])
                .first()
            )

            if not agent:
                print(f"Creating Agent: {agent_data['name']}")
                agent = models.Agent(
                    id=str(uuid.uuid4()),
                    owner_id=system_user.id,
                    name=agent_data["name"],
                    slug=agent_data["slug"],
                    description=agent_data["description"],
                    visibility="public",
                )
                db.add(agent)
                db.commit()
                db.refresh(agent)

                # Create Initial Version
                version = models.AgentVersion(
                    id=str(uuid.uuid4()),
                    agent_id=agent.id,
                    version="1.0.0",
                    manifest=agent_data["manifest"],
                    status="published",
                    published_at=datetime.now(),
                )
                db.add(version)
                db.commit()
            else:
                print(f"Updating Agent: {agent_data['name']}")
                # Update existing agent details
                agent.name = agent_data["name"]
                agent.description = agent_data["description"]

                # Find published version or create new one
                version = (
                    db.query(models.AgentVersion)
                    .filter(
                        models.AgentVersion.agent_id == agent.id,
                        models.AgentVersion.status == "published",
                    )
                    .first()
                )

                if version:
                    version.manifest = agent_data["manifest"]
                else:
                    version = models.AgentVersion(
                        id=str(uuid.uuid4()),
                        agent_id=agent.id,
                        version="1.0.0",
                        manifest=agent_data["manifest"],
                        status="published",
                        published_at=datetime.now(),
                    )
                    db.add(version)

                db.commit()

        print("Marketplace seeding completed successfully!")

    except SQLAlchemyError as e:
        print(f"Database error seeding marketplace: {e}")
        db.rollback()
    except Exception as e:
        print(f"Unexpected error seeding marketplace: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_marketplace()
