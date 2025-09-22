# backend/app/routes/auth_db.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, LoginIn
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.crud import user as crud_user
import os

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = crud_user.get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud_user.create_user(db, email=payload.email, name=payload.name, password_plain=payload.password)
    return user


# Register DB-backed login only when not in development to avoid conflicting
# with the dev token-based login (which is mounted in development).
if os.getenv("ENVIRONMENT", "development") != "development":
    @router.post("/login")
    def login(payload: LoginIn, db: Session = Depends(get_db)):
        user = crud_user.get_user_by_email(db, payload.email)
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        access = create_access_token(user.id)
        refresh, jti, exp = create_refresh_token(user.id)
        return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
