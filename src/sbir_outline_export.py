"""
sbir_outline_export.py

Generates a high-level SBIR / demo proposal outline for Ghost Lantern Labs (GLL).
Output: docs/sbir_outline_day59.md

This is NOT marketing fluff. It captures:
- What GLL actually does today (Day 59)
- Why it matters for DoD / SBIR / serious customers
- How profiles (nuclear / sports / legal / SOC) fit in
"""

from pathlib import Path
from datetime import datetime

# If these imports ever break, the script still works without them.
try:
    from profile_config import get_active_profile
except Exception:  # pragma: no cover
    get_active_profile = None  # type: ignore


def build_sbir_outline() -> str:
    """Return the full SBIR / demo outline as Markdown text."""

    timestamp = datetime.utcnow().isoformat() + "Z"

    active_profile_name = "Unknown"
    if get_active_profile is not None:
        try:
            prof = get_active_profile()
            active_profile_name = getattr(prof, "display_name", "Unknown")
        except Exception:
            pass

    lines: list[str] = []

    # Header
    lines.append(f"# Ghost Lantern Labs — SBIR / Demo Outline (Day 59)")
    lines.append("")
    lines.append(f"_Generated: {timestamp}_")
    lines.append(f"_Active Profile at Export: **{active_profile_name}**_")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 1. Problem / Mission Need
    lines.append("## 1. Problem / Mission Need")
    lines.append("")
    lines.append("- Modern ISR and cyber missions drown in noisy, partial telemetry.")
    lines.append("- Commanders need **fusion-grade answers**, not more raw feeds.")
    lines.append("- AI tools are often **vendor-locked, cloud-dependent, and fragile under jamming**.")
    lines.append("- Units lack an **offline-first, vendor-agnostic fusion platform** they can tailor to their mission.")
    lines.append("")

    # 2. Ghost Lantern Labs (GLL) — Core Concept
    lines.append("## 2. Ghost Lantern Labs (GLL) — Core Concept")
    lines.append("")
    lines.append("GLL is a **modular cyber-fusion intelligence platform** designed to run on:")
    lines.append("- Secure local hardware (e.g., Mac mini / NUC / on-prem servers)")
    lines.append("- Disconnected / degraded / contested environments")
    lines.append("")
    lines.append("At Day 59, GLL can already:")
    lines.append("- Ingest multi-sensor telemetry (optical, seismic, EMS, radiation, generic metrics).")
    lines.append("- Clean / sanitize bad data and **quarantine adversarial input**.")
    lines.append("- Run a **fusion-scoring engine** that highlights critical events.")
    lines.append("- Trigger **alerts, daily reports, mission briefs, and reliability summaries**.")
    lines.append("- Use the **Spectral Owl** reasoning layer through a vendor-agnostic AI adapter.")
    lines.append("- Operate with **AI-Independence Phase 2**: multi-provider adapter + local-rules fallback path designed.")
    lines.append("")

    # 3. Current Technical Capabilities (Day 59 Snapshot)
    lines.append("## 3. Current Technical Capabilities (Day 59 Snapshot)")
    lines.append("")
    lines.append("### 3.1 Fusion & Telemetry Pipeline")
    lines.append("- `fusion_ingest.py` — collects sensor samples into a unified ingest stream.")
    lines.append("- `fusion_sanitizer.py` — cleans NaNs, negatives, and malformed fields.")
    lines.append("- `fusion_scoring.py` — applies physics-aware + schema-aware scoring.")
    lines.append("- `fusion_alerts.py` — produces **critical alert** outputs for operators.")
    lines.append("- `daily_report.py` / `daily_mission_brief.py` — human-readable daily summaries.")
    lines.append("")
    lines.append("### 3.2 Bad Data & Adversarial Resilience")
    lines.append("- `simulate_bad_quarantine.py` — generates bad/hostile telemetry for testing.")
    lines.append("- `bad_data_quarantine.py` — quarantines corrupted rows for forensics.")
    lines.append("- `bad_data_heatmap_prep.py` & `bad_data_heatmap_plot.py` — turn anomalies into visual analytics.")
    lines.append("- `anti_dos.py` & metrics — detect flooding, spoofing, and volumetric anomalies.")
    lines.append("")
    lines.append("### 3.3 Spectral Owl — AI Reasoning Layer")
    lines.append("- `spectral_owl/llm_adapter.py` — clean AI contract, vendor-agnostic.")
    lines.append("- `spectral_owl/owl_brain_phase2.py` — multi-provider reasoning, wired through the adapter.")
    lines.append("- `spectral_owl/threat_memory.py` — rolling log of significant threat events.")
    lines.append("- `spectral_owl/threat_memory_summary.py` — operator-friendly snapshot of threat history.")
    lines.append("")
    lines.append("### 3.4 AI-Independence Plan (Phase 1–2 Complete)")
    lines.append("- **Phase 1** (DONE): Single, clean LLM contract; adapter layer; documentation in `AI_Independence_Plan.md`.")
    lines.append("- **Phase 2** (DONE at Day 57): multi-provider adapter stubs, env-variable switching, and probe utilities.")
    lines.append("- **Phase 3** (PLANNED): local/offline chain + degraded-mode behavior with explicit tags and tests.")
    lines.append("")

    # 4. Profiles & Use Cases
    lines.append("## 4. Profiles & Use Cases (Profile-Aware GLL)")
    lines.append("")
    lines.append("GLL is already structured for **profile-based operation**:")
    lines.append("- `profile_config.py` and `config_profiles.py` manage active profiles.")
    lines.append("- Profiles include:")
    lines.append("  - `aftac_nuclear` — nuclear monitoring / Golden Dome / treaty verification style missions.")
    lines.append("  - `sports_team` — performance, workload, and injury-risk style telemetry (future extension).")
    lines.append("  - `law_firm` — case pipeline / risk / workload telemetry (Family Law demo for Shari).")
    lines.append("  - `commercial_soc` — SOC / SIEM-style threat telemetry.")
    lines.append("")
    lines.append("The codebase supports switching and future auto-switching between these profiles **without code rewrite**.")
    lines.append("")

    # 5. Operator & Commander Interfaces (CLI, HTML, GUI)
    lines.append("## 5. Operator & Commander Interfaces (CLI, HTML, GUI)")
    lines.append("")
    lines.append("### 5.1 CLI — `ghost_cli.py`")
    lines.append("- 20+ operational tools for:")
    lines.append("  - QA validation and pipeline health.")
    lines.append("  - Mission brief generation (text + HTML).")
    lines.append("  - Spectral Owl memory viewing and diagnostics.")
    lines.append("  - Family Law demo scenario for a legal profile (Shari demo).")
    lines.append("  - Exporting GUI overlays (minimap, SOS, snapshot bundles, dashboard JSON).")
    lines.append("")
    lines.append("### 5.2 HTML — `mission_brief_html.py`")
    lines.append("- Generates `docs/daily_mission_brief.html` with:")
    lines.append("  - Active profile.")
    lines.append("  - Sensor reliability bars.")
    lines.append("  - Core mission summary text.")
    lines.append("")
    lines.append("### 5.3 GUI — `apps/gui/app.py`")
    lines.append("- Displays:")
    lines.append("  - Fusion minimap overlay (threat distribution by profile/region).")
    lines.append("  - SOS overlay (threat memory + AI engine state + profile context).")
    lines.append("  - Hooks for future live charts, decks, and command dashboards.")
    lines.append("")

    # 6. Reliability & Readiness (Day 59 Workload)
    lines.append("## 6. Reliability & Readiness (Day 59 Additions)")
    lines.append("")
    lines.append("- `sensor_reliability.py` — produces a **reliability score (0–100%)** per sensor.")
    lines.append("- `sensor_readiness_brief.py` — combines manifest health + reliability into a commander brief.")
    lines.append("- `daily_mission_brief.py` & `mission_brief_html.py` updated to show sensor reliability.")
    lines.append("- CLI Option 24: **Export Sensor Reliability Report**.")
    lines.append("")
    lines.append("Result: GLL has pre-failure awareness and can warn commanders **before** a sensor becomes useless.")
    lines.append("")

    # 7. Demo & Pitch Readiness (for Day 100 + Beyond)
    lines.append("## 7. Demo & Pitch Readiness (Day 100 Target)")
    lines.append("")
    lines.append("By Day 100, the GLL stack is expected to deliver:")
    lines.append("- A full **Day 100 demo deck manifest** (`demo_deck_manifest.py`).")
    lines.append("- A working CLI + HTML + GUI path that walks:")
    lines.append("  - Sensor ingestion → fusion → scoring → alerts → mission brief.")
    lines.append("  - Spectral Owl threat memory + AI-independence story.")
    lines.append("  - Profile-aware views (AFTAC-style + Family Law demo).")
    lines.append("")
    lines.append("This outline document is the **seed for an SBIR white paper, conference demo description, or pitch deck script.**")
    lines.append("")

    # 8. Next R&D Steps (Post–Day 59)
    lines.append("## 8. Next R&D Steps (Post–Day 59)")
    lines.append("")
    lines.append("- Phase 3 AI-Independence (Day 80–90 window):")
    lines.append("  - Design and test a full degraded-mode chain (cloud → backup → local).")
    lines.append("  - Explicit logging and tagging when degraded mode is used.")
    lines.append("")
    lines.append("- Continued GUI evolution:")
    lines.append("  - More rich minimap, charts, and overlays.")
    lines.append("  - Deck-friendly screenshot exports and overlays.")
    lines.append("")
    lines.append("- Mission-specific scenarios:")
    lines.append("  - AFTAC / Golden Dome nuclear scenario.")
    lines.append("  - Legal / bankruptcy / family law scenario for Shari.")
    lines.append("  - Sports team performance / injury risk demo (future).")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("_End of SBIR / demo outline export._")

    return "\n".join(lines)


def export_sbir_outline() -> str:
    base = Path(__file__).parent
    docs_dir = base / "docs"
    docs_dir.mkdir(exist_ok=True)

    out_path = docs_dir / "sbir_outline_day59.md"
    text = build_sbir_outline()
    out_path.write_text(text, encoding="utf-8")

    return f"[OK] SBIR / demo outline exported → {out_path}"


if __name__ == "__main__":
    print(export_sbir_outline())

