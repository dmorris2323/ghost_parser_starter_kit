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
  8) Mission briefing (profile-aware, text + HTML)
  9) Exit
 10) Anti-DoS environment scan
 11) Cloud Sync Check
 12) Threat Memory Summary
 13) Build Daily Visual Pack
 14) Show Active Profile Status
 15) Run Family Law Demo (Shari)
 16) Owl Memory Diagnostics
 17) Spectral Dashboard Export (API bundle)
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
 39) Full Readiness + HTML Refresh
 40) Fusion Temporal Forecast (6h)
 41) Adversary Pattern Analysis
 42) Golden Dome Daily Watch
 43) Nuclear Decision Card
 44) Treaty Evidence Bundle
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime, timezone

BASE = Path(__file__).resolve().parent.parent  # /parser_starter_kit
SRC = BASE / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def run_py(rel_path: str) -> int:
    """
    Helper to run another Python module in src/ as a script.
    """
    script = SRC / rel_path
    if not script.exists():
        print(f"[ERROR] Script not found: {script}")
        return 1
    print(f"[INFO] Running: {script}")
    result = subprocess.run([sys.executable, str(script)], cwd=str(SRC))
    if result.returncode != 0:
        print(f"[WARN] {rel_path} exited with code {result.returncode}")
    return result.returncode


def print_menu():
    print(
        """
Ghost Lantern Labs — Operator Console
-------------------------------------

  1) Run QA validation
  2) Show latest 20 log events
  3) Build operator snapshot
  4) Run full fusion pipeline + snapshot
  5) Spectral Owl memory viewer
  6) Spectral Owl analysis (fusion scoring check)
  7) Pipeline health check
  8) Mission briefing (profile-aware, text + HTML)
  9) Exit
 10) Anti-DoS environment scan
 11) Cloud Sync Check
 12) Threat Memory Summary
 13) Build Daily Visual Pack
 14) Show Active Profile Status
 15) Run Family Law Demo (Shari)
 16) Owl Memory Diagnostics
 17) Spectral Dashboard Export (API bundle)
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
 39) Full Readiness + HTML Refresh
 40) Fusion Temporal Forecast (6h)
 41) Adversary Pattern Analysis
 42) Golden Dome Daily Watch
 43) Nuclear Decision Card
 44) Treaty Evidence Bundle
"""
    )


