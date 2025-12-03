"""
commercial_readiness_brief.py

Generates a human-readable "Commercial Readiness Brief" for Ghost Lantern Labs (GLL).

Purpose:
- Translate all the technical modules (sensors, fusion, AI independence, demos, profiles)
  into clear language for:
    * Recruiters
    * SBIR reviewers
    * Commanders
    * Potential clients (AFTAC, SOC, sports orgs, law firms)

Output:
- docs/commercial_readiness_brief_day59.txt  (or whatever day you run it)

Usage:
    python commercial_readiness_brief.py
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Dict, Any, List

BASE = Path(__file__).parent
DOCS_DIR = BASE / "docs"
DATA_DIR = BASE / "data"

# Ensure docs directory exists
DOCS_DIR.mkdir(parents=True, exist_ok=True)


def safe_read(path: Path) -> str:
    """Read a file safely, returning fallback text if missing."""
    if not path.exists():
        return f"[missing: {path.name}]"
    try:
        return path.read_text().strip()
    except Exception as e:
        return f"[error reading {path.name}: {e}]"


def detect_profiles() -> List[str]:
    """Try to detect which profiles GLL is currently configured to support."""
    profiles = []

    # Nuclear / AFTAC
    golden = (BASE / "golden_dome_alignment_report.py", BASE / "docs" / "golden_dome_status.txt")
    if golden[0].exists() or golden[1].exists():
        profiles.append("Nuclear / AFTAC-style monitoring")

    # Legal / family law
    legal_files = [
        BASE / "legal_ingest_family_law.py",
        BASE / "family_law_scoring.py",
        BASE / "family_law_brief.py",
        BASE / "demos" / "family_law_demo" / "README_FAMILY_LAW_DEMO.txt",
    ]
    if any(p.exists() for p in legal_files):
        profiles.append("Legal / Family Law (collections, bankruptcy, family scenarios)")

    # Commercial SOC / cyber
    if (BASE / "anti_dos.py").exists() or (BASE / "system_metrics_rollup.py").exists():
        profiles.append("Commercial SOC / Cyber Defense")

    # Sports / generic telemetry (future)
    if (BASE / "sensor_interface.py").exists() and (BASE / "fusion_ingest.py").exists():
        profiles.append("Sports / Performance / Generic Telemetry (future-ready)")

    return profiles


def estimate_maturity() -> Dict[str, Any]:
    """
    Very rough maturity estimate based on presence of key components.
    This is not perfect, but it gives you a talking point.
    """
    score = 0
    notes = []

    # Fusion pipeline
    if (BASE / "fusion_scoring.py").exists():
        score += 10
        notes.append("Fusion scoring engine present.")
    if (BASE / "fusion_sanitizer.py").exists():
        score += 10
        notes.append("Bad-data sanitizer present.")
    if (BASE / "fusion_alerts.py").exists():
        score += 10
        notes.append("Alert engine present.")
    if (BASE / "daily_mission_brief.py").exists():
        score += 10
        notes.append("Mission brief generator present.")

    # AI Independence
    if (BASE / "docs" / "AI_Independence_Plan.md").exists():
        score += 10
        notes.append("AI-Independence Plan documented.")
    if (BASE / "llm_phase2_adapter.py").exists():
        score += 10
        notes.append("Multi-provider LLM adapter implemented.")
    if (BASE / "spectral_owl" / "local_rules_engine.py").exists():
        score += 10
        notes.append("Local rules engine in place for degraded mode.")

    # GUI / dashboards
    gui_app = BASE.parent / "apps" / "gui" / "app.py"
    if gui_app.exists():
        score += 10
        notes.append("Streamlit GUI app present.")
    if (BASE / "spectral_dashboard_api.py").exists():
        score += 10
        notes.append("Dashboard API bundle implemented.")

    # Demos / legal / family law
    if (BASE / "demos" / "family_law_demo").exists():
        score += 10
        notes.append("Legal/Family law demo pipeline complete.")

    # Reliability / sensor health
    if (BASE / "sensor_health.py").exists():
        score += 5
        notes.append("Sensor health monitor present.")
    if (BASE / "sensor_reliability.py").exists():
        score += 5
        notes.append("Sensor reliability predictor present.")

    # QA & self-diagnostics
    if (BASE / "qa_validator.py").exists():
        score += 10
        notes.append("QA validator present.")
    if (BASE / "run_history_intel.py").exists():
        score += 5
        notes.append("Run-history intelligence timeline present.")

    # Clamp score and classify stage
    if score >= 80:
        stage = "Alpha/Pre-Beta Product (demo-ready for serious stakeholders)"
    elif score >= 60:
        stage = "Advanced Prototype (engineer + investor/demo ready)"
    elif score >= 40:
        stage = "Prototype (technical demo, not yet a product)"
    else:
        stage = "Concept / Early Prototype"

    return {
        "score": score,
        "stage": stage,
        "notes": notes,
    }


def build_commercial_brief() -> str:
    """Assemble the commercial readiness brief as plain text."""
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M:%S")

    maturity = estimate_maturity()
    profiles = detect_profiles()

    ai_plan = safe_read(BASE / "docs" / "AI_Independence_Plan.md")
    golden_status = safe_read(BASE / "docs" / "golden_dome_status.txt")
    demo_roadmap = safe_read(BASE / "docs" / "demo_roadmap_day100.md")

    lines: List[str] = []
    lines.append("GHOST LANTERN LABS — COMMERCIAL READINESS BRIEF")
    lines.append("================================================")
    lines.append(f"Generated: {date_str}")
    lines.append("")
    lines.append("1. HIGH-LEVEL DESCRIPTION")
    lines.append("-------------------------")
    lines.append(
        "Ghost Lantern Labs (GLL) is a modular cyber–intel fusion platform designed "
        "for environments that need resilient sensing, AI-assisted analysis, and "
        "operator-grade mission briefings — even when cloud access is degraded."
    )
    lines.append("")
    lines.append("Core capabilities currently implemented:")
    lines.append("  • Multi-sensor ingest and fusion scoring")
    lines.append("  • Bad-data sanitization and quarantine")
    lines.append("  • Threat memory and spectral owl reasoning engine")
    lines.append("  • Mission and daily briefs (text + HTML + GUI)")
    lines.append("  • AI-independence architecture (multi-provider adapter + offline rules)")
    lines.append("  • Legal/family-law demo pipeline for non-military scenarios")
    lines.append("")

    lines.append("2. MATURITY ESTIMATE")
    lines.append("--------------------")
    lines.append(f"Estimated readiness score: {maturity['score']} / 100")
    lines.append(f"Stage: {maturity['stage']}")
    lines.append("")
    lines.append("Signals contributing to this estimate:")
    for n in maturity["notes"]:
        lines.append(f"  • {n}")
    lines.append("")

    lines.append("3. SUPPORTED MISSION PROFILES (DETECTED)")
    lines.append("----------------------------------------")
    if profiles:
        for p in profiles:
            lines.append(f"  • {p}")
    else:
        lines.append("  • [No profiles detected] (check profile_config and demo pipelines)")
    lines.append("")

    lines.append("4. AI INDEPENDENCE & SOVEREIGNTY POSTURE")
    lines.append("----------------------------------------")
    lines.append(
        "GLL is designed so that no single AI vendor can break the system. All AI calls "
        "flow through a clean adapter contract (llm_phase2_adapter), with a local "
        "rules engine available for degraded/offline modes."
    )
    lines.append("")
    lines.append("Key documents and modules:")
    lines.append("  • docs/AI_Independence_Plan.md")
    lines.append("  • src/llm_phase2_adapter.py")
    lines.append("  • src/spectral_owl/local_rules_engine.py")
    lines.append("")
    lines.append("Excerpt / status from AI_Independence_Plan.md:")
    lines.append("----------------------------------------------")
    lines.append(ai_plan if ai_plan else "[No AI independence plan text found]")
    lines.append("")

    lines.append("5. GOLDEN DOME / NUCLEAR ALIGNMENT SNAPSHOT")
    lines.append("-------------------------------------------")
    lines.append(
        "GLL is being aligned with AFTAC / Golden Dome style missions, focusing on "
        "multi-sensor nuclear / EMS / seismic / radiation fusion and treaty-monitoring workflows."
    )
    lines.append("")
    lines.append("Status excerpt (if present):")
    lines.append("-------------------------------------------")
    lines.append(golden_status if golden_status else "[No golden_dome_status.txt found]")
    lines.append("")

    lines.append("6. DAY-100 DEMO & ROADMAP ALIGNMENT")
    lines.append("-----------------------------------")
    lines.append(
        "The current 100-day pre-BMT sprint is aimed at delivering a demo-ready system "
        "that can be shown to both technical and non-technical stakeholders (e.g., "
        "family law scenario for a collections attorney, ISR/nuclear scenario for AFTAC-style audiences)."
    )
    lines.append("")
    lines.append("Demo Roadmap excerpt:")
    lines.append("---------------------")
    lines.append(demo_roadmap if demo_roadmap else "[No demo_roadmap_day100.md found]")
    lines.append("")

    lines.append("7. COMMERCIAL TALKING POINTS")
    lines.append("----------------------------")
    lines.append("For recruiters / clients, GLL currently demonstrates that the builder can:")
    lines.append("  • Design and implement a full fusion data pipeline.")
    lines.append("  • Engineer AI-adjacent systems that do not die when the model dies.")
    lines.append("  • Build CLI + GUI tooling for operators (mission briefs, overlays, minimaps).")
    lines.append("  • Translate defense-style workflows into civilian domains (legal, SOC, sports).")
    lines.append("  • Document AI independence, nuclear alignment, and demo roadmaps.")
    lines.append("")
    lines.append("These talking points can be used directly in resumes, proposals, or briefings.")
    lines.append("")

    lines.append("8. NEXT 3 COMMERCIALIZATION STEPS")
    lines.append("-------------------------------")
    lines.append("Recommended next moves to make GLL commercially credible:")
    lines.append("  1) Lock a single profile into a polished demo (e.g., Family Law + ISR-style reliability).")
    lines.append("  2) Build a stable, repeatable Day-100 demo flow with screenshots + GUI overlays.")
    lines.append("  3) Map at least one SBIR / STTR or defense use case directly to current capabilities.")
    lines.append("")
    lines.append("End of Commercial Readiness Brief.")
    lines.append("")

    return "\n".join(lines)


def write_brief() -> Path:
    """Write the commercial readiness brief to docs/ and return its path."""
    today = datetime.datetime.now().strftime("%Y%m%d")
    out_path = DOCS_DIR / f"commercial_readiness_brief_{today}.txt"
    text = build_commercial_brief()
    out_path.write_text(text)
    return out_path


def main() -> Dict[str, Any]:
    """Main entry point for CLI usage."""
    path = write_brief()
    return {
        "status": "ok",
        "path": str(path),
    }


if __name__ == "__main__":
    result = main()
    print("Commercial Readiness Brief generated:")
    print(f"  → {result['path']}")

