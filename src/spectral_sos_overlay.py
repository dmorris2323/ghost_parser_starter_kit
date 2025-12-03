"""
spectral_sos_overlay.py
-----------------------

Builds a Spectral SOS overlay bundle for the GUI and CLI.

Outputs:
  - In-memory dict (build_sos_overlay)
  - JSON file at src/gui_sos_overlay.json (export_sos_overlay)
"""

from pathlib import Path
from datetime import datetime, timezone
import json

# Local imports – all exist in your src/ tree
from profile_config import get_active_profile
from spectral_owl.threat_memory import load_events
from spectral_owl.threat_memory_summary import build_summary as build_threat_summary

# Try to learn which AI provider is active, but fail gracefully
def _get_ai_provider_info():
    # Default
    info = {
        "provider": "unknown",
        "mode": "unknown",
    }

    # Try llm_phase2_adapter (Phase 2 AI-Independence)
    try:
        from llm_phase2_adapter import get_active_provider_key  # type: ignore[attr-defined]
        try:
            key = get_active_provider_key()
        except TypeError:
            # If implementation takes no args vs args, still handle
            key = get_active_provider_key  # pragma: no cover
        info["provider"] = str(key)
        info["mode"] = "phase2_adapter"
        return info
    except Exception:
        pass

    # Try llm_config fallback
    try:
        from llm_config import get_active_provider  # type: ignore[attr-defined]
        key = get_active_provider()
        info["provider"] = str(key)
        info["mode"] = "llm_config"
        return info
    except Exception:
        pass

    return info


def _load_critical_alerts():
    """
    Load basic alert stats from critical_alerts.csv if present.
    Returns a dict with count and a few recent alerts.
    """
    path = Path(__file__).parent / "critical_alerts.csv"
    if not path.exists():
        return {"count": 0, "recent": []}

    lines = path.read_text().strip().split("\n")
    if len(lines) <= 1:
        return {"count": 0, "recent": []}

    header = lines[0].split(",")
    rows = [dict(zip(header, row.split(","))) for row in lines[1:] if row.strip()]

    # Last 5 alerts
    recent = rows[-5:]
    return {
        "count": len(rows),
        "recent": recent,
    }


def _load_threat_memory_stats():
    """
    Summarize threat_memory.csv into simple stats for the overlay.
    """
    data_dir = Path(__file__).parent / "data"
    path = data_dir / "threat_memory.csv"
    if not path.exists():
        return {
            "total_events": 0,
            "recent_sample": [],
        }

    lines = path.read_text().strip().split("\n")
    if len(lines) <= 1:
        return {
            "total_events": 0,
            "recent_sample": [],
        }

    header = lines[0].split(",")
    rows = [dict(zip(header, row.split(","))) for row in lines[1:] if row.strip()]

    return {
        "total_events": len(rows),
        "recent_sample": rows[-5:],
    }


def build_sos_overlay():
    """
    Build the full SOS overlay bundle as a dict.
    This is what the GUI will show in the SOS panel.
    """
    profile = get_active_profile()
    ai_info = _get_ai_provider_info()
    alerts = _load_critical_alerts()
    threat_mem = _load_threat_memory_stats()
    threat_text = build_threat_summary()

    bundle = {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "profile": {
            "key": getattr(profile, "key", getattr(profile, "name", "unknown")),
            "display_name": getattr(profile, "display_name", "Unknown Profile"),
            "description": getattr(profile, "description", ""),
        },
        "ai_engine": ai_info,
        "alerts": alerts,
        "threat_memory": threat_mem,
        "threat_summary_text": threat_text,
    }

    return bundle


def export_sos_overlay():
    """
    Build the SOS overlay bundle and write it to gui_sos_overlay.json
    so the GUI can load it.

    Returns a small status dict for CLI display.
    """
    bundle = build_sos_overlay()
    out_path = Path(__file__).parent / "gui_sos_overlay.json"
    out_path.write_text(json.dumps(bundle, indent=2))

    return {
        "status": "written",
        "file": str(out_path),
        "timestamp": bundle["timestamp"],
    }


if __name__ == "__main__":
    result = export_sos_overlay()
    print(result)

