"""
Provider stubs for CRM and POS integrations.
External calls are disabled by default; enable with env flags if needed.
"""

from __future__ import annotations

import os
from typing import Any, Dict


class IntegrationsProvider:
    def __init__(self) -> None:
        self.enable_external = os.getenv("ENABLE_EXTERNAL_INTEGRATIONS", "0") == "1"

    async def send_crm_lead(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enable_external:
            return {"sent": False, "reason": "disabled", "echo": payload}
        # Placeholder for real external CRM call
        return {"sent": True, "provider": "mock-crm", "id": "crm_demo_123"}

    async def send_pos_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enable_external:
            return {"sent": False, "reason": "disabled", "echo": payload}
        # Placeholder for real external POS call
        return {"sent": True, "provider": "mock-pos", "id": "pos_demo_123"}


def get_integrations_provider() -> IntegrationsProvider:
    return IntegrationsProvider()
