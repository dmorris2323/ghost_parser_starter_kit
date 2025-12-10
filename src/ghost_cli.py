"""
ghost_cli.py — Ghost Lantern Labs Operator Console
--------------------------------------------------

Central operator menu for Ghost Lantern Labs.

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
 34) Operator Safety Layer Report
 35) Sensor Latency Intelligence
 36) Golden Dome Nuclear Readiness Snapshot
 37) Switch Profile — Nuclear Early-Warning
 38) Fusion Heat Index (Battlespace Temperature)
 39) Generate Pre-Launch ISR Watchboard
 40) Fusion Temporal Forecast (6h)
 41) Adversary Pattern Analysis
 42) Installation Threat Map
 43) Sensor Outage Predictor
 44) Distributed Squadron Readiness Snapshot
 45) Perimeter Incident Report
 46) Base Defense Storyboard
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent


def run_py(rel_path: str) -> int:
    """
    Helper to run another Python file in src/ via subprocess.
    Example: run_py("qa_validator.py")
    """
    target = BASE / rel_path
    if not target.exists():
        print(f"[WARN] Script not found: {target}")
        return 1
    return subprocess.call([sys.executable, str(target)])


def show_menu() -> None:
    print(
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
 34) Operator Safety Layer Report
 35) Sensor Latency Intelligence
 36) Golden Dome Nuclear Readiness Snapshot
 37) Switch Profile — Nuclear Early-Warning
 38) Fusion Heat Index (Battlespace Temperature)
 39) Generate Pre-Launch ISR Watchboard
 40) Fusion Temporal Forecast (6h)
 41) Adversary Pattern Analysis
 42) Installation Threat Map
 43) Sensor Outage Predictor
 44) Distributed Squadron Readiness Snapshot
 45) Perimeter Incident Report
 46) Base Defense Storyboard
"""
    )


