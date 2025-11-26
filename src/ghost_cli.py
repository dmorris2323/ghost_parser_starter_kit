"""
ghost_cli.py — GLL Operator Console

Menu:
 1) Run full QA validation
 2) Show last 20 log events
 3) Build operator snapshot
 4) Run full pipeline + snapshot
 5) View Spectral Owl memory
 6) Run Spectral Owl (stub)
 7) Run pipeline health check
 8) Mission briefing
 9) Exit
10) Anti-DoS environment scan
"""

import os
from pathlib import Path

from fusion_logger import log_event
from qa_validator import run_all as run_qa
from fusion_scoring import score_fusion
from commander_extract import commander_extract
from heatmap_prep import generate_heatmap_data
from fusion_alerts import fusion_alerts
from daily_report import build_daily_report
from operator_snapshot import build_operator_snapshot
from pipeline_health import pipeline_health
from spectral_owl.owl_memory import recall_all
from spectral_owl.owl_brain import think, analyze_fusion


# ---------------------------
# Simple CLI color theming
# ---------------------------

THEME = os.getenv("GLL_CLI_THEME", "none").lower()

COLOR_CODES = {
    "none": "",
    "blue": "\033[94m",
    "red": "\033[91m",
    "yellow": "\033[93m",
    "reset": "\033[0m",
}


def themed(text: str) -> str:
    """Apply a simple color theme to headings based on GLL_CLI_THEME."""
    code = COLOR_CODES.get(THEME, "")
    reset = COLOR_CODES["reset"] if code else ""
    return f"{code}{text}{reset}"


# ---------------------------
# Menu rendering
# ---------------------------

def show_menu() -> None:
    print()
    print(themed("GLL OPERATOR CONSOLE — ghost_cli"))
    print(themed("================================"))
    print("1) Run full QA validation")
    print("2) Show last 20 log events")
    print("3) Build operator snapshot")
    print("4) Run full pipeline + snapshot")
    print("5) View Spectral Owl memory")
    print("6) Run Spectral Owl (stub)")
    print("7) Run pipeline health check")
    print("8) Mission briefing")
    print("9) Exit")
    print("10) Anti-DoS environment scan")


# ---------------------------
# Actions
# ---------------------------

def action_run_qa() -> None:
    print("\n🔍 Running full QA validation...\n")
    run_qa()
    log_event("ghost_cli", "qa_run", "Full QA validation executed")


def action_show_logs() -> None:
    log_path = Path("fusion_ops_log.csv")
    if not log_path.exists():
        print("\n(No fusion_ops_log.csv found yet.)\n")
        log_event("ghost_cli", "logs_view", "no_log_file")
        return

    print("\n📜 LAST 20 LOG EVENTS\n")
    lines = log_path.read_text().splitlines()
    for line in lines[-20:]:
        print(line)
    log_event("ghost_cli", "logs_view", "last_20_shown")


def action_build_snapshot() -> None:
    print("\n🧾 Building operator snapshot...\n")
    out_path = build_operator_snapshot()
    print(f"✅ Operator snapshot written to {out_path}")
    log_event("ghost_cli", "snapshot", str(out_path))


def action_pipeline_plus_snapshot() -> None:
    print("\n🚀 Running full GLL pipeline...\n")

    # fusion_scoring
    print("▶ fusion_scoring...")
    score_fusion()
    log_event("ghost_cli", "pipeline_step", "fusion_scoring complete")

    # commander_extract
    print("▶ commander_extract...")
    commander_extract()
    log_event("ghost_cli", "pipeline_step", "commander_extract complete")

    # heatmap_prep
    print("▶ heatmap_prep...")
    generate_heatmap_data()
    log_event("ghost_cli", "pipeline_step", "heatmap_prep complete")

    # fusion_alerts
    print("▶ fusion_alerts...")
    fusion_alerts()
    log_event("ghost_cli", "pipeline_step", "fusion_alerts complete")

    # daily_report
    print("▶ daily_report...")
    build_daily_report()
    log_event("ghost_cli", "pipeline_step", "daily_report complete")

    print("\n🧾 Building operator snapshot...\n")
    out_path = build_operator_snapshot()
    log_event("operator_snapshot", "completed", str(out_path))
    print(f"✅ Operator snapshot written to {out_path}")
    log_event("ghost_cli", "pipeline_snapshot", str(out_path))

    print("✅ Full pipeline + snapshot completed.")
    print(f"📄 Snapshot at: {out_path}")


def action_view_owl_memory() -> None:
    print("\n📘 SPECTRAL OWL MEMORY LOG\n")
    lines = recall_all()
    if not lines:
        print("(No owl_memory.txt entries yet.)")
        log_event("ghost_cli", "owl_memory_view", "empty")
        return

    for line in lines:
        print(line.strip())
    log_event("ghost_cli", "owl_memory_view", f"{len(lines)} lines")


def action_run_owl_stub() -> None:
    print("\n🦉 Spectral Owl is booting (stub)...\n")
    msg = think("system check")
    print(msg)
    log_event("ghost_cli", "owl_stub", "think(system check)")


def action_pipeline_health() -> None:
    print("\n🔧 PIPELINE HEALTH CHECK\n")
    report = pipeline_health()
    print(report)
    log_event("ghost_cli", "pipeline_health", "run")


def build_mission_brief() -> str:
    """
    Build a short mission briefing:
      - pipeline health summary
      - Spectral Owl assessment
      - daily report status
    """
    health = pipeline_health()
    owl_assessment = analyze_fusion()

    daily_path = Path("daily_report.txt")
    if daily_path.exists():
        daily_status = "Daily report present."
    else:
        daily_status = "No daily_report.txt found yet."

    brief = (
        "🎯 GLL MISSION BRIEFING\n\n"
        "1) Pipeline Health:\n"
        f"{health}\n\n"
        "2) Spectral Owl Assessment:\n"
        f"{owl_assessment}\n\n"
        "3) Daily Report Status:\n"
        f"{daily_status}\n"
    )
    return brief


def action_mission_brief() -> None:
    print()
    print(build_mission_brief())
    log_event("ghost_cli", "mission_brief", "run")


def action_anti_dos_scan() -> None:
    """
    Uses the Spectral Owl's fusion analysis as an Anti-DoS environment scan stub.
    Later, this can be extended to look at quarantine volume, ingest rate, etc.
    """
    print("\n🛡 ANTI-DOS SYSTEM SCAN\n")
    result = analyze_fusion()
    print(result)
    log_event("ghost_cli", "anti_dos_scan", "run")


# ---------------------------
# Main loop
# ---------------------------

def main() -> None:
    while True:
        show_menu()
        choice = input("Select option (1-10): ").strip()

        if choice == "1":
            action_run_qa()
        elif choice == "2":
            action_show_logs()
        elif choice == "3":
            action_build_snapshot()
        elif choice == "4":
            action_pipeline_plus_snapshot()
        elif choice == "5":
            action_view_owl_memory()
        elif choice == "6":
            action_run_owl_stub()
        elif choice == "7":
            action_pipeline_health()
        elif choice == "8":
            action_mission_brief()
        elif choice == "9":
            print("Exiting ghost_cli. Stay lethal.")
            log_event("ghost_cli", "exit", "")
            break
        elif choice == "10":
            action_anti_dos_scan()
        else:
            print("Invalid choice. Please select 1–10.")


if __name__ == "__main__":
    main()

