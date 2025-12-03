"""
sbir_pitch_outline_builder.py

Ghost Lantern Labs – SBIR Phase I Pitch Outline Builder

This script builds a markdown pitch outline for a future SBIR Phase I proposal,
using the artifacts you already have (if they exist).

Output:
  src/docs/sbir_pitch_outline_day59.md

It does NOT call any AI or external services. It just inspects your repo
and writes a structured outline you can refine later.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, List


BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "docs"
ROOT_DIR = BASE_DIR.parent  # repo root


def _exists(path: Path) -> bool:
    return path.exists()


def collect_artifact_status() -> Dict[str, str]:
    """
    Check high-value artifacts and return a status dict.
    """
    candidates = {
        "AI_Independence_Plan": DOCS_DIR / "AI_Independence_Plan.md",
        "AI_Independence_Phase2": DOCS_DIR / "AI_Independence_Phase2.md",
        "AI_Independence_Phase3": DOCS_DIR / "AI_Independence_Phase3.md",
        "Golden_Dome_Status": DOCS_DIR / "golden_dome_status.txt",
        "Demo_Roadmap_Day100": DOCS_DIR / "demo_roadmap_day100.md",
        "Daily_Mission_Brief": DOCS_DIR / "daily_mission_brief.txt",
        "Profile_Mission_Brief": DOCS_DIR / "profile_mission_brief.txt",
        "Reliability_Report": DOCS_DIR / "reliability_report.txt",
        "Cross_Sensor_Report": DOCS_DIR / "cross_sensor_report.txt",
        "SBIR_Readiness_Assessment": DOCS_DIR / "sbir_readiness_assessment.txt",
        "SBIR_Readiness_Score": DOCS_DIR / "sbir_readiness_score.json",
        "Demo_Deck_Manifest": DOCS_DIR / "demo_deck_manifest_day58.json",
        "Legal_Framework": ROOT_DIR / "legal" / "GLL_Legal_Framework.md",
        "Code116_Operating_Agreement": ROOT_DIR / "legal" / "Code116_Operating_Agreement_Draft.md",
    }

    status = {}
    for label, path in candidates.items():
        status[label] = "present" if _exists(path) else "missing"
    return status


def build_outline_text(status: Dict[str, str]) -> str:
    ts = datetime.now().isoformat(timespec="seconds")

    def flag(name: str) -> str:
        mark = status.get(name, "missing")
        return "✅ present" if mark == "present" else "⚠️ missing"

    lines: List[str] = []
    lines.append("# Ghost Lantern Labs — SBIR Phase I Pitch Outline")
    lines.append("")
    lines.append(f"_Auto-generated on {ts}_")
    lines.append("")
    lines.append("---")
    lines.append("## 1. Problem / Threat Space")
    lines.append("")
    lines.append("- Modern ISR, cyber, and nuclear/EMS missions are flooded with telemetry.")
    lines.append("- Commanders and analysts struggle to fuse multi-sensor data fast enough to act.")
    lines.append("- AI dependence and cloud fragility create single points of failure.")
    lines.append("- Golden Dome–style concepts demand pre-failure detection, not just alerting.")
    lines.append("")
    lines.append("## 2. GLL Solution Overview")
    lines.append("")
    lines.append("- Ghost Lantern Labs (GLL) is a modular **cyber–fusion platform** that:")
    lines.append("  - Ingests multi-sensor telemetry (seismic, optical, EMS, radiation, generic metrics).")
    lines.append("  - Cleans, scores, and fuses data into commander-ready briefings.")
    lines.append("  - Runs fully offline with an AI-independence contract (no single-model lock-in).")
    lines.append("  - Provides GUI + CLI + HTML mission briefs for warfighters and operators.")
    lines.append("")
    lines.append("## 3. Technical Innovation")
    lines.append("")
    lines.append("- Vendor-agnostic LLM adapter (AI-Independence Plan).")
    lines.append("- Spectral Owl: offline-first analysis brain with multi-provider fallback.")
    lines.append("- Sensor reliability scoring and cross-sensor validation.")
    lines.append("- Threat memory + doctrine tagging (maps events to known patterns and PLA/Golden Dome logic).")
    lines.append("- Legal vertical demo (family-law pipeline) proving non-military portability.")
    lines.append("")
    lines.append("Artifact status for innovation docs:")
    lines.append(f"- AI Independence Plan: {flag('AI_Independence_Plan')}")
    lines.append(f"- AI Independence Phase 2: {flag('AI_Independence_Phase2')}")
    lines.append(f"- AI Independence Phase 3: {flag('AI_Independence_Phase3')}")
    lines.append("")
    lines.append("## 4. Operational Fit (Golden Dome / Pacific / C2)")
    lines.append("")
    lines.append("- Designed to support Golden Dome–style missile defense and Pacific large-scale exercises.")
    lines.append("- Aligns sensor fusion with USAF/USSF doctrine and mission briefs.")
    lines.append("- Supports profiles:")
    lines.append("  - Nuclear / AFTAC-like profile")
    lines.append("  - Commercial SOC profile")
    lines.append("  - Sports team telemetry profile")
    lines.append("  - Legal / case workload profile")
    lines.append("")
    lines.append("Key operational artifacts:")
    lines.append(f"- Golden Dome status: {flag('Golden_Dome_Status')}")
    lines.append(f"- Daily Mission Brief: {flag('Daily_Mission_Brief')}")
    lines.append(f"- Profile Mission Brief: {flag('Profile_Mission_Brief')}")
    lines.append(f"- Cross-Sensor Report: {flag('Cross_Sensor_Report')}")
    lines.append("")
    lines.append("## 5. Commercialization & Dual-Use Potential")
    lines.append("")
    lines.append("- Defense use: AFTAC, missile warning, ISR fusion cells, Pacific exercises.")
    lines.append("- Civilian use:")
    lines.append("  - Sports: team performance + injury risk fusion.")
    lines.append("  - Legal: caseload risk, aging, and bottleneck detection.")
    lines.append("  - Banking/insurance: anomaly detection and risk scoring.")
    lines.append("")
    lines.append("Business artifacts:")
    lines.append(f"- GLL Legal Framework: {flag('Legal_Framework')}")
    lines.append(f"- Code116 Operating Agreement: {flag('Code116_Operating_Agreement')}")
    lines.append(f"- Demo deck manifest: {flag('Demo_Deck_Manifest')}")
    lines.append("")
    lines.append("## 6. Work Plan (Phase I)")
    lines.append("")
    lines.append("Phase I focuses on turning the working prototype into a fieldable experiment:")
    lines.append("")
    lines.append("1. **Refine data ingest + reliability:**")
    lines.append("   - Harden ingest for 2–3 real sensor feeds (simulated or partner-provided).")
    lines.append("   - Expand reliability + cross-sensor validation metrics.")
    lines.append("")
    lines.append("2. **User-facing GUI and dashboard:**")
    lines.append("   - Polish Spectral Owl dashboard and overlays (SOS + minimap + reliability).")
    lines.append("   - Add task flows tailored to 1–2 target users (e.g., AFTAC analyst, SOC lead).")
    lines.append("")
    lines.append("3. **Pilot experiment:**")
    lines.append("   - Run limited-scope trials with simulated Pacific / Golden Dome scenarios.")
    lines.append("   - Capture quantitative metrics (alert time, false positives, survivability offline).")
    lines.append("")
    lines.append("4. **Transition plan:**")
    lines.append("   - Define how Phase I artifacts feed Phase II (scale, more sensors, coalition export).")
    lines.append("")
    lines.append("## 7. Team & Ecosystem")
    lines.append("")
    lines.append("- Founder: USAF Reserve 1N0X1 (Intelligence), nuclear/ISR focus.")
    lines.append("- Backed by:")
    lines.append("  - Air Force and Space Force doctrine alignment work.")
    lines.append("  - Ongoing master’s-level cybersecurity trajectory.")
    lines.append("  - Multi-vertical experimentation (legal, sports, SOC).")
    lines.append("")
    lines.append("## 8. Current Readiness Snapshot")
    lines.append("")
    lines.append(f"- SBIR Readiness Assessment: {flag('SBIR_Readiness_Assessment')}")
    lines.append(f"- SBIR Score JSON: {flag('SBIR_Readiness_Score')}")
    lines.append(f"- Reliability Report: {flag('Reliability_Report')}")
    lines.append("")
    lines.append("> This outline is a starting point. Phase I proposal text can be built by")
    lines.append("> expanding each bullet into 2–4 sentences and attaching the demo packet.")
    lines.append("")

    return "\n".join(lines)


def write_outline() -> str:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    status = collect_artifact_status()
    text = build_outline_text(status)
    out_path = DOCS_DIR / "sbir_pitch_outline_day59.md"
    out_path.write_text(text)
    return str(out_path)


if __name__ == "__main__":
    path = write_outline()
    print(f"SBIR pitch outline written to: {path}")

