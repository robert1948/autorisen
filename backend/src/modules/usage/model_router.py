"""Intelligent model router — select the cheapest model that fits the task.

Classifies incoming prompts by complexity and routes them to the
appropriate model tier:

- **simple** → Haiku (FAQ, greetings, short factual lookups)
- **moderate** → Haiku (most analysis, summarisation, coding help)
- **complex** → Sonnet (multi-step reasoning, planning, long-form generation)

The classification is intentionally lightweight (regex heuristics + length
checks) so it adds near-zero latency.  A future Phase-3 upgrade can swap
in a small fine-tuned classifier.

Usage::

    from backend.src.modules.usage.model_router import select_model

    model = select_model(user_prompt)
"""

from __future__ import annotations

import logging
import os
import re

log = logging.getLogger(__name__)

# ── Model tiers ───────────────────────────────────────────────────────────────
# Overridable via environment variables so operators can pin models.

BUDGET_MODEL = os.getenv("BUDGET_MODEL", "claude-3-5-haiku-20241022")
PREMIUM_MODEL = os.getenv("PREMIUM_MODEL", "claude-sonnet-4-20250514")

# ── Complexity signals ────────────────────────────────────────────────────────

# Phrases / patterns that indicate the user needs deep, multi-step reasoning.
_COMPLEX_PATTERNS: list[re.Pattern[str]] = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"compare\s+and\s+contrast",
        r"step[\s-]by[\s-]step",
        r"multi[\s-]?step",
        r"detailed\s+analysis",
        r"comprehensive\s+(plan|report|review|audit)",
        r"design\s+(a|an|the)\s+(system|architecture|pipeline)",
        r"create\s+(a|an)\s+(business\s+plan|strategy|roadmap)",
        r"evaluate\s+(the\s+)?pros?\s+and\s+cons?",
        r"write\s+(a|an)\s+(full|complete|detailed)",
        r"generate\s+(a|an)\s+(full|detailed)",
        r"in[-\s]depth",
        r"long[\s-]form",
        r"scenario\s+analysis",
        r"risk\s+assessment",
        r"financial\s+model",
        r"refactor\s+(the\s+)?(entire|whole|full)",
    ]
]

# Phrases that indicate trivial / FAQ-style queries.
_SIMPLE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"^(hi|hello|hey|thanks|thank\s+you|ok|okay)\b",
        r"what\s+is\s+(your|the)\s+",
        r"^how\s+do\s+I\s+(log\s?in|sign\s?up|reset|cancel|upgrade)",
        r"^(yes|no|sure|got\s+it)\s*[.!?]*$",
        r"what\s+plan\s+am\s+I\s+on",
        r"^(show|list|get)\s+(my|the)\s+",
    ]
]

# ── Length thresholds ─────────────────────────────────────────────────────────
# Very short prompts are almost certainly simple.
_SHORT_THRESHOLD = 80  # chars
# Very long prompts are more likely to need deeper reasoning.
_LONG_THRESHOLD = 2000  # chars


# ── Public API ────────────────────────────────────────────────────────────────

def classify_complexity(text: str) -> str:
    """Classify a prompt as ``simple``, ``moderate``, or ``complex``.

    This is a fast heuristic — no LLM call involved.
    """
    text = (text or "").strip()
    if not text:
        return "simple"

    # Short one-liners are almost always simple.
    if len(text) < _SHORT_THRESHOLD:
        for pat in _SIMPLE_PATTERNS:
            if pat.search(text):
                return "simple"

    # Check for known complexity signals.
    for pat in _COMPLEX_PATTERNS:
        if pat.search(text):
            return "complex"

    # Length-based heuristic for remaining cases.
    if len(text) > _LONG_THRESHOLD:
        return "complex"

    return "moderate"


def select_model(
    text: str,
    *,
    force_model: str | None = None,
) -> str:
    """Choose the appropriate model for *text*.

    Parameters
    ----------
    text:
        The user prompt (or the last user message in a conversation).
    force_model:
        If set, bypass routing and return this model.  Useful when the
        caller already knows the model (e.g. from an env-var override).

    Returns
    -------
    str
        A model identifier suitable for the Anthropic ``model`` parameter.
    """
    if force_model:
        return force_model

    complexity = classify_complexity(text)

    if complexity == "complex":
        log.debug("Model router → PREMIUM (%s) for complex prompt", PREMIUM_MODEL)
        return PREMIUM_MODEL

    # Both "simple" and "moderate" go to the budget model.
    log.debug("Model router → BUDGET (%s) for %s prompt", BUDGET_MODEL, complexity)
    return BUDGET_MODEL
