# backend/app/services/providers/demo_cape_ai.py
from typing import Dict, Any
from app.services.ai_provider import AIProvider

class DemoCapeAIService(AIProvider):
    async def answer_faq(self, question: str, meta: Dict[str, Any] | None = None) -> str:
        return f"(demo) FAQ answer to: {question}"

    async def schedule(self, command: str, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        # naive parse stub
        return {"status": "scheduled", "command": command, "when": "TBD (demo)"}
