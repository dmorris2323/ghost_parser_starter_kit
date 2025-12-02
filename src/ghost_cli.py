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
  8) Mission briefing (text)
  9) Exit
 10) Anti-DoS environment scan
 11) Cloud Sync Check
 12) Threat Memory Summary
 13) Sensor Manifest Health Check
 14) Sensor Readiness Brief
 15) Switch Profile (Quick Select)
 16) Fusion Mini-Map (Text + PNG)
 17) Build GUI Demo Pack (HTML + PNG + Profile Brief)
 18) Golden Dome Alignment Report
 19) System Status Dashboard (Text)
"""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

from operator_snapshot import build_operator_snapshot
from pipeline_health import evaluate_pipeline_health
from mission_briefing import build_mission_briefing
from spectral_owl.owl_brain import analyze_fusion
from spectral_owl.threat_memory_summary import build_summary as build_threat_summary
from manifest_health import run_manifest_health
from sensor_readiness_brief import build_readiness_brief
from profile_auto_switch import auto_switch
from profile_status import build_profile_status
from fusion_minimap import build_minimap
from fusion_minimap_png import main as build_minimap_png
from demo_gui_pack import build_gui_demo_pack
from golden_dome_alignment_report import write_golden_dome_report
from system_status_dashboard_txt import write_system_status_dashboard
from cloud.azure_ingest import (
    upload_fusion_output,
    list_fusion_blobs,
    cloud_sync_health_check,
)


BASE_DIR = Path(__file__).parent
LOG_PATH = BASE_DIR / "fusion_ops_log.csv"
OWL_MEMORY_PATH = BASE_DIR / "owl_memory.txt"
SCORED_OUTPUT_PATH = BASE_DIR / "data" / "scored_output.csv"


def run_subprocess(cmd: list[str]) -> int:
    """Run a subprocess command and stream output."""
    print(f"\n[RUN] {' '.join(str(c) for c in cmd)}\n")
    result = subprocess.run(cmd)
    return result.returncode


def show_latest_log_events(n: int = 20) -> None:
    """Print the latest N events from fusion_ops_log.csv if present."""
    if not LOG_PATH.exists():
        print(f"[WARN] {LOG_PATH} not found.")
        return

    with LOG_PATH.open() as f:
        reader = csv.reader(f)
        rows = list(reader)

    print(f"\n=== Latest {min(n, len(rows))} log events from {LOG_PATH.name} ===")
    for row in rows[-n:]:
        print(" | ".join(row))


def show_owl_memory(n: int = 50) -> None:
    """Display last N lines of owl_memory.txt directly."""
    if not OWL_MEMORY_PATH.exists():
        print(f"[WARN] {OWL_MEMORY_PATH} not found.")
        return

    lines = OWL_MEMORY_PATH.read_text(encoding="utf-8").splitlines()
    tail = lines[-n:] if len(lines) > n else lines

    print("\n=== Spectral Owl Memory (latest entries) ===")
    for line in tail:
        print(line)


def main_menu() -> None:
    while True:
        print(
            """
Ghost Lantern Labs — Operator Console
=====================================
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
 16) Fusion Mini-Map (Text + PNG)
 17) Build GUI Demo Pack (HTML + PNG + Profile Brief)
 18) Golden Dome Alignment Report
 19) System Status Dashboard (Text)
"""
        )

        choice = input("Select an option: ").strip()

        if choice == "1":
            code = run_subprocess([sys.executable, "qa_validator.py"])
            if code == 0:
                print("\n[OK] QA validation completed.")
            else:
                print(f"\n[ERROR] QA validation exited with code {code}.")

        elif choice == "2":
            show_latest_log_events(20)

        elif choice == "3":
            snapshot_path = build_operator_snapshot()
            print(f"\n[OK] Operator snapshot built → {snapshot_path}")

        elif choice == "4":
            print("\n[PIPELINE] Running fusion_run.py ...\n")
            code = run_subprocess([sys.executable, "fusion_run.py"])
            if code != 0:
                print(f"[ERROR] fusion_run.py exited with code {code}")
            snapshot_path = build_operator_snapshot()
            print(f"[OK] Operator snapshot built → {snapshot_path}")

        elif choice == "5":
            show_owl_memory(50)

        elif choice == "6":
            print("\n[OWL] Analyzing fused output...\n")
            result = analyze_fusion()
            print(result)

        elif choice == "7":
            print("\n[HEALTH] Evaluating pipeline health...\n")
            report = evaluate_pipeline_health()
            print(report)

        elif choice == "8":
            print("\n[BRIEFING] Building mission briefing...\n")
            brief = build_mission_briefing()
            print(brief)

        elif choice == "9":
            print("\nExiting Ghost Lantern Labs CLI. Stay lethal.\n")
            sys.exit(0)

        elif choice == "10":
            print("\n[Anti-DoS] Running anti_dos.py and anti_dos_metrics.py ...\n")
            run_subprocess([sys.executable, "anti_dos.py"])
            run_subprocess([sys.executable, "anti_dos_metrics.py"])

        elif choice == "11":
            print("\n[Cloud Sync Check]\n")
            health = cloud_sync_health_check()
            print(f"Health: {health}")

            if SCORED_OUTPUT_PATH.exists():
                print(f"\nFound fusion output at {SCORED_OUTPUT_PATH}, attempting simulated upload...")
                upload_result = upload_fusion_output(str(SCORED_OUTPUT_PATH))
                print(f"Upload result: {upload_result}")
            else:
                print("\nNo scored_output.csv found. Skipping upload test.")

            listing = list_fusion_blobs()
            print(f"\nCloud archive listing: {listing}")

        elif choice == "12":
            print("\n[Threat Memory Summary]\n")
            summary = build_threat_summary()
            print(summary)

        elif choice == "13":
            print("\n[Sensor Manifest Health Check]\n")
            result = run_manifest_health()
            print(result)

        elif choice == "14":
            print("\n[Sensor Readiness Brief]\n")
            brief = build_readiness_brief()
            print(brief)

        elif choice == "15":
            domain = input("Enter domain (nuclear/sports/legal/soc): ").strip()
            result = auto_switch(domain)
            print(result)
            print("\n[Profile Status]\n")
            print(build_profile_status())

        elif choice == "16":
            print("\n[Fusion Mini-Map] Building text + PNG...\n")
            mm_result = build_minimap()
            print("Text minimap result:", mm_result)
            png_result = build_minimap_png()
            print("PNG minimap result:", png_result)

        elif choice == "17":
            print("\n[GUI DEMO PACK] Building HTML + PNG + Profile Brief...\n")
            result = build_gui_demo_pack()
            print("[OK] GUI demo pack built.")
            print("Artifacts:")
            for k, v in result["artifacts"].items():
                print(f"  - {k}: {v}")

        elif choice == "18":
            print("\n[Golden Dome Alignment] Generating report...\n")
            path = write_golden_dome_report()
            print(f"[OK] Golden Dome alignment report written → {path}")
            try:
                text = path.read_text(encoding="utf-8")
                print("\n" + text)
            except Exception as e:
                print(f"[WARN] Could not read report: {e}")

        elif choice == "19":
            print("\n[System Status Dashboard] Building consolidated dashboard...\n")
            path = write_system_status_dashboard()
            print(f"[OK] System status dashboard written → {path}")
            try:
                text = path.read_text(encoding="utf-8")
                print("\n" + text)
            except Exception as e:
                print(f"[WARN] Could not read dashboard: {e}")

        else:
            print(f"\n[WARN] Invalid choice: {choice}\n")


if __name__ == "__main__":
    main_menu()

