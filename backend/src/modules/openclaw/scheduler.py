"""Automated daily aggregation scheduler for OpenClaw telemetry rollups."""

from __future__ import annotations

import logging
import os
import threading
import time
from datetime import datetime, timezone
from typing import Optional

from backend.src.db.session import SessionLocal
from backend.src.modules.openclaw.service import OpenClawService

log = logging.getLogger("openclaw.scheduler")

ENABLED = os.getenv("OPENCLAW_AGGREGATION_SCHEDULER_ENABLED", "0").lower() in {
    "1",
    "true",
    "yes",
}
INTERVAL_HOURS = int(os.getenv("OPENCLAW_AGGREGATION_INTERVAL_HOURS", "24"))
DAYS_BACK = int(os.getenv("OPENCLAW_AGGREGATION_DAYS_BACK", "1"))

_scheduler_thread: Optional[threading.Thread] = None
_stop_event = threading.Event()
_service = OpenClawService()


def _run_once() -> None:
    db = SessionLocal()
    try:
        result = _service.run_daily_aggregation(
            db,
            actor_id=None,
            days_back=DAYS_BACK,
            dry_run=False,
        )
        log.info(
            "OpenClaw aggregation run complete: days_back=%d rollups=%d at=%s",
            result.days_back,
            len(result.rollups),
            datetime.now(timezone.utc).isoformat(),
        )
    except Exception:
        log.exception("OpenClaw aggregation run failed")
    finally:
        db.close()


def _scheduler_loop() -> None:
    log.info(
        "OpenClaw aggregation scheduler started (interval=%dh days_back=%d)",
        INTERVAL_HOURS,
        DAYS_BACK,
    )
    _stop_event.wait(30)

    while not _stop_event.is_set():
        _run_once()
        for _ in range(max(1, INTERVAL_HOURS * 360)):
            if _stop_event.is_set():
                break
            time.sleep(10)

    log.info("OpenClaw aggregation scheduler stopped")


def start_scheduler() -> None:
    global _scheduler_thread
    if not ENABLED:
        log.info(
            "OpenClaw aggregation scheduler disabled (OPENCLAW_AGGREGATION_SCHEDULER_ENABLED != 1)"
        )
        return
    if _scheduler_thread and _scheduler_thread.is_alive():
        log.warning("OpenClaw aggregation scheduler already running")
        return

    _stop_event.clear()
    _scheduler_thread = threading.Thread(
        target=_scheduler_loop,
        name="openclaw-aggregation-scheduler",
        daemon=True,
    )
    _scheduler_thread.start()
    log.info("OpenClaw aggregation scheduler thread launched")


def stop_scheduler() -> None:
    _stop_event.set()
    if _scheduler_thread:
        _scheduler_thread.join(timeout=15)
        log.info("OpenClaw aggregation scheduler thread joined")
