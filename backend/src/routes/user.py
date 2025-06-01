from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from src.database import SessionLocal
from src.models import User
from src.schemas.user import UserRegisterRequest, SuccessMessage
from src.utils import hash_password

router = APIRouter()

# Dependency to provide a DB session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register-user", response_model=SuccessMessage, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    # Check if a user with the same email already exists
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Create and store new user with hashed password
    new_user = User(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return SuccessMessage(message="User registration successful")
