"""
golden_dome_sbir_note.py

Builds a short SBIR / proposal-ready note describing
GLL's Golden Dome + reliability capabilities as of Day 61.

Output:
    docs/golden_dome_sbir_note_day61.txt
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any

from sensor_reliability import compute_reliability_all
from golden_dome_readiness_report import build_readiness_report
from profile_config import get_active_profile


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
OUT_PATH = DOCS_DIR / "golden_dome_sbir_note_day61.txt"


def build_sbir_note() -> Dict[str, Any]:
    """
    Build a short, proposal-ready narrative describing
    what GLL can do today for Golden Dome-style missions.
    """
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    reliability = compute_reliability_all()
    readiness = build_readiness_report()
    profile = get_active_profile()

    avg_rel = reliability["avg_reliability"]
    sensors = reliability["sensors"]

    profile_name = getattr(profile, "display_name", "Unknown Profile")
    profile_key = getattr(profile, "key", "unknown_profile")

    lines: list[str] = []
    lines.append("GLL GOLDEN DOME / RELIABILITY CAPABILITY NOTE — DAY 61")
    lines.append("")
    lines.append("Overview:")
    lines.append(
        "  Ghost Lantern Labs (GLL) provides a profile-aware, "
        "multi-sensor fusion layer capable of computing and briefing "
        "its own operational readiness for Golden Dome-style missions."
    )
    lines.append("")
    lines.append("Active Profile Context:")
    lines.append(f"  - Profile Key:   {profile_key}")
    lines.append(f"  - Profile Name:  {profile_name}")
    lines.append("")
    lines.append("Sensor Reliability Snapshot:")
    lines.append(f"  - Average Reliability: {avg_rel:.2f}%")
    for name, val in sorted(sensors.items()):
        lines.append(f"  - {name}: {val:.2f}%")
    lines.append("")
    lines.append("Golden Dome Readiness:")
    lines.append(f"  - Assessment: {readiness['label']}")
    lines.append(f"  - Readiness Report: {readiness['path']}")
    lines.append("")
    lines.append("SBIR-Relevant Features (Day 61 Baseline):")
    lines.append("  1) Automated reliability estimation from run history.")
    lines.append("  2) Profile-aware readiness labeling (GREEN/AMBER/YELLOW/RED).")
    lines.append("  3) Human-readable SITREP and readiness reports for commanders.")
    lines.append(
        "  4) Extensible architecture to integrate real optical/seismic/EMS/"
        "radiation sensors without redesign."
    )
    lines.append("")
    lines.append("Proposed SBIR Use Cases:")
    lines.append(
        "  - Phase I: Prototype multi-sensor reliability and readiness engine "
        "for a notional Golden Dome sector, using synthetic telemetry."
    )
    lines.append(
        "  - Phase II: Integrate with live or recorded sensor feeds to drive "
        "decision support for air and missile defense operators."
    )
    lines.append("")
    lines.append("Status (Day 61):")
    lines.append(
        "  GLL's Golden Dome module is now capable of computing its own "
        "sensor reliability metrics, mapping them to mission readiness "
        "labels, and generating daily SITREPs suitable for briefing."
    )

    text = "\n".join(lines)
    OUT_PATH.write_text(text, encoding="utf-8")

    return {
        "path": str(OUT_PATH),
        "avg_reliability": avg_rel,
        "profile_name": profile_name,
        "readiness_label": readiness["label"],
    }


if __name__ == "__main__":
    out = build_sbir_note()
    print("Golden Dome SBIR note written:")
    print(f"  -> {out['path']}")
    print(f"Profile: {out['profile_name']}")
    print(f"Average reliability: {out['avg_reliability']:.2f}%")
    print(f"Readiness: {out['readiness_label']}")

