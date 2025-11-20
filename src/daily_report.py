from datetime import datetime
from pathlib import Path
import csv

import pandas as pd

from fusion_logger import log_event
from settings import COMMANDER_FILE, OPS_LOG_FILE, DAILY_REPORT_FILE
from validators import validate_row_integrity
from error_handler import safe_run


def build_daily_report(
    day_label: str = "Day 45",
    commander_file: Path | str = COMMANDER_FILE,
    log_file: Path | str = OPS_LOG_FILE,
    out_file: Path | str = DAILY_REPORT_FILE,
):
    """
    Build a simple text-based daily report using:
      - commander_extract.csv
      - fusion_ops_log.csv

    Output:
      - daily_report.txt
    """

    commander_path = Path(commander_file)
    log_path = Path(log_file)
    out_path = Path(out_file)

    # 1) Check commander file exists
    if not commander_path.exists():
        msg = f"Commander file not found: {commander_path.resolve()}"
        print(f"❌ {msg}")
        log_event("daily_report", "error", msg)
        return None

    # 2) Load commander summary
    df_cmd = pd.read_csv(commander_path)

    # 3) Validate commander data integrity
    if not validate_row_integrity(df_cmd, "daily_report"):
        return None

    # --- Commander summary ---
    total_events = len(df_cmd)
    if "Confidence_Level" in df_cmd.columns:
        crit_mask = df_cmd["Confidence_Level"].astype(str).str.lower() == "critical"
        num_critical = crit_mask.sum()
    else:
        num_critical = 0

    # Top 3 lines as mini-brief
    top_brief_lines = []
    for _, row in df_cmd.head(3).iterrows():
        desc = row.get("Description", "No description")
        score = row.get("Score", "NA")
        conf = row.get("Confidence_Level", "NA")
        top_brief_lines.append(f"- [{conf}] Score {score}: {desc}")

    # --- Ops log summary ---
    recent_errors = 0
    recent_missing = 0
    last_entries = []

    if log_path.exists():
        with open(log_path, newline="") as f:
            reader = list(csv.DictReader(f))
            tail = reader[-10:]
            for entry in tail:
                last_entries.append(
                    f"{entry['timestamp']} | {entry['module']} | {entry['status']} | {entry['note']}"
                )
                status = entry.get("status", "").lower()
                if status == "error":
                    recent_errors += 1
                if status == "missing_file":
                    recent_missing += 1

    # --- Build report text ---
    now_str = datetime.utcnow().isoformat()

    lines = []
    lines.append("========================================")
    lines.append(f"GLL DAILY REPORT — {day_label}")
    lines.append(f"Generated (UTC): {now_str}")
    lines.append("========================================")
    lines.append("")
    lines.append("Commander Extract Summary")
    lines.append(f"- Total events: {total_events}")
    lines.append(f"- Critical events: {num_critical}")
    lines.append("")
    lines.append("Top Events:")
    lines.extend(top_brief_lines or ["- No events available"])
    lines.append("")
    lines.append("Ops Log Summary")
    lines.append(f"- Recent errors: {recent_errors}")
    lines.append(f"- Recent missing files: {recent_missing}")
    lines.append("")
    lines.append("Last 10 Log Entries:")
    if last_entries:
        lines.extend(last_entries)
    else:
        lines.append("- No log entries found.")
    lines.append("")
    lines.append("End of Report")
    lines.append("========================================")
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"🧾 Daily report written to {out_path.name}")
    log_event("daily_report", "completed", f"Report -> {out_path.name}")

    return out_path


if __name__ == "__main__":
    safe_run("daily_report", build_daily_report)

