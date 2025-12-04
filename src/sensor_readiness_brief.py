"""
sensor_readiness_brief.py

Builds a consolidated sensor readiness brief including:

- Which sensors are enabled / disabled (manifest_health)
- Sensor profile info (warning/critical thresholds)
- Sensor drift prediction (sensor_drift_predictor)
- Reliability report (if generated previously)

Output is a plain-text brief consumed by:
  - daily_mission_brief.py
  - mission_brief_html.py
  - GUI sidebar
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from manifest_health import run_manifest_health
from sensor_profile_loader import load_profile
from sensor_drift_predictor import get_drift_scores

BASE = Path(__file__).parent
DOCS_DIR = BASE / "docs"


def _load_reliability_text() -> str:
    path = DOCS_DIR / "reliability_report.txt"
    if not path.exists():
        return "Reliability report not generated yet. Run sensor_reliability.py."
    try:
        return path.read_text().strip()
    except Exception:
        return "Reliability report present but could not be read."


def build_readiness_brief() -> str:
    mh = run_manifest_health()
    drift = get_drift_scores()
    reliability_text = _load_reliability_text()

    lines: List[str] = []
    lines.append("=== SENSOR READINESS BRIEF ===")
    lines.append("")
    lines.append(f"Total sensors in manifest : {mh.get('total', 0)}")
    lines.append(f"Enabled                    : {len(mh.get('enabled', []))}")
    lines.append(f"Disabled                   : {len(mh.get('disabled', []))}")
    lines.append("")

    if mh.get("disabled"):
        lines.append("Disabled sensors:")
        for s in mh["disabled"]:
            lines.append(f"  - {s}")
        lines.append("")

    lines.append("=== ENABLED SENSOR DETAILS ===")
    for name in mh.get("enabled", []):
        prof = load_profile(name) or {}
        desc = prof.get("description", "No profile description.")
        warn = prof.get("warning_threshold", "n/a")
        crit = prof.get("critical_threshold", "n/a")

        d = drift.get(name)
        if d:
            drift_status = d.status
            drift_pct = int(round(d.drift_score * 100))
            horizon = d.projected_hours_to_issue
            drift_line = f"{drift_status} ({drift_pct}%, {horizon})"
        else:
            drift_line = "no data"

        lines.append(f"[{name.upper()}]")
        lines.append(f"  Description : {desc}")
        lines.append(f"  Thresholds  : warning={warn}  critical={crit}")
        lines.append(f"  Drift       : {drift_line}")
        lines.append("")

    lines.append("=== SENSOR RELIABILITY (SUMMARY) ===")
    lines.append(reliability_text)
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    text = build_readiness_brief()
    out_path = DOCS_DIR / "sensor_readiness_brief.txt"
    DOCS_DIR.mkdir(exist_ok=True)
    out_path.write_text(text)
    print(f"[OK] Sensor readiness brief written → {out_path}")


if __name__ == "__main__":
    main()

