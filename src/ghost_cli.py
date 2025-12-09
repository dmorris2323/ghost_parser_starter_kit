"""
ghost_cli.py — Ghost Lantern Labs Operator Console
--------------------------------------------------

Central operator menu for Ghost Lantern Labs.

This version is defensive:
- If a backing module/script is missing, the CLI will NOT crash on import.
- Only the specific option will print an error.
"""

import sys
import subprocess
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SRC = Path(__file__).resolve().parent


def run_py(script: str) -> int:
    """
    Run a Python script located in src/ by filename.
    Returns the subprocess exit code. Prints a clear error
    if the script is not present.
    """
    script_path = SRC / script
    if not script_path.exists():
        print(f"[ERROR] Script not found: {script_path}")
        return 1
    return subprocess.call([sys.executable, str(script_path)])


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
 40) GLL Readiness + System Integrity + HTML Refresh
"""
    )


def tail_log(lines: int = 20) -> None:
    """
    Show last N lines of the main log file, if present.
    """
    candidates = [
        SRC / "logs" / "app.log",
        SRC / "app.log",
        BASE_DIR / "logs" / "app.log",
    ]
    log_path = None
    for c in candidates:
        if c.exists():
            log_path = c
            break

    if not log_path:
        print("[WARN] No log file found (looked for logs/app.log).")
        return

    text = log_path.read_text().splitlines()
    print(f"=== Last {lines} lines of {log_path} ===")
    for line in text[-lines:]:
        print(line)


def main() -> None:
    while True:
        show_menu()
        choice = input("Select option: ").strip()

        if choice == "1":
            # QA validation
            rc = run_py("qa_validator.py")
            if rc == 0:
                print("[OK] QA validation complete.")
            else:
                print("[WARN] QA validation script returned non-zero status.")

        elif choice == "2":
            # Latest 20 log events
            tail_log(20)

        elif choice == "3":
            # Operator snapshot
            try:
                sys.path.insert(0, str(SRC))
                from operator_snapshot import build_operator_snapshot  # type: ignore
                out = build_operator_snapshot()
                print(f"[OK] Operator snapshot written → {out}")
            except Exception as e:
                print(f"[ERROR] operator_snapshot failed: {e!r}")

        elif choice == "4":
            # Full fusion pipeline + snapshot
            print("[INFO] Running fusion_ingest pipeline...")
            run_py("fusion_ingest.py")
            try:
                sys.path.insert(0, str(SRC))
                from operator_snapshot import build_operator_snapshot  # type: ignore
                out = build_operator_snapshot()
                print(f"[OK] Operator snapshot written → {out}")
            except Exception as e:
                print(f"[ERROR] operator_snapshot failed: {e!r}")

        elif choice == "5":
            # Spectral Owl memory viewer
            try:
                sys.path.insert(0, str(SRC))
                from spectral_owl.owl_memory import load_memory_log  # type: ignore
                mem = load_memory_log()
                print("=== Spectral Owl Memory Log ===")
                print(json.dumps(mem, indent=2))
            except Exception as e:
                print(f"[ERROR] Owl memory viewer failed: {e!r}")

        elif choice == "6":
            # Spectral Owl analysis (fusion scoring check)
            try:
                sys.path.insert(0, str(SRC))
                from spectral_owl.owl_brain_phase2 import run_fusion_check  # type: ignore
                out = run_fusion_check()
                print("=== Spectral Owl Fusion Analysis ===")
                print(json.dumps(out, indent=2))
            except ImportError:
                print("[WARN] owl_brain_phase2.run_fusion_check not available; trying fallback script.")
                run_py("spectral_owl_analysis.py")
            except Exception as e:
                print(f"[ERROR] Owl analysis failed: {e!r}")

        elif choice == "7":
            # Pipeline health check
            try:
                sys.path.insert(0, str(SRC))
                from pipeline_health import evaluate_pipeline_health  # type: ignore
                out = evaluate_pipeline_health()
                print("=== Pipeline Health ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] pipeline_health failed: {e!r}")

        elif choice == "8":
            # Mission briefing (profile-aware)
            try:
                sys.path.insert(0, str(SRC))
                from profile_mission_brief import build_profile_mission_brief  # type: ignore
                text = build_profile_mission_brief()
                print("=== Mission Brief (Profile-Aware) ===")
                print(text)
            except ImportError:
                print("[WARN] profile_mission_brief not available; falling back to daily_mission_brief.")
                try:
                    from daily_mission_brief import build_mission_brief  # type: ignore
                    text = build_mission_brief()
                    print("=== Daily Mission Brief ===")
                    print(text)
                except Exception as e:
                    print(f"[ERROR] mission brief failed: {e!r}")
            except Exception as e:
                print(f"[ERROR] mission brief failed: {e!r}")

        elif choice == "9":
            print("Exiting Ghost Lantern Labs operator console.")
            break

        elif choice == "10":
            # Anti-DoS environment scan
            run_py("anti_dos_scan.py")

        elif choice == "11":
            # Cloud Sync Check
            run_py("cloud_sync_check.py")

        elif choice == "12":
            # Threat Memory Summary
            run_py("threat_memory_summary.py")

        elif choice == "13":
            # Build Daily Visual Pack
            run_py("daily_visual_pack.py")

        elif choice == "14":
            # Show Active Profile Status
            try:
                sys.path.insert(0, str(SRC))
                from profile_engine import get_active_profile  # type: ignore
                p = get_active_profile()
                print("=== Active Profile ===")
                print(json.dumps(p, indent=2, default=str))
            except Exception as e:
                print(f"[ERROR] profile_engine.get_active_profile failed: {e!r}")

        elif choice == "15":
            # Run Family Law Demo (Shari)
            run_py("family_law_demo.py")

        elif choice == "16":
            # Owl Memory Diagnostics
            run_py("owl_memory_diagnostics.py")

        elif choice == "17":
            # Spectral Dashboard Export
            run_py("spectral_dashboard_api.py")

        elif choice == "18":
            # Mission Brief HTML Generator
            try:
                sys.path.insert(0, str(SRC))
                from mission_brief_html import write_html_brief  # type: ignore
                out = write_html_brief()
                print(f"[OK] HTML mission brief written → {out}")
            except Exception as e:
                print(f"[ERROR] mission_brief_html failed: {e!r}")

        elif choice == "19":
            # Export GUI Minimap Overlay
            try:
                sys.path.insert(0, str(SRC))
                from fusion_minimap_overlay import export_gui_minimap  # type: ignore
                out = export_gui_minimap()
                print(out)
            except Exception as e:
                print(f"[ERROR] fusion_minimap_overlay failed: {e!r}")

        elif choice == "20":
            # Export SOS Overlay
            try:
                sys.path.insert(0, str(SRC))
                from spectral_sos_overlay import build_sos_overlay, write_gui_overlay  # type: ignore
                data = build_sos_overlay()
                path = write_gui_overlay(data)
                print(f"[OK] SOS overlay exported → {path}")
            except Exception as e:
                print(f"[ERROR] spectral_sos_overlay failed: {e!r}")

        elif choice == "21":
            # Run-History Intelligence Timeline
            run_py("run_history_intel.py")

        elif choice == "22":
            # Export Spectral Snapshot Bundle
            try:
                sys.path.insert(0, str(SRC))
                from spectral_snapshot_export import export_spectral_snapshot  # type: ignore
                out = export_spectral_snapshot()
                print(f"[OK] Spectral snapshot bundle → {out}")
            except Exception as e:
                print(f"[ERROR] spectral_snapshot_export failed: {e!r}")

        elif choice == "23":
            # Build Demo Deck Manifest
            try:
                sys.path.insert(0, str(SRC))
                from demo_deck_manifest import build_demo_deck_manifest  # type: ignore
                out = build_demo_deck_manifest()
                print(f"[OK] Demo deck manifest → {out}")
            except Exception as e:
                print(f"[ERROR] demo_deck_manifest failed: {e!r}")

        elif choice == "24":
            # Export Sensor Reliability Report
            try:
                sys.path.insert(0, str(SRC))
                from sensor_reliability import export_reliability_report  # type: ignore
                out = export_reliability_report()
                print(out)
            except Exception as e:
                print(f"[ERROR] sensor_reliability export failed: {e!r}")

        elif choice == "25":
            # Cross-Sensor Validation + Report
            try:
                sys.path.insert(0, str(SRC))
                from cross_sensor_validator import run_cross_validation  # type: ignore
                from cross_sensor_report import build_report  # type: ignore
                print(run_cross_validation())
                print(build_report())
            except Exception as e:
                print(f"[ERROR] Cross-sensor validation failed: {e!r}")

        elif choice == "26":
            # Generate SBIR Phase I One-Pager
            try:
                sys.path.insert(0, str(SRC))
                from sbir_onepager import write_onepager  # type: ignore
                out = write_onepager()
                print(f"SBIR One-Pager written to: {out}")
            except Exception as e:
                print(f"[ERROR] SBIR one-pager failed: {e!r}")

        elif choice == "27":
            # Golden Dome Validator
            try:
                sys.path.insert(0, str(SRC))
                from golden_dome_validator import build_validation  # type: ignore
                out = build_validation()
                print(f"Golden Dome Validation complete → {out['path']}")
            except Exception as e:
                print(f"[ERROR] golden_dome_validator failed: {e!r}")

        elif choice == "28":
            # Test Spectral Owl Fallback Mode
            try:
                sys.path.insert(0, str(SRC))
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
                print(f"[ERROR] fallback test failed: {e!r}")

        elif choice == "29":
            # Golden Dome Drift Report
            try:
                sys.path.insert(0, str(SRC))
                from golden_dome_drift import write_drift  # type: ignore
                out = write_drift()
                print(out)
            except Exception as e:
                print(f"[ERROR] golden_dome_drift failed: {e!r}")

        elif choice == "30":
            # Sensor Reliability Trendline
            try:
                sys.path.insert(0, str(SRC))
                from reliability_trend import compute_trend  # type: ignore
                out = compute_trend()
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] reliability_trend failed: {e!r}")

        elif choice == "31":
            # Owl Confidence Estimator
            try:
                sys.path.insert(0, str(SRC))
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
            # Crisis Mode Toggle
            try:
                sys.path.insert(0, str(SRC))
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
                print(f"[ERROR] crisis_mode_flag failed: {e!r}")

        elif choice == "33":
            # Set Operator Name
            try:
                sys.path.insert(0, str(SRC))
                from operator_identity import set_identity  # type: ignore
                nm = input("Enter operator name: ").strip()
                print(set_identity(nm))
            except Exception as e:
                print(f"[ERROR] operator_identity failed: {e!r}")

        elif choice == "34":
            # Operator Safety Layer Report
            try:
                sys.path.insert(0, str(SRC))
                from operator_safety_layer import compute_osl  # type: ignore
                out = compute_osl()
                print("=== Operator Safety Layer ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Operator Safety Layer failed: {e!r}")

        elif choice == "35":
            # Sensor Latency Intelligence
            try:
                sys.path.insert(0, str(SRC))
                from sensor_latency import compute_latency_report  # type: ignore
                out = compute_latency_report()
                print("=== Sensor Latency ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] sensor_latency failed: {e!r}")

        elif choice == "36":
            # Golden Dome Nuclear Readiness Snapshot
            try:
                sys.path.insert(0, str(SRC))
                from golden_dome_snapshot import build_snapshot  # type: ignore
                out = build_snapshot()
                print("=== Nuclear Readiness Snapshot ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] golden_dome_snapshot failed: {e!r}")

        elif choice == "37":
            # Switch Profile — Nuclear Early-Warning
            try:
                sys.path.insert(0, str(SRC))
                from profile_engine import set_profile  # type: ignore
                out = set_profile("nuclear_early_warning")
                print(out)
            except Exception as e:
                print(f"[ERROR] profile_engine.set_profile failed: {e!r}")

        elif choice == "38":
            # Fusion Heat Index (Battlespace Temperature)
            try:
                sys.path.insert(0, str(SRC))
                from fusion_heat_index import compute_fhi  # type: ignore
                out = compute_fhi()
                print("=== FUSION HEAT INDEX ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] fusion_heat_index failed: {e!r}")

        elif choice == "39":
            # Generate Pre-Launch ISR Watchboard
            try:
                sys.path.insert(0, str(SRC))
                from prelaunch_watchboard import build_watchboard  # type: ignore
                out = build_watchboard()
                print(f"[OK] Watchboard written to: {out}")
            except Exception as e:
                print(f"[ERROR] prelaunch_watchboard failed: {e!r}")

        elif choice == "40":
            # NEW: GLL Readiness + System Integrity + HTML Refresh
            try:
                sys.path.insert(0, str(SRC))
                from gll_readiness import write_gll_readiness  # type: ignore
                from system_integrity import write_system_integrity  # type: ignore
                from mission_brief_html import write_html_brief  # type: ignore

                print("[INFO] Computing GLL readiness…")
                r_path = write_gll_readiness()
                print(f"[OK] GLL readiness snapshot → {r_path}")

                print("[INFO] Computing system integrity…")
                i_path = write_system_integrity()
                print(f"[OK] System integrity report → {i_path}")

                print("[INFO] Regenerating HTML mission brief…")
                h_path = write_html_brief()
                print(f"[OK] HTML mission brief → {h_path}")

            except Exception as e:
                print(f"[ERROR] Readiness/Integrity/HTML refresh failed: {e!r}")

        else:
            print(f"Unknown option: {choice!r}")


if __name__ == "__main__":
    main()

