"""Constants for flow orchestration."""

from __future__ import annotations

DEFAULT_ONBOARDING_TASKS = [
    {"id": "invite_team", "label": "Invite core teammates"},
    {"id": "connect_data_sources", "label": "Connect your data sources"},
    {"id": "configure_notifications", "label": "Configure notifications"},
    {"id": "launch_first_run", "label": "Launch your first CapeAI run"},
]
