from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import SessionLocal
from src.models import Developer
from src.schemas.developer import (
    DeveloperRegisterRequest,
    DeveloperProfile,
    DeveloperLoginRequest,
    OnboardingUpdateRequest  # ✅ Correct and single import
)
from src.schemas.user import SuccessMessage, Token
from src.utils import hash_password, verify_password, create_access_token
from src.dependencies.auth_guard import get_current_developer

router = APIRouter()


# Dependency to provide DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register-developer", response_model=SuccessMessage)
def register_developer(data: DeveloperRegisterRequest, db: Session = Depends(get_db)):
    if db.query(Developer).filter_by(email=data.email).first():
        raise HTTPException(status_code=400, detail="Developer already exists")

    onboarding_template = {
        "upload_portfolio": False,
        "complete_profile": False,
        "connect_github": False,
        "start_agent_task": False
    }

    developer = Developer(
        full_name=data.full_name,
        company=data.company,
        email=data.email,
        portfolio=data.portfolio,
        password=hash_password(data.password),
        onboarding=onboarding_template
    )
    db.add(developer)
    db.commit()
    db.refresh(developer)
    return {"success": True, "message": "Developer registered successfully"}


@router.post("/login-developer", response_model=Token)
def login_developer(data: DeveloperLoginRequest, db: Session = Depends(get_db)):
    developer = db.query(Developer).filter_by(email=data.email).first()
    if not developer or not verify_password(data.password, developer.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": developer.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/developer/me", response_model=DeveloperProfile)
def get_developer_profile(current_developer: Developer = Depends(get_current_developer)):
    return current_developer


@router.patch("/developer/onboarding", response_model=SuccessMessage)
def update_onboarding(
    payload: OnboardingUpdateRequest,
    db: Session = Depends(get_db),
    current_developer: Developer = Depends(get_current_developer)
):
    current_developer.onboarding = payload.onboarding
    db.commit()
    return {"success": True, "message": "Onboarding status updated"}
