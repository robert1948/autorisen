# backend/src/modules/auth/routes.py (or wherever)
from fastapi import APIRouter, Body, Depends, status
from .schemas import RegisterStep1In, RegisterStep2In, LoginIn

# ...

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register/step1", status_code=status.HTTP_201_CREATED)
def register_step1(payload: RegisterStep1In = Body(...)):
    # ... use payload.first_name, payload.email, etc.
    ...


@router.post("/register/step2")
def register_step2(
    payload: RegisterStep2In = Body(...),
    # if you read temp token from Authorization header:
    # current=Depends(get_temp_session)
): ...


@router.post("/login")
def login(payload: LoginIn = Body(...)): ...
