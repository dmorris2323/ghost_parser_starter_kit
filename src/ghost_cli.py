"""
ghost_cli.py — Ghost Lantern Labs Operator Console
VERSION: Day 54 — Snapshot + Health Integrated

This CLI now provides:
  1) QA validation
  2) Latest logs
  3) Operator snapshot (real)
  4) Full fusion pipeline (stub hook)
  5) Spectral Owl memory view
  6) Spectral Owl analysis
  7) Pipeline health check (real)
  8) Mission brief (stub — future)
  9) Exit
 10) Anti-DoS scan (stub)
 11) Cloud Sync Check (real)
 12) Threat Memory Summary (real)
"""

import sys
from pathlib import Path

from qa_validator import run_all_tests
from cloud.azure_ingest import (
    upload_fusion_output,
    list_fusion_blobs,
    download_latest_fusion_archive,
    cloud_sync_health_check,
)
from operator_snapshot import build_operator_snapshot
from pipeline_health import evaluate_pipeline_health


# ======================================================
#  CORE FUNCTIONS
# ======================================================

def run_full_pipeline():
    print("\n[Pipeline Execution Placeholder]")
    print("Implement: scoring → extract → heatmap → alerts → report.\n")


def generate_operator_snapshot():
    print("\n=== BUILDING OPERATOR SNAPSHOT ===")
    snapshot_text = build_operator_snapshot()
    print(snapshot_text)
    print("=== SNAPSHOT WRITTEN TO operator_snapshot.txt ===\n")


def show_latest_logs():
    log_path = Path("logs/fusion.log")
    if not log_path.exists():
        print("\nNo logs found.\n")
        return

    lines = log_path.read_text(encoding="utf-8").splitlines()
    tail = lines[-20:] if len(lines) > 20 else lines

    print("\n=== LATEST LOG EVENTS ===")
    for l in tail:
        print(l)
    print("================================\n")


def view_owl_memory():
    mem = Path("data/threat_memory.csv")
    if not mem.exists():
        print("\nNo threat memory recorded yet.\n")
        return

    print("\n=== SPECTRAL OWL MEMORY ===")
    print(mem.read_text(encoding="utf-8"))
    print("================================\n")


def run_owl_analysis():
    print("\n=== OWL ANALYSIS ===")
    from spectral_owl.owl_brain import analyze_fusion
    result = analyze_fusion("scored_output.csv")
    print(result)
    print("================================\n")


def pipeline_health_check():
    print("\n=== PIPELINE HEALTH CHECK ===")
    summary = evaluate_pipeline_health()
    print(f"Health Score: {summary['score']}/100")
    print(f"Status: {summary['status']}")
    print(f"QA Passed: {summary['qa_passed']}, QA Failed: {summary['qa_failed']}")
    print(f"Critical Alerts: {summary['critical_alerts']}")
    print(f"Notes: {summary['notes']}")
    print("Full report: pipeline_health.txt")
    print("================================\n")


def mission_briefing():
    print("\n=== MISSION BRIEF (Placeholder) ===")
    print("Future: integrate QA, Owl, pipeline health, alerts, and threat memory into one brief.")
    print("====================================\n")


def anti_dos_environment_scan():
    print("\n=== ANTI-DoS SCAN (Placeholder) ===")
    print("Wire this to anti_dos.py + log_intel.py for real anomaly scans.")
    print("====================================\n")


def cloud_sync_menu():
    print("\n=== CLOUD SYNC CHECK ===")
    health = cloud_sync_health_check()
    print(f"Health: {health}")

    scored = Path("data/scored_output.csv")
    if scored.exists():
        print("\nUploading fusion output → simulated cloud archive...")
        result = upload_fusion_output(str(scored))
        print(result)
    else:
        print("\nNo scored_output.csv detected — skipping upload.")

    listing = list_fusion_blobs()
    print(f"\nCloud Archive Listing: {listing}\n")


def threat_memory_summary_menu():
    print("\n=== THREAT MEMORY SUMMARY ===")
    from spectral_owl.threat_memory_summary import build_summary
    print(build_summary())
    print("================================\n")


# ======================================================
#  MENU UI
# ======================================================

def print_menu():
    print("\n===========================================")
    print("           GHOST LANTERN LABS CLI           ")
    print("===========================================")
    print(" 1) Run QA Validation")
    print(" 2) Show Latest Logs")
    print(" 3) Generate Operator Snapshot")
    print(" 4) Run Full Fusion Pipeline")
    print(" 5) View Spectral Owl Memory")
    print(" 6) Run Spectral Owl Analysis")
    print(" 7) Pipeline Health Check")
    print(" 8) Mission Brief")
    print(" 9) Exit")
    print("10) Anti-DoS Scan")
    print("11) Cloud Sync Check")
    print("12) Threat Memory Summary")
    print("===========================================\n")


# ======================================================
#  MAIN LOOP
# ======================================================

def main():
    while True:
        print_menu()
        choice = input("Select option: ").strip()

        if choice == "1":
            run_qa()
        elif choice == "2":
            show_latest_logs()
        elif choice == "3":
            generate_operator_snapshot()
        elif choice == "4":
            run_full_pipeline()
        elif choice == "5":
            view_owl_memory()
        elif choice == "6":
            run_owl_analysis()
        elif choice == "7":
            pipeline_health_check()
        elif choice == "8":
            mission_briefing()
        elif choice == "9":
            print("\nExiting Ghost CLI.")
            sys.exit(0)
        elif choice == "10":
            anti_dos_environment_scan()
        elif choice == "11":
            cloud_sync_menu()
        elif choice == "12":
            threat_memory_summary_menu()
        else:
            print("\nInvalid selection.\n")


def run_qa():
    print("\nRunning QA Suite...\n")
    summary = run_all_tests()
    print(summary)
    print("\nQA Complete.\n")


if __name__ == "__main__":
    main()

