"""
baseline_drift_check.py — GLL
-----------------------------
Checks if the average 'score' in scored_output.csv has drifted
significantly from a stored baseline.
"""

import csv
from pathlib import Path
import json
from statistics import mean

INPUT = Path("scored_output.csv")
BASELINE = Path("baseline_stats.json")
OUTPUT = Path("baseline_drift_report.txt")


def compute_mean_score() -> float:
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing {INPUT}")
    scores = []
    with INPUT.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if "score" in row:
                try:
                    scores.append(float(row["score"]))
                except ValueError:
                    continue
    if not scores:
        return 0.0
    return mean(scores)


def main():
    current_mean = compute_mean_score()

    if not BASELINE.exists():
        data = {"mean_score": current_mean}
        BASELINE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        OUTPUT.write_text(
            f"Baseline created with mean_score={current_mean:.3f}\n",
            encoding="utf-8",
        )
        print(f"[OK] Baseline created → {BASELINE}")
        return

    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    base_mean = baseline.get("mean_score", current_mean)
    diff = current_mean - base_mean

    lines = []
    lines.append("GLL Baseline Drift Report")
    lines.append("=========================")
    lines.append(f"Baseline mean score: {base_mean:.3f}")
    lines.append(f"Current mean score:  {current_mean:.3f}")
    lines.append(f"Difference:          {diff:.3f}")
    lines.append("")
    if abs(diff) > 0.2:
        lines.append("Status: DRIFT DETECTED (greater than 0.2)")
    else:
        lines.append("Status: within acceptable range.")

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] Wrote drift report → {OUTPUT}")


if __name__ == "__main__":
    main()

