"""
threat_doctrine_tagger.py — Ghost Lantern Labs
----------------------------------------------
Reads data/threat_memory.csv and writes:
  data/threat_memory_doctrine.csv

Adds a doctrine_tag field based on:
  - severity
  - source
  - note

Also sanitizes any weird extra columns (like None keys) so the CSV
writer doesn't fail.
"""

from pathlib import Path
import csv

INPUT = Path("data/threat_memory.csv")
OUTPUT = Path("data/threat_memory_doctrine.csv")


def classify_doctrine(row: dict) -> str:
    severity = (row.get("severity") or "").upper()
    source = (row.get("source") or "").lower()
    note = (row.get("note") or "").lower()

    # SSF / jamming / DoS / data denial style
    if "dos" in source or "jam" in source or "flood" in note:
        return "multi_sensor_resilience"

    # Bad data, corruption, quarantine
    if "bad data" in note or "corrupt" in note or "quarantine" in note:
        return "data_validation_and_sanity"

    # High severity = decision risk
    if severity == "HIGH":
        return "timeliness_and_decision_risk"

    # Moderate = monitored risk
    if severity == "MODERATE":
        return "risk_monitoring"

    # Everything else
    return "general_threat_awareness"


def main():
    if not INPUT.exists():
        print(f"[WARN] No {INPUT} found — nothing to tag.")
        return

    with INPUT.open("r", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)

        # Clean up fieldnames (remove None, duplicates)
        base_fieldnames = [fn for fn in (reader.fieldnames or []) if fn is not None]
        fieldnames = list(dict.fromkeys(base_fieldnames + ["doctrine_tag"]))

        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        with OUTPUT.open("w", encoding="utf-8", newline="") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()

            count = 0
            for row in reader:
                # Drop any keys not in fieldnames (especially None)
                clean_row = {k: v for k, v in row.items() if k in fieldnames and k is not None}

                tag = classify_doctrine(clean_row)
                clean_row["doctrine_tag"] = tag

                writer.writerow(clean_row)
                count += 1

    print(f"[OK] Wrote {count} rows → {OUTPUT}")


if __name__ == "__main__":
    main()

