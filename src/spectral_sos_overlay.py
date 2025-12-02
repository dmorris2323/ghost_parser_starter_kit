"""
spectral_sos_overlay.py — Spectral Owl Situation Overlay (S.O.S.)

Creates a unified operational overlay for GUI use:
- Threat memory snapshot
- Critical alerts summary
- Top fusion scores
- Active profile metadata
- AI engine (Phase-2 provider) metadata
"""

import json
import os
from pathlib import Path
import csv
from datetime import datetime

from spectral_owl.threat_memory_summary import build_summary as threat_summary
from profile_config import get_active_profile

BASE = Path(__file__).resolve().parent
OUTFILE = BASE / "gui_sos_overlay.json"


# -------------------------------------------------------------------
# Provider Resolution (Phase 2 – robust, no-crash)
# -------------------------------------------------------------------

def _fallback_provider() -> str:
    """
    Fallback provider resolution:
    - Try environment variable GLL_LLM_PROVIDER
    - Otherwise return 'unknown'
    """
    return os.environ.get("GLL_LLM_PROVIDER", "unknown")


try:
    # Try to import from your Phase-2 adapter if it exposes this helper.
    from llm_phase2_adapter import get_active_provider as _adapter_get_active_provider  # type: ignore

    def get_active_provider() -> str:
        try:
            return _adapter_get_active_provider()
        except Exception:
            return _fallback_provider()

except ImportError:
    # Adapter does not expose get_active_provider; use fallback only.
    def get_active_provider() -> str:
        return _fallback_provider()


# -------------------------------------------------------------------
# Load critical alerts
# -------------------------------------------------------------------

def load_critical_alerts():
    p = BASE / "critical_alerts.csv"
    if not p.exists():
        return []
    rows = []
    with p.open() as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    # Only top 5 for the overlay
    return rows[:5]


# -------------------------------------------------------------------
# Load top fusion scores
# -------------------------------------------------------------------

def load_top_scores():
    p = BASE / "scored_output.csv"
    if not p.exists():
        return []
    rows = []
    with p.open() as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                row["score"] = float(row.get("score", 0))
                rows.append(row)
            except Exception:
                # Skip rows with invalid score
                continue

    rows = sorted(rows, key=lambda x: x["score"], reverse=True)
    return rows[:5]


# -------------------------------------------------------------------
# Build S.O.S. Overlay
# -------------------------------------------------------------------

def build_sos_overlay():
    """
    Build the Spectral Owl Situation Overlay and write it to gui_sos_overlay.json.
    Structure:

    {
      "timestamp": "...Z",
      "active_profile": { "key": "...", "display_name": "..." },
      "ai_engine": { "provider": "..." },
      "threat_memory_summary": "...",
      "critical_alerts": [...],
      "top_scores": [...]
    }
    """
    profile = get_active_profile()
    provider = get_active_provider()

    out = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "active_profile": {
            "key": getattr(profile, "key", "unknown"),
            "display_name": getattr(profile, "display_name", "Unknown Profile"),
        },
        "ai_engine": {
            "provider": provider
        },
        "threat_memory_summary": threat_summary(),
        "critical_alerts": load_critical_alerts(),
        "top_scores": load_top_scores(),
    }

    OUTFILE.write_text(json.dumps(out, indent=2))
    return {"status": "ok", "file": str(OUTFILE)}


if __name__ == "__main__":
    print(build_sos_overlay())

