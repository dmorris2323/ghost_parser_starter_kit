"""
spectral_owl.owl_brain
----------------------

Core offline brain for Spectral Owl.

Responsibilities:
 - Analyze fused scores in data/scored_output.csv
 - Decide if the situation is stable or critical
 - Log threat memory events
 - Provide a compact threat_snapshot() for mission briefings
"""

from __future__ import annotations

from pathlib import Path
import csv
from typing import Dict, List

from spectral_owl.threat_memory import append_event, load_events, count_by_type


FUSION_PATH = Path("data/scored_output.csv")


def analyze_fusion(path: Path | str = FUSION_PATH, critical_threshold: float = 0.8) -> Dict:
    """
    Read scored_output.csv, look at 'score' column, and classify the situation.

    Returns a dict like:
      {
        "status": "no_data" | "bad_schema" | "ok" | "critical",
        "total_rows": int,
        "critical_events": int,
        "recommendation": str,
      }
    """
    p = Path(path)

    if not p.exists():
        msg = f"{p} not found."
        return {
            "status": "no_data",
            "total_rows": 0,
            "critical_events": 0,
            "recommendation": "No fusion scores available.",
            "message": msg,
        }

    with p.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []

        if "score" not in fieldnames:
            return {
                "status": "bad_schema",
                "total_rows": 0,
                "critical_events": 0,
                "recommendation": "Fix scored_output schema: missing 'score' column.",
                "message": "score column missing in scored_output.csv",
            }

        total = 0
        critical_count = 0

        for row in reader:
            total += 1
            try:
                score = float(row.get("score", 0.0))
            except ValueError:
                score = 0.0

            if score >= critical_threshold:
                critical_count += 1

    if total == 0:
        return {
            "status": "no_data",
            "total_rows": 0,
            "critical_events": 0,
            "recommendation": "No rows in scored_output.csv.",
            "message": "Empty scored_output.csv",
        }

    if critical_count == 0:
        status = "ok"
        rec = "Situation stable — no high risk events."
        # Log a low-severity event to threat memory
        append_event(
            event_type="fusion_status",
            severity="low",
            doctrine_tag="Fusion_Ops",
            note="No critical fused events detected.",
            source="owl_brain",
        )
    else:
        status = "critical"
        rec = f"{critical_count} critical event(s). Recommend operator review."
        append_event(
            event_type="fusion_critical",
            severity="high",
            doctrine_tag="Fusion_Ops",
            note=rec,
            source="owl_brain",
        )

    return {
        "status": status,
        "total_rows": total,
        "critical_events": critical_count,
        "recommendation": rec,
    }


def threat_snapshot(max_events: int = 5) -> str:
    """
    Compact summary string for mission briefings.

    Includes:
      - Total events
      - Counts by type
      - Last few events (up to max_events)
    """
    events = load_events()
    total = len(events)
    counts = count_by_type(events)

    lines: List[str] = []
    lines.append("=== THREAT SNAPSHOT (OWL) ===")
    lines.append(f"Total logged threat events: {total}")
    lines.append("")

    if not events:
        lines.append("No threat memory events logged yet.")
        return "\n".join(lines)

    lines.append("Counts by type:")
    for t, c in sorted(counts.items(), key=lambda x: x[0]):
        lines.append(f"  - {t}: {c}")
    lines.append("")

    lines.append(f"Last {min(max_events, total)} event(s):")
    for ev in events[-max_events:]:
        ts = ev.get("timestamp", "unknown_time")
        etype = ev.get("type", "UNKNOWN")
        sev = ev.get("severity", "unknown")
        note = ev.get("note", "")
        lines.append(f"  [{ts}] {etype} (sev={sev}) — {note}")

    return "\n".join(lines)


if __name__ == "__main__":
    # Simple standalone test
    print("=== OWL BRAIN FUSION ANALYSIS TEST ===")
    result = analyze_fusion()
    print(result)
    print()

    print(threat_snapshot())

