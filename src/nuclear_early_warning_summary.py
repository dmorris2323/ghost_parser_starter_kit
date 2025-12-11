#!/usr/bin/env python3
"""
nuclear_early_warning_summary.py

Ghost Lantern Labs – Nuclear Hardening Block
--------------------------------------------

Purpose:
    Aggregate nuclear early-warning artifacts into a single, hardened,
    commander-grade summary view.

Inputs (all optional, defensive):
    docs/prelaunch_watchboard.json
    docs/nuclear_cross_validation.json
    docs/nuclear_drift_adjusted_score.json
    docs/nuclear_temporal_volatility.json
    docs/sensor_concurrence_matrix.json

Outputs:
    docs/nuclear_early_warning_summary.json
    docs/nuclear_early_warning_summary.txt

This module is aggregation-only and does NOT modify upstream files.
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


def _load(path: str) -> Any:
    return _safe_read_json(path)


def _derive_overall_level(base_level: str, drift_score: float, volatility: float) -> str:
    """
    Adjust the prelaunch_watchboard's early_warning_level using
    drift-adjusted score and volatility index.

    Very simple ladder logic:
        - If drift-adjusted score < 20 => STEADY
        - If 20–45 => TENSE
        - If 45–70 => ALERT
        - If >70 => CRITICAL
    Volatility above 70 can bump a band up by one level.
    """
    base_level = base_level.upper() if base_level else "UNKNOWN"

    # map level to numeric
    ladder = ["STEADY", "TENSE", "ALERT", "CRITICAL"]
    if base_level not in ladder:
        # fall back to score-based mapping
        if drift_score < 20.0:
            base_level = "STEADY"
        elif drift_score < 45.0:
            base_level = "TENSE"
        elif drift_score < 70.0:
            base_level = "ALERT"
        else:
            base_level = "CRITICAL"

    idx = ladder.index(base_level)

    # volatility bump
    if volatility >= 70.0 and idx < len(ladder) - 1:
        idx += 1

    return ladder[idx]


def build_nuclear_early_warning_summary() -> Dict[str, Any]:
    os.makedirs(DOCS_DIR, exist_ok=True)

    prelaunch_path = os.path.join(DOCS_DIR, "prelaunch_watchboard.json")
    cross_val_path = os.path.join(DOCS_DIR, "nuclear_cross_validation.json")
    drift_path = os.path.join(DOCS_DIR, "nuclear_drift_adjusted_score.json")
    vol_path = os.path.join(DOCS_DIR, "nuclear_temporal_volatility.json")
    conc_path = os.path.join(DOCS_DIR, "sensor_concurrence_matrix.json")

    prelaunch = _load(prelaunch_path)
    cross_val = _load(cross_val_path)
    drift = _load(drift_path)
    vol = _load(vol_path)
    conc = _load(conc_path)

    inputs_present = {
        "prelaunch_watchboard_json": prelaunch is not None,
        "nuclear_cross_validation_json": cross_val is not None,
        "nuclear_drift_adjusted_score_json": drift is not None,
        "nuclear_temporal_volatility_json": vol is not None,
        "sensor_concurrence_matrix_json": conc is not None,
    }

    # Base early warning level & score
    base_level = "UNKNOWN"
    base_score = 0.0
    crisis_mode = False
    if isinstance(prelaunch, dict):
        base_level = prelaunch.get("early_warning_level", "UNKNOWN")
        try:
            base_score = float(prelaunch.get("early_warning_score", 0.0))
        except Exception:
            base_score = 0.0
        crisis_mode = bool(prelaunch.get("crisis_mode", False))

    # Drift-adjusted and drift confidence
    drift_adjusted_score = 0.0
    drift_confidence = 0.0
    if isinstance(drift, dict):
        try:
            drift_adjusted_score = float(drift.get("drift_adjusted_early_warning_score", 0.0))
        except Exception:
            drift_adjusted_score = 0.0
        try:
            drift_confidence = float(drift.get("drift_confidence", 0.0))
        except Exception:
            drift_confidence = 0.0

    # Volatility index
    volatility_index = 0.0
    if isinstance(vol, dict):
        try:
            volatility_index = float(vol.get("volatility_index", 0.0))
        except Exception:
            volatility_index = 0.0

    # Cross-validation alignment
    alignment = "UNKNOWN"
    alignment_score = 0.0
    align_rationale: List[str] = []
    if isinstance(cross_val, dict):
        alignment = cross_val.get("alignment", "UNKNOWN")
        try:
            alignment_score = float(cross_val.get("alignment_score", 0.0))
        except Exception:
            alignment_score = 0.0
        align_rationale = cross_val.get("alignment_rationale", []) or []

    # Concurrence info (for now just count sensors)
    sensor_count = 0
    if isinstance(conc, dict):
        if isinstance(conc.get("sensors"), list):
            sensor_count = len(conc["sensors"])

    overall_level = _derive_overall_level(
        base_level=base_level,
        drift_score=drift_adjusted_score or base_score,
        volatility=volatility_index,
    )

    rationale: List[str] = []
    rationale.append(
        f"Base early-warning level from prelaunch_watchboard: {base_level} ({base_score:.1f}/100)."
    )
    if drift_adjusted_score > 0.0:
        rationale.append(
            f"Drift-adjusted early-warning score: {drift_adjusted_score:.1f}/100 with drift confidence {drift_confidence:.1f}/100."
        )
    else:
        rationale.append("No drift-adjusted score available; using base early-warning score.")
    rationale.append(
        f"Temporal volatility index: {volatility_index:.1f}/100 (higher values indicate more rapid or clustered activity)."
    )
    rationale.append(
        f"Nuclear cross-validation alignment: {alignment} ({alignment_score:.1f}/100)."
    )
    if sensor_count > 0:
        rationale.append(
            f"{sensor_count} nuclear-relevant sensors included in the concurrence matrix."
        )
    rationale.extend(align_rationale)

    result: Dict[str, Any] = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "inputs_present": inputs_present,
        "base_early_warning_level": base_level,
        "base_early_warning_score": base_score,
        "crisis_mode": crisis_mode,
        "drift_adjusted_early_warning_score": drift_adjusted_score,
        "drift_confidence": drift_confidence,
        "volatility_index": volatility_index,
        "alignment": alignment,
        "alignment_score": alignment_score,
        "sensor_count_in_concurrence_matrix": sensor_count,
        "overall_nuclear_early_warning_level": overall_level,
        "rationale": rationale,
    }

    # JSON
    json_path = os.path.join(DOCS_DIR, "nuclear_early_warning_summary.json")
    with open(json_path, "w", encoding="utf-8") as f_json:
        json.dump(result, f_json, indent=2, sort_keys=True)

    # TXT
    lines: List[str] = []
    lines.append("GLL Nuclear Early Warning Summary (Hardened View)")
    lines.append("=================================================")
    lines.append(f"Generated at (UTC): {result['generated_at']}")
    lines.append("")
    lines.append(f"Base Early Warning Level: {base_level}")
    lines.append(f"Base Early Warning Score: {base_score:.1f}/100")
    lines.append(f"Crisis Mode: {'ON' if crisis_mode else 'OFF'}")
    lines.append("")
    lines.append(f"Drift-Adjusted Early Warning Score: {drift_adjusted_score:.1f}/100")
    lines.append(f"Drift Confidence: {drift_confidence:.1f}/100")
    lines.append(f"Temporal Volatility Index: {volatility_index:.1f}/100")
    lines.append("")
    lines.append(f"Nuclear Alignment: {alignment} ({alignment_score:.1f}/100)")
    lines.append(f"Sensors in Concurrence Matrix: {sensor_count}")
    lines.append("")
    lines.append("Inputs Present:")
    for name, present in inputs_present.items():
        lines.append(f"  - {name}: {'OK' if present else 'MISSING'}")
    lines.append("")
    lines.append("Rationale:")
    for r in rationale:
        lines.append(f"  - {r}")

    txt_path = os.path.join(DOCS_DIR, "nuclear_early_warning_summary.txt")
    with open(txt_path, "w", encoding="utf-8") as f_txt:
        f_txt.write("\n".join(lines))

    return result


if __name__ == "__main__":
    out = build_nuclear_early_warning_summary()
    print("Nuclear early warning summary generated:")
    print(f"  - {os.path.join('docs', 'nuclear_early_warning_summary.json')}")
    print(f"  - {os.path.join('docs', 'nuclear_early_warning_summary.txt')}")

