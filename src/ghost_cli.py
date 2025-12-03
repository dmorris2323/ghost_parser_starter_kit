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
"""

import sys
import subprocess
from pathlib import Path

# Base directory for running scripts
BASE_DIR = Path(__file__).parent

# Import only the modules we absolutely need as Python calls
# (everything else we hit via subprocess to avoid fragile imports)
try:
    from cloud.azure_ingest import cloud_sync_health_check
except Exception:
    cloud_sync_health_check = None  # type: ignore

try:
    from sensor_reliability import export_reliability_report
except Exception:
    export_reliability_report = None  # type: ignore


def run_script(script_name: str, args=None) -> int:
    """
    Run a Python script in this src directory via subprocess,
    show its stdout/stderr, and return the exit code.
    """
    if args is None:
        args = []

    script_path = BASE_DIR / script_name
    if not script_path.exists():
        print(f"[ERROR] Script not found: {script_path}")
        return 1

    print(f"[RUN] {script_path.name} {' '.join(args)}")
    proc = subprocess.run(
        [sys.executable, str(script_path), *args],
        cwd=str(BASE_DIR),
        capture_output=True,
        text=True,
    )

    if proc.stdout:
        print(proc.stdout.strip())
    if proc.stderr:
        print(proc.stderr.strip())

    if proc.returncode == 0:
        print(f"[OK] {script_path.name} completed.")
    else:
        print(f"[FAIL] {script_path.name} exited with code {proc.returncode}.")

    return proc.returncode


def print_menu() -> None:
    print("")
    print("Ghost Lantern Labs — Operator Console")
    print("-------------------------------------")
    print("Menu options:")
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
    print("")


def show_latest_log_events() -> None:
    """
    Show the latest 20 lines from fusion_ops_log.csv if it exists.
    """
    log_path = BASE_DIR / "fusion_ops_log.csv"
    if not log_path.exists():
        print("[INFO] fusion_ops_log.csv not found.")
        return

    lines = log_path.read_text(encoding="utf-8").splitlines()
    tail = lines[-20:] if len(lines) > 20 else lines
    print("=== Latest Fusion Ops Log Events (tail) ===")
    for line in tail:
        print(line)


def show_spectral_owl_memory() -> None:
    """
    Show a quick view of Owl / threat memory.
    Tries threat_memory.csv, then owl_memory.txt, if present.
    """
    candidates = [
        BASE_DIR / "data" / "threat_memory.csv",
        BASE_DIR / "data" / "threat_memory_doctrine.csv",
        BASE_DIR / "owl_memory.txt",
        BASE_DIR / "threat_memory.txt",
    ]

    printed_any = False
    for path in candidates:
        if path.exists():
            print(f"\n=== Memory View: {path.name} (tail) ===")
            lines = path.read_text(encoding="utf-8").splitlines()
            tail = lines[-20:] if len(lines) > 20 else lines
            for line in tail:
                print(line)
            printed_any = True

    if not printed_any:
        print("[INFO] No threat/Owl memory files found yet.")


def show_owl_memory_diagnostics() -> None:
    """
    Run threat_memory_stats.py if present; otherwise fallback to the basic memory view.
    """
    stats_script = BASE_DIR / "threat_memory_stats.py"
    if stats_script.exists():
        run_script("threat_memory_stats.py")
    else:
        print("[WARN] threat_memory_stats.py not found, falling back to basic memory viewer.")
        show_spectral_owl_memory()


def run_mission_brief_profile_aware() -> None:
    """
    Prefer profile_mission_brief.py, fall back to mission_briefing.py
    or daily_mission_brief.py if needed.
    """
    if (BASE_DIR / "profile_mission_brief.py").exists():
        run_script("profile_mission_brief.py")
    elif (BASE_DIR / "mission_briefing.py").exists():
        run_script("mission_briefing.py")
    else:
        print("[WARN] profile_mission_brief/mission_briefing not found, using daily_mission_brief.")
        run_script("daily_mission_brief.py")


def run_family_law_demo() -> None:
    """
    Run the family law demo (Shari) end to end:
    - legal_ingest_family_law.py
    - family_law_scoring.py
    - family_law_brief.py
    """
    print("[INFO] Running Family Law Demo (Shari)...")
    run_script("legal_ingest_family_law.py")
    run_script("family_law_scoring.py")
    run_script("family_law_brief.py")

    demo_dir = BASE_DIR / "demos" / "family_law_demo"
    if demo_dir.exists():
        print(f"[OK] Family law demo artifacts available in: {demo_dir}")
    else:
        print("[INFO] Demo directory not found yet; check family_law_*.csv/txt in src/data or src/.")


def cloud_sync_check_cli() -> None:
    """
    Use cloud.azure_ingest.cloud_sync_health_check if available.
    """
    if cloud_sync_health_check is None:
        print("[ERROR] cloud_sync_health_check not available (import failed).")
        return

    try:
        result = cloud_sync_health_check()
        print("[Cloud Sync Health]")
        print(result)
    except Exception as e:
        print(f"[ERROR] Cloud sync health check failed: {e}")


def spectral_dashboard_export_cli() -> None:
    """
    Run spectral_dashboard_api.py to export the dashboard bundle.
    """
    run_script("spectral_dashboard_api.py")


def minimap_export_cli() -> None:
    """
    Export GUI minimap overlay via fusion_minimap_overlay.py
    """
    run_script("fusion_minimap_overlay.py")


def sos_overlay_export_cli() -> None:
    """
    Export SOS overlay via spectral_sos_overlay.py
    """
    run_script("spectral_sos_overlay.py")


def run_history_intel_cli() -> None:
    """
    Run run_history_intel.py to generate the run-history intelligence brief.
    """
    run_script("run_history_intel.py")
    brief_path = BASE_DIR / "run_history_intel_brief.txt"
    if brief_path.exists():
        print(f"[OK] Run-history intel brief → {brief_path}")


def spectral_snapshot_export_cli() -> None:
    """
    Export spectral snapshot bundle via spectral_snapshot_export.py
    """
    run_script("spectral_snapshot_export.py")


def demo_deck_manifest_cli() -> None:
    """
    Build demo deck manifest via demo_deck_manifest.py
    """
    run_script("demo_deck_manifest.py")


def mission_brief_html_cli() -> None:
    """
    Generate daily_mission_brief.html via mission_brief_html.py
    """
    run_script("mission_brief_html.py")
    html_path = BASE_DIR / "docs" / "daily_mission_brief.html"
    if html_path.exists():
        print(f"[OK] HTML mission brief → {html_path}")


def sensor_reliability_export_cli() -> None:
    """
    Export sensor reliability report using sensor_reliability.export_reliability_report()
    """
    if export_reliability_report is None:
        print("[ERROR] export_reliability_report not available (import failed).")
        return

    try:
        result = export_reliability_report()
        print(result)
    except Exception as e:
        print(f"[ERROR] Failed to export sensor reliability report: {e}")


def main() -> None:
    while True:
        print_menu()
        choice = input("Select an option: ").strip()

        if choice == "1":
            # Run QA validation
            run_script("qa_validator.py")

        elif choice == "2":
            # Show latest 20 log events
            show_latest_log_events()

        elif choice == "3":
            # Build operator snapshot
            run_script("operator_snapshot.py")
            snap_path = BASE_DIR / "operator_snapshot.txt"
            if snap_path.exists():
                print(f"[OK] Operator snapshot written → {snap_path}")

        elif choice == "4":
            # Run full fusion pipeline + snapshot
            run_script("fusion_run.py")
            run_script("operator_snapshot.py")

        elif choice == "5":
            # Spectral Owl memory viewer
            show_spectral_owl_memory()

        elif choice == "6":
            # Spectral Owl analysis (fusion scoring check)
            # Prefer owl_brain_phase2; fall back to owl_brain
            if (BASE_DIR / "spectral_owl" / "owl_brain_phase2.py").exists():
                run_script("spectral_owl/owl_brain_phase2.py")
            else:
                run_script("spectral_owl/owl_brain.py")

        elif choice == "7":
            # Pipeline health check
            run_script("pipeline_health.py")

        elif choice == "8":
            # Mission briefing (profile-aware)
            run_mission_brief_profile_aware()

        elif choice == "9":
            print("Exiting Ghost CLI.")
            break

        elif choice == "10":
            # Anti-DoS environment scan
            run_script("anti_dos.py")

        elif choice == "11":
            # Cloud Sync Check
            cloud_sync_check_cli()

        elif choice == "12":
            # Threat Memory Summary (high-level)
            if (BASE_DIR / "spectral_owl" / "threat_memory_summary.py").exists():
                run_script("spectral_owl/threat_memory_summary.py")
            else:
                print("[WARN] threat_memory_summary.py not found; falling back to memory viewer.")
                show_spectral_owl_memory()

        elif choice == "13":
            # Build Daily Visual Pack
            run_script("generate_daily_visual_pack.py")

        elif choice == "14":
            # Show Active Profile Status
            run_script("profile_status.py")

        elif choice == "15":
            # Run Family Law Demo (Shari)
            run_family_law_demo()

        elif choice == "16":
            # Owl Memory Diagnostics
            show_owl_memory_diagnostics()

        elif choice == "17":
            # Spectral Dashboard Export
            spectral_dashboard_export_cli()

        elif choice == "18":
            # Mission Brief HTML Generator
            mission_brief_html_cli()

        elif choice == "19":
            # Export GUI Minimap Overlay
            minimap_export_cli()

        elif choice == "20":
            # Export SOS Overlay
            sos_overlay_export_cli()

        elif choice == "21":
            # Run-History Intelligence Timeline
            run_history_intel_cli()

        elif choice == "22":
            # Export Spectral Snapshot Bundle
            spectral_snapshot_export_cli()

        elif choice == "23":
            # Build Demo Deck Manifest
            demo_deck_manifest_cli()

        elif choice == "24":
            # Export Sensor Reliability Report
            sensor_reliability_export_cli()

        else:
            print(f"[WARN] Unknown option: {choice}")


if __name__ == "__main__":
    main()

