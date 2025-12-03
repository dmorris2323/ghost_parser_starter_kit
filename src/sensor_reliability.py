"""
sensor_reliability.py
Predicts reliability of each sensor and exports a simple report.
"""

from pathlib import Path
from datetime import datetime
import random

SENSORS = ["optical", "seismic", "ems", "radiation"]

def calculate_reliability(sensor: str) -> dict:
    # Placeholder logic until live metrics are wired:
    # Random values represent uptime/drift/missing-data penalties.
    base = random.uniform(0.7, 0.98)
    drift = random.uniform(-0.05, 0.03)
    health = random.uniform(-0.05, 0.05)
    score = max(0.0, min(1.0, base + drift + health))  # clamp

    return {
        "sensor": sensor,
        "score": round(score * 100, 2),
        "status": "OK" if score > 0.75 else "WARN" if score > 0.55 else "CRITICAL"
    }

def build_reliability_table() -> list:
    out = []
    for s in SENSORS:
        out.append(calculate_reliability(s))
    return out

def ascii_bar(score: float) -> str:
    blocks = int(score // 5)
    return "[" + ("█" * blocks) + ("░" * (20 - blocks)) + f"] {score:.1f}%"

def export_reliability_report():
    results = build_reliability_table()

    lines = []
    lines.append("=== SENSOR RELIABILITY REPORT ===")
    lines.append(f"Generated: {datetime.utcnow().isoformat()}Z")
    lines.append("")

    for r in results:
        lines.append(f"{r['sensor'].upper():10} {ascii_bar(r['score'])}")

    out = Path(__file__).parent / "docs" / "reliability_report.txt"
    out.write_text("\n".join(lines), encoding="utf-8")
    return f"[OK] Reliability exported → {out}"

if __name__ == "__main__":
    print(export_reliability_report())

