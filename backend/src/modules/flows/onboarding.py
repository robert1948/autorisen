"""Helpers for onboarding checklist state."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.modules.flows.constants import DEFAULT_ONBOARDING_TASKS


def ensure_checklist(
    db: Session,
    *,
    user_id: str,
    thread_id: Optional[str] = None,
) -> models.OnboardingChecklist:
    checklist = db.scalar(
        select(models.OnboardingChecklist).where(
            models.OnboardingChecklist.user_id == user_id
        )
    )
    if checklist is None:
        tasks = {
            task["id"]: {"label": task["label"], "done": False}
            for task in DEFAULT_ONBOARDING_TASKS
        }
        checklist = models.OnboardingChecklist(
            user_id=user_id,
            thread_id=thread_id or "ui-onboarding",
            tasks=tasks,
        )
        db.add(checklist)
        db.commit()
        db.refresh(checklist)
    elif thread_id and checklist.thread_id != thread_id:
        checklist.thread_id = thread_id
        db.add(checklist)
        db.commit()
        db.refresh(checklist)
    return checklist


def update_task(
    db: Session,
    *,
    user_id: str,
    thread_id: Optional[str],
    task_id: str,
    done: bool,
    label: Optional[str] = None,
) -> models.OnboardingChecklist:
    checklist = ensure_checklist(db, user_id=user_id, thread_id=thread_id)
    tasks = checklist.tasks or {
        task["id"]: {"label": task["label"], "done": False}
        for task in DEFAULT_ONBOARDING_TASKS
    }
    current = tasks.get(task_id, {})
    task_label = label or current.get("label") or task_id.replace("_", " ").title()
    tasks[task_id] = {"label": task_label, "done": done}
    checklist.tasks = tasks
    db.add(checklist)
    db.commit()
    db.refresh(checklist)
    return checklist


def serialize_checklist(checklist: models.OnboardingChecklist) -> dict:
    tasks = checklist.tasks or {}
    completed = sum(1 for task in tasks.values() if task.get("done"))
    total = len(tasks)
    return {
        "tasks": tasks,
        "summary": {
            "completed": completed,
            "total": total,
        },
    }
