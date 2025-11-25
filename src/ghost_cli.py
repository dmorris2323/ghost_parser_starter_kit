"""
ghost_cli.py — GLL Operator Console
Day 50–51 consolidated version

Menu:
1) Run full QA validation
2) Show last 20 log events
3) Build operator snapshot
4) Run full pipeline + snapshot
5) View Spectral Owl memory
6) Run Spectral Owl (stub)
7) Exit
"""

from pathlib import Path
from datetime import datetime

from fusion_logger import log_event
from qa_validator import run_all as run_qa

from fusion_scoring import score_fusion
from commander_extract import commander_extract
from heatmap_prep import generate_heatmap_data
from fusion_alerts import fusion_alerts
from daily_report import build_daily_report

from spectral_owl.owl_brain import analyze_fusion
from spectral_owl.owl_memory import recall_all, remember


LOG_PATH = Path("fusion_ops_log.csv")
SNAPSHOT_PATH = Path("operator_snapshot.txt")


def show_menu() -> None:
    print("\nGLL OPERATOR CONSOLE — ghost_cli")
    print("================================")
    print("1) Run full QA validation")
    print("2) Show last 20 log events")
    print("3) Build operator snapshot")
    print("4) Run full pipeline + snapshot")
    print("5) View Spectral Owl memory")
    print("6) Run Spectral Owl (stub)")
    print("7) Exit")


def action_run_qa() -> None:
    print("\n🔍 Running full QA validation...\n")
    run_qa()
    log_event("ghost_cli", "qa_run", "Full QA harness executed")


def action_show_logs() -> None:
    print("\n📜 LAST 20 LOG EVENTS\n")
    if not LOG_PATH.exists():
        print(f"(No log file found at {LOG_PATH.resolve()})")
        log_event("ghost_cli", "logs_missing", str(LOG_PATH))
        return

    lines = LOG_PATH.read_text().splitlines()
    tail = lines[-20:] if len(lines) > 20 else lines
    for line in tail:
        print(line)
    log_event("ghost_cli", "logs_view", f"Shown last {len(tail)} events")


def build_operator_snapshot() -> None:
    """
    Build a simple operator snapshot file summarizing
    the current commander extract, alerts, and daily report.
    """
    parts = []

    parts.append("GLL OPERATOR SNAPSHOT")
    parts.append("======================")
    parts.append(f"Generated: {datetime.utcnow().isoformat()}Z")
    parts.append("")

    # Commander extract (high-level)
    cmd_path = Path("commander_extract.csv")
    if cmd_path.exists():
        parts.append("[COMMANDER EXTRACT]")
        parts.append(f"Source: {cmd_path}")
        try:
            text = cmd_path.read_text().splitlines()
            # show header + up to 5 rows
            preview = text[:6]
            parts.extend(preview)
        except Exception as e:
            parts.append(f"Error reading commander_extract.csv: {e}")
        parts.append("")
    else:
        parts.append("[COMMANDER EXTRACT] missing")
        parts.append("")

    # Critical alerts
    alert_path = Path("critical_alerts.csv")
    if alert_path.exists():
        parts.append("[CRITICAL ALERTS]")
        parts.append(f"Source: {alert_path}")
        try:
            text = alert_path.read_text().splitlines()
            preview = text[:6]
            parts.extend(preview)
        except Exception as e:
            parts.append(f"Error reading critical_alerts.csv: {e}")
        parts.append("")
    else:
        parts.append("[CRITICAL ALERTS] none or file missing")
        parts.append("")

    # Daily report
    rpt_path = Path("daily_report.txt")
    if rpt_path.exists():
        parts.append("[DAILY REPORT]")
        parts.append(f"Source: {rpt_path}")
        try:
            text = rpt_path.read_text().splitlines()
            preview = text[:20]  # first ~20 lines
            parts.extend(preview)
        except Exception as e:
            parts.append(f"Error reading daily_report.txt: {e}")
        parts.append("")
    else:
        parts.append("[DAILY REPORT] missing")
        parts.append("")

    SNAPSHOT_PATH.write_text("\n".join(parts))
    log_event("operator_snapshot", "completed", str(SNAPSHOT_PATH))
    remember("snapshot_built", f"Snapshot at {SNAPSHOT_PATH}")
    print(f"✅ Operator snapshot written to {SNAPSHOT_PATH}")


def run_full_pipeline() -> None:
    print("\n🚀 Running full GLL pipeline...\n")

    # 1) Scoring
    print("▶ fusion_scoring...")
    score_fusion()
    log_event("ghost_cli", "pipeline_step", "fusion_scoring complete")

    # 2) Commander extract
    print("▶ commander_extract...")
    commander_extract()
    log_event("ghost_cli", "pipeline_step", "commander_extract complete")

    # 3) Heatmap prep
    print("▶ heatmap_prep...")
    generate_heatmap_data()
    log_event("ghost_cli", "pipeline_step", "heatmap_prep complete")

    # 4) Alerts
    print("▶ fusion_alerts...")
    fusion_alerts()
    log_event("ghost_cli", "pipeline_step", "fusion_alerts complete")

    # 5) Daily report
    print("▶ daily_report...")
    build_daily_report()
    log_event("ghost_cli", "pipeline_step", "daily_report complete")


def action_pipeline_plus_snapshot() -> None:
    run_full_pipeline()
    print("\n🧾 Building operator snapshot...\n")
    build_operator_snapshot()
    log_event("ghost_cli", "pipeline_snapshot", str(SNAPSHOT_PATH))
    print(f"✅ Full pipeline + snapshot completed.\n📄 Snapshot at: {SNAPSHOT_PATH}")


def action_view_owl_memory() -> None:
    print("\n📘 SPECTRAL OWL MEMORY LOG\n")
    lines = recall_all()
    if not lines:
        print("(No memory entries yet.)")
    else:
        for line in lines:
            print(line.strip())
    log_event("ghost_cli", "owl_memory_view", f"{len(lines)} entries")


def action_run_owl_stub() -> None:
    print("\n🦉 Spectral Owl is booting (stub)...")
    result = analyze_fusion()
    print(result)
    remember("owl_analysis", result)
    log_event("ghost_cli", "owl_stub", "Owl analysis invoked")


def main() -> None:
    while True:
        show_menu()
        choice = input("Select option (1-7): ").strip()

        if choice == "1":
            action_run_qa()
        elif choice == "2":
            action_show_logs()
        elif choice == "3":
            build_operator_snapshot()
        elif choice == "4":
            action_pipeline_plus_snapshot()
        elif choice == "5":
            action_view_owl_memory()
        elif choice == "6":
            action_run_owl_stub()
        elif choice == "7":
            print("Exiting ghost_cli. Stay lethal.")
            log_event("ghost_cli", "exit", "")
            break
        else:
            print("Invalid choice. Please select 1–7.")


if __name__ == "__main__":
    main()

