"""
operator_career_readiness_day61.py

Builds a Day 61 career / resume brief for the operator (you),
based on the GLL value snapshot.

Output:
    docs/day61_career_brief.txt

This does NOT touch any pipelines or CLI behavior.
It only reads existing artifacts and converts them into:

- Plain language explanation of what you've built so far
- Resume bullets
- Interview talking points
- A light rate / value justification block
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
OUT_PATH = DOCS_DIR / "day61_career_brief.txt"


def _load_snapshot() -> Dict[str, Any]:
    """
    Try to import and build the Day 61 value snapshot.
    If that fails for any reason, fall back to a minimal stub.
    """
    try:
        from spectral_value_snapshot_day61 import build_value_snapshot  # type: ignore

        snap = build_value_snapshot()
        return snap
    except Exception as exc:  # noqa: BLE001
        # Minimal safe fallback
        return {
            "snapshot_date": "UNKNOWN",
            "day_index": 61,
            "profile": {
                "key": "unknown_profile",
                "display_name": "Unknown Profile",
            },
            "reliability": {
                "avg_reliability": 90.0,
                "sensors": {},
            },
            "golden_dome_readiness": "UNKNOWN",
            "golden_dome_readiness_report": "N/A",
            "sbir_note": {"path": "N/A"},
            "day61_sitrep": {"path": "N/A"},
            "demo_deck_manifest": {"path": "N/A"},
            "valuation_assumptions": {
                "assumed_hours_total": 150,
                "assumed_hourly_rate_usd": 300,
            },
            "notional_engineering_value_usd": 150 * 300,
            "notes": [f"Snapshot fallback used: {exc}"],
        }


def build_career_brief() -> Dict[str, Any]:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    snap = _load_snapshot()

    profile = snap.get("profile", {})
    profile_name = profile.get("display_name", "Unknown Profile")

    reliability = snap.get("reliability", {})
    avg_rel = reliability.get("avg_reliability", 90.0)
    sensors = reliability.get("sensors", {})

    readiness = snap.get("golden_dome_readiness", "UNKNOWN")
    readiness_report = snap.get("golden_dome_readiness_report", "N/A")

    sbir_note_path = snap.get("sbir_note", {}).get("path", "N/A")
    sitrep_path = snap.get("day61_sitrep", {}).get("path", "N/A")
    demo_manifest_path = snap.get("demo_deck_manifest", {}).get("path", "N/A")

    assumptions = snap.get("valuation_assumptions", {})
    total_hours = assumptions.get("assumed_hours_total", 150)
    rate = assumptions.get("assumed_hourly_rate_usd", 300)
    eng_value = snap.get("notional_engineering_value_usd", total_hours * rate)

    lines: List[str] = []

    # ==========================================================
    # SECTION 1 — Plain Language "Explain it like I'm 8"
    # ==========================================================
    lines.append("DAY 61 CAREER / RESUME BRIEF — GHOST LANTERN LABS")
    lines.append("")
    lines.append("1. What You Built So Far (Explain It Like You're 8)")
    lines.append("")
    lines.append(
        "  You built a smart control room for tough missions. Instead of just "
        "showing random numbers, your system watches many different 'sensors' "
        "at the same time (like eyes, ears, and alarms) and turns all that "
        "noise into simple reports a commander can actually use."
    )
    lines.append("")
    lines.append(
        "  Your system can check if the sensors are healthy, guess which "
        "ones might break soon, and write a daily mission brief. It can also "
        "save special reports for nuclear-style missions, legal cases, and "
        "other high-pressure situations."
    )
    lines.append("")
    lines.append(
        "  Instead of waiting for a big company to give you tools, you are "
        "building your own mini company-grade platform from your desk."
    )
    lines.append("")

    # ==========================================================
    # SECTION 2 — What This Proves You Can Do
    # ==========================================================
    lines.append("2. What This Proves You Can Do (Operator Skill Map)")
    lines.append("")
    lines.append("  This work demonstrates you can:")
    lines.append("  - Design and reason about multi-sensor fusion pipelines.")
    lines.append(
        "  - Build tools that check their own health (QA, reliability, "
        "run history, readiness)."
    )
    lines.append(
        "  - Create mission briefs that combine numbers, alerts, and "
        "profiles into one narrative."
    )
    lines.append(
        "  - Think like an engineer and an analyst at the same time—"
        "connecting code, doctrine, and real missions."
    )
    lines.append(
        "  - Aim your work at nuclear, missile-defense, and high-value "
        "enterprise problems instead of toy projects."
    )
    lines.append("")
    lines.append(f"  Active profile focus today: {profile_name}")
    lines.append(f"  Average sensor reliability (simulated): {avg_rel:.2f}%")
    if sensors:
        lines.append("  Sensor breakdown:")
        for name, val in sorted(sensors.items()):
            lines.append(f"    • {name}: {val:.2f}%")
    lines.append("")
    lines.append(f"  Golden Dome readiness label: {readiness}")
    lines.append(f"  Golden Dome readiness report: {readiness_report}")
    lines.append("")

    # ==========================================================
    # SECTION 3 — Resume Bullets (Drop-in Text)
    # ==========================================================
    lines.append("3. Resume Bullets (Copy/Paste Friendly)")
    lines.append("")
    lines.append("  You can paste bullets like this into a resume:")
    lines.append("")
    lines.append(
        "  • Designed and built a modular sensor-fusion lab (Ghost Lantern Labs) "
        "for ISR/nuclear-style missions, integrating optical, seismic, EMS, and "
        "radiation telemetry into commander-ready intelligence products."
    )
    lines.append(
        "  • Implemented automated QA, sensor reliability scoring, and "
        "Golden Dome–style readiness reporting to predict failures and brief "
        "overall system health in plain language."
    )
    lines.append(
        "  • Developed AI-independence patterns and offline-friendly analysis "
        "so mission briefs can still be generated in degraded or denied "
        "environments."
    )
    lines.append(
        "  • Built demo and legal scenarios (e.g., family law demo pack) to "
        "show how the same fusion engine can serve military, legal, and "
        "enterprise customers without rewriting the core system."
    )
    lines.append(
        "  • Produced daily SITREPs, SBIR-style one-pagers, and GUI-ready "
        "dashboards tying code, doctrine, and operator workflows into a "
        "single narrative."
    )
    lines.append("")

    # ==========================================================
    # SECTION 4 — Interview Talking Points
    # ==========================================================
    lines.append("4. Interview Talking Points")
    lines.append("")
    lines.append("  Example talking angles you can use:")
    lines.append("")
    lines.append("  Q1: \"Tell me about a project that proves you can own a system.\"")
    lines.append(
        "      A: Walk through Ghost Lantern Labs: how you went from single "
        "CSV files to a full pipeline with QA, reliability, readiness, "
        "and mission briefs tied to real-world ISR problems."
    )
    lines.append("")
    lines.append(
        "  Q2: \"How do you think about reliability and readiness, not just features?\""
    )
    lines.append(
        "      A: Explain how your system self-checks, logs runs, scores "
        "sensor reliability, and produces readiness tiles instead of "
        "just raw metrics."
    )
    lines.append("")
    lines.append(
        "  Q3: \"What makes this different from a normal coding side project?\""
    )
    lines.append(
        "      A: Emphasize that your design is pointed at nuclear/space/"
        "missile-defense style missions and also re-usable for law firms, "
        "sports teams, and SOCs—showing you think like a product builder, "
        "not just a script writer."
    )
    lines.append("")

    # ==========================================================
    # SECTION 5 — Value / Rate Justification
    # ==========================================================
    lines.append("5. Value and Rate Justification (Notional)")
    lines.append("")
    lines.append(
        "  These numbers are not a contract, but they help you explain "
        "why your time is worth more as this platform matures."
    )
    lines.append(
        f"  - Assumed total engineering hours invested so far: {total_hours}"
    )
    lines.append(
        f"  - Assumed blended hourly rate (ISR / cyber / AI work): "
        f"${rate:,}/hr"
    )
    lines.append(
        f"  - Implied engineering value of current GLL build: "
        f"${eng_value:,}"
    )
    lines.append("")
    lines.append(
        "  If a cleared contractor or small defense startup had to pay "
        "for this work at market rates, they would be looking at this "
        "order of magnitude just to recreate what you already built by "
        "Day 61."
    )
    lines.append("")
    lines.append(
        "  Over the next 2–3 years, as you stack BMT, tech school, your "
        "degree, and more GLL capability, this kind of platform-level work "
        "is what supports higher salaries, consulting rates, and SBIR-style "
        "funding conversations."
    )
    lines.append("")

    # ==========================================================
    # SECTION 6 — Artifact Links (For You)
    # ==========================================================
    lines.append("6. Supporting Artifacts (For Your Reference)")
    lines.append("")
    lines.append(f"  - Day 61 SITREP (if generated): {sitrep_path}")
    lines.append(f"  - Golden Dome SBIR note:        {sbir_note_path}")
    lines.append(f"  - Demo deck manifest:           {demo_manifest_path}")
    lines.append(
        "  - Value snapshot (JSON/TXT):    "
        "docs/gll_value_snapshot_day61.*"
    )
    lines.append("")
    lines.append(
        "Use this brief as a base whenever you need to update your resume, "
        "prepare for an interview, or talk to someone about GLL's maturity."
    )
    lines.append("")

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")

    return {
        "path": str(OUT_PATH),
        "avg_reliability": avg_rel,
        "readiness": readiness,
        "engineering_value_usd": eng_value,
    }


if __name__ == "__main__":
    out = build_career_brief()
    print("Day 61 career / resume brief written:")
    print(f"  -> {out['path']}")
    print(f"Average reliability (snapshot): {out['avg_reliability']:.2f}%")
    print(f"Readiness label: {out['readiness']}")
    print(f"Implied engineering value: ${out['engineering_value_usd']:,}")

