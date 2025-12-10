"""
golden_dome_daily_watch.py — Golden Dome Daily Watch
----------------------------------------------------
Nuclear-focused daily watch product combining:

  • Nuclear readiness snapshot (Golden Dome)
  • Drift status
  • Fusion trust score
  • Temporal forecast (next 6 hours)

Outputs:
  - src/docs/golden_dome_daily_watch.json
  - src/docs/golden_dome_daily_watch.txt
"""

from pathlib import Path
from datetime import datetime, timezone
import json

from golden_dome_snapshot import build_snapshot
from golden_dome_drift import compute_drift
from fusion_trust import compute_trust
from fusion_temporal_forecast import forecast_next_6h

BASE = Path(__file__).resolve().parent.parent  # /parser_starter_kit
SRC = BASE / "src"
DOCS = SRC / "docs"

OUT_JSON = DOCS / "golden_dome_daily_watch.json"
OUT_TXT = DOCS / "golden_dome_daily_watch.txt"


def build_daily_watch() -> dict:
    """Build the Golden Dome Daily Watch bundle and return a summary dict."""
    DOCS.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).isoformat()

    snapshot = build_snapshot()
    drift = compute_drift()
    trust = compute_trust()
    temporal = forecast_next_6h()

    payload = {
        "generated_at": ts,
        "nuclear_snapshot": snapshot,
        "drift": drift,
        "fusion_trust": trust,
        "temporal_forecast": temporal,
    }

    # Write JSON payload
    OUT_JSON.write_text(json.dumps(payload, indent=2))

    # Write human-readable text report
    lines = [
        "=== GOLDEN DOME DAILY WATCH ===",
        f"Generated at (UTC): {ts}",
        "",
        ">> Nuclear Readiness Snapshot",
        json.dumps(snapshot, indent=2),
        "",
        ">> Drift Status",
        json.dumps(drift, indent=2),
        "",
        ">> Fusion Trust",
        json.dumps(trust, indent=2),
        "",
        ">> Temporal Forecast (Next 6 Hours)",
        json.dumps(temporal, indent=2),
        "",
        "Note: This product is for situational awareness and rapid commander briefings.",
    ]
    OUT_TXT.write_text("\n".join(lines))

    return {
        "generated_at": ts,
        "json_path": str(OUT_JSON),
        "text_path": str(OUT_TXT),
        "readiness": snapshot.get("readiness_level", snapshot.get("status", "UNKNOWN")),
    }


if __name__ == "__main__":
    out = build_daily_watch()
    print(json.dumps(out, indent=2))

