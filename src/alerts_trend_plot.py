"""
alerts_trend_plot.py — GLL
--------------------------
Creates a simple trend plot of critical alerts over time
based on critical_alerts.csv.
"""

from pathlib import Path
import csv

import matplotlib.pyplot as plt

INPUT = Path("critical_alerts.csv")
OUTPUT = Path("alerts_trend.png")


def main():
    if not INPUT.exists():
        print("[WARN] No critical_alerts.csv found.")
        return

    rows = []
    with INPUT.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    if not rows:
        print("[WARN] No rows in critical_alerts.csv.")
        return

    # Simple index-based growth line
    y = list(range(1, len(rows) + 1))

    plt.figure(figsize=(8, 4))
    plt.plot(y)
    plt.title("GLL Critical Alert Count (Sequential)")
    plt.xlabel("Alert Index")
    plt.ylabel("Alert Count Growth")
    plt.tight_layout()
    plt.savefig(OUTPUT, dpi=200)
    plt.close()
    print(f"[OK] Wrote alerts trend plot → {OUTPUT}")


if __name__ == "__main__":
    main()

