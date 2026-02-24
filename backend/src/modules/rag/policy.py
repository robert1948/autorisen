"""RAG module — Unsupported policy enforcement.

Provides middleware-level and service-level enforcement of the
'unsupported' policy: when an AI response is not backed by any
approved document, it can be refused, flagged, or allowed.

This module is the authoritative policy gate. Other agents can
call ``enforce_policy()`` to check whether their responses should
be flagged or withheld.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, Optional

log = logging.getLogger(__name__)

# The banner injected when policy == "flag" and the response is ungrounded
UNSUPPORTED_BANNER = (
    "⚠️ UNSUPPORTED — This answer is not backed by any approved "
    "document in your library. Verify independently before acting on it."
)

# Refusal message when policy == "refuse" and the response is ungrounded
REFUSAL_MESSAGE = (
    "This query could not be answered because no approved documents "
    "match. Under the current unsupported policy, answers without "
    "document backing are not permitted. Please upload relevant "
    "documents or adjust the query."
)


class PolicyDecision:
    """Outcome of an unsupported-policy evaluation."""

    __slots__ = ("allowed", "flagged", "refused", "reason", "banner")

    def __init__(
        self,
        *,
        allowed: bool = True,
        flagged: bool = False,
        refused: bool = False,
        reason: Optional[str] = None,
        banner: Optional[str] = None,
    ):
        self.allowed = allowed
        self.flagged = flagged
        self.refused = refused
        self.reason = reason
        self.banner = banner

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "flagged": self.flagged,
            "refused": self.refused,
            "reason": self.reason,
            "banner": self.banner,
        }


def enforce_policy(
    *,
    grounded: bool,
    policy: str = "flag",
    response_text: Optional[str] = None,
) -> PolicyDecision:
    """Evaluate the unsupported policy against a grounding check.

    Args:
        grounded: True if the response has at least one approved-doc citation.
        policy: One of ``"refuse"``, ``"flag"``, ``"allow"``.
        response_text: The AI response text (used to check if banner is
            already present when policy is ``"flag"``).

    Returns:
        A ``PolicyDecision`` describing what action to take.
    """
    if grounded:
        return PolicyDecision(allowed=True)

    policy = policy.lower().strip()

    if policy == "refuse":
        log.info("Unsupported policy REFUSE: blocking ungrounded response")
        return PolicyDecision(
            allowed=False,
            refused=True,
            reason=REFUSAL_MESSAGE,
        )

    if policy == "flag":
        # Check if the banner is already present
        already_flagged = (
            response_text
            and UNSUPPORTED_BANNER.split("—")[0].strip() in response_text
        )
        log.info(
            "Unsupported policy FLAG: %s",
            "already flagged" if already_flagged else "adding banner",
        )
        return PolicyDecision(
            allowed=True,
            flagged=True,
            banner=None if already_flagged else UNSUPPORTED_BANNER,
        )

    # policy == "allow" or unknown
    return PolicyDecision(allowed=True)


def apply_policy_to_response(
    response_text: str,
    decision: PolicyDecision,
) -> Optional[str]:
    """Apply a policy decision to a response string.

    Returns:
        The (possibly modified) response, or ``None`` if refused.
    """
    if decision.refused:
        return None

    if decision.banner and decision.flagged:
        return f"{decision.banner}\n\n{response_text}"

    return response_text


def check_response_grounding(
    response: Dict[str, Any],
) -> bool:
    """Check whether a generic agent response dict appears grounded.

    Looks for evidence/citation markers that the RAG pipeline would have
    attached. Non-RAG agent responses are considered grounded by default
    (they don't claim document backing).
    """
    # RAG responses have explicit grounded flag
    if "grounded" in response:
        return bool(response["grounded"])

    # Evidence trace present with citations
    evidence = response.get("evidence")
    if isinstance(evidence, dict):
        citations = evidence.get("citations", [])
        return len(citations) > 0

    # Non-RAG agents: considered grounded by default
    # (they don't operate under the approved-doc-only contract)
    return True