def main() -> None:
    while True:
        show_menu()
        choice = input("Select option: ").strip()

        # --- CORE OPS ---
        if choice == "1":
            run_py("qa_validator.py")

        elif choice == "2":
            run_py("log_intel.py")

        elif choice == "3":
            run_py("operator_snapshot.py")

        elif choice == "4":
            run_py("fusion_run.py")

        elif choice == "5":
            run_py("spectral_owl/owl_memory.py")

        elif choice == "6":
            try:
                from spectral_owl.owl_brain_phase2 import analyze_fusion  # type: ignore
                out = analyze_fusion()
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Owl analysis failed: {e!r}")

        elif choice == "7":
            run_py("pipeline_health.py")

        elif choice == "8":
            run_py("daily_mission_brief.py")

        elif choice == "9":
            print("Exiting Ghost Lantern Labs CLI.")
            break

        # --- DEFENSIVE + CLOUD ---
        elif choice == "10":
            run_py("anti_dos.py")

        elif choice == "11":
            run_py("cloud/azure_ingest.py")

        # --- THREAT MEMORY / VISUAL PACK / PROFILE ---
        elif choice == "12":
            run_py("spectral_owl/threat_memory_summary.py")

        elif choice == "13":
            run_py("generate_daily_visual_pack.py")

        elif choice == "14":
            run_py("profile_status.py")

        elif choice == "15":
            run_py("family_law_brief.py")

        elif choice == "16":
            run_py("spectral_owl/owl_memory.py")

        elif choice == "17":
            run_py("spectral_dashboard_api.py")

        elif choice == "18":
            run_py("mission_brief_html.py")

        elif choice == "19":
            run_py("fusion_minimap_overlay.py")

        elif choice == "20":
            run_py("spectral_sos_overlay.py")

        elif choice == "21":
            run_py("run_history_intel.py")

        elif choice == "22":
            run_py("spectral_snapshot_export.py")

        elif choice == "23":
            run_py("demo_deck_manifest.py")

        # --- RELIABILITY / CROSS-SENSOR / SBIR / GOLDEN DOME ---
        elif choice == "24":
            try:
                from sensor_reliability import export_reliability_report  # type: ignore
                print(export_reliability_report())
            except Exception as e:
                print(f"[ERROR] Reliability export failed: {e!r}")

        elif choice == "25":
            try:
                from cross_sensor_validator import run_cross_validation  # type: ignore
                from cross_sensor_report import build_report  # type: ignore
                print(run_cross_validation())
                print(build_report())
            except Exception as e:
                print(f"[ERROR] Cross-sensor validation failed: {e!r}")

        elif choice == "26":
            try:
                from sbir_onepager import write_onepager  # type: ignore
                out = write_onepager()
                print(f"SBIR One-Pager written to: {out}")
            except Exception as e:
                print(f"[ERROR] SBIR One-Pager failed: {e!r}")

        elif choice == "27":
            try:
                from golden_dome_validator import build_validation  # type: ignore
                out = build_validation()
                print(f"Golden Dome Validation complete → {out['path']}")
            except Exception as e:
                print(f"[ERROR] Golden Dome validation failed: {e!r}")

        elif choice == "28":
            try:
                from spectral_fallback_tree import build_fallback_response  # type: ignore
                sample = {
                    "critical_alerts": 0,
                    "warning_alerts": 3,
                    "avg_reliability": 91.0,
                }
                out = build_fallback_response(sample)
                print("=== Fallback Response ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Fallback test failed: {e!r}")

        elif choice == "29":
            try:
                from golden_dome_drift import write_drift  # type: ignore
                print(write_drift())
            except Exception as e:
                print(f"[ERROR] Drift report failed: {e!r}")

        elif choice == "30":
            try:
                from reliability_trend import compute_trend  # type: ignore
                print(compute_trend())
            except Exception as e:
                print(f"[ERROR] Reliability trend failed: {e!r}")

        elif choice == "31":
            try:
                from spectral_owl.owl_confidence import compute_confidence  # type: ignore
                sample = {
                    "critical_alerts": 1,
                    "warning_alerts": 4,
                    "avg_reliability": 92,
                }
                print(compute_confidence(sample))
            except Exception as e:
                print(f"[ERROR] Owl confidence failed: {e!r}")

        elif choice == "32":
            try:
                from crisis_mode_flag import enable, disable, status  # type: ignore
                print(f"Current: {status()}")
                ch = input("Turn ON or OFF? ").strip().lower()
                if ch == "on":
                    print(enable())
                elif ch == "off":
                    print(disable())
                else:
                    print("Invalid.")
            except Exception as e:
                print(f"[ERROR] Crisis Mode toggle failed: {e!r}")

        elif choice == "33":
            try:
                from operator_identity import set_identity  # type: ignore
                nm = input("Enter operator name: ").strip()
                print(set_identity(nm))
            except Exception as e:
                print(f"[ERROR] Operator identity failed: {e!r}")

        elif choice == "34":
            try:
                from operator_safety_layer import compute_osl  # type: ignore
                out = compute_osl()
                print("=== Operator Safety Layer ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] OSL failed: {e!r}")

        elif choice == "35":
            run_py("sensor_latency.py")

        elif choice == "36":
            try:
                from golden_dome_snapshot import build_snapshot  # type: ignore
                out = build_snapshot()
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Nuclear readiness snapshot failed: {e!r}")

        elif choice == "37":
            try:
                from profile_engine import set_profile  # type: ignore
                print(set_profile("nuclear_early_warning"))
            except Exception as e:
                print(f"[ERROR] Profile switch failed: {e!r}")

        elif choice == "38":
            try:
                from fusion_heat_index import compute_fhi  # type: ignore
                out = compute_fhi()
                print("=== FUSION HEAT INDEX ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] FHI failed: {e!r}")

        elif choice == "39":
            try:
                from prelaunch_watchboard import build_watchboard  # type: ignore
                out = build_watchboard()
                print(f"[OK] Watchboard written to: {out}")
            except Exception as e:
                print(f"[ERROR] Watchboard failed: {e!r}")

        elif choice == "40":
            try:
                from fusion_temporal_forecast import forecast_next_6h  # type: ignore
                out = forecast_next_6h()
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Temporal forecast failed: {e!r}")

        elif choice == "41":
            try:
                from adversary_pattern_engine import analyze_patterns  # type: ignore
                out = analyze_patterns()
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Adversary pattern engine failed: {e!r}")

        elif choice == "42":
            run_py("installation_threat_map.py")

        elif choice == "43":
            run_py("sensor_outage_predictor.py")

        elif choice == "44":
            run_py("distributed_readiness.py")

        elif choice == "45":
            run_py("perimeter_incident_report.py")

        elif choice == "46":
            run_py("base_defense_storyboard.py")

        else:
            print(f"Unknown option: {choice}")


if __name__ == "__main__":
    main()

