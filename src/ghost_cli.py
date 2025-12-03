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
"""

import sys
import subprocess
from pathlib import Path

# === CORE IMPORTS (modules you already have in src/) ===
from operator_snapshot import build_operator_snapshot
from pipeline_health import evaluate_pipeline_health
from mission_briefing import build_mission_briefing
from spectral_owl.threat_memory_summary import build_summary as build_threat_summary
from generate_daily_visual_pack import main as build_daily_visual_pack
from profile_status import build_profile_status
from profile_mission_brief import build_profile_mission_brief
from cloud.azure_ingest import cloud_sync_health_check, upload_fusion_output
from fusion_minimap_overlay import export_gui_minimap
from spectral_sos_overlay import export_sos_overlay
from run_history_intel import main as run_history_intel
from demo_deck_manifest import build_demo_deck_manifest
from gui_screenshot_export import export_screenshots
from spectral_dashboard_api import build_dashboard_bundle
from legal_ingest_family_law import main as ingest_family_law
from family_law_scoring import main as score_family_law
from family_law_brief import main as brief_family_law


def print_menu():
    print("\n=== GHOST LANTERN LABS — OPERATOR CONSOLE ===")
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
    print("==============================================")


def main():
    while True:
        print_menu()
        choice = input("\nSelect an option: ").strip()

        # 9) Exit
        if choice == "9":
            print("Exiting Ghost Lantern Console...")
            sys.exit(0)

        # 1) Run QA validation
        elif choice == "1":
            subprocess.run([sys.executable, "qa_validator.py"])

        # 2) Show latest 20 log events
        elif choice == "2":
            log = Path("fusion_ops_log.csv")
            if not log.exists():
                print("[WARN] fusion_ops_log.csv not found.")
            else:
                lines = log.read_text().strip().split("\n")
                print("\n".join(lines[-20:]))

        # 3) Build operator snapshot
        elif choice == "3":
            print(build_operator_snapshot())

        # 4) Run full fusion pipeline + snapshot
        elif choice == "4":
            print("[RUN] Fusion pipeline...")
            subprocess.run([sys.executable, "fusion_run.py"])
            print("[RUN] Building operator snapshot...")
            print(build_operator_snapshot())

        # 5) Spectral Owl memory viewer
        elif choice == "5":
            from spectral_owl.owl_memory import load_memory_log
            print(load_memory_log())

        # 6) Spectral Owl analysis (fusion scoring check)
        elif choice == "6":
            from spectral_owl.owl_brain_phase2 import analyze_fusion
            print(analyze_fusion())

        # 7) Pipeline health check
        elif choice == "7":
            print(evaluate_pipeline_health())

        # 8) Mission briefing (profile-aware)
        elif choice == "8":
            # Uses profile-aware mission brief wrapper
            print(build_profile_mission_brief())

        # 10) Anti-DoS environment scan
        elif choice == "10":
            subprocess.run([sys.executable, "anti_dos.py"])

        # 11) Cloud Sync Check
        elif choice == "11":
            health = cloud_sync_health_check()
            print(f"[Cloud Health] {health}")

            # Optional: simulate upload of scored_output if present
            scored = Path("data/scored_output.csv")
            if scored.exists():
                print("[Cloud] Found data/scored_output.csv — attempting simulated upload...")
                print(upload_fusion_output(str(scored)))
            else:
                print("[Cloud] No scored_output.csv found; skipping upload.")

        # 12) Threat Memory Summary
        elif choice == "12":
            print(build_threat_summary())

        # 13) Build Daily Visual Pack
        elif choice == "13":
            print(build_daily_visual_pack())

        # 14) Show Active Profile Status
        elif choice == "14":
            print(build_profile_status())

        # 15) Run Family Law Demo (Shari)
        elif choice == "15":
            print("[Family Law Demo] Ingesting case sample...")
            ingest_family_law()
            print("[Family Law Demo] Scoring outcomes...")
            score_family_law()
            print("[Family Law Demo] Building brief...")
            brief_family_law()
            print("[Family Law Demo] Complete — check family_law_demo pack in /src/demos/family_law_demo")

        # 16) Owl Memory Diagnostics
        elif choice == "16":
            from spectral_owl.owl_memory import load_memory_log
            mem = load_memory_log()
            if not mem:
                print("[Owl Memory] No entries found.")
            else:
                lines = mem.strip().split("\n")
                print(f"[Owl Memory] Total entries: {len(lines)}")
                print("Last 5 entries:")
                print("\n".join(lines[-5:]))

        # 17) Spectral Dashboard Export
        elif choice == "17":
            bundle = build_dashboard_bundle()
            print(bundle)

        # 18) Mission Brief HTML Generator
        elif choice == "18":
            # This will generate /src/docs/daily_mission_brief.html
            subprocess.run([sys.executable, "mission_brief_html.py"])

        # 19) Export GUI Minimap Overlay
        elif choice == "19":
            print(export_gui_minimap())

        # 20) Export SOS Overlay
        elif choice == "20":
            print(export_sos_overlay())

        # 21) Run-History Intelligence Timeline
        elif choice == "21":
            print(run_history_intel())

        # 22) Export Spectral Snapshot Bundle
        elif choice == "22":
            print(export_screenshots())

        # 23) Build Demo Deck Manifest
        elif choice == "23":
            print(build_demo_deck_manifest())

        else:
            print("[ERR] Invalid option.")


if __name__ == "__main__":
    main()

