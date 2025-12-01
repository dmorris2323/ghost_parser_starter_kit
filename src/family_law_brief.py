"""
family_law_brief.py — GLL
-------------------------
Produces a simple human-readable brief for family law cases
based on family_law_scored.csv.
"""

import csv
from pathlib import Path

INPUT = Path("data/family_law_scored.csv")
OUTPUT = Path("family_law_brief.txt")


def load_cases():
    cases = []
    with INPUT.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["gll_score"] = float(row["gll_score"])
            cases.append(row)
    return cases


def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing {INPUT}, run family_law_scoring.py first.")

    cases = load_cases()
    cases.sort(key=lambda r: r["gll_score"], reverse=True)

    lines = []
    lines.append("GLL Family Law Prioritization Brief")
    lines.append("===================================")
    lines.append("")
    lines.append(f"Total cases: {len(cases)}")
    lines.append("")
    lines.append("Top urgent cases:")
    lines.append("")

    for row in cases[:3]:
        lines.append(
            f"- {row['case_id']} | {row['client_name']} | {row['case_type']} | "
            f"Score={row['gll_score']} | Severity={row['gll_severity']} | "
            f"Days until hearing={row['days_until_hearing']}"
        )

    lines.append("")
    lines.append("Recommendation: Address HIGH severity and near-term hearings first.")

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] Wrote brief → {OUTPUT}")


if __name__ == "__main__":
    main()

