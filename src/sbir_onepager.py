"""
sbir_onepager.py

Generates a DoD-style SBIR Phase I one-pager from Ghost Lantern Labs
capabilities, profiles, AI-independence posture, and current technical maturity.

Usage:
    python sbir_onepager.py
"""

from __future__ import annotations
import datetime
from pathlib import Path
from typing import Dict, Any, List

BASE = Path(__file__).parent
DOCS = BASE / "docs"
DOCS.mkdir(exist_ok=True, parents=True)


def safe(path: Path) -> str:
    """Safe read helper."""
    if not path.exists():
        return ""
    try:
        return path.read_text().strip()
    except:
        return ""


def detect_capabilities() -> List[str]:
    caps = []

    # Sensor + Fusion
    if (BASE / "fusion_ingest.py").exists():
        caps.append("Multi-sensor ingest (optical, seismic, EMS, radiation)")

    if (BASE / "fusion_scoring.py").exists():
        caps.append("Fusion scoring + anomaly detection engine")

    if (BASE / "fusion_sanitizer.py").exists():
        caps.append("Bad-data sanitizer and corruption quarantine")

    if (BASE / "sensor_reliability.py").exists():
        caps.append("Predictive sensor reliability model (pre-failure detection)")

    # Mission Brief
    if (BASE / "daily_mission_brief.py").exists():
        caps.append("Mission brief generator (text + HTML + GUI)")

    # GUI
    gui = BASE.parent / "apps" / "gui" / "app.py"
    if gui.exists():
        caps.append("Operator dashboard (Streamlit GUI + overlays)")

    # AI Independence
    if (BASE / "llm_phase2_adapter.py").exists():
        caps.append("AI-Independence engine (multi-provider + offline rules)")

    # Threat Memory
    if (BASE / "spectral_owl" / "threat_memory.py").exists():
        caps.append("Threat-memory engine + cross-sensor reasoning")

    return caps


def detect_markets() -> List[str]:
    mk = []
    # Defense / ISR
    mk.append("Space / Nuclear ISR (AFTAC-style detection workflows)")
    mk.append("Cyber Fusion & Defensive Counter-AI Operations")

    # Legal
    if (BASE / "family_law_brief.py").exists():
        mk.append("Legal analytics (family law, collections, case prep)")

    # Commercial SOC
    if (BASE / "anti_dos.py").exists():
        mk.append("Commercial SOC anomaly detection & automation")

    return mk


def build_onepager() -> str:
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    caps = detect_capabilities()
    mkts = detect_markets()

    # AI Independence pull
    aip = safe(BASE / "docs" / "AI_Independence_Plan.md")
    aip_excerpt = aip[:350] + "…" if aip else "[AI Independence Plan missing]"

    # Golden Dome alignment
    golden = safe(BASE / "docs" / "golden_dome_status.txt")
    golden_excerpt = golden[:350] + "…" if golden else "[No nuclear alignment file]"

    lines: List[str] = []
    lines.append("GHOST LANTERN LABS — SBIR PHASE I ONE-PAGER")
    lines.append("===========================================")
    lines.append(f"Date: {now}")
    lines.append("")
    lines.append("1. PROBLEM AREA")
    lines.append("----------------")
    lines.append(
        "U.S. forces require reliable, multi-sensor fusion systems capable of detecting, "
        "interpreting, and briefing complex events (cyber, EMS, nuclear, legal, or commercial) "
        "under degraded communications and without reliance on a single AI vendor."
    )
    lines.append("")
    lines.append("2. PROPOSED SOLUTION (GLL)")
    lines.append("--------------------------")
    lines.append(
        "Ghost Lantern Labs (GLL) is a modular ISR-grade platform providing multi-sensor ingest, "
        "fusion scoring, anomaly detection, AI-independent reasoning, and automated operator briefings "
        "for both defense and civilian sectors."
    )
    lines.append("")
    lines.append("Key Capabilities:")
    for c in caps:
        lines.append(f"  • {c}")
    lines.append("")
    lines.append("3. TECHNICAL APPROACH")
    lines.append("----------------------")
    lines.append("GLL uses a layered pipeline:")
    lines.append("  1) Sensor ingest → 2) Sanitization → 3) Fusion Scoring → 4) Threat Memory → 5) Mission Brief.")
    lines.append(
        "A local rules engine ensures functionality even when cloud AI services degrade or fail."
    )
    lines.append("")
    lines.append("AI Independence Excerpt:")
    lines.append("------------------------")
    lines.append(aip_excerpt)
    lines.append("")
    lines.append("4. TARGET USERS / MARKETS")
    lines.append("--------------------------")
    for m in mkts:
        lines.append(f"  • {m}")
    lines.append("")
    lines.append("5. DUAL-USE READINESS")
    lines.append("----------------------")
    lines.append("Nuclear Alignment Excerpt:")
    lines.append("--------------------------")
    lines.append(golden_excerpt)
    lines.append("")
    lines.append("6. EXPECTED DELIVERABLES FOR PHASE I")
    lines.append("-------------------------------------")
    lines.append("  • Operational fusion engine with reliability scoring")
    lines.append("  • Degraded-mode AI reasoning engine (Spectral Owl offline rules)")
    lines.append("  • GUI dashboard for operators")
    lines.append("  • Profiling tools for ISR or legal workflows")
    lines.append("  • Phase II transition plan (DoD or civilian)")
    lines.append("")
    lines.append("7. TEAM QUALIFICATIONS")
    lines.append("-----------------------")
    lines.append(
        "Team Lead: USAF Reserve Intelligence Analyst (1N0X1) with cyber fusion engineering, "
        "AI system architecture, sensor telemetry, and mission briefing experience."
    )
    lines.append("")
    lines.append("8. COMMERCIALIZATION STRATEGY")
    lines.append("------------------------------")
    lines.append("SBIR → Defense pilot → Cloud marketplace → Legal analytics → SOC integrations")
    lines.append("")
    lines.append("END OF ONE-PAGER")
    lines.append("")

    return "\n".join(lines)


def write_onepager() -> Path:
    today = datetime.datetime.now().strftime("%Y%m%d")
    out = DOCS / f"sbir_onepager_{today}.txt"
    out.write_text(build_onepager())
    return out


if __name__ == "__main__":
    path = write_onepager()
    print("SBIR One-Pager generated:")
    print(f" → {path}")

