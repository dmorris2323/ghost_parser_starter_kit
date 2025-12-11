#!/usr/bin/env python3
"""
prelaunch_signals_analyzer.py

Ghost Lantern Labs – Impact Module 3
------------------------------------

Nuclear Early-Warning – Pre-Boost Fusion Upgrade

Purpose:
    Fuse multiple pre-launch relevant artifacts into a single commander-level
    "Pre-Boost Threat Card" so that GLL can answer:

        "Given what we know right now, how worried should we be about a
         pre-launch environment, and how trustworthy is that assessment?"

Inputs (all optional, best-effort use):
    - src/docs/prelaunch_watchboard.json
        • Existing ISR pre-launch watchboard.
    - src/docs/golden_dome_daily_watch.json
        • Nuclear readiness + drift + fusion trust.
    - src/docs/sps_behavior_report.json
        • SPS Module 3 – Behavioral Integrity Monitor.

Outputs:
    - src/docs/preboost_threat_card.json
    - src/docs/preboost_threat_card.txt

Design:
    - Never fails hard because of missing inputs.
    - Uses simple keyword / structure heuristics to derive a 0–100 risk score.
    - Produces a banded threat level:
        • LOW
        • GUARDED
        • ELEVATED
        • CRITICAL
    - Includes explicit caveats about data quality and SPS status.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple
from datetime import datetime
import json


BASE_DIR = Path(__file__).resolve().parent               # .../src
DOCS_DIR = BASE_DIR / "docs"

PRELAUNCH_WATCHBOARD = DOCS_DIR / "prelaunch_watchboard.json"
GOLDEN_DOME_DAILY = DOCS_DIR / "golden_dome_daily_watch.json"
SPS_BEHAVIOR = DOCS_DIR / "sps_behavior_report.json"

PREBOOST_JSON = DOCS_DIR / "preboost_threat_card.json"
PREBOOST_TXT = DOCS_DIR / "preboost_threat_card.txt"


# ---------------------------------------------------------------------------
# Safe JSON loaders
# ---------------------------------------------------------------------------

def _safe_load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8")
        return json.loads(text)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Generic recursive scanners for "risk-ish" signals
# ---------------------------------------------------------------------------

def _flatten_strings(obj: Any, acc: List[str] | None = None) -> List[str]:
    """
    Recursively collect all string values from a nested JSON-like object.
    """
    if acc is None:
        acc = []
    if isinstance(obj, str):
        acc.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            _flatten_strings(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            _flatten_strings(v, acc)
    return acc


def _count_keywords(strings: List[str], keywords: List[str]) -> int:
    text = " ".join(strings).lower()
    return sum(text.count(k.lower()) for k in keywords)


# ---------------------------------------------------------------------------
# Heuristics for scoring
# ---------------------------------------------------------------------------

def _score_prelaunch_watchboard(data: Any | None) -> Tuple[float, List[str]]:
    """
    Look inside prelaunch_watchboard.json for hints of elevated activity.
    We don't assume a specific schema; we just scan text and simple fields.

    Returns:
        (score_contrib, reasons)
    """
    if data is None:
        return 0.0, ["No prelaunch_watchboard.json found – cannot leverage pre-launch ISR board."]

    reasons: List[str] = []
    strings = _flatten_strings(data)

    critical_hits = _count_keywords(strings, ["critical", "crucial", "launch imminent"])
    high_hits = _count_keywords(strings, ["high", "elevated", "amber"])
    missile_hits = _count_keywords(strings, ["missile", "launch", "silo", "pad", "booster"])

    score = 0.0

    if critical_hits > 0:
        score += min(40.0, 15.0 * critical_hits)
        reasons.append(f"Prelaunch watchboard text contains CRITICAL indicators ({critical_hits} hits).")

    if high_hits > 0:
        score += min(20.0, 5.0 * high_hits)
        reasons.append(f"Prelaunch watchboard text shows elevated/high language ({high_hits} hits).")

    if missile_hits > 0:
        score += min(15.0, 3.0 * missile_hits)
        reasons.append(f"Prelaunch watchboard references missile/launch concepts ({missile_hits} hits).")

    if score == 0.0:
        reasons.append("Prelaunch watchboard does not show obvious 'critical/high/missile' language.")

    return score, reasons


def _score_golden_dome_daily(data: Any | None) -> Tuple[float, List[str]]:
    """
    Use the Golden Dome Daily Watch JSON (if present) to add or subtract
    confidence and risk based on nuclear readiness and fusion trust.

    We look for:
        - readiness level words
        - trust / confidence fields
        - forecast language
    """
    if data is None:
        return 0.0, ["No golden_dome_daily_watch.json found – cannot leverage daily nuclear readiness."]

    reasons: List[str] = []
    strings = _flatten_strings(data)

    # High readiness language
    dome_crit = _count_keywords(strings, ["red", "critical", "high alert"])
    dome_warn = _count_keywords(strings, ["amber", "watch", "heightened"])

    score = 0.0

    if dome_crit > 0:
        score += min(25.0, 10.0 * dome_crit)
        reasons.append(f"Golden Dome daily watch indicates CRITICAL/RED posture ({dome_crit} hits).")

    if dome_warn > 0 and dome_crit == 0:
        score += min(15.0, 5.0 * dome_warn)
        reasons.append(f"Golden Dome daily watch indicates AMBER/watch posture ({dome_warn} hits).")

    if score == 0.0:
        reasons.append("Golden Dome daily watch does not show obvious RED/AMBER language.")

    return score, reasons


def _score_sps_behavior(data: Any | None) -> Tuple[float, List[str], str]:
    """
    Evaluate SPS behavioral status (GREEN / AMBER / RED).
    This affects confidence, not the "external" threat directly.

    We return:
        (confidence_modifier, reasons, level)
    """
    if data is None:
        return 0.0, ["No SPS behavioral report found – assuming neutral confidence."], "UNKNOWN"

    status = (data.get("status") or {}) if isinstance(data, dict) else {}
    level = str(status.get("level", "UNKNOWN")).upper()
    reasons: List[str] = []

    if level == "RED":
        reasons.append(
            "SPS Behavioral Monitor is RED – internal system behavior is risky; "
            "treat any pre-boost assessment as degraded and verify manually."
        )
        return -15.0, reasons, level

    if level == "AMBER":
        reasons.append(
            "SPS Behavioral Monitor is AMBER – exercise caution; cross-check with "
            "additional sources if using this for serious decisions."
        )
        return -5.0, reasons, level

    if level == "GREEN":
        reasons.append(
            "SPS Behavioral Monitor is GREEN – system behavior appears stable; "
            "confidence in this assessment is slightly boosted."
        )
        return 5.0, reasons, level

    reasons.append(
        f"SPS Behavioral Monitor level is {level} – treating as neutral confidence."
    )
    return 0.0, reasons, level


# ---------------------------------------------------------------------------
# Threat banding
# ---------------------------------------------------------------------------

def _band_preboost_risk(score: float) -> Tuple[str, str]:
    """
    Map a 0–100 risk score into band + human-readable summary.
    """
    if score < 20:
        return "LOW", (
            "Pre-boost threat currently assessed as LOW. Maintain routine watch, "
            "but no immediate launch environment indicators are dominant."
        )
    if score < 40:
        return "GUARDED", (
            "Pre-boost threat is GUARDED. Some indicators are present or the "
            "nuclear readiness posture is elevated. Maintain heightened awareness."
        )
    if score < 70:
        return "ELEVATED", (
            "Pre-boost threat is ELEVATED. Multiple indicators and/or nuclear "
            "readiness signals are aligning. Commanders should be briefed."
        )
    return "CRITICAL", (
        "Pre-boost threat is CRITICAL. Strong indicator alignment and/or Golden "
        "Dome posture suggest a potentially active pre-launch environment."
    )


# ---------------------------------------------------------------------------
# Core analysis
# ---------------------------------------------------------------------------

def build_preboost_threat_card() -> Dict[str, Any]:
    """
    Main entrypoint: fuse signals and build the Pre-Boost Threat Card.
    """
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    prelaunch_data = _safe_load_json(PRELAUNCH_WATCHBOARD)
    dome_data = _safe_load_json(GOLDEN_DOME_DAILY)
    sps_data = _safe_load_json(SPS_BEHAVIOR)

    total_score = 0.0
    reasons: List[str] = []

    # Prelaunch watchboard contribution
    s1, r1 = _score_prelaunch_watchboard(prelaunch_data)
    total_score += s1
    reasons.extend(r1)

    # Golden Dome daily watch contribution
    s2, r2 = _score_golden_dome_daily(dome_data)
    total_score += s2
    reasons.extend(r2)

    # SPS confidence modifier
    conf_mod, r3, sps_level = _score_sps_behavior(sps_data)
    total_score += conf_mod
    reasons.extend(r3)

    # Clamp score to 0–100
    total_score = max(0.0, min(100.0, total_score))

    band, band_summary = _band_preboost_risk(total_score)

    card: Dict[str, Any] = {
        "title": "Ghost Lantern Labs – Pre-Boost Threat Card",
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "inputs": {
            "prelaunch_watchboard_path": str(PRELAUNCH_WATCHBOARD) if PRELAUNCH_WATCHBOARD.exists() else None,
            "golden_dome_daily_watch_path": str(GOLDEN_DOME_DAILY) if GOLDEN_DOME_DAILY.exists() else None,
            "sps_behavior_report_path": str(SPS_BEHAVIOR) if SPS_BEHAVIOR.exists() else None,
        },
        "scores": {
            "combined_risk_score": round(total_score, 1),
            "sps_confidence_modifier": round(conf_mod, 1),
        },
        "status": {
            "preboost_risk_band": band,
            "preboost_summary": band_summary,
            "sps_behavior_level": sps_level,
        },
        "reasons": reasons,
        "caveats": [
            "This card is generated from available GLL artifacts only; it is "
            "UNCLASSIFIED and should not be used as a substitute for DCGS/USNDS/ICADS.",
            "Treat this as a training and demonstration aid unless validated and "
            "accredited for operational use.",
        ],
    }

    return card


def _format_preboost_text(card: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("Ghost Lantern Labs – Pre-Boost Threat Card")
    lines.append("=" * 72)
    lines.append("")
    lines.append(f"Generated at : {card.get('generated_at')}")
    lines.append("")

    status = card.get("status", {}) or {}
    scores = card.get("scores", {}) or {}
    inputs = card.get("inputs", {}) or {}

    lines.append("Status")
    lines.append("------")
    lines.append(f"Risk band      : {status.get('preboost_risk_band', 'UNKNOWN')}")
    lines.append(f"Risk summary   : {status.get('preboost_summary', '')}")
    lines.append(f"SPS behavior   : {status.get('sps_behavior_level', 'UNKNOWN')}")
    lines.append("")

    lines.append("Score Breakdown")
    lines.append("----------------")
    lines.append(f"Combined risk score     : {scores.get('combined_risk_score', 'N/A')}")
    lines.append(f"SPS confidence modifier : {scores.get('sps_confidence_modifier', 'N/A')}")
    lines.append("")

    lines.append("Inputs Used")
    lines.append("-----------")
    lines.append(f"Prelaunch watchboard JSON : {inputs.get('prelaunch_watchboard_path')}")
    lines.append(f"Golden Dome daily watch   : {inputs.get('golden_dome_daily_watch_path')}")
    lines.append(f"SPS behavior report       : {inputs.get('sps_behavior_report_path')}")
    lines.append("")

    lines.append("Reasons / Indicators")
    lines.append("--------------------")
    reasons = card.get("reasons", []) or []
    if reasons:
        for r in reasons:
            lines.append(f"- {r}")
    else:
        lines.append("- No specific reasons extracted; heuristic engine found no strong indicators.")
    lines.append("")

    lines.append("Caveats")
    lines.append("-------")
    for c in card.get("caveats", []) or []:
        lines.append(f"- {c}")
    lines.append("")

    return "\n".join(lines)


def write_preboost_threat_card() -> Dict[str, Any]:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    card = build_preboost_threat_card()

    PREBOOST_JSON.write_text(json.dumps(card, indent=2), encoding="utf-8")

    text = _format_preboost_text(card)
    PREBOOST_TXT.write_text(text, encoding="utf-8")

    return {
        "json_path": str(PREBOOST_JSON),
        "txt_path": str(PREBOOST_TXT),
        "card": card,
    }


if __name__ == "__main__":
    result = write_preboost_threat_card()
    print("Pre-Boost Threat Card written:")
    print(f"  JSON: {result['json_path']}")
    print(f"  TXT:  {result['txt_path']}")

