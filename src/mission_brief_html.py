"""
mission_brief_html.py — Build Daily Mission Brief HTML
------------------------------------------------------
Takes the text brief + analytics (trust, OSL, latency, nuclear readiness,
temporal forecast, adversary patterns) and renders docs/daily_mission_brief.html
using docs/mission_brief_template.html.
"""

import json
from pathlib import Path

from daily_mission_brief import write_daily_brief
from fusion_trust import compute_trust
from operator_safety_layer import compute_osl
from sensor_latency import compute_latency_report
from golden_dome_snapshot import build_snapshot
from fusion_temporal_forecast import forecast_next_6h
from adversary_pattern_engine import analyze_patterns

BASE = Path(__file__).resolve().parent.parent  # /parser_starter_kit
SRC = BASE / "src"
DOCS = SRC / "docs"

TEMPLATE = DOCS / "mission_brief_template.html"
OUTFILE = DOCS / "daily_mission_brief.html"
TEXT_BRIEF_FILE = DOCS / "daily_mission_brief.txt"


def build_html_brief() -> str:
    """
    Build the HTML mission brief and return the output path as string.
    """

    # Ensure text brief exists & is current
    write_daily_brief()

    if not TEMPLATE.exists():
        raise FileNotFoundError(f"Template not found: {TEMPLATE}")

    template_html = TEMPLATE.read_text()

    # Load the text brief
    if TEXT_BRIEF_FILE.exists():
        brief_text = TEXT_BRIEF_FILE.read_text()
    else:
        brief_text = "No daily_mission_brief.txt found. Run daily_mission_brief.py."

    # Compute analytics blocks
    trust = compute_trust()
    osl = compute_osl()
    latency = compute_latency_report()
    nuclear = build_snapshot()
    temporal = forecast_next_6h()
    patterns = analyze_patterns()

    # Replace placeholders (no-op if not present in template)
    html = template_html
    html = html.replace("{{BRIEF_TEXT}}", brief_text)
    html = html.replace("{{FUSION_TRUST}}", json.dumps(trust, indent=2))
    html = html.replace("{{OSL}}", json.dumps(osl, indent=2))
    html = html.replace("{{SENSOR_LATENCY}}", json.dumps(latency, indent=2))
    html = html.replace("{{NUCLEAR_READINESS}}", json.dumps(nuclear, indent=2))
    html = html.replace("{{TEMPORAL_FORECAST}}", json.dumps(temporal, indent=2))
    html = html.replace("{{ADV_PATTERNS}}", json.dumps(patterns, indent=2))

    OUTFILE.write_text(html)
    return str(OUTFILE)


def write_daily_brief() -> str:
    """
    Backward-compatible name some older calls expect.
    Just builds the HTML and returns the path.
    """
    return build_html_brief()


if __name__ == "__main__":
    out = build_html_brief()
    print(out)

