"""FinOps budget alerting — threshold-based warnings for AI spending.

Provides a lightweight check that emits structured log warnings and
stores alert state in-memory so the same threshold is not re-alerted
every request.  The admin cost endpoint exposes alert status.

Usage::

    from backend.src.modules.usage.budget_alerts import check_budget_thresholds

    alerts = check_budget_thresholds(spent=420.0, cap=500.0)
    # → [{"level": "warning", "pct": 80, "message": "..."}]
"""

from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timezone
from typing import Any

log = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────

# Thresholds as percentages of the budget cap.
ALERT_THRESHOLDS: list[dict[str, Any]] = [
    {"pct": 50, "level": "info", "label": "halfway"},
    {"pct": 80, "level": "warning", "label": "high"},
    {"pct": 95, "level": "critical", "label": "near_limit"},
]

# How often (seconds) the same threshold can re-fire.  Default: 1 hour.
_COOLDOWN_SECONDS = 3600


class BudgetAlertTracker:
    """Thread-safe in-memory tracker for budget alert state.

    Stores the last time each threshold was triggered so we don't
    spam logs/webhooks on every request.
    """

    def __init__(self, cooldown_seconds: int = _COOLDOWN_SECONDS) -> None:
        self._lock = threading.Lock()
        self._cooldown = cooldown_seconds
        # {pct: last_fired_timestamp}
        self._last_fired: dict[int, float] = {}

    def check(self, spent: float, cap: float) -> list[dict[str, Any]]:
        """Evaluate all thresholds and return newly-triggered alerts.

        Parameters
        ----------
        spent : float
            Current period spend in USD.
        cap : float
            The platform monthly budget cap in USD.

        Returns
        -------
        list[dict]
            Each dict has ``pct``, ``level``, ``label``, ``message``,
            ``spent_usd``, ``cap_usd``, ``timestamp``.
        """
        if cap <= 0:
            return []  # budget disabled

        now = time.monotonic()
        pct_used = (spent / cap) * 100
        alerts: list[dict[str, Any]] = []

        with self._lock:
            for threshold in ALERT_THRESHOLDS:
                thr_pct = threshold["pct"]
                if pct_used < thr_pct:
                    continue

                last = self._last_fired.get(thr_pct, 0)
                if (now - last) < self._cooldown:
                    continue  # still in cooldown

                self._last_fired[thr_pct] = now

                alert = {
                    "pct": thr_pct,
                    "level": threshold["level"],
                    "label": threshold["label"],
                    "spent_usd": round(spent, 2),
                    "cap_usd": cap,
                    "pct_used": round(pct_used, 1),
                    "message": (
                        f"AI budget alert: {pct_used:.0f}% used "
                        f"(${spent:.2f} / ${cap:.2f})"
                    ),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                alerts.append(alert)

                # Emit structured log at the appropriate level.
                if threshold["level"] == "critical":
                    log.critical(
                        "BUDGET ALERT [%s]: %s", threshold["label"], alert["message"]
                    )
                elif threshold["level"] == "warning":
                    log.warning(
                        "BUDGET ALERT [%s]: %s", threshold["label"], alert["message"]
                    )
                else:
                    log.info(
                        "BUDGET ALERT [%s]: %s", threshold["label"], alert["message"]
                    )

        return alerts

    def reset(self) -> None:
        """Clear alert state (e.g. at billing period rollover)."""
        with self._lock:
            self._last_fired.clear()

    @property
    def status(self) -> dict[str, Any]:
        """Current alert state for admin visibility."""
        with self._lock:
            return {
                "thresholds": [
                    {"pct": t["pct"], "level": t["level"], "label": t["label"]}
                    for t in ALERT_THRESHOLDS
                ],
                "fired": {
                    pct: ts for pct, ts in self._last_fired.items()
                },
                "cooldown_seconds": self._cooldown,
            }


# Module-level singleton
budget_tracker = BudgetAlertTracker()


def check_budget_thresholds(spent: float, cap: float) -> list[dict[str, Any]]:
    """Convenience wrapper around the module singleton."""
    return budget_tracker.check(spent, cap)
