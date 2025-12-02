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
 13) Sensor Manifest Health Check
 14) Sensor Readiness Brief
 15) Switch Profile (Quick Select)
 16) Build Fusion Mini-Map
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from operator_snapshot import build_operator_snapshot
from pipeline_health import evaluate_pipeline_health
from mission_briefing import build_mission_briefing

from spectral_owl.owl_brain import analyze_fusion
from spectral_owl.threat_memory_summary import build_summary as build_threat_summary
from spectral_owl.threat_memory import load_events

from manifest_health import run_manifest_health
from sensor_readiness_brief import build_readiness_brief
from profile_auto_switch import auto_switch

from cloud.azure_ingest import (
    upload_fusion_output,
    list_fusion_blobs,
    download_latest_fusion_archive,
    cloud_sync_health_check,
)

from fusion_minimap import build_minimap


BASE_DIR = Path(__file__).parent
LOG_PATH = BASE_DIR / "fusion_ops_log.csv"
THREAT_MEMORY_PATH = BASE_DIR / "data" / "threat_memory.csv"
OWL_MEMORY_PATH = BASE_DIR / "owl_memory.txt"


def print_menu() -> None:
    print("\nGhost Lantern Labs — Operator Console")
    print("--------------------------------------")
    print("  1) Run QA validation")
    print("  2) Show latest 20 log events (fusion_ops_log.csv if present)")
    print("  3) Build operator snapshot")
    print("  4) Run full fusion pipeline + snapshot")
    print("  5) Spectral Owl memory viewer")
    print("  6) Spectral Owl analysis (fusion scoring check)")
    print("  7) Pipeline health check")
    print("  8) Mission briefing")
    print("  9) Exit")
    print(" 10) Anti-DoS environment scan")
    print(" 11) Cloud Sync Check")
    print(" 12) Threat Memory Summary")
    print(" 13) Sensor Manifest Health Check")
    print(" 14) Sensor Readiness Brief")
    print(" 15) Switch Profile (Quick Select)")
    print(" 16) Build Fusion Mini-Map")
    print("")


def run_subprocess(cmd: list[str]) -> None:
    """Run a Python script via subprocess and stream output."""
    try:
        result = subprocess.run(
            cmd,
            cwd=BASE_DIR,
            text=True,
            capture_output=True,
        )
    except Exception as e:
        print(f"[ERROR] Failed to run {cmd}: {e}")
        return

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print("--- STDERR ---")
        print(result.stderr)


def option_1_run_qa() -> None:
    print("\n[QA] Running qa_validator.py …\n")
    run_subprocess([sys.executable, "qa_validator.py"])


def option_2_show_logs() -> None:
    print("\n[LOGS] Latest fusion_ops_log.csv events:\n")
    if not LOG_PATH.exists():
        print("No fusion_ops_log.csv found.")
        return

    lines = LOG_PATH.read_text(encoding="utf-8").splitlines()
    tail = lines[-20:] if len(lines) > 20 else lines
    for line in tail:
        print(line)


def option_3_operator_snapshot() -> None:
    print("\n[SNAPSHOT] Building operator snapshot …\n")
    try:
        path = build_operator_snapshot()
        print(f"Operator snapshot built: {path}")
        if Path(path).exists():
            print("\n--- Snapshot Content (tail) ---")
            tail = Path(path).read_text(encoding="utf-8").splitlines()[-20:]
            for line in tail:
                print(line)
    except Exception as e:
        print(f"[ERROR] Failed to build operator snapshot: {e}")


def option_4_full_pipeline_plus_snapshot() -> None:
    print("\n[FUSION] Running full fusion pipeline (fusion_run.py) …\n")
    run_subprocess([sys.executable, "fusion_run.py"])
    print("\n[SNAPSHOT] Building operator snapshot …\n")
    option_3_operator_snapshot()


def option_5_owl_memory_viewer() -> None:
    print("\n[OWL MEMORY] Threat memory and Owl notes.\n")

    if THREAT_MEMORY_PATH.exists():
        print(f"Threat memory CSV: {THREAT_MEMORY_PATH}")
        events = load_events()
        print(f"Total events: {len(events)}")
        print("\nLast up to 5 events:")
        for ev in events[-5:]:
            ts = ev.get("timestamp", "unknown")
            etype = ev.get("type", "UNKNOWN")
            sev = ev.get("severity", "unknown")
            note = ev.get("note", "")
            print(f"  [{ts}] {etype} (sev={sev}) — {note}")
    else:
        print("No threat_memory.csv file yet.")

    if OWL_MEMORY_PATH.exists():
        print(f"\nOwl memory text file: {OWL_MEMORY_PATH}")
        tail = OWL_MEMORY_PATH.read_text(encoding="utf-8").splitlines()[-20:]
        print("\nLast lines from owl_memory.txt:")
        for line in tail:
            print(line)
    else:
        print("\nNo owl_memory.txt file yet.")


