# src/owl_degraded_mode.py
"""
owl_degraded_mode.py

Deterministic degraded-mode responses for Spectral Owl.
This module guarantees:
- No crashes
- No network
- No external provider assumptions
- A stable dict contract for UI / CLI / validation

Use this when:
- crisis_mode_flag is ON
- a provider fails
- the system gates are not GREEN
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class DegradedContext:
    context: str
    reason: str
    gate_status: str = "UNKNOWN"  # e.g. GREEN/YELLOW/RED/UNKNOWN
    difficulty: str = "UNKNOWN"
    pattern_id: Optional[str] = None


def build_degraded_response(
    *,
    prompt: str,
    ctx: DegradedContext,
    observations: Optional[List[str]] = None,
    recommended_actions: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Stable contract returned to callers.
    """
    observations = observations or []
    recommended_actions = recommended_actions or []

    # Keep it deterministic, predictable, and safe.
    summary = (
        f"Degraded Mode active for '{ctx.context}'. "
        f"Reason: {ctx.reason}. "
        f"Gate: {ctx.gate_status}. "
        f"Difficulty: {ctx.difficulty}."
    )

    if ctx.pattern_id:
        summary += f" Pattern: {ctx.pattern_id}."

    return {
        "mode": "DEGRADED",
        "generated_at": _utc_now_iso(),
        "context": {
            "context": ctx.context,
            "reason": ctx.reason,
            "gate_status": ctx.gate_status,
            "difficulty": ctx.difficulty,
            "pattern_id": ctx.pattern_id,
        },
        "prompt_echo": prompt[:4000],  # bounded
        "output": {
            "summary": summary,
            "observations": observations[:20],
            "recommended_actions": recommended_actions[:20],
            "confidence": 0.35,  # intentionally capped in degraded mode
        },
        "safety": {
            "offline": True,
            "no_external_calls": True,
            "deterministic": True,
        },
    }

