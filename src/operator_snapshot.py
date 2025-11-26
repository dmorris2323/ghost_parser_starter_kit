"""
operator_snapshot.py — Day 51
Generates the operator_snapshot.txt file.
"""

from datetime import datetime
from pathlib import Path
import pandas as pd
from fusion_logger import log_event

def build_operator_snapshot(out_path: str = "operator_snapshot.txt") -> None:
    """
    Collects key GLL outputs into a single operator snapshot file.
    """

    snapshot = []

    # Timestamp
    snapshot.append(f"OPERATOR SNAPSHOT — {datetime.utcnow().isoformat()}\n")
    snapshot.append("==============================================\n\n")

    # scored_output.csv
    scored = Path("scored_output.csv")
    if scored.exists():
        df = pd.read_csv(scored)
        snapshot.append(f"[scored_output.csv] {len(df)} rows\n")
    else:
        snapshot.append("[scored_output.csv] MISSING\n")

    # commander_extract.csv
    cmd = Path("commander_extract.csv")
    if cmd.exists():
        df = pd.read_csv(cmd)
        snapshot.append(f"[commander_extract.csv] {len(df)} events\n")
    else:
        snapshot.append("[commander_extract.csv] MISSING\n")

    # critical_alerts.csv
    crit = Path("critical_alerts.csv")
    if crit.exists():
        df = pd.read_csv(crit)
        snapshot.append(f"[critical_alerts.csv] {len(df)} critical alerts\n")
    else:
        snapshot.append("[critical_alerts.csv] MISSING\n")

    # daily_report.txt
    report = Path("daily_report.txt")
    if report.exists():
        text = report.read_text().strip()
        snapshot.append("\n--- DAILY REPORT ---\n")
        snapshot.append(text + "\n\n")
    else:
        snapshot.append("\n--- DAILY REPORT ---\nMISSING\n")

    # Write snapshot file
    with open(out_path, "w") as f:
        f.writelines(snapshot)

    log_event("operator_snapshot", "completed", out_path)
    print(f"✅ Operator snapshot written to {out_path}")

