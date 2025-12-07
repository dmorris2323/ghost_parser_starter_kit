"""
mission_brief_html.py — Build HTML mission brief from text + tiles.

Placeholders supported in docs/mission_brief_template.html:

  {{BRIEF_TEXT}}
  {{GOLDEN_DOME_TILE}}
  {{GOLDEN_DOME_DRIFT}}
  {{CRISIS_MODE}}
  {{OPERATOR}}
"""

from pathlib import Path
import json

from daily_mission_brief import build_mission_brief
from golden_dome_tile import build_golden_dome_tile
from golden_dome_drift import compute_drift
from sensor_reliability import compute_reliability_all
from crisis_mode_flag import status as crisis_status
from operator_identity import get_identity

TEMPLATE_PATH = Path("docs/mission_brief_template.html")
OUTPUT_PATH = Path("docs/daily_mission_brief.html")


def get_template_html() -> str:
    if TEMPLATE_PATH.exists():
        return TEMPLATE_PATH.read_text()

    # Minimal default template if none exists
    return """<html>
<head>
<title>Daily Mission Brief</title>
</head>
<body>
<h1>Mission Brief — Ghost Lantern Labs</h1>

<p>Operator: {{OPERATOR}}</p>
<p>Crisis Mode: {{CRISIS_MODE}}</p>

<pre>{{BRIEF_TEXT}}</pre>

<h2>Golden Dome Readiness</h2>
<pre>{{GOLDEN_DOME_TILE}}</pre>

<h2>Golden Dome Drift</h2>
<pre>{{GOLDEN_DOME_DRIFT}}</pre>

</body>
</html>
"""


def write_daily_brief() -> str:
    brief_text = build_mission_brief()

    # Sensor stats for tile
    reliability_summary = {}
    try:
        reliability_summary = compute_reliability_all()
    except Exception:
        reliability_summary = {}

    avg_rel = 90.0
    if isinstance(reliability_summary, dict):
        avg_rel = reliability_summary.get("avg_reliability", 90.0) or 90.0

    # Drift / agreement
    drift = {}
    try:
        drift = compute_drift()
    except Exception:
        drift = {}

    agreement = 90.0
    if isinstance(drift, dict):
        agreement = drift.get("agreement_score", 90.0) or 90.0

    # Build Golden Dome tile
    profile_name = "Active Profile"
    tile = build_golden_dome_tile(
        reliability=avg_rel,
        agreement=agreement,
        profile=profile_name,
    )

    html = get_template_html()
    html = html.replace("{{BRIEF_TEXT}}", brief_text)
    html = html.replace("{{GOLDEN_DOME_TILE}}", json.dumps(tile, indent=2))
    html = html.replace(
        "{{GOLDEN_DOME_DRIFT}}",
        json.dumps(drift, indent=2) if isinstance(drift, (dict, list)) else str(drift),
    )
    html = html.replace("{{CRISIS_MODE}}", crisis_status())
    html = html.replace("{{OPERATOR}}", get_identity())

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html)
    return str(OUTPUT_PATH)


if __name__ == "__main__":
    path = write_daily_brief()
    print(f"Daily mission brief HTML written to: {path}")

