from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import SessionLocal
from src.models import Developer
from src.utils import hash_password, verify_password
from src.auth import create_access_token
from src.dependencies.auth_guard import get_current_developer
from src.schemas.developer import (
    DeveloperRegisterRequest,
    DeveloperProfile,
)
from src.schemas.user import LoginRequest, SuccessMessage

router = APIRouter()

# Dependency to provide DB session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/login-developer", response_model=SuccessMessage)
def login_developer(payload: LoginRequest, db: Session = Depends(get_db)):
    developer = db.query(Developer).filter(
        Developer.email == payload.email).first()
    if not developer or not verify_password(payload.password, developer.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": developer.email})
    return SuccessMessage(message=access_token)


@router.get("/developer/me", response_model=DeveloperProfile)
def get_developer_me(current_dev: Developer = Depends(get_current_developer)):
    return current_dev
