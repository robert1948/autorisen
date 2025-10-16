from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import time
import hmac, hashlib, base64

router = APIRouter(prefix="/chatkit", tags=["chatkit"])

class TokenReq(BaseModel):
    user_id: str | None = None

def _make_client_secret(workflow_id: str, user_id: str) -> str:
    """
    Minimal demo token: HMAC-sign a short-lived payload.
    Replace this with the official ChatKit session creation if you prefer.
    """
    secret = os.environ.get("OPENAI_API_KEY")
    if not secret:
        raise RuntimeError("OPENAI_API_KEY missing")
    # rotate roughly every minute to keep it short-lived
    payload = f"{workflow_id}:{user_id}:{int(time.time()/60)}"
    sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest()
    token = f"{payload}.{base64.urlsafe_b64encode(sig).decode()}"
    return base64.urlsafe_b64encode(token.encode()).decode()

@router.post("/token")
def issue_token(req: TokenReq):
    wf = os.environ.get("CHATKIT_WORKFLOW_ID")
    if not wf:
        raise HTTPException(500, "CHATKIT_WORKFLOW_ID not set")
    user = req.user_id or "anon"
    return {"client_secret": _make_client_secret(wf, user)}
