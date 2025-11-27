"""
bad_data_summary.py — Day 53
Summarize bad_data_quarantine.csv so operators (and Spectral Owl)
can quickly understand the shape of bad/attack-flavored data.
"""

from pathlib import Path
from collections import Counter

import csv

from fusion_logger import log_event

QUARANTINE_PATH = Path("bad_data_quarantine.csv")


def summarize_quarantine(path: Path = QUARANTINE_PATH) -> str:
    if not path.exists():
        msg = f"{path} not found. No bad data recorded yet."
        log_event("bad_data_summary", "no_file", msg)
        return msg

    severities = Counter()
    reasons = Counter()
    total_rows = 0
    total_count = 0

    with path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_rows += 1
            try:
                c = int(row.get("count", 1))
            except ValueError:
                c = 1

            total_count += c
            severities[row.get("severity", "unknown")] += c
            reasons[row.get("reason", "unknown")] += c

    lines = []
    lines.append(f"Bad-data quarantine summary for {path.name}:")
    lines.append(f"- Rows: {total_rows}")
    lines.append(f"- Total events quarantined (count sum): {total_count}")
    lines.append("")
    lines.append("By severity:")
    for sev, c in severities.most_common():
        lines.append(f"  - {sev}: {c}")
    lines.append("")
    lines.append("Top reasons:")
    for reason, c in reasons.most_common():
        lines.append(f"  - {reason}: {c}")

    summary = "\n".join(lines)
    log_event("bad_data_summary", "summary_built", f"rows={total_rows}, total={total_count}")
    return summary


if __name__ == "__main__":
    print(summarize_quarantine())

