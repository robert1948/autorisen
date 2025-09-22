from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.user import User
from app.core.security import hash_password


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, email: str, name: str, password_plain: str) -> User:
    user = User(
        email=email,
        name=name,
        password_hash=hash_password(password_plain),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def set_password_changed(db: Session, user: User):
    user.password_changed_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
