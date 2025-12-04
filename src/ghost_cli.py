"""
ghost_cli.py — Ghost Lantern Labs Operator Console
--------------------------------------------------

Menu options:
  1) Run QA validation
  2) Show latest 20 log events
  3) Build operator snapshot
  4) Run full fusion pipeline + snapshot
  5) Spectral Owl memory viewer
  6) Spectral Owl analysis (fusion scoring check)
  7) Pipeline health check
  8) Mission briefing (profile-aware)
  9) Exit
 10) Anti-DoS environment scan
 11) Cloud Sync Check
 12) Threat Memory Summary
 13) Build Daily Visual Pack
 14) Show Active Profile Status
 15) Run Family Law Demo (Shari)
 16) Owl Memory Diagnostics
 17) Spectral Dashboard Export
 18) Mission Brief HTML Generator
 19) Export GUI Minimap Overlay
 20) Export SOS Overlay
 21) Run-History Intelligence Timeline
 22) Export Spectral Snapshot Bundle
 23) Build Demo Deck Manifest
 24) Export Sensor Reliability Report
 25) Cross-Sensor Validation + Report
 26) Generate SBIR Phase I One-Pager
"""

import sys
import subprocess
from pathlib import Path

# === CORE IMPORTS =================================
from operator_snapshot import build_operator_snapshot
from pipeline_health import evaluate_pipeline_health
from mission_briefing import build_mission_briefing
from profile_status import build_profile_status
from generate_daily_visual_pack import main as build_daily_pack
from spectral_owl.threat_memory_summary import build_summary as build_threat_summary
from cloud.azure_ingest import upload_fusion_output
from fusion_minimap_overlay import export_gui_minimap
from spectral_sos_overlay import export_sos_overlay
from run_history_intel import main as run_history_timeline
from demo_deck_manifest import build_demo_deck_manifest
from sensor_reliability import export_reliability_report
from cross_sensor_validator import run_cross_validation
from cross_sensor_report import build_report
from sbir_onepager import write_onepager


LOG_FILE = Path("fusion_ops_log.csv")


# ==================================================
def show_logs():
    if not LOG_FILE.exists():
        return "[No fusion_ops_log.csv file present]"
    lines = LOG_FILE.read_text().strip().split("\n")
    last = lines[-20:]
    return "\n".join(last)


def menu():
    print("")
    print("=== GHOST LANTERN LABS — OPERATOR CONSOLE ===")
    print("---------------------------------------------")
    print("  1) Run QA validation")
    print("  2) Show latest 20 log events")
    print("  3) Build operator snapshot")
    print("  4) Run full fusion pipeline + snapshot")
    print("  5) Spectral Owl memory viewer")
    print("  6) Spectral Owl analysis (fusion scoring check)")
    print("  7) Pipeline health check")
    print("  8) Mission briefing (profile-aware)")
    print("  9) Exit")
    print(" 10) Anti-DoS environment scan")
    print(" 11) Cloud Sync Check")
    print(" 12) Threat Memory Summary")
    print(" 13) Build Daily Visual Pack")
    print(" 14) Show Active Profile Status")
    print(" 15) Run Family Law Demo (Shari)")
    print(" 16) Owl Memory Diagnostics")
    print(" 17) Spectral Dashboard Export")
    print(" 18) Mission Brief HTML Generator")
    print(" 19) Export GUI Minimap Overlay")
    print(" 20) Export SOS Overlay")
    print(" 21) Run-History Intelligence Timeline")
    print(" 22) Export Spectral Snapshot Bundle")
    print(" 23) Build Demo Deck Manifest")
    print(" 24) Export Sensor Reliability Report")
    print(" 25) Cross-Sensor Validation + Report")
    print(" 26) Generate SBIR Phase I One-Pager")
    print("")


def main():
    while True:
        menu()
        choice = input("Select an option: ").strip()

        # === EXIT ==========================================
        if choice == "9":
            print("Exiting GLL Operator Console.")
            sys.exit(0)

        # === 1) QA VALIDATION ==============================
        elif choice == "1":
            from qa_validator import run_all_checks
            print(run_all_checks())

        # === 2) SHOW LOGS ==================================
        elif choice == "2":
            print(show_logs())

        # === 3) SNAPSHOT ===================================
        elif choice == "3":
            out = build_operator_snapshot()
            print(f"Snapshot built: {out}")

        # === 4) FULL PIPELINE ==============================
        elif choice == "4":
            subprocess.run(["python", "fusion_ingest.py"])
            out = build_operator_snapshot()
            print(f"Full pipeline + snapshot complete: {out}")

        # === 5) OWL MEMORY VIEWER ==========================
        elif choice == "5":
            from spectral_owl.owl_memory import load_memory_log
            mem = load_memory_log()
            print(mem)

        # === 6) OWL ANALYSIS ===============================
        elif choice == "6":
            from spectral_owl.owl_brain import analyze_fusion
            out = analyze_fusion()
            print(out)

        # === 7) PIPELINE HEALTH ============================
        elif choice == "7":
            print(evaluate_pipeline_health())

        # === 8) MISSION BRIEF ==============================
        elif choice == "8":
            print(build_mission_briefing())

        # === 10) ANTI-DOS SCAN =============================
        elif choice == "10":
            from anti_dos import run_anti_dos_scan
            print(run_anti_dos_scan())

        # === 11) CLOUD SYNC ================================
        elif choice == "11":
            print(upload_fusion_output())

        # === 12) THREAT MEMORY SUMMARY =====================
        elif choice == "12":
            print(build_threat_summary())

        # === 13) DAILY VISUAL PACK =========================
        elif choice == "13":
            print(build_daily_pack())

        # === 14) PROFILE STATUS ============================
        elif choice == "14":
            print(build_profile_status())

        # === 15) FAMILY LAW DEMO ===========================
        elif choice == "15":
            from legal_ingest_family_law import main as ingest
            from family_law_scoring import main as score
            from family_law_brief import main as brief
            ingest()
            score()
            brief()
            print("Family law demo complete.")

        # === 16) OWL MEMORY DIAGNOSTICS ====================
        elif choice == "16":
            from spectral_owl.owl_memory import diagnostics
            print(diagnostics())

        # === 17) DASHBOARD EXPORT ==========================
        elif choice == "17":
            from spectral_dashboard_api import build_dashboard_bundle
            print(build_dashboard_bundle())

        # === 18) HTML BRIEF ================================
        elif choice == "18":
            subprocess.run(["python", "mission_brief_html.py"])

        # === 19) MINIMAP EXPORT =============================
        elif choice == "19":
            print(export_gui_minimap())

        # === 20) SOS OVERLAY ================================
        elif choice == "20":
            print(export_sos_overlay())

        # === 21) RUN-HISTORY TIMELINE =======================
        elif choice == "21":
            print(run_history_timeline())

        # === 22) SPECTRAL SNAPSHOT BUNDLE ===================
        elif choice == "22":
            from spectral_snapshot_bundle import export_snapshot_bundle
            print(export_snapshot_bundle())

        # === 23) DEMO DECK MANIFEST =========================
        elif choice == "23":
            print(build_demo_deck_manifest())

        # === 24) RELIABILITY REPORT =========================
        elif choice == "24":
            print(export_reliability_report())

        # === 25) CROSS-SENSOR VALIDATION ====================
        elif choice == "25":
            print(run_cross_validation())
            print(build_report())

        # === 26) SBIR ONE-PAGER =============================
        elif choice == "26":
            out = write_onepager()
            print(f"SBIR One-Pager written to: {out}")

        else:
            print("Invalid selection. Try again.")


if __name__ == "__main__":
    main()

