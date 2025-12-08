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
"""

import sys
import subprocess
import json
from pathlib import Path


def run_py(script: str) -> int:
    """
    Helper to run a Python script in this src/ directory.
    Prints stdout/stderr and returns exit code.
    """
    result = subprocess.run(
        [sys.executable, script],
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode


def tail_file(path: Path, n: int = 20) -> str:
    if not path.exists():
        return f"[INFO] File not found: {path}"
    lines = path.read_text().splitlines()
    tail = lines[-n:] if len(lines) > n else lines
    return "\n".join(tail)


def show_menu() -> None:
    print("""
Ghost Lantern Labs — Operator Console

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
""")


def main() -> None:
    while True:
        show_menu()
        choice = input("Select option (1-35, or q to quit): ").strip()

        if choice.lower() in {"q", "quit", "exit"}:
            print("Exiting Ghost Lantern Labs console.")
            break

        # --- CORE OPS ---
        if choice == "1":
            # QA validation
            try:
                from qa_validator import run_all
                print(run_all())
            except Exception as e:
                print(f"[ERROR] QA validation failed: {e}")

        elif choice == "2":
            # Latest 20 log events
            log_path = Path("fusion_ops_log.csv")
            print(tail_file(log_path, 20))

        elif choice == "3":
            # Build operator snapshot
            try:
                from operator_snapshot import build_operator_snapshot
                out = build_operator_snapshot()
                print(f"[OK] Operator snapshot built → {out}")
            except Exception as e:
                print(f"[ERROR] Operator snapshot failed: {e}")

        elif choice == "4":
            # Full fusion pipeline + snapshot
            print("[INFO] Running full fusion pipeline...")
            run_py("fusion_run.py")
            try:
                from operator_snapshot import build_operator_snapshot
                out = build_operator_snapshot()
                print(f"[OK] Fusion + snapshot complete → {out}")
            except Exception as e:
                print(f"[WARN] Fusion ran, but snapshot failed: {e}")

        elif choice == "5":
            # Spectral Owl memory viewer (use threat_memory_summary)
            try:
                from spectral_owl.threat_memory_summary import build_summary
                print(build_summary())
            except Exception as e:
                print(f"[ERROR] Owl memory viewer failed: {e}")

        elif choice == "6":
            # Spectral Owl analysis (simplified: fusion scoring check)
            print("[INFO] Running fusion scoring (Owl analysis path)...")
            rc = run_py("fusion_scoring.py")
            print(f"[INFO] fusion_scoring.py exit code: {rc}")

        elif choice == "7":
            # Pipeline health check
            try:
                from pipeline_health import evaluate_pipeline_health
                report = evaluate_pipeline_health()
                print(json.dumps(report, indent=2))
            except Exception as e:
                print(f"[ERROR] Pipeline health failed: {e}")

        elif choice == "8":
            # Mission briefing (profile-aware if available)
            try:
                try:
                    from profile_mission_brief import build_profile_mission_brief
                    text = build_profile_mission_brief()
                except Exception:
                    from daily_mission_brief import build_mission_brief
                    text = build_mission_brief()
                print(text)
            except Exception as e:
                print(f"[ERROR] Mission briefing failed: {e}")

        elif choice == "9":
            print("Exiting Ghost Lantern Labs console.")
            break

        # --- DEFENSIVE / ENVIRONMENTAL ---
        elif choice == "10":
            # Anti-DoS environment scan
            print("[INFO] Running Anti-DoS scan...")
            run_py("anti_dos.py")

        elif choice == "11":
            # Cloud Sync Check (Azure stub)
            try:
                from cloud.azure_ingest import upload_fusion_output, upload_operator_snapshot
                print(upload_fusion_output())
                print(upload_operator_snapshot())
            except Exception as e:
                print(f"[ERROR] Cloud sync check failed: {e}")

        # --- THREAT MEMORY / DEMOS / VISUALS ---
        elif choice == "12":
            # Threat Memory Summary
            try:
                from spectral_owl.threat_memory_summary import build_summary
                print(build_summary())
            except Exception as e:
                print(f"[ERROR] Threat Memory Summary failed: {e}")

        elif choice == "13":
            # Build Daily Visual Pack
            print("[INFO] Building Daily Visual Pack...")
            run_py("generate_daily_visual_pack.py")

        elif choice == "14":
            # Show Active Profile Status
            try:
                from profile_status import build_profile_status
                print(build_profile_status())
            except Exception as e:
                print(f"[ERROR] Profile status failed: {e}")

        elif choice == "15":
            # Run Family Law Demo (Shari)
            print("[INFO] Running Family Law Demo...")
            run_py("legal_ingest_family_law.py")
            run_py("family_law_scoring.py")
            run_py("family_law_brief.py")

        elif choice == "16":
            # Owl Memory Diagnostics
            print("[INFO] Running Owl Memory Diagnostics...")
            run_py("threat_memory_stats.py")

        elif choice == "17":
            # Spectral Dashboard Export
            print("[INFO] Exporting Spectral Dashboard bundle...")
            run_py("spectral_dashboard_api.py")

        elif choice == "18":
            # Mission Brief HTML Generator
            print("[INFO] Generating HTML mission brief...")
            run_py("mission_brief_html.py")

        elif choice == "19":
            # Export GUI Minimap Overlay
            print("[INFO] Exporting GUI minimap overlay...")
            run_py("fusion_minimap_overlay.py")

        elif choice == "20":
            # Export SOS Overlay
            print("[INFO] Exporting SOS overlay...")
            run_py("spectral_sos_overlay.py")

        elif choice == "21":
            # Run-History Intelligence Timeline
            print("[INFO] Building run-history intelligence timeline...")
            run_py("run_history_intel.py")

        elif choice == "22":
            # Export Spectral Snapshot Bundle
            print("[INFO] Exporting spectral snapshot bundle...")
            run_py("spectral_snapshot_export.py")

        elif choice == "23":
            # Build Demo Deck Manifest
            print("[INFO] Building demo deck manifest...")
            run_py("demo_deck_manifest.py")

        # --- RELIABILITY / GOLDEN DOME / TRENDS / OSL ---
        elif choice == "24":
            # Export Sensor Reliability Report
            try:
                from sensor_reliability import export_reliability_report
                out = export_reliability_report()
                print(f"[OK] Sensor reliability report exported → {out}")
            except Exception as e:
                print(f"[ERROR] Sensor reliability export failed: {e}")

        elif choice == "25":
            # Cross-Sensor Validation + Report
            try:
                from cross_sensor_validator import run_cross_validation
                from cross_sensor_report import build_report
                cv = run_cross_validation()
                rep = build_report()
                print(cv)
                print(rep)
            except Exception as e:
                print(f"[ERROR] Cross-sensor validation failed: {e}")

        elif choice == "26":
            # Generate SBIR Phase I One-Pager
            try:
                from sbir_onepager import write_onepager
                out = write_onepager()
                print(f"[OK] SBIR One-Pager written to: {out}")
            except Exception as e:
                print(f"[ERROR] SBIR one-pager failed: {e}")

        elif choice == "27":
            # Golden Dome Validator
            try:
                from golden_dome_validator import build_validation
                out = build_validation()
                print(f"[OK] Golden Dome Validation complete → {out['path']}")
            except Exception as e:
                print(f"[ERROR] Golden Dome validation failed: {e}")

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
                print(f"[ERROR] Fallback test failed: {e}")

        elif choice == "29":
            # Golden Dome Drift Report
            try:
                from golden_dome_drift import write_drift
                out = write_drift()
                print(f"[OK] Golden Dome drift report written → {out}")
            except Exception as e:
                print(f"[ERROR] Golden Dome drift generation failed: {e}")

        elif choice == "30":
            # Sensor Reliability Trendline
            try:
                from reliability_trend import compute_trend
                trend = compute_trend()
                print(json.dumps(trend, indent=2))
            except Exception as e:
                print(f"[ERROR] Reliability trend failed: {e}")

        elif choice == "31":
            # Owl Confidence Estimator
            try:
                from spectral_owl.owl_confidence import compute_confidence
                sample = {"critical_alerts": 1, "warning_alerts": 4, "avg_reliability": 92}
                print(f"Owl confidence: {compute_confidence(sample)}")
            except Exception as e:
                print(f"[ERROR] Owl confidence failed: {e}")

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
                    print("Invalid selection.")
            except Exception as e:
                print(f"[ERROR] Crisis mode toggle failed: {e}")

        elif choice == "33":
            # Set Operator Name
            try:
                from operator_identity import set_identity
                nm = input("Enter operator name: ").strip()
                print(set_identity(nm))
            except Exception as e:
                print(f"[ERROR] Operator identity set failed: {e}")

        elif choice == "34":
            # Operator Safety Layer Report
            try:
                from operator_safety_layer import compute_osl
                out = compute_osl()
                print("=== Operator Safety Layer ===")
                print(json.dumps(out, indent=2))
            except Exception as e:
                print(f"[ERROR] Operator Safety Layer failed: {e}")

        elif choice == "35":
            # Sensor Latency Intelligence
            try:
                from sensor_latency import log_latency, write_latency_report, compute_latency_report
                entry = log_latency()
                path = write_latency_report()
                report = compute_latency_report()
                print("[OK] Latency entry logged:")
                print(json.dumps(entry, indent=2))
                print(f"[OK] Latency report written → {path}")
                print("=== Latency Report ===")
                print(json.dumps(report, indent=2))
            except Exception as e:
                print(f"[ERROR] Sensor latency intelligence failed: {e}")

        else:
            print(f"[WARN] Unknown option: {choice}")


if __name__ == "__main__":
    main()

