"""
analyst_notes.py — Ghost Lantern Labs
-------------------------------------

Generates simple, rule-based analyst notes based on:

- data/run_history.csv           (sensor performance and threat hints)
- data/threat_levels.csv         (classified LOW/MEDIUM/HIGH per run)

This is deliberately:
- Offline
- Deterministic
- Easy to explain to a commander

These notes will be pulled into daily_mission_brief.py
to replace the placeholder "analyst notes" section.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any
import csv
from statistics import mean


BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RUN_HISTORY_PATH = DATA_DIR / "run_history.csv"
THREAT_LEVELS_PATH = DATA_DIR / "threat_levels.csv"


def _load_csv(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def _summarize_threat_levels(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(rows)
    if total == 0:
        return {
            "total": 0,
            "high": 0,
            "med": 0,
            "low": 0,
            "latest_level": "UNKNOWN",
        }

    high = sum(1 for r in rows if r.get("threat_level") == "HIGH")
    med = sum(1 for r in rows if r.get("threat_level") == "MEDIUM")
    low = sum(1 for r in rows if r.get("threat_level") == "LOW")
    latest = rows[-1].get("threat_level", "UNKNOWN") or "UNKNOWN"

    return {
        "total": total,
        "high": high,
        "med": med,
        "low": low,
        "latest_level": latest,
    }


def _summarize_hints(history: List[Dict[str, Any]]) -> Dict[str, float]:
    if not history:
        return {
            "avg_max_threat": 0.0,
            "avg_avg_threat": 0.0,
        }

    max_vals = []
    avg_vals = []

    for r in history:
        try:
            max_t = float(r.get("max_threat_hint", 0.0))
            avg_t = float(r.get("avg_threat_hint", 0.0))
        except ValueError:
            max_t = 0.0
            avg_t = 0.0

        max_vals.append(max_t)
        avg_vals.append(avg_t)

    return {
        "avg_max_threat": round(mean(max_vals), 3),
        "avg_avg_threat": round(mean(avg_vals), 3),
    }


def build_notes() -> str:
    """
    Build a short, rule-based analyst note section using
    run history and threat level trends.
    """
    run_history = _load_csv(RUN_HISTORY_PATH)
    threat_rows = _load_csv(THREAT_LEVELS_PATH)

    threat_summary = _summarize_threat_levels(threat_rows)
    hint_summary = _summarize_hints(run_history)

    lines: List[str] = []

    # 1) Threat trend commentary
    if threat_summary["total"] == 0:
        lines.append("• No threat trend data available yet. Run sensor_run_history.py and threat_level_classifier.py.")
        return "\n".join(lines)

    high = threat_summary["high"]
    med = threat_summary["med"]
    low = threat_summary["low"]
    latest = threat_summary["latest_level"]
    avg_max = hint_summary["avg_max_threat"]
    avg_avg = hint_summary["avg_avg_threat"]

    # Basic trend description
    lines.append("• Threat trend summary:")
    if high > 0:
        lines.append(f"  - System has observed {high} HIGH-level runs, indicating recurring elevated conditions.")
    elif med > 0:
        lines.append(f"  - System has observed {med} MEDIUM-level runs, with no HIGH events logged yet.")
    else:
        lines.append("  - All logged runs are LOW-level; environment appears calm so far.")

    lines.append(f"  - Latest classified threat level: {latest}.")
    lines.append(f"  - Average max threat hint across runs: {avg_max:.3f}.")
    lines.append(f"  - Average baseline (avg threat hint): {avg_avg:.3f}.")

    # 2) Simple risk posture recommendation
    if latest == "HIGH":
        lines.append("• Recommended posture: ELEVATED. Maintain close monitoring and be prepared to brief anomalies quickly.")
    elif latest == "MEDIUM":
        lines.append("• Recommended posture: WATCHFUL. Maintain routine monitoring with periodic review of HIGH-candidate events.")
    else:
        lines.append("• Recommended posture: ROUTINE. No immediate indicators of critical instability, but continue normal surveillance.")

    # 3) Data quality hints
    if run_history:
        total_runs = len(run_history)
        fallback_unknown = sum(
            1 for r in run_history if (r.get("fallback_reason") or "").lower() not in ("", "none", "normal")
        )
        if fallback_unknown > 0:
            lines.append(
                f"• Data note: {fallback_unknown} of {total_runs} runs reported a non-trivial fallback_reason; "
                "review those cases for sensor gaps or configuration issues."
            )
        else:
            lines.append(
                f"• Data note: All {total_runs} runs report normal fallback status; no obvious sensor-layer gaps detected."
            )

    return "\n".join(lines)


if __name__ == "__main__":
    print(build_notes())

