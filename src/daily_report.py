from datetime import datetime
from pathlib import Path
import pandas as pd

from fusion_logger import log_event, LOG_FILE
from settings import COMMANDER_FILE, DAILY_REPORT_FILE


def build_daily_report(
    commander_file: Path | str = COMMANDER_FILE,
    log_file: Path | str = LOG_FILE,
    out_file: Path | str = DAILY_REPORT_FILE,
    day_label: str = "Day 40"
):
    lines = []
    ts = datetime.utcnow().isoformat()

    lines.append(f"=== GLL DAILY REPORT — {day_label} ===")
    lines.append(f"Generated (UTC): {ts}")
    lines.append("")

    # 1) Commander Extract summary
    c_path = Path(commander_file)
    if c_path.exists():
        try:
            df_cmd = pd.read_csv(c_path)
            lines.append(">> Commander Extract Summary")
            lines.append(f"Total events summarized: {len(df_cmd)}")

            # Top line threat (if exists)
            if len(df_cmd) > 0:
                top = df_cmd.iloc[0]
                lines.append(
                    f"Top Event: id={top.get('id','NA')} "
                    f"| Score={top.get('Score','NA')} "
                    f"| Confidence={top.get('Confidence_Level','NA')}"
                )
                lines.append(f"Description: {top.get('Description','NA')}")
            else:
                lines.append("No events in commander_extract.csv.")
            lines.append("")
        except Exception as e:
            lines.append(f"[ERROR] Could not read commander extract: {e}")
    else:
        lines.append(">> Commander Extract Summary")
        lines.append("File not found — no commander_extract.csv present.")
        lines.append("")

    # 2) System health from fusion_ops_log.csv
    l_path = Path(log_file)
    if l_path.exists():
        try:
            df_log = pd.read_csv(l_path)
            lines.append(">> System Health Summary")
            # Count errors vs total
            total_rows = len(df_log)
            error_rows = df_log[df_log["status"].str.lower() == "error"]
            lines.append(f"Total log entries: {total_rows}")
            lines.append(f"Errors recorded: {len(error_rows)}")

            # Last 3 events
            lines.append("Recent activity (last 3 entries):")
            for _, row in df_log.tail(3).iterrows():
                lines.append(
                    f"  [{row.get('timestamp','NA')}] "
                    f"{row.get('module','NA')} | {row.get('status','NA')} "
                    f"| {row.get('note','')}"
                )
            lines.append("")
        except Exception as e:
            lines.append(f"[ERROR] Could not read ops log: {e}")
    else:
        lines.append(">> System Health Summary")
        lines.append("No fusion_ops_log.csv found — logger may not have run yet.")
        lines.append("")

    # 3) Wrap up
    lines.append(">> Analyst Notes (fill in manually):")
    lines.append("- [ ] Key threat takeaway:")
    lines.append("- [ ] System issues to address next run:")
    lines.append("- [ ] Items to brief to leadership / instructor:")
    lines.append("")
    lines.append("=== END OF REPORT ===")

    with open(out_file, "w") as f:
        f.write("\n".join(lines))

    print(f"✅ Daily report written to {out_file}")
    try:
        log_event("daily_report", "completed", f"Output -> {out_file}")
    except Exception:
        pass

    return out_file


if __name__ == "__main__":
    build_daily_report()

