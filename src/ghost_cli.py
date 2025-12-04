"""
ghost_cli.py — Ghost Lantern Labs Operator Console
FULL WORKING VERSION (Options 1–28)
"""

import sys
import subprocess
from pathlib import Path

from operator_snapshot import build_operator_snapshot
from pipeline_health import evaluate_pipeline_health
from mission_briefing import build_mission_briefing
from spectral_owl.threat_memory_summary import build_summary as build_threat_summary
from generate_daily_visual_pack import main as build_daily_pack
from profile_status import build_profile_status
from legal_ingest_family_law import main as ingest_family_law
from family_law_scoring import main as score_family_law
from family_law_brief import main as brief_family_law
from cloud.azure_ingest import upload_fusion_output
from spectral_owl.owl_brain_phase2 import analyze_fusion
from spectral_owl.owl_memory import load_memory_log
from spectral_dashboard_api import build_dashboard_bundle
from fusion_minimap_overlay import export_gui_minimap
from spectral_sos_overlay import build_sos_overlay
from run_history_intel import main as intel_timeline
from spectral_snapshot_export import export_spectral_snapshot
from demo_deck_manifest import build_demo_deck_manifest
from golden_dome_validator import build_validation
from spectral_fallback_tree import build_fallback_response


def menu():
    print("""
Ghost Lantern Labs — Operator Console
-------------------------------------

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
""")

    return input("Select option: ").strip()


def main():
    while True:
        choice = menu()

        if choice == "1":
            subprocess.run(["python", "qa_validator.py"])

        elif choice == "2":
            path = Path("fusion_ops_log.csv")
            if not path.exists():
                print("No log file found.")
            else:
                lines = path.read_text().splitlines()
                print("\n".join(lines[-20:]))

        elif choice == "3":
            out = build_operator_snapshot()
            print(f"Snapshot built → {out}")

        elif choice == "4":
            subprocess.run(["python", "fusion_ingest.py"])
            out = build_operator_snapshot()
            print(f"Pipeline + Snapshot complete → {out}")

        elif choice == "5":
            log = load_memory_log()
            print(log)

        elif choice == "6":
            sample = {
                "critical_alerts": 0,
                "warning_alerts": 1,
                "avg_reliability": 95.1
            }
            print(analyze_fusion(sample))

        elif choice == "7":
            out = evaluate_pipeline_health()
            print(out)

        elif choice == "8":
            out = build_mission_briefing()
            print(out)

        elif choice == "9":
            print("Exiting.")
            sys.exit(0)

        elif choice == "10":
            subprocess.run(["python", "anti_dos.py"])

        elif choice == "11":
            upload_fusion_output()
            print("Cloud Sync Complete.")

        elif choice == "12":
            print(build_threat_summary())

        elif choice == "13":
            print(build_daily_pack())

        elif choice == "14":
            print(build_profile_status())

        elif choice == "15":
            ingest_family_law()
            score_family_law()
            print(brief_family_law())

        elif choice == "16":
            print("Owl Memory Diagnostics:")
            print(load_memory_log())

        elif choice == "17":
            out = build_dashboard_bundle()
            print(out)

        elif choice == "18":
            subprocess.run(["python", "mission_brief_html.py"])

        elif choice == "19":
            print(export_gui_minimap())

        elif choice == "20":
            out = build_sos_overlay()
            print(out)

        elif choice == "21":
            print(intel_timeline())

        elif choice == "22":
            print(export_spectral_snapshot())

        elif choice == "23":
            print(build_demo_deck_manifest())

        elif choice == "24":
            from sensor_reliability import export_reliability_report
            print(export_reliability_report())

        elif choice == "25":
            from cross_sensor_validator import run_cross_validation
            from cross_sensor_report import build_report
            print(run_cross_validation())
            print(build_report())

        elif choice == "26":
            from sbir_onepager import write_onepager
            out = write_onepager()
            print(f"SBIR One-Pager → {out}")

        elif choice == "27":
            out = build_validation()
            print(f"Golden Dome Validation → {out['path']}")

        elif choice == "28":
            sample = {
                "critical_alerts": 0,
                "warning_alerts": 3,
                "avg_reliability": 91.0
            }
            out = build_fallback_response(sample)
            print("=== Fallback Response ===")
            print(out)

        else:
            print("Invalid selection.")


if __name__ == "__main__":
    main()

