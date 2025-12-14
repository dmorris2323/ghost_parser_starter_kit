# src/owl_fallback_router.py
"""
owl_fallback_router.py

Simple, deterministic provider routing + fallback chain.

This does NOT call external services.
It only selects an ordered plan that other code can use.

Why:
- We keep Phase 2 routing logic stable and testable
- Avoids "magic" behavior
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

DEFAULT_CHAIN = ["LOCAL_DUMMY", "LOCAL_SMALL", "REMOTE_PRIMARY", "REMOTE_FALLBACK"]


@dataclass
class RouteDecision:
    selected_chain: List[str]
    reason: str
    crisis_mode: bool
    allow_remote: bool


def decide_route(
    *,
    crisis_mode: bool,
    allow_remote: bool,
    preferred: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Returns a dict with a deterministic chain.
    - If crisis_mode: only local options.
    - If allow_remote False: only local options.
    """
    chain = preferred[:] if preferred else DEFAULT_CHAIN[:]

    if crisis_mode or not allow_remote:
        # hard cut to local options only
        chain = [c for c in chain if c.startswith("LOCAL")]
        reason = "CRISIS_MODE" if crisis_mode else "REMOTE_DISABLED"
        if not chain:
            chain = ["LOCAL_DUMMY"]
        decision = RouteDecision(chain, reason, crisis_mode, allow_remote)
        return {
            "selected_chain": decision.selected_chain,
            "reason": decision.reason,
            "crisis_mode": decision.crisis_mode,
            "allow_remote": decision.allow_remote,
        }

    # Normal mode
    decision = RouteDecision(chain, "NORMAL", crisis_mode, allow_remote)
    return {
        "selected_chain": decision.selected_chain,
        "reason": decision.reason,
        "crisis_mode": decision.crisis_mode,
        "allow_remote": decision.allow_remote,
    }

