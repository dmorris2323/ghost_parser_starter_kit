"""
mission_brief_html.py

Builds the daily HTML mission brief for Ghost Lantern Labs.

- Pulls text brief from daily_mission_brief.build_mission_brief()
- Loads the active profile (for display badge)
- Builds a Golden Dome readiness tile
- Optionally injects:
    - Cross-sensor report
    - Reliability report
    - Minimap text
    - SOS overlay JSON

Writes:
    src/docs/daily_mission_brief.html
    using template:
    src/docs/mission_brief_template.html
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from daily_mission_brief import build_mission_brief
from profile_config import get_active_profile
from golden_dome_tile import build_golden_dome_tile


BASE = Path(__file__).resolve().parent
DOCS_DIR = BASE / "docs"
TEMPLATE_PATH = DOCS_DIR / "mission_brief_template.html"
OUTPUT_PATH = DOCS_DIR / "daily_mission_brief.html"

SYSTEM_METRICS_JSON = BASE / "system_metrics.json"
CROSS_SENSOR_REPORT = DOCS_DIR / "cross_sensor_report.txt"
RELIABILITY_REPORT = DOCS_DIR / "reliability_report.txt"
MINIMAP_TEXT = BASE / "minimap.txt"
SOS_OVERLAY_JSON = BASE / "gui_sos_overlay.json"


def _ensure_default_template() -> None:
    """
    Make sure we have a simple HTML template with all placeholders.
    Safe to call every run.
    """
    if TEMPLATE_PATH.exists():
        return

    TEMPLATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    TEMPLATE_PATH.write_text(
        """<html>
<head>
  <title>Daily Mission Brief – Ghost Lantern Labs</title>
</head>
<body>
  <h1>Mission Brief — Ghost Lantern Labs</h1>
  <h3>Active Profile: {{ACTIVE_PROFILE}}</h3>

  <h2>Text Brief</h2>
  <pre>{{BRIEF_TEXT}}</pre>

  <h2>Golden Dome Readiness</h2>
  <pre>{{GOLDEN_DOME_TILE}}</pre>

  <h2>Sensor Reliability Report</h2>
  <pre>{{RELIABILITY_REPORT}}</pre>

  <h2>Cross-Sensor Validation</h2>
  <pre>{{CROSS_SENSOR}}</pre>

  <h2>Fusion Minimap</h2>
  <pre>{{MINIMAP}}</pre>

  <h2>SOS Overlay</h2>
  <pre>{{SOS_OVERLAY}}</pre>
</body>
</html>
""",
        encoding="utf-8",
    )


def _read_or_default(path: Path, default_msg: str) -> str:
    if path.exists():
        try:
            return path.read_text(encoding="utf-8")
        except Exception:
            return f"{default_msg} (file unreadable)"
    return default_msg


def _load_metrics_fallback() -> Dict[str, Any]:
    """
    Try to load system metrics for more realistic Golden Dome stats.
    If anything fails, return safe defaults.
    """
    default = {
        "avg_reliability": 92.5,
        "agreement_score": 88.0,
    }

    if not SYSTEM_METRICS_JSON.exists():
        return default

    try:
        raw = json.loads(SYSTEM_METRICS_JSON.read_text(encoding="utf-8"))
    except Exception:
        return default

    avg_rel = raw.get("avg_reliability", default["avg_reliability"])
    agree = raw.get("agreement_score", default["agreement_score"])

    try:
        avg_rel = float(avg_rel)
    except Exception:
        avg_rel = default["avg_reliability"]

    try:
        agree = float(agree)
    except Exception:
        agree = default["agreement_score"]

    return {
        "avg_reliability": avg_rel,
        "agreement_score": agree,
    }


def write_daily_brief() -> str:
    """
    Build and write the HTML daily mission brief.

    Returns:
        str: path to OUTPUT_PATH
    """
    _ensure_default_template()

    # 1) Get the core text brief (string only)
    brief_text = build_mission_brief()
    if not isinstance(brief_text, str):
        brief_text = str(brief_text)

    # 2) Active profile display name
    profile = get_active_profile()
    display_name = getattr(profile, "display_name", None) or getattr(
        profile, "name", None
    )
    if not display_name:
        display_name = str(profile)

    # 3) Metrics for Golden Dome tile
    stats = _load_metrics_fallback()
    avg_rel = stats["avg_reliability"]
    agreement = stats["agreement_score"]

    dome_tile = build_golden_dome_tile(
        reliability=avg_rel,
        agreement=agreement,
        profile=display_name,
    )

    # 4) Optional embedded reports
    cross_sensor_text = _read_or_default(
        CROSS_SENSOR_REPORT,
        "No cross-sensor report found. Run CLI Option 25.",
    )
    reliability_text = _read_or_default(
        RELIABILITY_REPORT,
        "No reliability report found. Run CLI Option 24.",
    )
    minimap_text = _read_or_default(
        MINIMAP_TEXT,
        "No minimap data found. Run fusion_minimap or CLI Option 19.",
    )
    sos_overlay_text = _read_or_default(
        SOS_OVERLAY_JSON,
        "No SOS overlay found. Run spectral_sos_overlay or CLI Option 20.",
    )

    # If SOS overlay is JSON, pretty-print it for readability.
    if sos_overlay_text and sos_overlay_text.startswith("{"):
        try:
            sos_obj = json.loads(sos_overlay_text)
            sos_overlay_text = json.dumps(sos_obj, indent=2)
        except Exception:
            # keep raw text
            pass

    # 5) Load template and inject placeholders
    html = TEMPLATE_PATH.read_text(encoding="utf-8")

    html = html.replace("{{BRIEF_TEXT}}", brief_text)
    html = html.replace("{{ACTIVE_PROFILE}}", display_name)
    html = html.replace(
        "{{GOLDEN_DOME_TILE}}", json.dumps(dome_tile, indent=2)
    )
    html = html.replace("{{CROSS_SENSOR}}", cross_sensor_text)
    html = html.replace("{{RELIABILITY_REPORT}}", reliability_text)
    html = html.replace("{{MINIMAP}}", minimap_text)
    html = html.replace("{{SOS_OVERLAY}}", sos_overlay_text)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    return str(OUTPUT_PATH)


if __name__ == "__main__":
    print(write_daily_brief())

