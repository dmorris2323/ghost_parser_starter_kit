"""
legal_ingest_family_law.py — GLL
--------------------------------
Ingests family_law_cases_sample.csv and produces a normalized
family_law_fused.csv for scoring & briefing.
"""

import csv
from pathlib import Path

SOURCE = Path("data/family_law_cases_sample.csv")
OUTPUT = Path("data/family_law_fused.csv")


def normalize_row(row: dict) -> dict:
    days = int(row["days_until_hearing"])
    dv_flag = int(row["domestic_violence_flag"])
    prior = int(row["prior_contempts"])
    risk = float(row["child_risk_score"])
    behind = 1 if row["payment_status"].strip().lower() == "behind" else 0

    return {
        "case_id": row["case_id"],
        "client_name": row["client_name"],
        "case_type": row["case_type"],
        "days_until_hearing": days,
        "domestic_violence_flag": dv_flag,
        "prior_contempts": prior,
        "child_risk_score": risk,
        "payment_behind": behind,
    }


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Missing {SOURCE}")

    with SOURCE.open("r", encoding="utf-8") as f_in, OUTPUT.open(
        "w", encoding="utf-8", newline=""
    ) as f_out:
        reader = csv.DictReader(f_in)
        fieldnames = [
            "case_id",
            "client_name",
            "case_type",
            "days_until_hearing",
            "domestic_violence_flag",
            "prior_contempts",
            "child_risk_score",
            "payment_behind",
        ]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            clean = normalize_row(row)
            writer.writerow(clean)

    print(f"[OK] Wrote normalized family-law data → {OUTPUT}")


if __name__ == "__main__":
    main()

