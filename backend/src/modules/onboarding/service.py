"""Onboarding business logic."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.src.db import models


def _utcnow() -> datetime:
    return datetime.utcnow()


def get_active_session(db: Session, user_id: str) -> Optional[models.OnboardingSession]:
    stmt = (
        select(models.OnboardingSession)
        .where(
            models.OnboardingSession.user_id == user_id,
            models.OnboardingSession.status == "active",
        )
        .order_by(models.OnboardingSession.started_at.desc())
    )
    return db.scalars(stmt).first()


def get_latest_session(db: Session, user_id: str) -> Optional[models.OnboardingSession]:
    active = get_active_session(db, user_id)
    if active:
        return active
    stmt = (
        select(models.OnboardingSession)
        .where(models.OnboardingSession.user_id == user_id)
        .order_by(models.OnboardingSession.started_at.desc())
    )
    return db.scalars(stmt).first()


DEFAULT_STEPS: list[tuple[str, str, int, bool]] = [
    ("welcome", "Welcome", 1, True),
    ("profile", "Confirm your profile", 2, True),
    ("checklist_connect_data", "Connect data", 3, False),
    ("checklist_create_first_project", "Create your first project", 4, False),
    ("checklist_invite_teammate", "Invite a teammate", 5, False),
    ("checklist_run_first_agent", "Run your first agent", 6, False),
    ("trust_privacy", "Review privacy commitments", 7, True),
    ("trust_security", "Review security commitments", 8, True),
    ("complete", "Complete onboarding", 9, True),
]


def _ensure_step_catalog(db: Session) -> None:
    if db.scalars(select(models.OnboardingStep)).first():
        return
    for step_key, title, order_index, required in DEFAULT_STEPS:
        db.add(
            models.OnboardingStep(
                step_key=step_key,
                title=title,
                order_index=order_index,
                required=required,
            )
        )
    db.commit()


def get_steps(db: Session) -> list[models.OnboardingStep]:
    _ensure_step_catalog(db)
    stmt = select(models.OnboardingStep).order_by(models.OnboardingStep.order_index)
    return db.scalars(stmt).all()


def ensure_step_state(
    db: Session,
    session_id: str,
    steps: list[models.OnboardingStep],
) -> list[models.UserOnboardingStepState]:
    existing = db.scalars(
        select(models.UserOnboardingStepState).where(
            models.UserOnboardingStepState.session_id == session_id
        )
    ).all()
    existing_keys = {state.step_key for state in existing}
    for step in steps:
        if step.step_key in existing_keys:
            continue
        db.add(
            models.UserOnboardingStepState(
                session_id=session_id,
                step_key=step.step_key,
                status="pending",
            )
        )
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        # Concurrent insert — just re-read
    return db.scalars(
        select(models.UserOnboardingStepState).where(
            models.UserOnboardingStepState.session_id == session_id
        )
    ).all()


def compute_progress(
    steps: list[models.OnboardingStep],
    states: list[models.UserOnboardingStepState],
) -> int:
    if not steps:
        return 0
    state_map = {state.step_key: state for state in states}
    required_steps = [step for step in steps if step.required]
    if not required_steps:
        return 0
    completed_required = sum(
        1
        for step in required_steps
        if state_map.get(step.step_key) and state_map[step.step_key].status == "completed"
    )
    return int((completed_required / len(required_steps)) * 100)


def log_event(
    db: Session,
    *,
    session_id: str,
    user_id: str,
    event_type: str,
    step_key: Optional[str] = None,
    payload: Optional[dict[str, Any]] = None,
) -> None:
    db.add(
        models.OnboardingEventLog(
            session_id=session_id,
            user_id=user_id,
            event_type=event_type,
            step_key=step_key,
            payload=payload,
        )
    )


def build_status_payload(
    session: Optional[models.OnboardingSession],
    steps: list[models.OnboardingStep],
    states: list[models.UserOnboardingStepState],
) -> dict[str, Any]:
    if not session:
        return {
            "session": None,
            "steps": [],
            "progress": 0,
        }
    return {
        "session": session,
        "steps": serialize_steps(steps, states),
        "progress": compute_progress(steps, states),
    }


def serialize_steps(
    steps: list[models.OnboardingStep],
    states: list[models.UserOnboardingStepState],
) -> list[dict[str, Any]]:
    state_map = {state.step_key: state for state in states}
    payload_steps: list[dict[str, Any]] = []
    for step in steps:
        state = state_map.get(step.step_key)
        payload_steps.append(
            {
                "step_key": step.step_key,
                "title": step.title,
                "order_index": step.order_index,
                "required": bool(step.required),
                "role_scope_json": step.role_scope_json,
                "state":
                {
                    "status": state.status,
                    "completed_at": state.completed_at,
                    "skipped_at": state.skipped_at,
                }
                if state
                else None,
            }
        )
    return payload_steps


def get_status(db: Session, user: models.User) -> dict[str, Any]:
    session = get_latest_session(db, user.id)
    if not session:
        return build_status_payload(None, [], [])
    steps = get_steps(db)
    states = ensure_step_state(db, session.id, steps)
    return build_status_payload(session, steps, states)


def start_onboarding(db: Session, user: models.User) -> dict[str, Any]:
    # Reuse existing session — prefer active, then fall back to latest (completed)
    session = get_active_session(db, user.id)
    if not session:
        # Check for a completed session first to avoid creating duplicates
        session = get_latest_session(db, user.id)
    if not session:
        session = models.OnboardingSession(
            user_id=user.id,
            status="active",
            onboarding_completed=False,
            last_step_key="welcome",
        )
        db.add(session)
        db.flush()
        log_event(db, session_id=session.id, user_id=user.id, event_type="start")
    steps = get_steps(db)
    states = ensure_step_state(db, session.id, steps)
    db.commit()
    db.refresh(session)
    return build_status_payload(session, steps, states)


def update_profile(
    db: Session,
    user: models.User,
    payload: dict[str, Any],
) -> dict[str, Any]:
    profile = db.scalar(
        select(models.UserProfile).where(models.UserProfile.user_id == user.id)
    )
    profile_data: dict[str, Any] = {}
    if profile and isinstance(profile.profile, dict):
        profile_data.update(profile.profile)
    profile_data.update(payload)
    if profile is None:
        profile = models.UserProfile(user_id=user.id, profile=profile_data)
        db.add(profile)
    else:
        profile.profile = profile_data
    if "first_name" in payload and payload["first_name"] is not None:
        user.first_name = str(payload["first_name"])
    if "last_name" in payload and payload["last_name"] is not None:
        user.last_name = str(payload["last_name"])
    if "company_name" in payload and payload["company_name"] is not None:
        user.company_name = str(payload["company_name"])
    if "role" in payload and payload["role"] is not None:
        user.role = str(payload["role"])
    session = get_active_session(db, user.id)
    if not session:
        session = models.OnboardingSession(
            user_id=user.id,
            status="active",
            onboarding_completed=False,
            last_step_key="welcome",
        )
        db.add(session)
        db.flush()
    log_event(
        db,
        session_id=session.id,
        user_id=user.id,
        event_type="profile_update",
        payload=payload,
    )
    db.commit()
    db.refresh(profile)
    return {"profile": profile.profile}


def set_step_status(
    db: Session,
    user: models.User,
    step_key: str,
    status: str,
) -> dict[str, Any]:
    session = get_active_session(db, user.id)
    if not session:
        session = models.OnboardingSession(
            user_id=user.id,
            status="active",
            onboarding_completed=False,
            last_step_key="welcome",
        )
        db.add(session)
        db.flush()
    step = db.scalar(
        select(models.OnboardingStep).where(models.OnboardingStep.step_key == step_key)
    )
    if not step:
        raise ValueError("Step not found")
    state = db.scalar(
        select(models.UserOnboardingStepState).where(
            models.UserOnboardingStepState.session_id == session.id,
            models.UserOnboardingStepState.step_key == step_key,
        )
    )
    if not state:
        state = models.UserOnboardingStepState(
            session_id=session.id,
            step_key=step_key,
            status="pending",
        )
        db.add(state)
        try:
            db.flush()
        except IntegrityError:
            db.rollback()
            # Row was inserted concurrently — refetch
            state = db.scalar(
                select(models.UserOnboardingStepState).where(
                    models.UserOnboardingStepState.session_id == session.id,
                    models.UserOnboardingStepState.step_key == step_key,
                )
            )
            if not state:  # pragma: no cover — defensive
                raise ValueError("Step state could not be resolved")
            # Re-fetch the session too since we rolled back
            session = get_active_session(db, user.id)
            if not session:
                raise ValueError("Session lost after rollback")
            step = db.scalar(
                select(models.OnboardingStep).where(models.OnboardingStep.step_key == step_key)
            )
            if not step:
                raise ValueError("Step not found")
    state.status = status
    if status == "completed":
        state.completed_at = _utcnow()
        state.skipped_at = None
    elif status == "skipped":
        state.skipped_at = _utcnow()
        state.completed_at = None
    session.last_step_key = step_key
    log_event(
        db,
        session_id=session.id,
        user_id=user.id,
        event_type=f"step_{status}",
        step_key=step_key,
    )
    steps = get_steps(db)
    states = ensure_step_state(db, session.id, steps)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Concurrent ensure_step_state collision — re-read and return
        steps = get_steps(db)
        session = get_active_session(db, user.id)
        if not session:
            raise ValueError("Session lost after commit retry")
        states = db.scalars(
            select(models.UserOnboardingStepState).where(
                models.UserOnboardingStepState.session_id == session.id
            )
        ).all()
    return build_status_payload(session, steps, states)


def get_next_step(db: Session, user: models.User) -> dict[str, Any]:
    session = get_active_session(db, user.id)
    if not session:
        session = models.OnboardingSession(
            user_id=user.id,
            status="active",
            onboarding_completed=False,
            last_step_key="welcome",
        )
        db.add(session)
        db.flush()
        log_event(db, session_id=session.id, user_id=user.id, event_type="start")

    steps = get_steps(db)
    states = ensure_step_state(db, session.id, steps)
    db.commit()

    state_map = {state.step_key: state for state in states}
    next_step = None
    for step in steps:
        if not step.required:
            continue
        state = state_map.get(step.step_key)
        if not state or state.status != "completed":
            next_step = step
            break
    payload_steps = serialize_steps(steps, states)
    step_payload = (
        next((item for item in payload_steps if item["step_key"] == next_step.step_key), None)
        if next_step
        else None
    )
    return {
        "step": step_payload,
        "progress": compute_progress(steps, states),
    }


def mark_step_blocked(
    db: Session,
    user: models.User,
    step_key: str,
    reason: str,
    notes: Optional[str] = None,
) -> dict[str, Any]:
    session = get_active_session(db, user.id)
    if not session:
        session = models.OnboardingSession(
            user_id=user.id,
            status="active",
            onboarding_completed=False,
            last_step_key="welcome",
        )
        db.add(session)
        db.flush()

    step = db.scalar(
        select(models.OnboardingStep).where(models.OnboardingStep.step_key == step_key)
    )
    if not step:
        raise ValueError("Step not found")

    state = db.scalar(
        select(models.UserOnboardingStepState).where(
            models.UserOnboardingStepState.session_id == session.id,
            models.UserOnboardingStepState.step_key == step_key,
        )
    )
    if not state:
        state = models.UserOnboardingStepState(
            session_id=session.id,
            step_key=step_key,
            status="pending",
        )
        db.add(state)

    state.status = "blocked"
    session.last_step_key = step_key
    log_event(
        db,
        session_id=session.id,
        user_id=user.id,
        event_type="step_blocked",
        step_key=step_key,
        payload={"reason": reason, "notes": notes},
    )

    steps = get_steps(db)
    states = ensure_step_state(db, session.id, steps)
    db.commit()
    payload_steps = serialize_steps(steps, states)
    step_payload = next((item for item in payload_steps if item["step_key"] == step_key), None)
    if not step_payload:
        raise ValueError("Step not found")
    return {
        "step": step_payload,
        "progress": compute_progress(steps, states),
    }


def acknowledge_trust(
    db: Session,
    user: models.User,
    key: str,
    metadata: Optional[dict[str, Any]] = None,
) -> models.TrustAcknowledgement:
    session = get_active_session(db, user.id)
    if not session:
        session = models.OnboardingSession(
            user_id=user.id,
            status="active",
            onboarding_completed=False,
            last_step_key="welcome",
        )
        db.add(session)
        db.flush()
    existing = db.scalar(
        select(models.TrustAcknowledgement).where(
            models.TrustAcknowledgement.user_id == user.id,
            models.TrustAcknowledgement.key == key,
        )
    )
    if existing:
        return existing
    ack = models.TrustAcknowledgement(
        session_id=session.id,
        user_id=user.id,
        key=key,
        metadata_json=metadata,
    )
    db.add(ack)
    log_event(
        db,
        session_id=session.id,
        user_id=user.id,
        event_type="trust_ack",
        step_key=key,
        payload=metadata,
    )
    db.commit()
    db.refresh(ack)
    return ack


def complete_onboarding(db: Session, user: models.User) -> dict[str, Any]:
    session = get_active_session(db, user.id)
    if not session:
        session = models.OnboardingSession(
            user_id=user.id,
            status="active",
            onboarding_completed=False,
            last_step_key="welcome",
        )
        db.add(session)
        db.flush()
    session.status = "completed"
    session.onboarding_completed = True
    session.completed_at = _utcnow()
    log_event(db, session_id=session.id, user_id=user.id, event_type="complete")
    steps = get_steps(db)
    states = ensure_step_state(db, session.id, steps)
    db.commit()
    return build_status_payload(session, steps, states)
