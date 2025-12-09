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
"""

import sys
import subprocess
import json
from pathlib import Path


BASE = Path(__file__).parent


def run_py(rel_path: str) -> int:
    """Helper to run another Python module in this src/ directory."""
    script = BASE / rel_path
    if not script.exists():
        print(f"[ERROR] Script not found: {script}")
        return 1
    return subprocess.call([sys.executable, str(script)])


def tail_file(path: Path, n: int = 20) -> None:
    if not path.exists():
        print(f"[WARN] File not found: {path}")
        return
    lines = path.read_text().splitlines()
    for line in lines[-n:]:
        print(line)


def main() -> None:
    while True:
        print("\nGhost Lantern Labs — Ghost CLI")
        print("--------------------------------")
        print("  1) Run QA validation")
        print("  2) Show latest 20 log events")
        print("  3) Build operator snapshot")
        print("  4) Run full fusion pipeline + snapshot")
        print("  5) Spectral Owl memory viewer")
        print("  6) Spectral Owl analysis (fusion scoring check)")
        print("  7) Pipeline health check")
        print("  8) Mission briefing (profile-aware)")
        print("  9) Exit")
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
        choice = input("\nSelect option: ").strip()

        # 1) QA validation
        if choice == "1":
            run_py("qa_validator.py")

        # 2) Latest 20 log events
        elif choice == "2":
            tail_file(BASE / "fusion_ops_log.csv", n=20)

        # 3) Operator snapshot
        elif choice == "3":
            try:
                from operator_snapshot import build_operator_snapshot
                out = build_operator_snapshot()
                print(f"[OK] Operator snapshot written → {out}")
            except Exception as e:
                print(f"[ERROR] Snapshot failed: {e!r}")

        # 4) Full fusion pipeline + snapshot
        elif choice == "4":
            try:
                run_py("fusion_ingest.py")
                run_py("fusion_scoring.py")
                from operator_snapshot import build_operator_snapshot
                out = build_operator_snapshot()
                print(f"[OK] Fusion + snapshot complete → {out}")
            except Exception as e:
                print(f"[ERROR] Fusion pipeline failed: {e!r}")

        # 5) Spectral Owl memory viewer
        elif choice == "5":
            try:
                from spectral_owl.threat_memory_summary import build_summary
                print(build_summary())
            except Exception as e:
                print(f"[ERROR] Owl memory viewer failed: {e!r}")

        # 6) Spectral Owl analysis (fusion scoring check)
        elif choice == "6":
            try:
                from spectral_owl.owl_brain_phase2 import analyze_fusion
                from fusion_scoring import load_scores
                scores = load_scores()
                out = analyze_fusion(scores)
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Owl analysis failed: {e!r}")

        # 7) Pipeline health check
        elif choice == "7":
            try:
                from pipeline_health import evaluate_pipeline_health
                report = evaluate_pipeline_health()
                print(json.dumps(report, indent=2))
            except Exception as e:
                print(f"[ERROR] Pipeline health failed: {e!r}")

        # 8) Mission briefing (profile-aware text)
        elif choice == "8":
            try:
                from daily_mission_brief import build_mission_brief
                print(build_mission_brief())
            except Exception as e:
                print(f"[ERROR] Mission briefing failed: {e!r}")

        # 9) Exit
        elif choice == "9":
            print("Exiting Ghost CLI.")
            break

        # 10) Anti-DoS environment scan
        elif choice == "10":
            run_py("anti_dos.py")

        # 11) Cloud Sync Check
        elif choice == "11":
            try:
                from cloud.azure_ingest import check_cloud_status
                print(check_cloud_status())
            except Exception as e:
                print(f"[ERROR] Cloud sync check failed: {e!r}")

        # 12) Threat Memory Summary
        elif choice == "12":
            try:
                from spectral_owl.threat_memory_summary import build_summary
                print(build_summary())
            except Exception as e:
                print(f"[ERROR] Threat memory summary failed: {e!r}")

        # 13) Build Daily Visual Pack
        elif choice == "13":
            try:
                from generate_daily_visual_pack import main as build_daily_pack
                print(build_daily_pack())
            except Exception as e:
                print(f"[ERROR] Daily visual pack failed: {e!r}")

        # 14) Show Active Profile Status
        elif choice == "14":
            try:
                from profile_status import build_profile_status
                print(build_profile_status())
            except Exception as e:
                print(f"[ERROR] Profile status failed: {e!r}")

        # 15) Run Family Law Demo (Shari)
        elif choice == "15":
            try:
                from legal_ingest_family_law import main as ingest_family_law
                from family_law_scoring import main as score_family_law
                from family_law_brief import main as brief_family_law
                ingest_family_law()
                score_family_law()
                print(brief_family_law())
            except Exception as e:
                print(f"[ERROR] Family Law demo failed: {e!r}")

        # 16) Owl Memory Diagnostics
        elif choice == "16":
            try:
                from spectral_owl.owl_memory import owl_memory_diagnostics
                print(owl_memory_diagnostics())
            except Exception as e:
                print(f"[ERROR] Owl memory diagnostics failed: {e!r}")

        # 17) Spectral Dashboard Export
        elif choice == "17":
            try:
                from spectral_dashboard_api import build_dashboard_bundle
                out = build_dashboard_bundle()
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Spectral dashboard export failed: {e!r}")

        # 18) Mission Brief HTML Generator
        elif choice == "18":
            try:
                from mission_brief_html import write_daily_brief as write_html_brief
                out = write_html_brief()
                print(f"[OK] HTML brief written → {out}")
            except Exception as e:
                print(f"[ERROR] Mission brief HTML failed: {e!r}")

        # 19) Export GUI Minimap Overlay
        elif choice == "19":
            try:
                from fusion_minimap_overlay import export_gui_minimap
                out = export_gui_minimap()
                print(out)
            except Exception as e:
                print(f"[ERROR] Minimap export failed: {e!r}")

        # 20) Export SOS Overlay
        elif choice == "20":
            try:
                from spectral_sos_overlay import build_sos_overlay
                out = build_sos_overlay()
                print(f"[OK] SOS overlay exported → {out}")
            except Exception as e:
                print(f"[ERROR] SOS overlay export failed: {e!r}")

        # 21) Run-History Intelligence Timeline
        elif choice == "21":
            try:
                from run_history_intel import main as run_history_intel_main
                print(run_history_intel_main())
            except Exception as e:
                print(f"[ERROR] Run-history intel failed: {e!r}")

        # 22) Export Spectral Snapshot Bundle
        elif choice == "22":
            try:
                from spectral_snapshot_bundle import export_spectral_snapshot
                out = export_spectral_snapshot()
                print(f"[OK] Spectral snapshot exported → {out}")
            except Exception as e:
                print(f"[ERROR] Spectral snapshot export failed: {e!r}")

        # 23) Build Demo Deck Manifest
        elif choice == "23":
            try:
                from demo_deck_manifest import build_demo_deck_manifest
                out = build_demo_deck_manifest()
                print(f"[OK] Demo deck manifest written → {out}")
            except Exception as e:
                print(f"[ERROR] Demo deck manifest failed: {e!r}")

        # 24) Export Sensor Reliability Report
        elif choice == "24":
            try:
                from sensor_reliability import export_reliability_report
                out = export_reliability_report()
                print(f"[OK] Sensor reliability report → {out}")
            except Exception as e:
                print(f"[ERROR] Reliability export failed: {e!r}")

        # 25) Cross-Sensor Validation + Report
        elif choice == "25":
            try:
                from cross_sensor_validator import run_cross_validation
                from cross_sensor_report import build_report
                print(run_cross_validation())
                print(build_report())
            except Exception as e:
                print(f"[ERROR] Cross-sensor validation failed: {e!r}")

        # 26) Generate SBIR Phase I One-Pager
        elif choice == "26":
            try:
                from sbir_onepager import write_onepager
                out = write_onepager()
                print(f"SBIR One-Pager written to: {out}")
            except Exception as e:
                print(f"[ERROR] SBIR one-pager failed: {e!r}")

        # 27) Golden Dome Validator
        elif choice == "27":
            try:
                from golden_dome_validator import build_validation
                out = build_validation()
                print(f"Golden Dome Validation complete → {out['path']}")
            except Exception as e:
                print(f"[ERROR] Golden Dome validation failed: {e!r}")

        # 28) Test Spectral Owl Fallback Mode
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

        # 29) Golden Dome Drift Report
        elif choice == "29":
            try:
                from golden_dome_drift import write_drift
                print(write_drift())
            except Exception as e:
                print(f"[ERROR] Golden Dome drift failed: {e!r}")

        # 30) Sensor Reliability Trendline
        elif choice == "30":
            try:
                from reliability_trend import compute_trend
                print(compute_trend())
            except Exception as e:
                print(f"[ERROR] Reliability trend failed: {e!r}")

        # 31) Owl Confidence Estimator
        elif choice == "31":
            try:
                from spectral_owl.owl_confidence import compute_confidence
                sample = {"critical_alerts": 1, "warning_alerts": 4, "avg_reliability": 92}
                print(compute_confidence(sample))
            except Exception as e:
                print(f"[ERROR] Owl confidence failed: {e!r}")

        # 32) Crisis Mode Toggle
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

        # 33) Set Operator Name
        elif choice == "33":
            try:
                from operator_identity import set_identity
                nm = input("Enter operator name: ").strip()
                print(set_identity(nm))
            except Exception as e:
                print(f"[ERROR] Operator identity failed: {e!r}")

        # 34) Operator Safety Layer Report
        elif choice == "34":
            try:
                from operator_safety_layer import compute_osl
                out = compute_osl()
                print("=== Operator Safety Layer ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] OSL computation failed: {e!r}")

        # 35) Sensor Latency Intelligence
        elif choice == "35":
            try:
                from sensor_latency import compute_latency_report
                out = compute_latency_report()
                print("=== SENSOR LATENCY ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Sensor latency failed: {e!r}")

        # 36) Golden Dome Nuclear Readiness Snapshot
        elif choice == "36":
            try:
                from golden_dome_snapshot import build_snapshot
                out = build_snapshot()
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Nuclear readiness snapshot failed: {e!r}")

        # 37) Switch Profile — Nuclear Early-Warning
        elif choice == "37":
            try:
                from profile_engine import set_profile
                print(set_profile("nuclear_early_warning"))
            except Exception as e:
                print(f"[ERROR] Profile switch failed: {e!r}")

        # 38) Fusion Heat Index (Battlespace Temperature)
        elif choice == "38":
            try:
                from fusion_heat_index import compute_fhi
                out = compute_fhi()
                print("=== FUSION HEAT INDEX ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Fusion Heat Index failed: {e!r}")

        # 39) Generate Pre-Launch ISR Watchboard
        elif choice == "39":
            try:
                from prelaunch_watchboard import build_watchboard
                out = build_watchboard()
                print(f"[OK] Watchboard written to: {out}")
            except Exception as e:
                print(f"[ERROR] Watchboard failed: {e!r}")

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()

