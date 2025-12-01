"""
threat_memory_stats.py — GLL
----------------------------
Summarizes threat_memory.csv into counts by severity and profile.
"""

import csv
from pathlib import Path

INPUT = Path("data/threat_memory.csv")
OUTPUT = Path("threat_memory_stats.txt")


def main():
    if not INPUT.exists():
        print("[WARN] No threat_memory.csv found.")
        return

    counts_by_sev = {}
    counts_by_profile = {}

    with INPUT.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sev = row.get("severity", "UNKNOWN")
            profile = row.get("profile", "UNKNOWN")
            counts_by_sev[sev] = counts_by_sev.get(sev, 0) + 1
            counts_by_profile[profile] = counts_by_profile.get(profile, 0) + 1

    lines = []
    lines.append("GLL Threat Memory Stats")
    lines.append("=======================")
    lines.append("")
    lines.append("By Severity:")
    for k, v in sorted(counts_by_sev.items(), key=lambda x: x[0]):
        lines.append(f"  - {k}: {v}")
    lines.append("")
    lines.append("By Profile:")
    for k, v in sorted(counts_by_profile.items(), key=lambda x: x[0]):
        lines.append(f"  - {k}: {v}")

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] Wrote threat stats → {OUTPUT}")


if __name__ == "__main__":
    main()

