"""
bad_data_quarantine.py — Day 52
Quarantine suspicious or impossible telemetry rows so they can be
analyzed later (spoofing, jamming, deception, flood signatures).
"""

from datetime import datetime
from pathlib import Path
import csv

from fusion_logger import log_event

QUARANTINE_FILE = Path("quarantine_bad_rows.csv")


def quarantine_rows(df, reason: str, module_name: str = "fusion_sanitizer") -> None:
    """
    Append suspicious rows to quarantine_bad_rows.csv with minimal context.
    df: pandas DataFrame slice (rows to quarantine)
    reason: short reason string
    module_name: module raising the quarantine
    """
    if df is None or df.empty:
        return

    exists = QUARANTINE_FILE.exists()
    with QUARANTINE_FILE.open("a", newline="") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["timestamp", "module", "reason", "index", "row_dict"])

        ts = datetime.utcnow().isoformat()
        for idx, row in df.iterrows():
            writer.writerow([ts, module_name, reason, idx, row.to_dict()])

    log_event(
        module_name,
        "quarantine",
        f"{len(df)} rows quarantined ({reason}) -> {QUARANTINE_FILE.name}",
    )

