"""Onboarding API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_current_user

from . import schemas, service

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.get("/status", response_model=schemas.OnboardingStatusResponse)
def get_status(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> schemas.OnboardingStatusResponse:
    payload = service.get_status(db, current_user)
    return schemas.OnboardingStatusResponse(**payload)


@router.post("/start", response_model=schemas.OnboardingStartResponse)
def start_onboarding(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> schemas.OnboardingStartResponse:
    payload = service.start_onboarding(db, current_user)
    return schemas.OnboardingStartResponse(**payload)


@router.patch("/profile", response_model=schemas.OnboardingProfileResponse)
def update_profile(
    payload: schemas.OnboardingProfileUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> schemas.OnboardingProfileResponse:
    data = payload.dict(exclude_unset=True)
    merged_profile: dict[str, object] = {}
    if payload.profile:
        merged_profile.update(payload.profile)
    for key in ("first_name", "last_name", "company_name", "role"):
        value = data.get(key)
        if value is not None:
            merged_profile[key] = value
    result = service.update_profile(db, current_user, merged_profile)
    return schemas.OnboardingProfileResponse(**result)


@router.get("/steps", response_model=list[schemas.OnboardingStepOut])
def list_steps(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> list[schemas.OnboardingStepOut]:
    steps = service.get_steps(db)
    session = service.get_latest_session(db, current_user.id)
    states = []
    if session:
        states = service.ensure_step_state(db, session.id, steps)
    payload_steps = service.serialize_steps(steps, states)
    return [schemas.OnboardingStepOut(**step) for step in payload_steps]


@router.post("/steps/{step_key}/complete", response_model=schemas.OnboardingStepActionResponse)
def complete_step(
    step_key: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> schemas.OnboardingStepActionResponse:
    try:
        payload = service.set_step_status(db, current_user, step_key, "completed")
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    steps = payload["steps"]
    step_payload = next((step for step in steps if step["step_key"] == step_key), None)
    if not step_payload:
        raise HTTPException(status_code=404, detail="Step not found")
    return schemas.OnboardingStepActionResponse(
        step=schemas.OnboardingStepOut(**step_payload),
        progress=payload["progress"],
    )


@router.post("/steps/{step_key}/skip", response_model=schemas.OnboardingStepActionResponse)
def skip_step(
    step_key: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> schemas.OnboardingStepActionResponse:
    try:
        payload = service.set_step_status(db, current_user, step_key, "skipped")
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    steps = payload["steps"]
    step_payload = next((step for step in steps if step["step_key"] == step_key), None)
    if not step_payload:
        raise HTTPException(status_code=404, detail="Step not found")
    return schemas.OnboardingStepActionResponse(
        step=schemas.OnboardingStepOut(**step_payload),
        progress=payload["progress"],
    )


@router.post("/trust/{key}/ack", response_model=schemas.TrustAckResponse)
def acknowledge_trust(
    key: str,
    payload: schemas.TrustAckPayload | None = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> schemas.TrustAckResponse:
    ack = service.acknowledge_trust(
        db,
        current_user,
        key,
        metadata=payload.metadata if payload else None,
    )
    return schemas.TrustAckResponse(key=ack.key, acknowledged_at=ack.acknowledged_at)


@router.post("/complete", response_model=schemas.OnboardingCompleteResponse)
def complete_onboarding(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> schemas.OnboardingCompleteResponse:
    payload = service.complete_onboarding(db, current_user)
    session = payload["session"]
    return schemas.OnboardingCompleteResponse(
        session=schemas.OnboardingSessionOut.from_orm(session),
        progress=payload["progress"],
    )
