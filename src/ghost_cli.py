"""
ghost_cli.py — Ghost Lantern Labs Operator Console
--------------------------------------------------

Central launchpad for Ghost Lantern Labs tooling.

Menu options:
  1)  Run QA validation
  2)  Show latest 20 log events
  3)  Build operator snapshot
  4)  Run full fusion pipeline + snapshot
  5)  Spectral Owl memory viewer
  6)  Spectral Owl analysis (fusion scoring check)
  7)  Pipeline health check
  8)  Mission briefing (profile-aware)
  9)  Exit
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
 34) Operator Safety Layer Report
 35) Sensor Latency Intelligence
 36) Golden Dome Nuclear Readiness Snapshot
 37) Switch Profile — Nuclear Early-Warning
 38) Fusion Heat Index (Battlespace Temperature)
 39) Generate Pre-Launch ISR Watchboard
 40) Full Readiness + Integrity Sweep (readiness, integrity, HTML)
 41) Append to GLL Readiness Timeline
 42) Build Executive Snapshot Pack
 43) GLL Scoreboard
 44) Nuclear Mission Brief
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime


BASE = Path(__file__).resolve().parent


def run_py(relative: str) -> int:
    """
    Helper to run another Python file in this src directory (or a subdir).
    Example: run_py("qa_validator.py") or run_py("spectral_owl/threat_memory_summary.py")
    """
    target = BASE / relative
    return subprocess.call([sys.executable, str(target)])


def print_header() -> None:
    print("")
    print("ghost_cli.py — Ghost Lantern Labs Operator Console")
    print("Base directory:", BASE)
    print("Loaded at:", datetime.utcnow().isoformat() + "Z")
    print("--------------------------------------------------")
    print("")


def print_menu() -> None:
    print("Menu options:")
    print("  1)  Run QA validation")
    print("  2)  Show latest 20 log events")
    print("  3)  Build operator snapshot")
    print("  4)  Run full fusion pipeline + snapshot")
    print("  5)  Spectral Owl memory viewer")
    print("  6)  Spectral Owl analysis (fusion scoring check)")
    print("  7)  Pipeline health check")
    print("  8)  Mission briefing (profile-aware)")
    print("  9)  Exit")
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
    print(" 34) Operator Safety Layer Report")
    print(" 35) Sensor Latency Intelligence")
    print(" 36) Golden Dome Nuclear Readiness Snapshot")
    print(" 37) Switch Profile — Nuclear Early-Warning")
    print(" 38) Fusion Heat Index (Battlespace Temperature)")
    print(" 39) Generate Pre-Launch ISR Watchboard")
    print(" 40) Full Readiness + Integrity Sweep (readiness, integrity, HTML)")
    print(" 41) Append to GLL Readiness Timeline")
    print(" 42) Build Executive Snapshot Pack")
    print(" 43) GLL Scoreboard")
    print(" 44) Nuclear Mission Brief")
    print("")


def main() -> None:
    print_header()

    while True:
        print_menu()
        choice = input("Select option (1-44): ").strip()

        if choice == "1":
            run_py("qa_validator.py")

        elif choice == "2":
            run_py("log_intel.py")

        elif choice == "3":
            run_py("operator_snapshot.py")

        elif choice == "4":
            run_py("fusion_ingest.py")
            run_py("operator_snapshot.py")
            run_py("daily_report.py")

        elif choice == "5":
            try:
                run_py("spectral_owl/threat_memory_summary.py")
            except Exception as e:
                print(f"[ERROR] Owl memory viewer failed: {e!r}")

        elif choice == "6":
            try:
                run_py("fusion_scoring.py")
            except Exception as e:
                print(f"[ERROR] Fusion scoring check failed: {e!r}")

        elif choice == "7":
            run_py("pipeline_health.py")

        elif choice == "8":
            try:
                rc = run_py("profile_mission_brief.py")
                if rc != 0:
                    raise RuntimeError(f"profile_mission_brief.py exited with {rc}")
            except Exception:
                print("[WARN] profile_mission_brief.py failed, falling back to daily_mission_brief.py")
                run_py("daily_mission_brief.py")

        elif choice == "9":
            print("Exiting Ghost Lantern Labs CLI. Stay lethal.")
            break

        elif choice == "10":
            run_py("anti_dos.py")

        elif choice == "11":
            try:
                run_py("cloud/package_for_cloud.py")
            except Exception as e:
                print(f"[ERROR] Cloud packaging/check failed: {e!r}")

        elif choice == "12":
            try:
                run_py("spectral_owl/threat_memory_summary.py")
            except Exception as e:
                print(f"[ERROR] Threat memory summary failed: {e!r}")

        elif choice == "13":
            run_py("generate_daily_visual_pack.py")

        elif choice == "14":
            try:
                run_py("profile_status.py")
            except Exception as e:
                print(f"[ERROR] Profile status failed: {e!r}")

        elif choice == "15":
            try:
                run_py("legal_demo_pack.py")
            except Exception as e:
                print(f"[ERROR] Family law demo failed: {e!r}")

        elif choice == "16":
            try:
                from spectral_owl.owl_memory import owl_memory_diagnostics
                out = owl_memory_diagnostics()
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Owl memory diagnostics failed: {e!r}")

        elif choice == "17":
            try:
                run_py("spectral_dashboard_api.py")
            except Exception as e:
                print(f"[ERROR] Spectral dashboard export failed: {e!r}")

        elif choice == "18":
            try:
                run_py("mission_brief_html.py")
            except Exception as e:
                print(f"[ERROR] Mission brief HTML generation failed: {e!r}")

        elif choice == "19":
            try:
                run_py("fusion_minimap_overlay.py")
            except Exception as e:
                print(f"[ERROR] Minimap overlay export failed: {e!r}")

        elif choice == "20":
            try:
                run_py("spectral_sos_overlay.py")
            except Exception as e:
                print(f"[ERROR] SOS overlay export failed: {e!r}")

        elif choice == "21":
            try:
                run_py("run_history_intel.py")
            except Exception as e:
                print(f"[ERROR] Run-history intel timeline failed: {e!r}")

        elif choice == "22":
            try:
                run_py("gui_screenshot_export.py")
            except Exception as e:
                print(f"[ERROR] Spectral snapshot export failed: {e!r}")

        elif choice == "23":
            try:
                run_py("demo_deck_manifest.py")
            except Exception as e:
                print(f"[ERROR] Demo deck manifest failed: {e!r}")

        elif choice == "24":
            try:
                from sensor_reliability import export_reliability_report
                out = export_reliability_report()
                print(out)
            except Exception as e:
                print(f"[ERROR] Sensor reliability export failed: {e!r}")

        elif choice == "25":
            try:
                from cross_sensor_validator import run_cross_validation
                from cross_sensor_report import build_report
                print(run_cross_validation())
                print(build_report())
            except Exception as e:
                print(f"[ERROR] Cross-sensor validation failed: {e!r}")

        elif choice == "26":
            try:
                from sbir_onepager import write_onepager
                out = write_onepager()
                print(f"SBIR One-Pager written to: {out}")
            except Exception as e:
                print(f"[ERROR] SBIR one-pager failed: {e!r}")

        elif choice == "27":
            try:
                from golden_dome_validator import build_validation
                out = build_validation()
                print(f"Golden Dome Validation complete → {out['path']}")
            except Exception as e:
                print(f"[ERROR] Golden Dome validation failed: {e!r}")

        elif choice == "28":
            try:
                from spectral_fallback_tree import build_fallback_response
                sample = {
                    "critical_alerts": 0,
                    "warning_alerts": 3,
                    "avg_reliability": 91.0,
                }
                out = build_fallback_response(sample)
                print("=== Fallback Response ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Spectral Owl fallback test failed: {e!r}")

        elif choice == "29":
            try:
                from golden_dome_drift import write_drift
                out = write_drift()
                print(out)
            except Exception as e:
                print(f"[ERROR] Golden Dome drift report failed: {e!r}")

        elif choice == "30":
            try:
                from reliability_trend import compute_trend
                out = compute_trend()
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Reliability trendline failed: {e!r}")

        elif choice == "31":
            try:
                from spectral_owl.owl_confidence import compute_confidence
                sample = {
                    "critical_alerts": 1,
                    "warning_alerts": 4,
                    "avg_reliability": 92,
                }
                print(compute_confidence(sample))
            except Exception as e:
                print(f"[ERROR] Owl confidence estimator failed: {e!r}")

        elif choice == "32":
            try:
                from crisis_mode_flag import enable, disable, status
                print(f"Current: {status()}")
                ch = input("Turn ON or OFF? ").strip().lower()
                if ch == "on":
                    print(enable())
                elif ch == "off":
                    print(disable())
                else:
                    print("Invalid.")
            except Exception as e:
                print(f"[ERROR] Crisis mode toggle failed: {e!r}")

        elif choice == "33":
            try:
                from operator_identity import set_identity
                nm = input("Enter operator name: ").strip()
                print(set_identity(nm))
            except Exception as e:
                print(f"[ERROR] Set operator name failed: {e!r}")

        elif choice == "34":
            try:
                from operator_safety_layer import compute_osl
                out = compute_osl()
                print("=== Operator Safety Layer ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Operator Safety Layer failed: {e!r}")

        elif choice == "35":
            try:
                from sensor_latency import compute_latency_report
                out = compute_latency_report()
                print("=== SENSOR LATENCY REPORT ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Sensor latency intelligence failed: {e!r}")

        elif choice == "36":
            try:
                from golden_dome_snapshot import build_snapshot
                out = build_snapshot()
                print("=== NUCLEAR READINESS SNAPSHOT ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Nuclear readiness snapshot failed: {e!r}")

        elif choice == "37":
            try:
                from profile_engine import set_profile
                out = set_profile("nuclear_early_warning")
                print(out)
            except Exception as e:
                print(f"[ERROR] Switch to nuclear profile failed: {e!r}")

        elif choice == "38":
            try:
                from fusion_heat_index import compute_fhi
                out = compute_fhi()
                print("=== FUSION HEAT INDEX ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Fusion Heat Index failed: {e!r}")

        elif choice == "39":
            try:
                from prelaunch_watchboard import build_watchboard
                out = build_watchboard()
                print(f"[OK] Watchboard written to: {out}")
            except Exception as e:
                print(f"[ERROR] Pre-launch ISR watchboard failed: {e!r}")

        elif choice == "40":
            try:
                from gll_readiness import write_gll_readiness
                from system_integrity import write_system_integrity
                from mission_brief_html import write_daily_brief

                print("=== GLL READINESS ===")
                print(write_gll_readiness())
                print("=== SYSTEM INTEGRITY ===")
                print(write_system_integrity())
                print("=== HTML MISSION BRIEF ===")
                print(write_daily_brief())
            except Exception as e:
                print(f"[ERROR] Full readiness + integrity sweep failed: {e!r}")

        elif choice == "41":
            try:
                from gll_readiness_timeline import build_readiness_timeline
                out = build_readiness_timeline()
                print("=== GLL READINESS TIMELINE UPDATED ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Readiness timeline update failed: {e!r}")

        elif choice == "42":
            try:
                from executive_snapshot_pack import build_executive_snapshot
                out = build_executive_snapshot()
                print("=== EXECUTIVE SNAPSHOT PACK BUILT ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Executive snapshot pack failed: {e!r}")

        elif choice == "43":
            try:
                from gll_scoreboard import build_scoreboard
                out = build_scoreboard()
                print("=== GLL SCOREBOARD BUILT ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] GLL Scoreboard failed: {e!r}")

        elif choice == "44":
            try:
                from nuclear_mission_brief import build_nuclear_mission_brief
                out = build_nuclear_mission_brief()
                print("=== NUCLEAR MISSION BRIEF BUILT ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Nuclear mission brief failed: {e!r}")

        else:
            print(f"Unknown option: {choice!r}")
            continue

        input("\n[ENTER] to return to menu...")


if __name__ == "__main__":
    main()

