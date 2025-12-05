"""
uta_commander_readout_day61.py

Builds a short readout you could hand to a commander or instructor
during UTA, explaining:

- What GLL can do today (Day 61).
- Why it matters for Golden Dome / AFTAC / ISR.
- How it ties to reliability and readiness.

Output:
    docs/uta_commander_readout_day61.txt
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any

from sensor_reliability import compute_reliability_all
from golden_dome_readiness_report import build_readiness_report
from profile_config import get_active_profile


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
OUT_PATH = DOCS_DIR / "uta_commander_readout_day61.txt"


def build_commander_readout() -> Dict[str, Any]:
    """
    Build and write the UTA commander readout for Day 61.
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
    lines.append("UTA COMMANDER READOUT — GLL STATUS (DAY 61)")
    lines.append("")
    lines.append("Purpose:")
    lines.append(
        "  Provide a concise overview of the Ghost Lantern Labs (GLL) "
        "prototype for use in conversations with commanders, instructors, "
        "and mentors during UTA."
    )
    lines.append("")
    lines.append("Current Focus Profile:")
    lines.append(f"  - Key:   {profile_key}")
    lines.append(f"  - Name:  {profile_name}")
    lines.append("")
    lines.append("What GLL Does Today (Plain Language):")
    lines.append(
        "  GLL is a multi-sensor fusion lab that ingests telemetry from "
        "simulated optical, seismic, EMS, and radiation sources, cleans it, "
        "scores it, and produces decision-support products for commanders."
    )
    lines.append(
        "  As of Day 61, GLL can also measure its own reliability and "
        "generate a Golden Dome-style readiness assessment."
    )
    lines.append("")
    lines.append("Sensor Reliability Snapshot (Day 61):")
    lines.append(f"  - Average Reliability: {avg_rel:.2f}%")
    for name, val in sorted(sensors.items()):
        lines.append(f"  - {name}: {val:.2f}%")
    lines.append("")
    lines.append("Golden Dome Readiness Assessment:")
    lines.append(f"  - {readiness['label']}")
    lines.append(f"  - Detailed report: {readiness['path']}")
    lines.append("")
    lines.append("Why This Matters for the Unit / Mission:")
    lines.append(
        "  - Demonstrates ability to reason about sensor health, not just "
        "display raw data."
    )
    lines.append(
        "  - Shows how a small, lab-scale ISR platform can support "
        "Golden Dome / AFTAC-style missions with reliability and readiness metrics."
    )
    lines.append(
        "  - Provides a foundation for future integration with real data "
        "sources, exercises, or unit-level TTP development."
    )
    lines.append("")
    lines.append("How This Connects to My Development:")
    lines.append(
        "  - Builds hands-on experience with sensor fusion, reliability "
        "engineering, and ISR-grade reporting."
    )
    lines.append(
        "  - Aligns with 1N0X1 duties, AFTAC-style nuclear monitoring, and "
        "future SBIR / contractor opportunities."
    )
    lines.append("")
    lines.append("Talking Points for UTA / Mentors:")
    lines.append("  1) Ask what types of telemetry or mission data would be most useful to model in GLL.")
    lines.append("  2) Ask which readiness metrics commanders actually care about in your unit.")
    lines.append("  3) Offer to show a demo of reliability reports and Golden Dome readiness outputs.")
    lines.append(
        "  4) Listen for where current tools are fragile or noisy — those "
        "are future GLL modules."
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
    out = build_commander_readout()
    print("UTA commander readout written:")
    print(f"  -> {out['path']}")
    print(f"Profile: {out['profile_name']}")
    print(f"Average reliability: {out['avg_reliability']:.2f}%")
    print(f"Readiness: {out['readiness_label']}")

