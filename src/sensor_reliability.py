"""
sensor_reliability.py — Sensor Reliability Predictor + Report

Purpose:
  - Estimate reliability for each key sensor family (optical, seismic, EMS, radiation).
  - Produce a simple 0–100% score for commanders and dashboards.
  - Export a human-readable report under docs/reliability_report.txt.

This is intentionally lightweight and conservative. As GLL matures, you can swap
the internals for real metrics (uptime, error rate, drift, health failures) without
changing the interface.

Public functions:
  - compute_reliability_all() -> dict
  - build_reliability_lines() -> list[str]
  - export_reliability_report() -> dict
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List


BASE = Path(__file__).resolve().parent
DOCS_DIR = BASE / "docs"


def _ascii_bar(percent: int, width: int = 20) -> str:
    """
    Build a simple ASCII bar like:
      [██████████░░░░░░] 75%
    """
    if percent < 0:
        percent = 0
    if percent > 100:
        percent = 100

    filled = int((percent / 100.0) * width)
    empty = width - filled
    return "[" + ("█" * filled) + ("░" * empty) + f"] {percent:3d}%"


def compute_reliability_all() -> Dict[str, Dict[str, object]]:
    """
    Return a dict of reliability data for each major sensor type and overall.

    Structure:
      {
        "optical":   {"percent": 94, "status": "stable"},
        "seismic":   {"percent": 91, "status": "stable"},
        "ems":       {"percent": 89, "status": "stable"},
        "radiation": {"percent": 96, "status": "stable"},
        "overall":   {"percent": 93, "status": "stable"},
      }

    NOTE: Right now this is a conservative, hard-coded model standing in for a
    real uptime / health / drift analysis. The interface is what matters; the
    internals can be swapped later without breaking callers.
    """

    # Conservative "good but not perfect" baselines.
    reliability = {
        "optical":   {"percent": 94, "status": "stable"},
        "seismic":   {"percent": 91, "status": "stable"},
        "ems":       {"percent": 89, "status": "stable"},
        "radiation": {"percent": 96, "status": "stable"},
    }

    # Compute simple overall average.
    vals = [v["percent"] for v in reliability.values()]
    overall = round(sum(vals) / len(vals)) if vals else 0
    reliability["overall"] = {"percent": overall, "status": "stable"}

    return reliability


def build_reliability_lines(rel: Dict[str, Dict[str, object]]) -> List[str]:
    """
    Turn the reliability dict into human-readable CLI / text lines.
    Safe to call from daily_mission_brief, mission_brief_html, etc.
    """

    lines: List[str] = []
    order = ["optical", "seismic", "ems", "radiation"]

    for key in order:
        data = rel.get(key)
        if not data:
            continue
        pct = int(data.get("percent", 0))
        status = str(data.get("status", "unknown"))
        label = key.upper().ljust(10)
        bar = _ascii_bar(pct)
        lines.append(f"{label} {bar}  ({status})")

    overall = rel.get("overall")
    if overall:
        pct = int(overall.get("percent", 0))
        status = str(overall.get("status", "unknown"))
        lines.append("")
        lines.append(f"OVERALL   {_ascii_bar(pct)}  ({status})")

    return lines


def export_reliability_report() -> Dict[str, object]:
    """
    Compute reliability and export a text report to docs/reliability_report.txt.

    Return:
      {
        "status": "ok",
        "path": "/full/path/to/docs/reliability_report.txt",
        "sensors": <same dict as compute_reliability_all()>
      }
    """
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    rel = compute_reliability_all()

    lines: List[str] = []
    lines.append("=== SENSOR RELIABILITY REPORT ===")
    lines.append("")
    lines.extend(build_reliability_lines(rel))

    out_path = DOCS_DIR / "reliability_report.txt"
    out_path.write_text("\n".join(lines), encoding="utf-8")

    return {
        "status": "ok",
        "path": str(out_path),
        "sensors": rel,
    }


if __name__ == "__main__":
    result = export_reliability_report()
    print(f"Reliability report written → {result['path']}")

