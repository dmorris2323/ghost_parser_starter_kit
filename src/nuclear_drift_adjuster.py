#!/usr/bin/env python3
"""
nuclear_drift_adjuster.py

Ghost Lantern Labs – Nuclear Hardening Block
--------------------------------------------

Purpose:
    Factor sensor drift and reliability into nuclear early-warning scores,
    creating a "drift-adjusted" early warning view.

Inputs (all optional, defensive):
    docs/prelaunch_watchboard.json
    docs/reliability_report.json (if it exists)
    docs/golden_dome_drift_report.txt (optional, heuristic)

Outputs:
    docs/nuclear_drift_adjusted_score.json
    docs/nuclear_drift_adjusted_score.txt

The goal is to:
    - Penalize early-warning score if sensors are unreliable or drifting.
    - Provide a commander-readable "drift confidence" meter.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional, List

BASE_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(BASE_DIR, "docs")


def _safe_read_json(path: str) -> Optional[Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _safe_read_text(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def _extract_base_score(wb: Any) -> float:
    if not isinstance(wb, dict):
        return 0.0
    score = wb.get("early_warning_score", 0.0)
    try:
        return float(score)
    except Exception:
        return 0.0


def _estimate_reliability_penalty(rel_report: Any) -> Dict[str, Any]:
    """
    Try to infer an overall reliability penalty from a generic reliability report JSON.

    Expected patterns (but we don't strictly depend on them):
        {
          "global_reliability": 0.0–1.0
          "per_sensor": [...]
        }
    """
    penalty = 0.0
    notes: List[str] = []

    if not isinstance(rel_report, dict):
        return {"penalty": 0.0, "notes": ["No structured reliability report available."]}

    global_rel = rel_report.get("global_reliability")
    if global_rel is not None:
        try:
            global_rel = float(global_rel)
            # Reliability 1.0  => no penalty
            # Reliability 0.5  => moderate penalty
            # Reliability 0.0  => heavy penalty
            if global_rel >= 0.9:
                penalty = 0.0
                notes.append("High global reliability (>=0.9) – no drift penalty applied.")
            elif global_rel >= 0.7:
                penalty = 5.0
                notes.append("Slightly reduced reliability (0.7–0.9) – minor penalty.")
            elif global_rel >= 0.4:
                penalty = 15.0
                notes.append("Moderately reduced reliability (0.4–0.7) – moderate penalty.")
            else:
                penalty = 30.0
                notes.append("Low reliability (<0.4) – heavy drift penalty applied.")
        except Exception:
            notes.append("Could not parse global_reliability; skipping penalty.")
    else:
        notes.append("No global_reliability field; no penalty applied.")

    return {"penalty": penalty, "notes": notes}


def _estimate_drift_penalty(drift_txt: Optional[str]) -> Dict[str, Any]:
    """
    Heuristic penalty based on Golden Dome drift report text.
    """
    if not drift_txt:
        return {"penalty": 0.0, "notes": ["No Golden Dome drift text available."]}

    t = drift_txt.lower()
    notes: List[str] = []

    if "stable" in t and "no significant drift" in t:
        penalty = 0.0
        notes.append("Drift report indicates stable conditions – no drift penalty.")
    elif "mild drift" in t or "slow drift" in t:
        penalty = 5.0
        notes.append("Mild drift mentioned – small drift penalty.")
    elif "notable drift" in t or "increasing drift" in t:
        penalty = 15.0
        notes.append("Increasing drift observed – moderate drift penalty.")
    elif "severe drift" in t or "unacceptable drift" in t:
        penalty = 30.0
        notes.append("Severe drift mentioned – heavy drift penalty.")
    else:
        penalty = 10.0
        notes.append("Drift language ambiguous – applying conservative penalty.")
    return {"penalty": penalty, "notes": notes}


def build_nuclear_drift_adjusted_score() -> Dict[str, Any]:
    os.makedirs(DOCS_DIR, exist_ok=True)

    watchboard_path = os.path.join(DOCS_DIR, "prelaunch_watchboard.json")
    reliability_path = os.path.join(DOCS_DIR, "reliability_report.json")
    drift_report_path = os.path.join(DOCS_DIR, "golden_dome_drift_report.txt")

    watchboard = _safe_read_json(watchboard_path)
    reliability = _safe_read_json(reliability_path)
    drift_txt = _safe_read_text(drift_report_path)

    inputs_present = {
        "prelaunch_watchboard_json": watchboard is not None,
        "reliability_report_json": reliability is not None,
        "golden_dome_drift_report_txt": drift_txt is not None,
    }

    base_score = _extract_base_score(watchboard)
    rel_info = _estimate_reliability_penalty(reliability)
    drift_info = _estimate_drift_penalty(drift_txt)

    total_penalty = rel_info["penalty"] + drift_info["penalty"]
    adjusted_score = max(0.0, min(100.0, base_score - total_penalty))

    # Drift confidence: 100 when penalty <5, drops as penalty grows
    drift_confidence = max(0.0, 100.0 - (total_penalty * 2.0))

    rationale: List[str] = []
    rationale.append(f"Base early-warning score from watchboard: {base_score:.1f}/100.")
    rationale.append(
        f"Total drift/reliability penalty: {total_penalty:.1f} points (reliability + drift)."
    )
    rationale.extend(rel_info["notes"])
    rationale.extend(drift_info["notes"])
    rationale.append(
        f"Drift-adjusted early-warning score: {adjusted_score:.1f}/100; drift confidence: {drift_confidence:.1f}/100."
    )

    result: Dict[str, Any] = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "inputs_present": inputs_present,
        "base_early_warning_score": base_score,
        "total_penalty": total_penalty,
        "drift_adjusted_early_warning_score": adjusted_score,
        "drift_confidence": drift_confidence,
        "rationale": rationale,
    }

    # JSON
    json_path = os.path.join(DOCS_DIR, "nuclear_drift_adjusted_score.json")
    with open(json_path, "w", encoding="utf-8") as f_json:
        json.dump(result, f_json, indent=2, sort_keys=True)

    # TXT
    lines: List[str] = []
    lines.append("GLL Nuclear Drift-Adjusted Early Warning Score")
    lines.append("==============================================")
    lines.append(f"Generated at (UTC): {result['generated_at']}")
    lines.append("")
    lines.append(f"Base Early Warning Score: {base_score:.1f}/100")
    lines.append(f"Total Drift/Reliability Penalty: {total_penalty:.1f}")
    lines.append(f"Drift-Adjusted Early Warning Score: {adjusted_score:.1f}/100")
    lines.append(f"Drift Confidence: {drift_confidence:.1f}/100")
    lines.append("")
    lines.append("Inputs Present:")
    for name, present in inputs_present.items():
        lines.append(f"  - {name}: {'OK' if present else 'MISSING'}")
    lines.append("")
    lines.append("Rationale:")
    for r in rationale:
        lines.append(f"  - {r}")

    txt_path = os.path.join(DOCS_DIR, "nuclear_drift_adjusted_score.txt")
    with open(txt_path, "w", encoding="utf-8") as f_txt:
        f_txt.write("\n".join(lines))

    return result


if __name__ == "__main__":
    out = build_nuclear_drift_adjusted_score()
    print("Nuclear drift-adjusted early warning score generated:")
    print(f"  - {os.path.join('docs', 'nuclear_drift_adjusted_score.json')}")
    print(f"  - {os.path.join('docs', 'nuclear_drift_adjusted_score.txt')}")

