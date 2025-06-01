# backend/src/routes/onboarding.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..models import Developer
from ..schemas.developer import OnboardingState
from ..dependencies.auth_guard import get_current_developer
from ..database import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/onboarding", response_model=OnboardingState)
def get_onboarding_status(current_dev: Developer = Depends(get_current_developer)):
    return current_dev.onboarding or {}


@router.post("/onboarding")
def update_onboarding(data: dict, current_dev: Developer = Depends(get_current_developer), db: Session = Depends(get_db)):
    current_dev.onboarding = data
    db.commit()
    return {"success": True, "message": "Onboarding updated"}