def option_6_owl_analysis() -> None:
    print("\n[OWL ANALYSIS] Analyzing fusion scores …\n")
    try:
        result = analyze_fusion()
        for k, v in result.items():
            print(f"{k}: {v}")
    except Exception as e:
        print(f"[ERROR] Spectral Owl analysis failed: {e}")


def option_7_pipeline_health() -> None:
    print("\n[HEALTH] Evaluating pipeline health …\n")
    try:
        health = evaluate_pipeline_health()
        for k, v in health.items():
            print(f"{k}: {v}")
    except Exception as e:
        print(f"[ERROR] Pipeline health check failed: {e}")


def option_8_mission_briefing() -> None:
    print("\n[MISSION BRIEFING]\n")
    try:
        brief = build_mission_briefing()
        print(brief)
    except Exception as e:
        print(f"[ERROR] Failed to build mission briefing: {e}")


def option_10_anti_dos_scan() -> None:
    print("\n[ANTI-DOS] Running anti_dos.py …\n")
    run_subprocess([sys.executable, "anti_dos.py"])


def option_11_cloud_sync_check() -> None:
    print("\n[CLOUD] Cloud Sync Check\n")
    try:
        health = cloud_sync_health_check()
        print(f"Health: {health}")
    except Exception as e:
        print(f"[ERROR] Cloud sync health check failed: {e}")
        return

    scored = BASE_DIR / "data" / "scored_output.csv"
    if scored.exists():
        print(f"\nFound fusion output at {scored}, attempting simulated upload…")
        try:
            upload_result = upload_fusion_output(str(scored))
            print(f"Upload result: {upload_result}")
        except Exception as e:
            print(f"[ERROR] Upload failed: {e}")
    else:
        print("\nNo data/scored_output.csv found. Skipping upload test.")

    try:
        listing = list_fusion_blobs()
        print(f"\nCloud archive listing: {listing}")
    except Exception as e:
        print(f"[ERROR] Listing cloud archive failed: {e}")


def option_12_threat_memory_summary() -> None:
    print("\n[THREAT MEMORY SUMMARY]\n")
    try:
        summary = build_threat_summary()
        print(summary)
    except Exception as e:
        print(f"[ERROR] Failed to build threat memory summary: {e}")


def option_13_manifest_health() -> None:
    print("\n[SENSOR MANIFEST HEALTH]\n")
    try:
        result = run_manifest_health()
        print(result)
    except Exception as e:
        print(f"[ERROR] Manifest health check failed: {e}")


def option_14_sensor_readiness() -> None:
    print("\n[SENSOR READINESS BRIEF]\n")
    try:
        brief = build_readiness_brief()
        print(brief)
    except Exception as e:
        print(f"[ERROR] Sensor readiness brief failed: {e}")


def option_15_switch_profile() -> None:
    print("\n[PROFILE SWITCH]\n")
    domain = input("Enter domain (nuclear/sports/legal/soc): ").strip()
    try:
        result = auto_switch(domain)
        print(result)
    except Exception as e:
        print(f"[ERROR] Auto-switch failed: {e}")


def option_16_build_minimap() -> None:
    print("\n[FUSION MINI-MAP]\n")
    try:
        result = build_minimap()
        print(result)
        out_path = Path("minimap.txt")
        if out_path.exists():
            print("\n--- minimap.txt ---")
            print(out_path.read_text(encoding="utf-8"))
        else:
            print("minimap.txt not found after build.")
    except Exception as e:
        print(f"[ERROR] Failed to build fusion mini-map: {e}")


def main() -> None:
    while True:
        print_menu()
        choice = input("Select an option: ").strip()

        if choice == "1":
            option_1_run_qa()
        elif choice == "2":
            option_2_show_logs()
        elif choice == "3":
            option_3_operator_snapshot()
        elif choice == "4":
            option_4_full_pipeline_plus_snapshot()
        elif choice == "5":
            option_5_owl_memory_viewer()
        elif choice == "6":
            option_6_owl_analysis()
        elif choice == "7":
            option_7_pipeline_health()
        elif choice == "8":
            option_8_mission_briefing()
        elif choice == "9":
            print("Exiting Ghost CLI.")
            break
        elif choice == "10":
            option_10_anti_dos_scan()
        elif choice == "11":
            option_11_cloud_sync_check()
        elif choice == "12":
            option_12_threat_memory_summary()
        elif choice == "13":
            option_13_manifest_health()
        elif choice == "14":
            option_14_sensor_readiness()
        elif choice == "15":
            option_15_switch_profile()
        elif choice == "16":
            option_16_build_minimap()
        else:
            print("Invalid choice. Please select a valid option.")


if __name__ == "__main__":
    main()

