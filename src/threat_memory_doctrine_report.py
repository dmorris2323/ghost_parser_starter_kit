"""
threat_memory_doctrine_report.py — Ghost Lantern Labs
-----------------------------------------------------
Reads data/threat_memory_doctrine.csv and produces:

  docs/threat_memory_doctrine_report.txt

Summarizes:
  - counts by doctrine_tag
  - counts by doctrine_tag + severity
"""

from pathlib import Path
import csv
from collections import Counter

INPUT = Path("data/threat_memory_doctrine.csv")
OUTPUT = Path("docs/threat_memory_doctrine_report.txt")


def main():
    if not INPUT.exists():
        print(f"[WARN] No {INPUT} found. Run threat_doctrine_tagger.py first.")
        return

    by_tag = Counter()
    by_tag_sev = Counter()

    with INPUT.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tag = row.get("doctrine_tag", "UNKNOWN")
            sev = (row.get("severity") or "UNKNOWN").upper()
            by_tag[tag] += 1
            by_tag_sev[(tag, sev)] += 1

    lines = []
    lines.append("GLL Threat Memory Doctrine Report")
    lines.append("================================")
    lines.append("")
    lines.append("By Doctrine Tag:")
    for tag, count in sorted(by_tag.items(), key=lambda x: x[0]):
        lines.append(f"  - {tag}: {count}")
    lines.append("")
    lines.append("By Doctrine Tag + Severity:")
    for (tag, sev), count in sorted(by_tag_sev.items(), key=lambda x: (x[0][0], x[0][1])):
        lines.append(f"  - {tag} / {sev}: {count}")

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] Wrote doctrine report → {OUTPUT}")


if __name__ == "__main__":
    main()

