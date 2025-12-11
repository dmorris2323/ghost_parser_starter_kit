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
 42) Build War Room Brief
 43) Nuclear Risk Timeline
 44) Golden Dome Nuclear Brief Pack
 45) Base Defense Hotspots
 46) Strategic Readiness Index
 47) Defensive Cyber Intelligence Report
 48) Foreign Language Interpreter
 49) SPS Mutation Watcher Report
 50) Training Curve / AGI SUmmary
 51) SPS-System Immunity Scan
 52) SPS-System Integrity Report
 60) SPS Behavioral Integrity Monitor (Module 3)
 61) Pre-Boost Threat Card (Nuclear Early-Warning Fusion)
"""

import sys
import subprocess
import json
from pathlib import Path
from defensive_cyber_intel_module import analyze_defensive_cyber_intel
from language_interpreter import run_language_interpreter
from sps_mutation_watcher import write_mutation_report
from sps_behavior_monitor import write_behavior_report
from prelaunch_signals_analyzer import write_preboost_threat_card


BASE_DIR = Path(__file__).resolve().parent


def run_py(script: str) -> int:
    """
    Helper to run another Python script in src/ (or subdir) safely.
    """
    script_path = BASE_DIR / script
    if not script_path.exists():
        print(f"[WARN] Script not found: {script_path}")
        return 1
    return subprocess.run([sys.executable, str(script_path)], check=False).returncode


def tail_file(path: Path, n: int = 20) -> None:
    if not path.exists():
        print(f"[WARN] File not found: {path}")
        return
    try:
        # Use Python, not shell, to avoid env weirdness
        lines = path.read_text(errors="ignore").splitlines()[-n:]
        for line in lines:
            print(line)
    except Exception as e:
        print(f"[ERROR] Failed to read {path}: {e!r}")


def main() -> int:
    print(__doc__)

    while True:
        choice = input("Select option: ").strip()

        # ───────────────── 1–10 ─────────────────
        if choice == "1":
            # Run QA validation
            try:
                from qa_validator import main as qa_main
                qa_main()
            except Exception as e:
                print(f"[ERROR] QA validator failed: {e!r}")
                print("Falling back to: python qa_validator.py")
                run_py("qa_validator.py")

        elif choice == "2":
            # Show latest 20 log events
            print("=== fusion_events.log (tail -20) ===")
            tail_file(BASE_DIR / "fusion_events.log", 20)
            print("\n=== fusion_ops_log.csv (tail -20) ===")
            tail_file(BASE_DIR / "fusion_ops_log.csv", 20)

        elif choice == "3":
            # Build operator snapshot
            try:
                from operator_snapshot import build_operator_snapshot
                out = build_operator_snapshot()
                print("=== OPERATOR SNAPSHOT BUILT ===")
                print(f"Snapshot file → {out}")
            except Exception as e:
                print(f"[ERROR] Operator snapshot failed: {e!r}")
                run_py("operator_snapshot.py")

        elif choice == "4":
            # Run full fusion pipeline + snapshot
            print("[INFO] Running full fusion pipeline …")
            run_py("fusion_run.py")
            try:
                from operator_snapshot import build_operator_snapshot
                out = build_operator_snapshot()
                print("=== FULL PIPELINE + SNAPSHOT COMPLETE ===")
                print(f"Snapshot file → {out}")
            except Exception as e:
                print(f"[WARN] Pipeline ran but snapshot failed: {e!r}")

        elif choice == "5":
            # Spectral Owl memory viewer (threat memory summary)
            try:
                run_py("spectral_owl/threat_memory_summary.py")
            except Exception as e:
                print(f"[ERROR] Owl memory viewer failed: {e!r}")

        elif choice == "6":
            # Spectral Owl analysis (fusion scoring check)
            try:
                run_py("spectral_owl/owl_brain_phase2.py")
            except Exception as e:
                print(f"[ERROR] Owl analysis failed: {e!r}")

        elif choice == "7":
            # Pipeline health check
            try:
                from pipeline_health import evaluate_pipeline_health
                result = evaluate_pipeline_health()
                print("=== PIPELINE HEALTH ===")
                print(json.dumps(result, indent=2))
            except Exception as e:
                print(f"[ERROR] Pipeline health failed: {e!r}")
                run_py("pipeline_health.py")

        elif choice == "8":
            # Mission briefing (text)
            try:
                from daily_mission_brief import write_daily_brief
                out = write_daily_brief()
                print("=== DAILY MISSION BRIEF (TEXT) ===")
                print(out)
            except Exception as e:
                print(f"[ERROR] Mission brief failed: {e!r}")
                run_py("daily_mission_brief.py")

        elif choice == "9":
            print("Exiting Ghost Lantern Labs CLI.")
            return 0

        elif choice == "10":
            # Anti-DoS environment scan
            try:
                run_py("anti_dos.py")
            except Exception as e:
                print(f"[ERROR] Anti-DoS scan failed: {e!r}")

        # ───────────────── 11–20 ─────────────────
        elif choice == "11":
            # Cloud Sync Check
            try:
                run_py("cloud/azure_ingest.py")
            except Exception as e:
                print(f"[ERROR] Cloud sync check failed: {e!r}")

        elif choice == "12":
            # Threat Memory Summary (doctrine view)
            try:
                run_py("threat_memory_doctrine_report.py")
            except Exception as e:
                print(f"[ERROR] Threat memory summary failed: {e!r}")

        elif choice == "13":
            # Build Daily Visual Pack
            try:
                from generate_daily_visual_pack import main as build_pack
                build_pack()
            except Exception:
                run_py("generate_daily_visual_pack.py")

        elif choice == "14":
            # Show Active Profile Status
            try:
                from profile_status import print_status
                print_status()
            except Exception as e:
                print(f"[ERROR] Profile status failed: {e!r}")
                run_py("profile_status.py")

        elif choice == "15":
            # Run Family Law Demo (Shari)
            try:
                run_py("legal_demo_pack.py")
            except Exception as e:
                print(f"[ERROR] Family law demo failed: {e!r}")

        elif choice == "16":
            # Owl Memory Diagnostics
            try:
                run_py("spectral_owl/owl_memory.py")
            except Exception as e:
                print(f"[ERROR] Owl memory diagnostics failed: {e!r}")

        elif choice == "17":
            # Spectral Dashboard Export
            try:
                run_py("spectral_dashboard_api.py")
            except Exception as e:
                print(f"[ERROR] Spectral dashboard export failed: {e!r}")

        elif choice == "18":
            # Mission Brief HTML Generator
            try:
                run_py("mission_brief_html.py")
            except Exception as e:
                print(f"[ERROR] Mission brief HTML failed: {e!r}")

        elif choice == "19":
            # Export GUI Minimap Overlay
            try:
                run_py("fusion_minimap_overlay.py")
            except Exception as e:
                print(f"[ERROR] Minimap overlay export failed: {e!r}")

        elif choice == "20":
            # Export SOS Overlay
            try:
                run_py("spectral_sos_overlay.py")
            except Exception as e:
                print(f"[ERROR] SOS overlay export failed: {e!r}")

        # ───────────────── 21–30 ─────────────────
        elif choice == "21":
            # Run-History Intelligence Timeline
            try:
                run_py("run_history_intel.py")
            except Exception as e:
                print(f"[ERROR] Run-history intel failed: {e!r}")

        elif choice == "22":
            # Export Spectral Snapshot Bundle
            try:
                run_py("spectral_snapshot_export.py")
            except Exception as e:
                print(f"[ERROR] Spectral snapshot export failed: {e!r}")

        elif choice == "23":
            # Build Demo Deck Manifest
            try:
                run_py("demo_deck_manifest.py")
            except Exception as e:
                print(f"[ERROR] Demo deck manifest failed: {e!r}")

        elif choice == "24":
            # Export Sensor Reliability Report
            try:
                from sensor_reliability import export_reliability_report
                out = export_reliability_report()
                print("=== SENSOR RELIABILITY REPORT ===")
                print(out)
            except Exception as e:
                print(f"[ERROR] Reliability report failed: {e!r}")
                run_py("sensor_reliability.py")

        elif choice == "25":
            # Cross-Sensor Validation + Report
            try:
                from cross_sensor_validator import run_cross_validation
                from cross_sensor_report import build_report
                print(run_cross_validation())
                print(build_report())
            except Exception as e:
                print(f"[ERROR] Cross-sensor validation failed: {e!r}")

        elif choice == "26":
            # Generate SBIR Phase I One-Pager
            try:
                from sbir_onepager import write_onepager
                out = write_onepager()
                print(f"SBIR One-Pager written to: {out}")
            except Exception as e:
                print(f"[ERROR] SBIR one-pager failed: {e!r}")

        elif choice == "27":
            # Golden Dome Validator
            try:
                from golden_dome_validator import build_validation
                out = build_validation()
                print("=== GOLDEN DOME VALIDATION ===")
                print(f"Report: {out['path']}")
            except Exception as e:
                print(f"[ERROR] Golden Dome validation failed: {e!r}")

        elif choice == "28":
            # Test Spectral Owl Fallback Mode
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
            # Golden Dome Drift Report
            try:
                from golden_dome_drift import write_drift
                print(write_drift())
            except Exception as e:
                print(f"[ERROR] Golden Dome drift failed: {e!r}")

        elif choice == "30":
            # Sensor Reliability Trendline
            try:
                from reliability_trend import compute_trend
                print(json.dumps(compute_trend(), indent=2))
            except Exception as e:
                print(f"[ERROR] Reliability trend failed: {e!r}")

        # ───────────────── 31–40 ─────────────────
        elif choice == "31":
            # Owl Confidence Estimator
            try:
                from spectral_owl.owl_confidence import compute_confidence
                sample = {"critical_alerts": 1, "warning_alerts": 4, "avg_reliability": 92}
                print(compute_confidence(sample))
            except Exception as e:
                print(f"[ERROR] Owl confidence failed: {e!r}")

        elif choice == "32":
            # Crisis Mode Toggle
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
            # Set Operator Name
            try:
                from operator_identity import set_identity
                nm = input("Enter operator name: ").strip()
                print(set_identity(nm))
            except Exception as e:
                print(f"[ERROR] Operator identity failed: {e!r}")

        elif choice == "34":
            # Operator Safety Layer Report
            try:
                from operator_safety_layer import compute_osl
                out = compute_osl()
                print("=== Operator Safety Layer ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] OSL failed: {e!r}")

        elif choice == "35":
            # Sensor Latency Intelligence
            try:
                from sensor_latency import compute_latency_report
                out = compute_latency_report()
                print("=== SENSOR LATENCY REPORT ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Sensor latency failed: {e!r}")

        elif choice == "36":
            # Golden Dome Nuclear Readiness Snapshot
            try:
                from golden_dome_snapshot import build_snapshot
                snap = build_snapshot()
                print("=== NUCLEAR READINESS SNAPSHOT ===")
                print(json.dumps(snap, indent=2))
            except Exception as e:
                print(f"[ERROR] Nuclear snapshot failed: {e!r}")

        elif choice == "37":
            # Switch Profile — Nuclear Early-Warning
            try:
                from profile_engine import set_profile
                print(set_profile("nuclear_early_warning"))
            except Exception as e:
                print(f"[ERROR] Profile switch failed: {e!r}")

        elif choice == "38":
            # Fusion Heat Index (Battlespace Temperature)
            try:
                from fusion_heat_index import compute_fhi
                out = compute_fhi()
                print("=== FUSION HEAT INDEX ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Fusion Heat Index failed: {e!r}")

        elif choice == "39":
            # Generate Pre-Launch ISR Watchboard
            try:
                from prelaunch_watchboard import build_watchboard
                out = build_watchboard()
                print(f"[OK] Watchboard written to: {out}")
            except Exception as e:
                print(f"[ERROR] Watchboard failed: {e!r}")

        elif choice == "40":
                from fusion_temporal_forecast import forecast_next_6h
                print(json.dumps(forecast_next_6h(), indent=2))

        elif choice == "41":
                from adversary_pattern_engine import analyze_patterns
                print(json.dumps(analyze_patterns(), indent=2))

        elif choice == "42":
                from gll_war_room_brief import write_war_room_brief
                out = write_war_room_brief()
                print("=== WAR ROOM BRIEF BUILT ===")
                print(f"JSON → {out['json_path']}")
                print(f"TXT  → {out['txt_path']}")

        elif choice == "43":
            # Nuclear Risk Timeline
                from nuclear_risk_timeline import write_nuclear_risk_timeline
                out = write_nuclear_risk_timeline()
                print("=== NUCLEAR RISK TIMELINE BUILT ===")
                print(f"JSON → {out['json_path']}")
                print(f"TXT  → {out['txt_path']}")

        elif choice == "44":
            # Golden Dome Nuclear Brief Pack
                from golden_dome_brief_pack import write_golden_dome_brief_pack
                out = write_golden_dome_brief_pack()
                print("=== GOLDEN DOME BRIEF PACK BUILT ===")
                print(f"JSON → {out['json_path']}")
                print(f"TXT  → {out['txt_path']}")

        elif choice == "45":
            # Base Defense Hotspots
                from base_defense_hotspots import write_base_defense_hotspots
                out = write_base_defense_hotspots()
                print("=== BASE DEFENSE HOTSPOTS BUILT ===")
                print(f"JSON → {out['json_path']}")
                print(f"TXT  → {out['txt_path']}")

        elif choice == "46":
            # Strategic Readiness Index
                from strategic_readiness_index import write_strategic_readiness_index
                out = write_strategic_readiness_index()
                print("=== STRATEGIC READINESS INDEX BUILT ===")
                print(f"JSON → {out['json_path']}")
                print(f"TXT  → {out['txt_path']}")

        elif choice == "47":
            result = analyze_defensive_cyber_intel()
            print(json.dumps(result, indent=2))


        elif choice == "48":
            print("Running GLL Language Interpreter (Module 1 – Framework)...")
            result = run_language_interpreter()
            print("Language analysis written:")
            print(f"  JSON: {result['json_path']}")
            print(f"  TXT:  {result['txt_path']}")

        elif choice == "49":
            print("Running SPS Module 2 – Mutation Watcher...")
            result = write_mutation_report()
            print("SPS Mutation Watcher report written:")
            print(f"  JSON: {result['json_path']}")
            print(f"  TXT:  {result['txt_path']}")

        elif choice == "50":
            print("Running GLL System Immunity Scan (Mutation Watcher)...")
            from sps_mutation_watcher import check_integrity
            result = check_integrity()
            print(json.dumps(result, indent=2))
        elif choice == "51":
            print("Running SPS – System Immunity Scan...")
            from sps_mutation_watcher import run_sps_immunity_scan
            result = run_sps_immunity_scan()
            print(json.dumps(result, indent=2))

        elif choice == "52":
            print("Generating System Integrity Report...")
            from system_integrity_report import generate_system_integrity_report
            result = generate_system_integrity_report()
            print(f"System Integrity Report written to: {result['report_path']}")
            summary = result["summary"]
            print(
                f"Summary – Clean: {summary['clean']}, "
                f"Modified: {summary['modified']}, "
                f"Missing: {summary['missing']}, "
                f"Untracked: {summary['untracked_baseline']}"
        )

        elif choice == "60":
            print("Running SPS Module 3 – Behavioral Integrity Monitor...")
            result = write_behavior_report()
            print("SPS Behavioral Integrity report written:")
            print(f"  JSON: {result['json_path']}")
            print(f"  TXT:  {result['txt_path']}")

        elif choice == "61":
            print("Running Pre-Boost Threat Card analysis...")
            result = write_preboost_threat_card()
            print("Pre-Boost Threat Card written:")
            print(f"  JSON: {result['json_path']}")
            print(f"  TXT:  {result['txt_path']}")

        else:
            print("Invalid option. Try again.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

