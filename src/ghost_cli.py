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
"""

import sys
import subprocess
from pathlib import Path

# Core system pieces
from operator_snapshot import build_operator_snapshot
from pipeline_health import evaluate_pipeline_health
from mission_briefing import build_mission_briefing
from profile_mission_brief import main as run_profile_mission_brief

# Spectral Owl
from spectral_owl.owl_brain import analyze_fusion
from spectral_owl.owl_memory import load_memory_log
from spectral_owl.threat_memory_summary import build_summary as build_threat_summary

# Visual/demo packs
from generate_daily_visual_pack import main as build_daily_pack
from profile_status import build_profile_status
from legal_demo_pack import main as run_family_law_demo

# Cloud + overlays + dashboard
from cloud.azure_ingest import (
    upload_fusion_output,
    list_fusion_blobs,
    download_latest_fusion_archive,
    cloud_sync_health_check,
)
from spectral_dashboard_api import build_dashboard_bundle
from fusion_minimap_overlay import export_gui_minimap
from spectral_snapshot_bundle import build_snapshot_bundle

# 🔧 SAFE IMPORT FOR SOS OVERLAY
try:
    from spectral_sos_overlay import export_gui_sos_overlay
except ImportError:
    def export_gui_sos_overlay():
        return "SOS overlay exporter not available (spectral_sos_overlay.export_gui_sos_overlay missing)."

# Run-history intel
from run_history_intel import main as run_history_intel

# HTML brief
from mission_brief_html import main as build_mission_brief_html


BASE_DIR = Path(__file__).parent
LOG_FILE = BASE_DIR / "fusion_ops_log.csv"


def run_cmd(cmd, cwd=None):
    """Small helper to run a subprocess and print its output."""
    result = subprocess.run(
        [sys.executable] + cmd,
        cwd=cwd or BASE_DIR,
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())
    return result.returncode


def show_menu():
    print("\n=== Ghost Lantern Labs — Operator Console ===")
    print(" 1) Run QA validation")
    print(" 2) Show latest 20 log events")
    print(" 3) Build operator snapshot")
    print(" 4) Run full fusion pipeline + snapshot")
    print(" 5) Spectral Owl memory viewer")
    print(" 6) Spectral Owl analysis (fusion scoring check)")
    print(" 7) Pipeline health check")
    print(" 8) Mission briefing (profile-aware)")
    print(" 9) Exit")
    print("10) Anti-DoS environment scan")
    print("11) Cloud Sync Check")
    print("12) Threat Memory Summary")
    print("13) Build Daily Visual Pack")
    print("14) Show Active Profile Status")
    print("15) Run Family Law Demo (Shari)")
    print("16) Owl Memory Diagnostics")
    print("17) Spectral Dashboard Export")
    print("18) Mission Brief HTML Generator")
    print("19) Export GUI Minimap Overlay")
    print("20) Export SOS Overlay")
    print("21) Run-History Intelligence Timeline")
    print("22) Export Spectral Snapshot Bundle")
    print("=============================================")


def main():
    while True:
        show_menu()
        choice = input("Select an option: ").strip()

        if choice == "1":
            print("\n[QA Validation]\n")
            run_cmd(["qa_validator.py"])

        elif choice == "2":
            print("\n[Latest Log Events]\n")
            if not LOG_FILE.exists():
                print("No fusion_ops_log.csv found yet.")
            else:
                lines = LOG_FILE.read_text().strip().splitlines()
                for line in lines[-20:]:
                    print(line)

        elif choice == "3":
            print("\n[Operator Snapshot]\n")
            path = build_operator_snapshot()
            print(f"Snapshot written → {path}")

        elif choice == "4":
            print("\n[Full Fusion Pipeline + Snapshot]\n")
            run_cmd(["fusion_run.py"])
            path = build_operator_snapshot()
            print(f"Snapshot written → {path}")

        elif choice == "5":
            print("\n[Spectral Owl Memory Viewer]\n")
            try:
                events = load_memory_log()
            except Exception as e:
                print(f"Error loading Owl memory: {e}")
                events = []

            if not events:
                print("No Owl memory events yet.")
            else:
                print("Last 20 events:")
                for e in events[-20:]:
                    print(f"- {e}")

        elif choice == "6":
            print("\n[Spectral Owl Analysis]\n")
            try:
                result = analyze_fusion()
                print(result)
            except Exception as e:
                print(f"Error running Spectral Owl analysis: {e}")

        elif choice == "7":
            print("\n[Pipeline Health Check]\n")
            try:
                health = evaluate_pipeline_health()
                print(health)
            except Exception as e:
                print(f"Error evaluating pipeline health: {e}")

        elif choice == "8":
            print("\n[Mission Briefing — Profile-Aware]\n")
            try:
                run_profile_mission_brief()
            except Exception as e:
                print(f"Error building mission brief: {e}")

        elif choice == "9":
            print("Exiting Ghost CLI. Stay lethal.")
            break

        elif choice == "10":
            print("\n[Anti-DoS Environment Scan]\n")
            code = run_cmd(["anti_dos.py"])
            if code != 0:
                print("Anti-DoS scan encountered an error.")

        elif choice == "11":
            print("\n[Cloud Sync Check]\n")
            try:
                health = cloud_sync_health_check()
                print(f"Health: {health}")
            except Exception as e:
                print(f"Cloud health check failed: {e}")

            scored = BASE_DIR / "data" / "scored_output.csv"
            if scored.exists():
                try:
                    upload_result = upload_fusion_output(str(scored))
                    print(f"\nUpload result: {upload_result}")
                except Exception as e:
                    print(f"Upload failed: {e}")
            else:
                print("\nNo data/scored_output.csv found. Skipping upload test.")

            try:
                listing = list_fusion_blobs()
                print(f"\nCloud archive listing: {listing}")
            except Exception as e:
                print(f"Listing archive failed: {e}")

        elif choice == "12":
            print("\n[Threat Memory Summary]\n")
            try:
                summary = build_threat_summary()
                print(summary)
            except Exception as e:
                print(f"Error building threat memory summary: {e}")

        elif choice == "13":
            print("\n[Build Daily Visual Pack]\n")
            try:
                result = build_daily_pack()
                print(result)
            except Exception as e:
                print(f"Error building daily visual pack: {e}")

        elif choice == "14":
            print("\n[Active Profile Status]\n")
            try:
                status = build_profile_status()
                print(status)
            except Exception as e:
                print(f"Error getting profile status: {e}")

        elif choice == "15":
            print("\n[Family Law Demo — Shari]\n")
            try:
                result = run_family_law_demo()
                print(result)
            except Exception as e:
                print(f"Error running family law demo: {e}")

        elif choice == "16":
            print("\n[Owl Memory Diagnostics]\n")
            code = run_cmd(["threat_memory_stats.py"])
            if code != 0:
                print("Owl memory diagnostics encountered an error.")

        elif choice == "17":
            print("\n[Spectral Dashboard Export]\n")
            try:
                bundle = build_dashboard_bundle()
                out_file = BASE_DIR / "docs" / "spectral_dashboard_bundle.json"
                out_file.parent.mkdir(exist_ok=True, parents=True)
                import json
                out_file.write_text(json.dumps(bundle, indent=2))
                print(f"Spectral dashboard bundle written to: {out_file}")
            except Exception as e:
                print(f"Error building dashboard bundle: {e}")

        elif choice == "18":
            print("\n[Mission Brief HTML Generator]\n")
            try:
                result = build_mission_brief_html()
                print(result)
            except Exception as e:
                print(f"Error building HTML mission brief: {e}")

        elif choice == "19":
            print("\n[Export GUI Minimap Overlay]\n")
            try:
                result = export_gui_minimap()
                print(result)
            except Exception as e:
                print(f"Error exporting GUI minimap overlay: {e}")

        elif choice == "20":
            print("\n[Export SOS Overlay]\n")
            try:
                result = export_gui_sos_overlay()
                print(result)
            except Exception as e:
                print(f"Error exporting SOS overlay: {e}")

        elif choice == "21":
            print("\n[Run-History Intelligence Timeline]\n")
            try:
                result = run_history_intel()
                print(result)
            except Exception as e:
                print(f"Error running run-history intelligence: {e}")

        elif choice == "22":
            print("\n[Export Spectral Snapshot Bundle]\n")
            try:
                bundle = build_snapshot_bundle()
                out_file = BASE_DIR / "docs" / "spectral_snapshot_bundle.json"
                print(f"Spectral snapshot bundle written to: {out_file}")
            except Exception as e:
                print(f"Error building spectral snapshot bundle: {e}")

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()

