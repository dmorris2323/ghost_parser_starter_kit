"""
day61_investor_brief.py

Builds a one-page style investor / sponsor brief describing
Ghost Lantern Labs (GLL) as of Day 61.

Output:
    docs/day61_investor_brief.txt
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from spectral_value_snapshot_day61 import build_value_snapshot


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
OUT_PATH = DOCS_DIR / "day61_investor_brief.txt"


def build_investor_brief() -> Dict[str, Any]:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    snapshot = build_value_snapshot()

    profile = snapshot["profile"]
    reliability = snapshot["reliability"]
    avg_rel = reliability.get("avg_reliability", 90.0)
    sensors = reliability.get("sensors", {})

    readiness_label = snapshot["golden_dome_readiness"]
    sbir_note_path = snapshot["sbir_note"]["path"]
    sitrep_path = snapshot["day61_sitrep"]["path"]
    demo_manifest_path = snapshot["demo_deck_manifest"]["path"]

    engineering_value = snapshot["notional_engineering_value_usd"]
    assumptions = snapshot["valuation_assumptions"]

    lines: List[str] = []
    lines.append("GHOST LANTERN LABS — INVESTOR / SPONSOR BRIEF (DAY 61)")
    lines.append("")
    lines.append("1. Vision & Problem Space")
    lines.append(
        "  Ghost Lantern Labs (GLL) is a modular, ISR-grade sensor-fusion lab "
        "designed to turn noisy telemetry into commander-ready intelligence "
        "products. It is built for nuclear, missile defense, space, and high-value "
        "enterprise environments where reliability and readiness matter."
    )
    lines.append("")
    lines.append("2. Current Capability (Day 61 Snapshot)")
    lines.append("  - Profile-aware telemetry fusion (active profile):")
    lines.append(f"      • Key:   {profile['key']}")
    lines.append(f"      • Name:  {profile['display_name']}")
    lines.append("  - Multi-sensor pipeline (simulated today, real-data ready):")
    lines.append("      • Optical  (launch flash / plume)")
    lines.append("      • Seismic  (ground coupling / yield-like patterns)")
    lines.append("      • EMS      (jamming, interference, spoof attempts)")
    lines.append("      • Radiation (nuclear confirmation layer)")
    lines.append("")
    lines.append("3. Reliability & Readiness Engine")
    lines.append(
        "  GLL does not just display data — it measures and briefs its own health."
    )
    lines.append(f"  - Average Sensor Reliability (Day 61): {avg_rel:.2f}%")
    if sensors:
        for name, val in sorted(sensors.items()):
            lines.append(f"      • {name}: {val:.2f}%")
    else:
        lines.append("      • Sensor breakdown not available (fallback used).")
    lines.append("")
    lines.append("  - Golden Dome Readiness:")
    lines.append(f"      • Assessment: {readiness_label}")
    lines.append(
        f"      • Detailed report: {snapshot['golden_dome_readiness_report']}"
    )
    lines.append("")
    lines.append("4. Proof Artifacts (Day 61)")
    lines.append("  - Day 61 SITREP:")
    lines.append(f"      • {sitrep_path}")
    lines.append("  - Golden Dome SBIR Note:")
    lines.append(f"      • {sbir_note_path}")
    lines.append("  - Demo Deck Manifest (what we can show):")
    lines.append(f"      • {demo_manifest_path}")
    lines.append("  - Value Snapshot (this doc’s backing JSON/TXT):")
    lines.append(
        "      • docs/gll_value_snapshot_day61.json "
        "and docs/gll_value_snapshot_day61.txt"
    )
    lines.append("")
    lines.append("5. Engineering Investment to Date (Notional)")
    lines.append(
        "  The following numbers are **assumptions** to frame discussion, not "
        "formal accounting. They reflect what it would cost to re-create this "
        "capability using cleared ISR/cyber engineers."
    )
    lines.append(
        f"  - Assumed total engineering hours: "
        f"{assumptions['assumed_hours_total']}"
    )
    lines.append(
        f"  - Assumed blended hourly rate: "
        f"${assumptions['assumed_hourly_rate_usd']:,}/hr"
    )
    lines.append(
        f"  - Implied engineering value: "
        f"${engineering_value:,}"
    )
    lines.append("")
    lines.append("6. Near-Term Roadmap (Next 12–18 Months, High Level)")
    lines.append("  - Wire to real-world or exercise-grade telemetry.")
    lines.append("  - Harden AI-independence paths for denied environments.")
    lines.append("  - Expand sector profiles (AFTAC/nuclear, sports, legal, SOC).")
    lines.append("  - Build production-ready dashboard (Spectral Owl front-end).")
    lines.append("  - Package for SBIR / pilot contracts with clear KPIs.")
    lines.append("")
    lines.append("7. Why This Is Investable / Fundable")
    lines.append(
        "  - Addresses real ISR, missile defense, and high-value enterprise "
        "pain points: data overload, unreliable pipelines, and lack of "
        "self-awareness in current tools."
    )
    lines.append(
        "  - Architected from day one for environments where connectivity, "
        "AI vendors, and sensor availability are not guaranteed."
    )
    lines.append(
        "  - Demonstrates concrete progress: code, metrics, SITREPs, and "
        "demo deck rather than just a slideware concept."
    )

    text = "\n".join(lines)
    OUT_PATH.write_text(text, encoding="utf-8")

    return {
        "path": str(OUT_PATH),
        "engineering_value_usd": engineering_value,
        "readiness_label": readiness_label,
        "avg_reliability": avg_rel,
    }


if __name__ == "__main__":
    out = build_investor_brief()
    print("Day 61 investor/sponsor brief written:")
    print(f"  -> {out['path']}")
    print(f"Average reliability: {out['avg_reliability']:.2f}%")
    print(f"Readiness: {out['readiness_label']}")
    print(f"Implied value: ${out['engineering_value_usd']:,}")

