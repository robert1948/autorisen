# backend/src/auth/jwt_utils.py
import os
from datetime import datetime, timedelta, timezone

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

SECRET_KEY = os.getenv("SECRET_KEY", "dev_only_change_me")
ALGORITHM = "HS256"


def create_access_token(subject: str, minutes: int = 60, **claims) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=minutes)).timestamp()),
        **claims,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError as e:
        raise ValueError("expired") from e
    except InvalidTokenError as e:
        raise ValueError("invalid") from e
