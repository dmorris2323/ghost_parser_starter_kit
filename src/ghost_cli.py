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
  8) Mission briefing (text)
  9) Exit
 10) Anti-DoS environment scan
 11) Cloud Sync Check
 12) Threat Memory Summary
 13) Sensor Manifest Health Check
 14) Sensor Readiness Brief
 15) Switch Profile (Quick Select)
 16) Export Profile Mission Brief (text)
 17) Build Spectral Dashboard API Bundle
 18) Export HTML Mission Brief
 19) Export GUI Minimap Overlay
"""

import subprocess
import sys
from pathlib import Path

from qa_validator import run_all as run_qa
from operator_snapshot import build_operator_snapshot
from pipeline_health import evaluate_pipeline_health
from mission_briefing import build_mission_briefing
from spectral_owl.threat_memory_summary import build_summary as build_threat_summary
from generate_daily_visual_pack import main as build_daily_pack
from profile_status import build_profile_status
from legal_ingest_family_law import main as ingest_family_law
from family_law_scoring import main as score_family_law
from family_law_brief import main as brief_family_law
from manifest_health import run_manifest_health
from sensor_readiness_brief import build_readiness_brief
from profile_auto_switch import auto_switch
from profile_mission_brief import build_profile_mission_brief
from spectral_dashboard_api import build_dashboard_bundle
from mission_brief_html import build_html_brief
from fusion_minimap_overlay import export_gui_minimap

MENU = """
============================================
🔱 Ghost Lantern Labs — Operator Console
============================================

  1) Run QA validation
  2) Show latest 20 log events
  3) Build operator snapshot
  4) Run full fusion pipeline + snapshot
  5) Spectral Owl memory viewer
  6) Spectral Owl analysis (fusion scoring check)
  7) Pipeline health check
  8) Mission briefing (text)
  9) Exit
 10) Anti-DoS environment scan
 11) Cloud Sync Check
 12) Threat Memory Summary
 13) Sensor Manifest Health Check
 14) Sensor Readiness Brief
 15) Switch Profile (Quick Select)
 16) Export Profile Mission Brief (text)
 17) Build Spectral Dashboard API Bundle
 18) Export HTML Mission Brief
 19) Export GUI Minimap Overlay
"""

LOGFILE = Path("fusion_ops_log.csv")


def show_latest_logs():
    if not LOGFILE.exists():
        return "[NO LOG FILE FOUND]"
    lines = LOGFILE.read_text().splitlines()
    return "\n".join(lines[-20:])


def run_pipeline():
    """Run ingest → scoring → sanitizer → snapshot"""
    cmds = [
        ["python", "fusion_ingest.py"],
        ["python", "fusion_scoring.py"],
        ["python", "fusion_sanitizer.py"],
    ]
    for cmd in cmds:
        subprocess.run(cmd)
    snap = build_operator_snapshot()
    return {"status": "pipeline_complete", "snapshot": snap}


def show_memory():
    from spectral_owl.owl_memory import load_memory_log
    mem = load_memory_log()
    return "\n".join(mem) if mem else "[NO MEMORY LOG]"


def full_spectral_analysis():
    from spectral_owl.owl_brain import analyze_fusion
    out = analyze_fusion()
    return out


def main():
    while True:
        print(MENU)
        choice = input("Select an option: ").strip()

        if choice == "1":
            print(run_qa())

        elif choice == "2":
            print(show_latest_logs())

        elif choice == "3":
            print(build_operator_snapshot())

        elif choice == "4":
            print(run_pipeline())

        elif choice == "5":
            print(show_memory())

        elif choice == "6":
            print(full_spectral_analysis())

        elif choice == "7":
            print(evaluate_pipeline_health())

        elif choice == "8":
            print(build_mission_briefing())

        elif choice == "9":
            print("Exiting...")
            sys.exit(0)

        elif choice == "10":
            from anti_dos import run_anti_dos_scan
            print(run_anti_dos_scan())

        elif choice == "11":
            from cloud.azure_ingest import upload_fusion_output
            print(upload_fusion_output())

        elif choice == "12":
            print(build_threat_summary())

        elif choice == "13":
            print(run_manifest_health())

        elif choice == "14":
            print(build_readiness_brief())

        elif choice == "15":
            domain = input("Enter domain (nuclear/sports/legal/soc): ").strip()
            print(auto_switch(domain))

        elif choice == "16":
            print(build_profile_mission_brief())

        elif choice == "17":
            print(build_dashboard_bundle())

        elif choice == "18":
            print(build_html_brief())

        elif choice == "19":
            print(export_gui_minimap())

        else:
            print("Invalid selection. Try again.")


if __name__ == "__main__":
    main()

