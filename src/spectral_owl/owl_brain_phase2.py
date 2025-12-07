"""
spectral_owl/owl_brain_phase2.py

Phase 2 Spectral Owl brain:
- Reads scored_output.csv
- Computes simple fusion risk metrics
- Exposes analyze_fusion() and threat_snapshot()
  for CLI, mission briefs, and overlays.

This version is deliberately self-contained:
no external LLM calls, safe to run offline.
"""

from __future__ import annotations

import csv
import json
import statistics as stats
from pathlib import Path
from typing import Dict, Any, List

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SCORED_FILE = DATA_DIR / "scored_output.csv"


def _load_scored_rows() -> List[Dict[str, Any]]:
    """
    Load scored_output.csv and return a list of dict rows.

    Expected columns (minimum):
      - id
      - score  (float between 0 and 1)
    """
    if not SCORED_FILE.exists():
        return []

    rows: List[Dict[str, Any]] = []
    with SCORED_FILE.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Try to normalize score column
            score_raw = row.get("score") or row.get("Score") or row.get("threat_score")
            if score_raw is None:
                continue
            try:
                score_val = float(score_raw)
            except ValueError:
                continue
            row["score"] = score_val
            rows.append(row)
    return rows


def _compute_metrics(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute simple fusion metrics from scored rows.
    """
    if not rows:
        return {
            "status": "no_data",
            "total_events": 0,
            "critical_events": 0,
            "warning_events": 0,
            "avg_score": None,
            "max_score": None,
            "risk_level": "unknown",
        }

    scores = [r["score"] for r in rows]

    total = len(scores)
    avg_score = stats.fmean(scores)
    max_score = max(scores)

    # Simple buckets
    critical_events = sum(1 for s in scores if s >= 0.85)
    warning_events = sum(1 for s in scores if 0.6 <= s < 0.85)

    # Risk level heuristic
    if critical_events > 0 or avg_score >= 0.8:
        risk_level = "high"
    elif warning_events > 0 or avg_score >= 0.6:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "status": "ok",
        "total_events": total,
        "critical_events": critical_events,
        "warning_events": warning_events,
        "avg_score": avg_score,
        "max_score": max_score,
        "risk_level": risk_level,
    }


def analyze_fusion() -> Dict[str, Any]:
    """
    Main entry point used by ghost_cli and mission briefs.

    Returns a dict with:
      - status: "ok" | "no_data"
      - total_events
      - critical_events
      - warning_events
      - avg_score
      - max_score
      - risk_level: "low" | "medium" | "high" | "unknown"
    """
    rows = _load_scored_rows()
    metrics = _compute_metrics(rows)
    return metrics


def threat_snapshot() -> Dict[str, Any]:
    """
    Higher-level summary wrapper around analyze_fusion().

    Returns a dict like:
      {
        "summary": "...",
        "metrics": {...}
      }
    """
    metrics = analyze_fusion()

    if metrics["status"] != "ok":
        return {
            "summary": "No scored fusion data available. Run fusion_scoring first.",
            "metrics": metrics,
        }

    total = metrics["total_events"]
    crit = metrics["critical_events"]
    warn = metrics["warning_events"]
    avg = metrics["avg_score"]
    lvl = metrics["risk_level"]

    summary = (
        f"Fusion risk level: {lvl.upper()} — "
        f"{crit} critical, {warn} warning out of {total} events "
        f"(avg score {avg:.2f})."
    )

    return {
        "summary": summary,
        "metrics": metrics,
    }


def main() -> None:
    """
    CLI entrypoint for quick testing:

    python -m spectral_owl.owl_brain_phase2
    or
    python spectral_owl/owl_brain_phase2.py
    """
    snap = threat_snapshot()
    print(json.dumps(snap, indent=2, default=str))


if __name__ == "__main__":
    main()

