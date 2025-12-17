from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


# ============================================
# DEMO LOCK — READ ONLY / NO MUTATION GUARANTEE
# ============================================

DEMO_LOCK_ENABLED = True  # 🔒 MASTER SWITCH


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_demo_locked() -> bool:
    """
    Returns True if demo mode is active.
    Demo mode enforces read-only, no mutation behavior.
    """
    return bool(DEMO_LOCK_ENABLED)


def demo_lock_banner() -> str:
    """
    Standard banner injected into demo artifacts.
    """
    return (
        "DEMO MODE ACTIVE — READ ONLY\n"
        "No baselines updated. No training. No mutation.\n"
        "Assessment is probabilistic and bounded; operator judgment applies."
    )


def enforce_demo_lock(context: str) -> Dict[str, Any]:
    """
    Standardized envelope injected into demo outputs.
    """
    return {
        "demo_lock": True,
        "demo_context": str(context),
        "demo_generated_at_utc": _utc_now_iso(),
        "demo_notes": [
            "Demo lock enforced.",
            "System is operating in read-only mode.",
            "Outputs are deterministic and safe for briefing."
        ],
    }

