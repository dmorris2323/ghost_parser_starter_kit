"""
ghost_cli.py — Ghost Lantern Labs Operator Console
--------------------------------------------------

Menu options:
  1) Run QA validation
  2) Show latest 20 log events
  3) Build operator snapshot
  4) Run full fusion pipeline + snapshot
  5) Spectral Owl Memory Viewer
  6) Spectral Owl Analysis (fusion scoring check)
  7) Pipeline Health Check
  8) Mission Briefing (TXT)
  9) Exit
 10) Anti-DoS Environment Scan
 11) Cloud Sync Check
 12) Threat Memory Summary
 13) Sensor Manifest Health Check
 14) Sensor Readiness Brief
 15) Switch Profile (Quick Select)
 16) Build Mini-Map (Fusion)
 17) Build Dashboard API Bundle
 18) Launch Dashboard (HTML)
"""

import subprocess
import sys
import json
from pathlib import Path

# Core modules
from operator_snapshot import build_operator_snapshot
from pipeline_health import evaluate_pipeline_health
from mission_briefing import build_mission_briefing
from spectral_owl.threat_memory_summary import build_summary as build_threat_summary

# Cloud
from cloud.azure_ingest import (
    upload_fusion_output,
    cloud_sync_health_check,
    list_fusion_blobs,
)

# Sensor manifest / readiness / profiles
from manifest_health import run_manifest_health
from sensor_readiness_brief import build_readiness_brief
from profile_auto_switch import auto_switch

# Minimap + Dashboard API
from fusion_minimap import build_minimap
from spectral_dashboard_api import build_dashboard_bundle

# Owl memory
from spectral_owl.owl_memory import load_memory_log


def run_qa():
    try:
        subprocess.run([sys.executable, "qa_validator.py"], check=False)
    except Exception as e:
        print(f"[ERROR] QA failed: {e}")


def tail_log(path, n=20):
    p = Path(path)
    if not p.exists():
        print("[WARN] Log file does not exist.")
        return

    lines = p.read_text().splitlines()
    for line in lines[-n:]:
        print(line)


def run_pipeline_and_snapshot():
    print("[INFO] Running full fusion pipeline...")
    try:
        subprocess.run([sys.executable, "fusion_ingest.py"], check=False)
    except Exception as e:
        print(f"[ERROR] fusion_ingest failed: {e}")

    print("[INFO] Building operator snapshot...")
    try:
        snap = build_operator_snapshot()
        print(snap)
    except Exception as e:
        print(f"[ERROR] operator_snapshot failed: {e}")


def run_owl_analysis():
    try:
        from spectral_owl.owl_brain import analyze_fusion
        out = analyze_fusion()
        print(out)
    except Exception as e:
        print(f"[ERROR] Owl analysis failed: {e}")


def run_cloud_check():
    print("\n[Cloud Sync Check]\n")
    try:
        health = cloud_sync_health_check()
        print(f"Health: {health}")
    except Exception as e:
        print(f"[ERROR] Cloud health check failed: {e}")
        health = None

    scored = Path("src/data/scored_output.csv")
    if not scored.exists():
        # Fallback: try repo-root relative
        scored = Path("data/scored_output.csv")

    if scored.exists():
        try:
            upload_result = upload_fusion_output(str(scored))
            print(f"\nUpload result: {upload_result}")
        except Exception as e:
            print(f"[ERROR] Upload failed: {e}")
    else:
        print("\n[WARN] No scored_output.csv found. Skipping upload test.")

    try:
        listing = list_fusion_blobs()
        print(f"\nCloud archive listing: {listing}")
    except Exception as e:
        print(f"[ERROR] Listing cloud archive failed: {e}")


def run_dashboard_launch():
    html = Path("src/docs/daily_mission_brief.html")
    if not html.exists():
        html = Path("docs/daily_mission_brief.html")

    if not html.exists():
        print("[WARN] No dashboard HTML found. Run: python mission_brief_html.py")
        return

    try:
        subprocess.run(["open", str(html)])
    except Exception as e:
        print(f"[ERROR] Could not open HTML dashboard: {e}")


def main():
    while True:
        print("\n=== GHOST LANTERN LABS — OPERATOR CONSOLE ===")
        print(" 1) Run QA validation")
        print(" 2) Show latest 20 log events")
        print(" 3) Build operator snapshot")
        print(" 4) Run full fusion pipeline + snapshot")
        print(" 5) Spectral Owl Memory Viewer")
        print(" 6) Spectral Owl Analysis (fusion scoring)")
        print(" 7) Pipeline Health Check")
        print(" 8) Mission Briefing (TXT)")
        print(" 9) Exit")
        print("10) Anti-DoS environment scan")
        print("11) Cloud Sync Check")
        print("12) Threat Memory Summary")
        print("13) Sensor Manifest Health Check")
        print("14) Sensor Readiness Brief")
        print("15) Switch Profile (Quick Select)")
        print("16) Build Mini-Map (Fusion)")
        print("17) Build Dashboard API Bundle")
        print("18) Launch Dashboard (HTML)")

        choice = input("Select option: ").strip()

        if choice == "1":
            run_qa()

        elif choice == "2":
            tail_log("fusion_ops_log.csv")

        elif choice == "3":
            try:
                print(build_operator_snapshot())
            except Exception as e:
                print(f"[ERROR] operator_snapshot failed: {e}")

        elif choice == "4":
            run_pipeline_and_snapshot()

        elif choice == "5":
            try:
                mem = load_memory_log()
                if not mem:
                    print("[INFO] No Owl memory entries found.")
                else:
                    for m in mem[-20:]:
                        print(m)
            except Exception as e:
                print(f"[ERROR] Owl memory viewer failed: {e}")

        elif choice == "6":
            run_owl_analysis()

        elif choice == "7":
            try:
                print(evaluate_pipeline_health())
            except Exception as e:
                print(f"[ERROR] pipeline_health failed: {e}")

        elif choice == "8":
            try:
                brief = build_mission_briefing()
                print(brief)
            except Exception as e:
                print(f"[ERROR] mission_briefing failed: {e}")

        elif choice == "9":
            print("Goodbye, Operator.")
            break

        elif choice == "10":
            try:
                subprocess.run([sys.executable, "anti_dos.py"], check=False)
            except Exception as e:
                print(f"[ERROR] Anti-DoS scan failed: {e}")

        elif choice == "11":
            run_cloud_check()

        elif choice == "12":
            try:
                print(build_threat_summary())
            except Exception as e:
                print(f"[ERROR] Threat memory summary failed: {e}")

        elif choice == "13":
            try:
                print(run_manifest_health())
            except Exception as e:
                print(f"[ERROR] Manifest health failed: {e}")

        elif choice == "14":
            try:
                print(build_readiness_brief())
            except Exception as e:
                print(f"[ERROR] Sensor readiness brief failed: {e}")

        elif choice == "15":
            domain = input("Domain (nuclear/sports/legal/soc): ").strip()
            try:
                print(auto_switch(domain))
            except Exception as e:
                print(f"[ERROR] Profile auto-switch failed: {e}")

        elif choice == "16":
            try:
                result = build_minimap()
                print(json.dumps(result, indent=2))
            except Exception as e:
                print(f"[ERROR] Minimap build failed: {e}")

        elif choice == "17":
            try:
                out = build_dashboard_bundle()
                print("[OK] Dashboard bundle built.")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Dashboard bundle failed: {e}")

        elif choice == "18":
            run_dashboard_launch()

        else:
            print("[WARN] Invalid choice. Try again.")


if __name__ == "__main__":
    main()

