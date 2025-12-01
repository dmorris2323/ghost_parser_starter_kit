"""
family_law_scoring.py — GLL
---------------------------
Scores family law cases for urgency / risk.
"""

import csv
from pathlib import Path

INPUT = Path("data/family_law_fused.csv")
OUTPUT = Path("data/family_law_scored.csv")


def compute_score(row: dict) -> float:
    days = int(row["days_until_hearing"])
    dv = int(row["domestic_violence_flag"])
    prior = int(row["prior_contempts"])
    risk = float(row["child_risk_score"])
    behind = int(row["payment_behind"])

    score = 0.0
    score += (1.0 - min(days / 30.0, 1.0)) * 0.4  # closer hearings → higher urgency
    score += risk * 0.3
    score += dv * 0.2
    score += min(prior, 3) * 0.05
    score += behind * 0.05

    return round(score, 3)


def classify_severity(score: float) -> str:
    if score >= 0.8:
        return "HIGH"
    if score >= 0.5:
        return "MODERATE"
    return "LOW"


def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing {INPUT}, run legal_ingest_family_law.py first.")

    with INPUT.open("r", encoding="utf-8") as f_in, OUTPUT.open(
        "w", encoding="utf-8", newline=""
    ) as f_out:
        reader = csv.DictReader(f_in)
        fieldnames = reader.fieldnames + ["gll_score", "gll_severity"]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            score = compute_score(row)
            sev = classify_severity(score)
            row["gll_score"] = score
            row["gll_severity"] = sev
            writer.writerow(row)

    print(f"[OK] Wrote scored family-law data → {OUTPUT}")


if __name__ == "__main__":
    main()

