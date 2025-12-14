# src/crisis_mode_flag.py
"""
crisis_mode_flag.py

Single source of truth for "CRISIS MODE" (ON/OFF).
Used by validation harness, operator safety layer, and Spectral Owl degraded mode.

Design goals:
- Zero dependencies on other modules (avoid circular imports).
- File-backed state for persistence across runs.
- Stable function names so other modules can import safely.

State file:
- docs/integrity/crisis_mode.json
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

CRISIS_DIR = Path("docs") / "integrity"
CRISIS_PATH = CRISIS_DIR / "crisis_mode.json"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _default_state() -> Dict[str, Any]:
    return {
        "crisis_mode": "OFF",
        "updated_at": _utc_now_iso(),
        "reason": "default",
        "operator": "system",
    }


def read_crisis_mode() -> Dict[str, Any]:
    """
    Returns a dict:
      { crisis_mode: "ON"|"OFF", updated_at, reason, operator }

    Never raises. If file missing/corrupt -> returns default.
    """
    try:
        if not CRISIS_PATH.exists():
            return _default_state()
        raw = json.loads(CRISIS_PATH.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return _default_state()
        cm = str(raw.get("crisis_mode", "OFF")).upper().strip()
        if cm not in {"ON", "OFF"}:
            cm = "OFF"
        return {
            "crisis_mode": cm,
            "updated_at": str(raw.get("updated_at", _utc_now_iso())),
            "reason": str(raw.get("reason", "unspecified")),
            "operator": str(raw.get("operator", "unknown")),
        }
    except Exception:
        return _default_state()


def is_crisis_mode() -> bool:
    """Convenience boolean."""
    return read_crisis_mode().get("crisis_mode") == "ON"


def set_crisis_mode(*, enabled: bool, reason: str = "operator_action", operator: str = "operator") -> Dict[str, Any]:
    """
    Sets crisis mode and persists it.
    Returns the written dict.
    """
    state = {
        "crisis_mode": "ON" if enabled else "OFF",
        "updated_at": _utc_now_iso(),
        "reason": reason.strip() if reason else "operator_action",
        "operator": operator.strip() if operator else "operator",
    }
    _safe_mkdir(CRISIS_DIR)
    CRISIS_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return state


# Backward-compatible aliases (some modules may look for these)
def get_crisis_mode() -> Dict[str, Any]:
    return read_crisis_mode()


def crisis_mode_status() -> Dict[str, Any]:
    return read_crisis_mode()

