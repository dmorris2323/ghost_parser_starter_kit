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
 27) Golden Dome Validator
 28) Test Spectral Owl Fallback Mode
 29) Golden Dome Drift Report
 30) Sensor Reliability Trendline
 31) Owl Confidence Estimator
 32) Crisis Mode Toggle
 33) Set Operator Name
"""

import sys
import subprocess
from pathlib import Path

from operator_snapshot import build_operator_snapshot
from pipeline_health import evaluate_pipeline_health
from mission_briefing import build_mission_briefing
from generate_daily_visual_pack import main as build_daily_pack
from profile_status import build_profile_status
from legal_ingest_family_law import main as ingest_family_law
from family_law_scoring import main as score_family_law
from family_law_brief import main as brief_family_law
from cloud.azure_ingest import (
    upload_fusion_output,
    list_fusion_blobs,
    download_latest_fusion_archive,
    cloud_sync_health_check,
)
from golden_dome_drift import write_drift
from spectral_owl.owl_confidence import compute_confidence
from crisis_mode_flag import status as crisis_status
from operator_identity import get_identity

LOG_FILE = Path("fusion_ops_log.csv")


def run_script(script_path: str):
    """Safely run a Python script in this src folder."""
    try:
        result = subprocess.run([sys.executable, script_path])
        if result.returncode != 0:
            print(f"[WARN] Script {script_path} exited with code {result.returncode}.")
    except FileNotFoundError:
        print(f"[ERROR] Script not found: {script_path}")


def print_menu():
    print("\n=== Ghost Lantern Labs — Operator Console ===")
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
    print(" 27) Golden Dome Validator")
    print(" 28) Test Spectral Owl Fallback Mode")
    print(" 29) Golden Dome Drift Report")
    print(" 30) Sensor Reliability Trendline")
    print(" 31) Owl Confidence Estimator")
    print(" 32) Crisis Mode Toggle")
    print(" 33) Set Operator Name")
    print("============================================")
    print(f"Operator: {get_identity()} | Crisis Mode: {crisis_status()}")
    print("")


def main():
    while True:
        print_menu()
        choice = input("Select an option: ").strip()

        if choice == "1":
            run_script("qa_validator.py")

        elif choice == "2":
            if LOG_FILE.exists():
                lines = LOG_FILE.read_text().splitlines()
                tail = lines[-20:] if len(lines) > 20 else lines
                print("\n=== Last 20 fusion_ops_log events ===")
                for line in tail:
                    print(line)
                print("=====================================\n")
            else:
                print(f"No log file found at {LOG_FILE}")

        elif choice == "3":
            path = build_operator_snapshot()
            print(f"Operator snapshot written to: {path}")

        elif choice == "4":
            print("[INFO] Running fusion pipeline…")
            run_script("fusion_run.py")
            print("[INFO] Building operator snapshot…")
            path = build_operator_snapshot()
            print(f"Operator snapshot written to: {path}")

        elif choice == "5":
            run_script("spectral_owl/owl_memory.py")

        elif choice == "6":
            run_script("spectral_owl/owl_brain_phase2.py")

        elif choice == "7":
            result = evaluate_pipeline_health()
            print("\n=== Pipeline Health ===")
            print(result)
            print("=======================\n")

        elif choice == "8":
            brief = build_mission_briefing()
            print("\n=== Mission Brief ===")
            print(brief)
            print("=====================\n")

        elif choice == "9":
            print("Exiting Ghost Lantern Labs console.")
            sys.exit(0)

        elif choice == "10":
            run_script("anti_dos.py")

        elif choice == "11":
            print("\n[Cloud Sync Check]\n")
            health = cloud_sync_health_check()
            print(f"Health: {health}")

            scored = Path("data/scored_output.csv")
            if scored.exists():
                print("\n[Cloud] Uploading scored_output.csv…")
                result = upload_fusion_output(str(scored))
                print(f"Upload result: {result}")
            else:
                print("\nNo data/scored_output.csv found. Skipping upload test.")

            listing = list_fusion_blobs()
            print(f"\nCloud archive listing: {listing}")

        elif choice == "12":
            run_script("spectral_owl/threat_memory_summary.py")

        elif choice == "13":
            path = build_daily_pack()
            print(f"Daily visual pack built: {path}")

        elif choice == "14":
            status = build_profile_status()
            print("\n=== Active Profile Status ===")
            print(status)
            print("=============================\n")

        elif choice == "15":
            print("[Family Law Demo] Ingesting cases…")
            ingest_family_law()
            print("[Family Law Demo] Scoring cases…")
            score_family_law()
            print("[Family Law Demo] Building brief…")
            brief_family_law()
            print("Family Law Demo complete. See docs/family_law_demo/ outputs if present.")

        elif choice == "16":
            run_script("spectral_owl/owl_memory.py")

        elif choice == "17":
            run_script("spectral_dashboard_api.py")

        elif choice == "18":
            run_script("mission_brief_html.py")

        elif choice == "19":
            run_script("fusion_minimap_overlay.py")

        elif choice == "20":
            run_script("spectral_sos_overlay.py")

        elif choice == "21":
            run_script("run_history_intel.py")

        elif choice == "22":
            run_script("spectral_snapshot_export.py")

        elif choice == "23":
            run_script("demo_deck_manifest.py")

        elif choice == "24":
            run_script("sensor_reliability.py")

        elif choice == "25":
            run_script("cross_sensor_validator.py")
            run_script("cross_sensor_report.py")

        elif choice == "26":
            run_script("sbir_onepager.py")

        elif choice == "27":
            run_script("golden_dome_validator.py")

        elif choice == "28":
            run_script("spectral_fallback_tree.py")

        elif choice == "29":
            path = write_drift()
            print(f"Golden Dome drift report written to: {path}")
            p = Path(path)
            if p.exists():
                print("\n=== Golden Dome Drift ===")
                print(p.read_text())
                print("=========================\n")
            else:
                print("Drift report path exists in return but file not found on disk.")

        elif choice == "30":
            try:
                from reliability_trend import compute_trend
                out = compute_trend()
                print("\n=== Sensor Reliability Trendline ===")
                print(out)
                print("====================================\n")
            except Exception as e:
                print(f"[ERROR] Reliability trend failed: {e}")

        elif choice == "31":
            sample = {"critical_alerts": 1, "warning_alerts": 4, "avg_reliability": 92}
            print("\n=== Owl Confidence Estimator ===")
            print("Input:", sample)
            print("Confidence:", compute_confidence(sample))
            print("================================\n")

        elif choice == "32":
            from crisis_mode_flag import enable, disable, status
            print(f"Current: {status()}")
            ch = input("Turn ON or OFF? ").strip().lower()
            if ch == "on":
                print(enable())
            elif ch == "off":
                print(disable())
            else:
                print("Invalid.")

        elif choice == "33":
            from operator_identity import set_identity
            nm = input("Enter operator name: ").strip()
            print(set_identity(nm))

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()

