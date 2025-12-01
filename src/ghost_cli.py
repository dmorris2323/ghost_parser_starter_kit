"""
ghost_cli.py — Ghost Lantern Labs Operator Console
--------------------------------------------------

Menu options:
  1) Run QA validation
  2) Show latest 20 log events (fusion_ops_log.csv if present)
  3) Build operator snapshot
  4) Run full fusion pipeline + snapshot
  5) Spectral Owl memory viewer
  6) Spectral Owl analysis (fusion scoring check)
  7) Pipeline health check
  8) Mission briefing
  9) Exit
 10) Anti-DoS environment scan
 11) Cloud Sync Check
 12) Threat Memory Summary
 13) Build Daily Visual Pack (demos/day56)
 14) Show Active Profile Status
 15) Run Family Law Demo (Shari)
"""

import subprocess
import sys
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
from cloud.azure_ingest import (
    upload_fusion_output,
    list_fusion_blobs,
    cloud_sync_health_check,
)


def run_cmd(args):
    """Helper to run a script as a subprocess."""
    subprocess.run([sys.executable] + list(args))


def menu():
    print("====================================")
    print("   GHOST LANTERN LABS — GHOST CLI   ")
    print("====================================")
    print(" 1) Run QA validation")
    print(" 2) Show latest 20 log events")
    print(" 3) Build operator snapshot")
    print(" 4) Run full fusion pipeline + snapshot")
    print(" 5) Spectral Owl memory viewer")
    print(" 6) Spectral Owl analysis (fusion scoring check)")
    print(" 7) Pipeline health check")
    print(" 8) Mission briefing")
    print(" 9) Exit")
    print("10) Anti-DoS environment scan")
    print("11) Cloud Sync Check")
    print("12) Threat Memory Summary")
    print("13) Build Daily Visual Pack (demos/day56)")
    print("14) Show Active Profile Status")
    print("15) Run Family Law Demo (Shari)")
    print("====================================")


def handle_choice(choice: str) -> bool:
    """
    Returns False to exit, True to continue.
    """
    if choice == "1":
        print("\n=== QA VALIDATION ===\n")
        run_cmd(["qa_validator.py"])
        print("\n=====================\n")
        return True

    if choice == "2":
        print("\n=== LATEST LOG EVENTS ===\n")
        log_path = Path("fusion_ops_log.csv")
        if not log_path.exists():
            print("No fusion_ops_log.csv found.")
        else:
            lines = log_path.read_text(encoding="utf-8").splitlines()
            tail = lines[-20:]
            for line in tail:
                print(line)
        print("\n=========================\n")
        return True

    if choice == "3":
        print("\n=== OPERATOR SNAPSHOT ===\n")
        text = build_operator_snapshot()
        print(text)
        print("\n[OK] operator_snapshot.txt updated.\n")
        print("===================================\n")
        return True

    if choice == "4":
        print("\n=== FULL PIPELINE + SNAPSHOT ===\n")
        run_cmd(["fusion_run.py"])
        text = build_operator_snapshot()
        print(text)
        print("\n[OK] Full pipeline run plus operator snapshot.\n")
        print("=============================================\n")
        return True

    if choice == "5":
        print("\n=== SPECTRAL OWL MEMORY VIEWER ===\n")
        mem_path = Path("owl_memory.txt")
        if not mem_path.exists():
            print("No owl_memory.txt found.")
        else:
            print(mem_path.read_text(encoding="utf-8"))
        print("\n=================================\n")
        return True

    if choice == "6":
        print("\n=== SPECTRAL OWL ANALYSIS ===\n")
        # rely on owl_brain module CLI behavior
        run_cmd(["-m", "spectral_owl.owl_brain"])
        print("\n================================\n")
        return True

    if choice == "7":
        print("\n=== PIPELINE HEALTH CHECK ===\n")
        health = evaluate_pipeline_health()
        for k, v in health.items():
            print(f"{k}: {v}")
        print("\n=============================\n")
        return True

    if choice == "8":
        print("\n=== MISSION BRIEFING ===\n")
        text = build_mission_briefing()
        print(text)
        print("\n[OK] Mission briefing complete.\n")
        print("================================\n")
        return True

    if choice == "9":
        print("\nExiting Ghost CLI. Goodbye.\n")
        return False

    if choice == "10":
        print("\n=== ANTI-DOS ENVIRONMENT SCAN ===\n")
        run_cmd(["anti_dos.py"])
        print("\n=================================\n")
        return True

    if choice == "11":
        print("\n=== CLOUD SYNC CHECK ===\n")
        health = cloud_sync_health_check()
        print(f"Health: {health}")

        scored = Path("data/scored_output.csv")
        if scored.exists():
            print(f"\nFound fusion output at {scored}, attempting simulated upload...")
            upload_result = upload_fusion_output(str(scored))
            print(f"Upload result: {upload_result}")
        else:
            print("\nNo data/scored_output.csv found. Skipping upload test.")

        listing = list_fusion_blobs()
        print(f"\nCloud archive listing: {listing}")
        print("\n========================\n")
        return True

    if choice == "12":
        print("\n=== THREAT MEMORY SUMMARY ===\n")
        summary = build_threat_summary()
        print(summary)
        print("\n================================\n")
        return True

    if choice == "13":
        print("\n=== BUILDING DAILY VISUAL PACK ===\n")
        build_daily_pack()
        print("\n=== DAILY VISUAL PACK COMPLETE ===\n")
        return True

    if choice == "14":
        print("\n=== ACTIVE PROFILE STATUS ===\n")
        print(build_profile_status())
        print("\n=============================\n")
        return True

    if choice == "15":
        print("\n=== FAMILY LAW DEMO (SHARI) ===\n")
        ingest_family_law()
        score_family_law()
        brief_family_law()
        print("\n[OK] Family law demo complete. See family_law_brief.txt\n")
        print("=========================================\n")
        return True

    print("\nUnrecognized option. Please choose a valid menu item.\n")
    return True


def main():
    while True:
        menu()
        try:
            choice = input("Select an option: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting Ghost CLI.")
            break
        if not handle_choice(choice):
            break


if __name__ == "__main__":
    main()

