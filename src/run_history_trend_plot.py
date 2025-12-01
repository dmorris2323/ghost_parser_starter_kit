"""
run_history_trend_plot.py — Ghost Lantern Labs
----------------------------------------------
Reads data/run_history.csv and plots:
  - QA pass rate over time
  - QA failure count over time (simple line)

Outputs:
  run_history_trend.png
"""

from pathlib import Path
import csv

import matplotlib.pyplot as plt

RUN_HISTORY = Path("data/run_history.csv")
OUTPUT = Path("run_history_trend.png")


def load_history():
    if not RUN_HISTORY.exists():
        print("[WARN] No run_history.csv found.")
        return []

    rows = []
    with RUN_HISTORY.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def main():
    rows = load_history()
    if not rows:
        print("[WARN] No rows to plot.")
        return

    x = list(range(1, len(rows) + 1))
    pass_rates = []
    fails = []

    for row in rows:
        try:
            total = int(row.get("qa_total_tests") or 0)
            passed = int(row.get("qa_passed") or 0)
            failed = int(row.get("qa_failed") or 0)
        except ValueError:
            total = passed = failed = 0

        if total > 0:
            pass_rate = passed / total
        else:
            pass_rate = 0.0
        pass_rates.append(pass_rate)
        fails.append(failed)

    plt.figure(figsize=(8, 4))
    plt.plot(x, pass_rates, marker="o")
    plt.title("GLL QA Pass Rate Over Time")
    plt.xlabel("Run Index")
    plt.ylabel("Pass Rate (0–1)")
    plt.tight_layout()
    plt.savefig("run_history_pass_rate.png", dpi=200)
    plt.close()

    plt.figure(figsize=(8, 4))
    plt.plot(x, fails, marker="o")
    plt.title("GLL QA Failure Count Over Time")
    plt.xlabel("Run Index")
    plt.ylabel("Failures")
    plt.tight_layout()
    plt.savefig(OUTPUT, dpi=200)
    plt.close()

    print("[OK] Wrote run_history_pass_rate.png and run_history_trend.png")


if __name__ == "__main__":
    main()