def main():
    while True:
        print_menu()
        choice = input("Select option: ").strip()

        # --- Core 1–9 ---
        if choice == "1":
            run_py("qa_validator.py")

        elif choice == "2":
            run_py("log_intel.py")

        elif choice == "3":
            run_py("operator_snapshot.py")

        elif choice == "4":
            run_py("fusion_run.py")

        elif choice == "5":
            run_py("spectral_owl/threat_memory_summary.py")

        elif choice == "6":
            run_py("spectral_owl/owl_brain_phase2.py")

        elif choice == "7":
            run_py("pipeline_health.py")

        elif choice == "8":
            run_py("daily_mission_brief.py")
            run_py("mission_brief_html.py")

        elif choice == "9":
            print("Exiting Ghost Lantern CLI.")
            break

        # --- 10–20: Security, cloud, SOS/minimap, visual pack ---
        elif choice == "10":
            run_py("anti_dos.py")

        elif choice == "11":
            if (SRC / "cloud" / "env_check.py").exists():
                run_py("cloud/env_check.py")
            else:
                run_py("scripts/env_check.py")

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

        # --- 21–23: Run-history, snapshots, demo deck ---
        elif choice == "21":
            run_py("run_history_intel.py")

        elif choice == "22":
            if (SRC / "spectral_snapshot_bundle.py").exists():
                run_py("spectral_snapshot_bundle.py")
            else:
                print("[WARN] spectral_snapshot_bundle.py not found.")

        elif choice == "23":
            run_py("demo_deck_manifest.py")

        # --- 24–27: Reliability, cross-sensor, SBIR, Golden Dome ---
        elif choice == "24":
            run_py("sensor_reliability.py")

        elif choice == "25":
            run_py("cross_sensor_validator.py")
            run_py("cross_sensor_report.py")

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
                print(f"[ERROR] Golden Dome Validator failed: {e!r}")

        # --- 28–33: Fallback, drift, trend, confidence, crisis, operator ---
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
                print(f"[ERROR] Fallback test failed: {e!r}")

        elif choice == "29":
            run_py("golden_dome_drift.py")

        elif choice == "30":
            run_py("reliability_trend.py")

        elif choice == "31":
            try:
                from spectral_owl.owl_confidence import compute_confidence

                sample = {
                    "critical_alerts": 1,
                    "warning_alerts": 4,
                    "avg_reliability": 92,
                }
                print("Sample confidence:", compute_confidence(sample))
            except Exception as e:
                print(f"[ERROR] Owl confidence failed: {e!r}")

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
                print(f"[ERROR] Operator identity failed: {e!r}")

        # --- 34–36: OSL, latency, nuclear snapshot ---
        elif choice == "34":
            try:
                from operator_safety_layer import compute_osl

                out = compute_osl()
                print("=== Operator Safety Layer ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] OSL failed: {e!r}")

        elif choice == "35":
            run_py("sensor_latency.py")

        elif choice == "36":
            try:
                from golden_dome_snapshot import build_snapshot

                out = build_snapshot()
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Nuclear readiness snapshot failed: {e!r}")

        # --- 37–40: Nuclear profile, heat index, readiness package, forecast ---
        elif choice == "37":
            try:
                from profile_engine import set_profile

                print(set_profile("nuclear_early_warning"))
            except Exception as e:
                print(f"[ERROR] Profile switch failed: {e!r}")

        elif choice == "38":
            try:
                from fusion_heat_index import compute_fhi

                out = compute_fhi()
                print("=== FUSION HEAT INDEX ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] FHI failed: {e!r}")

        elif choice == "39":
            try:
                from gll_readiness import write_gll_readiness
                from system_integrity import write_system_integrity

                r1 = write_gll_readiness()
                r2 = write_system_integrity()
                print(f"[OK] GLL readiness written to: {r1}")
                print(f"[OK] System integrity written to: {r2}")
                run_py("mission_brief_html.py")
            except Exception as e:
                print(f"[ERROR] Full readiness package failed: {e!r}")

        elif choice == "40":
            try:
                from fusion_temporal_forecast import forecast_next_6h

                out = forecast_next_6h()
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Temporal forecast failed: {e!r}")

        # --- 41: Adversary Pattern Analysis ---
        elif choice == "41":
            try:
                from adversary_pattern_engine import analyze_patterns

                out = analyze_patterns()
                print("=== Adversary Pattern Analysis ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Adversary pattern engine failed: {e!r}")

        # --- 42–44: Daily watch, decision card, treaty bundle ---
        elif choice == "42":
            try:
                from golden_dome_daily_watch import build_daily_watch

                out = build_daily_watch()
                print("=== Golden Dome Daily Watch ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Golden Dome Daily Watch failed: {e!r}")

        elif choice == "43":
            try:
                from nuclear_decision_card import write_decision_card

                path = write_decision_card()
                print(f"[OK] Nuclear decision card written to: {path}")
            except Exception as e:
                print(f"[ERROR] Nuclear decision card failed: {e!r}")

        elif choice == "44":
            try:
                from treaty_evidence_bundle import build_treaty_bundle

                path = build_treaty_bundle()
                print(f"[OK] Treaty evidence bundle written to: {path}")
            except Exception as e:
                print(f"[ERROR] Treaty evidence bundle failed: {e!r}")

        else:
            print(f"Unknown choice: {choice!r}")

        print("\n[READY] Press Enter to continue...")
        input()


if __name__ == "__main__":
    main()

