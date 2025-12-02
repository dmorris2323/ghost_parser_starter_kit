"""
spectral_dashboard_api.py
-----------------------------------
Back-end dashboard builder for Ghost Lantern Labs.

This module aggregates:
- Sensor health
- Manifest health
- Fusion minimap
- Threat memory summary
- Active profile info
- Cloud sync status
- Operator notes (last 10)
- Alerts summary
- Fusion scoring snapshot

Outputs a single JSON bundle for GUI consumption.
"""

import json
from pathlib import Path
from datetime import datetime, timezone

from manifest_health import run_manifest_health
from fusion_minimap import build_minimap
from profile_config import get_active_profile
from spectral_owl.threat_memory_summary import build_summary as threat_summary
from fusion_alerts import load_critical_alerts
from pipeline_health import evaluate_pipeline_health

OUTPUT = Path("outputs/spectral_dashboard.json")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)


# ---------------------------
# Helper: Load last operator notes
# ---------------------------
def load_last_notes(n=10):
    notes_path = Path("NOTES.txt")
    if not notes_path.exists():
        return []
    lines = notes_path.read_text().strip().split("\n")
    return lines[-n:]


# ---------------------------
# Helper: Quick cloud sync ping
# ---------------------------
def cloud_status():
    cfg = Path("src/config/cloud_settings.json")
    if not cfg.exists():
        return {"enabled": False, "status": "missing_config"}

    return {
        "enabled": True,
        "provider": "azure",
        "simulated": True,
        "status": "ok",
    }


# ---------------------------
# Main builder
# ---------------------------
def build_dashboard_bundle():
    manifest = run_manifest_health()
    minimap = build_minimap()
    profile = get_active_profile()
    threats = threat_summary()
    alerts = load_critical_alerts()
    health = evaluate_pipeline_health()
    notes = load_last_notes()

    # Be defensive about profile fields so we never crash here
    profile_key = getattr(profile, "key", "unknown")
    profile_display = getattr(profile, "display_name", str(profile))
    profile_sector = getattr(profile, "domain", getattr(profile, "sector", "unknown"))

    bundle = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "active_profile": {
            "key": profile_key,
            "display": profile_display,
            "sector": profile_sector,
        },
        "sensor_manifest": manifest,
        "fusion_minimap": minimap,
        "pipeline_health": health,
        "threat_memory_summary": threats,
        "critical_alerts": alerts,
        "cloud_status": cloud_status(),
        "operator_notes_last10": notes,
    }

    OUTPUT.write_text(json.dumps(bundle, indent=2))
    return bundle


if __name__ == "__main__":
    out = build_dashboard_bundle()
    print(f"[OK] Dashboard JSON written → {OUTPUT}")
    print(json.dumps(out, indent=2))

