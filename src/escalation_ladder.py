"""
escalation_ladder.py

Week-1 Nuclear/AFTAC hardening:
- Convert risk/trust/alerts/degraded/ambiguity into a *bounded* watch posture
- Outputs a commander-defensible escalation recommendation
- Never crashes; safe for synthetic demos

Public API:
- recommend_escalation(...)
- write_escalation_artifacts(...)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


NUCLEAR_DIR = Path("docs") / "nuclear"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, obj: Any) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _write_txt(path: Path, text: str) -> None:
    _safe_mkdir(path.parent)
    path.write_text(text, encoding="utf-8")


def _coerce_int(x: Any, default: int = 0) -> int:
    try:
        return int(x)
    except Exception:
        return default


def _coerce_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _norm_alerts(alerts: Optional[Dict[str, Any]]) -> Dict[str, int]:
    a = alerts or {}
    return {
        "crit": _coerce_int(a.get("crit", 0)),
        "high": _coerce_int(a.get("high", 0)),
        "attack_like": _coerce_int(a.get("attack_like", 0)),
        "anomaly": _coerce_int(a.get("anomaly", 0)),
        "total": _coerce_int(a.get("total", 0)),
    }


def recommend_escalation(
    *,
    trust_score: Any,
    risk_score: Any,
    alerts: Optional[Dict[str, Any]] = None,
    degraded: bool = False,
    confidence: str = "UNKNOWN",
    ambiguity_flags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Returns a bounded escalation recommendation.

    posture levels:
      - ROUTINE
      - ELEVATED_WATCH
      - HEIGHTENED_COLLECTION
      - DUTY_OFFICER_NOTIFY
      - CRISIS_ACTION_TEAM
    """
    trust = _coerce_float(trust_score, 0.0)
    risk = _coerce_float(risk_score, 0.0)
    a = _norm_alerts(alerts)
    flags = [str(x) for x in (ambiguity_flags or [])]

    # scoring (bounded; deterministic)
    score = 0

    # risk contribution
    if risk >= 85:
        score += 4
    elif risk >= 65:
        score += 3
    elif risk >= 40:
        score += 2
    elif risk >= 20:
        score += 1

    # alert contribution
    if a["crit"] > 0:
        score += 4
    elif a["high"] >= 3:
        score += 3
    elif a["high"] > 0:
        score += 2
    elif a["attack_like"] >= 10:
        score += 2
    elif a["attack_like"] > 0:
        score += 1

    # trust/confidence modifiers (ambiguity reduces decisiveness but increases collection posture)
    if trust < 55:
        score += 2
    elif trust < 70:
        score += 1

    if str(confidence).upper() in {"VERY_LOW", "LOW"}:
        score += 1  # push toward collection/verification

    if degraded:
        score += 1

    if "MISSING_SIGNALS" in flags:
        score += 1

    # map score to posture (bounded)
    if score <= 2:
        posture = "ROUTINE"
    elif score <= 4:
        posture = "ELEVATED_WATCH"
    elif score <= 6:
        posture = "HEIGHTENED_COLLECTION"
    elif score <= 8:
        posture = "DUTY_OFFICER_NOTIFY"
    else:
        posture = "CRISIS_ACTION_TEAM"

    # posture-specific actions (no overclaims)
    actions: List[str] = []
    if posture == "ROUTINE":
        actions = [
            "Maintain normal watch cadence.",
            "Continue multi-source monitoring; avoid single-domain interpretation.",
        ]
    elif posture == "ELEVATED_WATCH":
        actions = [
            "Increase monitoring cadence and verify feed continuity.",
            "Queue cross-domain checks (EMS/COMMS/CYBER) before narrative conclusions.",
        ]
    elif posture == "HEIGHTENED_COLLECTION":
        actions = [
            "Prioritize restoration of missing signals; confirm sensor health.",
            "Run baseline vs injected validation and compare bounded deltas.",
            "Elevate analyst review (second set of eyes) before escalation.",
        ]
    elif posture == "DUTY_OFFICER_NOTIFY":
        actions = [
            "Notify duty leadership per local SOP; provide bounded language only.",
            "Cross-check independent sources; do not rely on a single indicator stream.",
            "Prepare a short decision card + pre-brief trust annotations for leadership.",
        ]
    else:  # CRISIS_ACTION_TEAM
        actions = [
            "Initiate crisis coordination per SOP (CAT/ops floor).",
            "Treat as time-sensitive: verify, corroborate, communicate uncertainties.",
            "Do not claim confirmation; present probabilities + unknowns.",
        ]

    rationale = {
        "computed_score": score,
        "drivers": {
            "risk_score": risk,
            "trust_score": trust,
            "alerts": a,
            "confidence": confidence,
            "degraded": bool(degraded),
            "ambiguity_flags": flags,
        },
        "notes": [
            "This ladder is deterministic and bounded to reduce analyst drift.",
            "Ambiguity increases verification posture, not certainty claims.",
        ],
    }

    return {
        "generated_at_utc": _utc_now_iso(),
        "type": "ESCALATION_LADDER_RECOMMENDATION",
        "safe_notice": "May be generated from synthetic telemetry for training/demos.",
        "posture": posture,
        "actions": actions,
        "rationale": rationale,
    }


def write_escalation_artifacts(rec: Dict[str, Any]) -> Dict[str, str]:
    _safe_mkdir(NUCLEAR_DIR)
    stamped = _ts()

    json_latest = NUCLEAR_DIR / "escalation_ladder_latest.json"
    txt_latest = NUCLEAR_DIR / "escalation_ladder_latest.txt"
    json_stamped = NUCLEAR_DIR / f"escalation_ladder_{stamped}.json"
    txt_stamped = NUCLEAR_DIR / f"escalation_ladder_{stamped}.txt"

    _write_json(json_latest, rec)
    _write_json(json_stamped, rec)

    # small txt render
    r = rec.get("rationale", {}).get("drivers", {})
    a = (r.get("alerts") or {})
    lines = []
    lines.append("GLL — ESCALATION LADDER (LATEST)")
    lines.append(f"Generated (UTC): {rec.get('generated_at_utc','')}")
    lines.append("")
    lines.append(f"Posture: {rec.get('posture','')}")
    lines.append("")
    lines.append("Drivers:")
    lines.append(f"- Risk: {r.get('risk_score',0)}")
    lines.append(f"- Trust: {r.get('trust_score',0)}")
    lines.append(f"- Confidence: {r.get('confidence','')}")
    lines.append(f"- Degraded: {r.get('degraded', False)}")
    lines.append(
        f"- Alerts: crit={a.get('crit',0)} high={a.get('high',0)} "
        f"attack_like={a.get('attack_like',0)} anomaly={a.get('anomaly',0)}"
    )
    lines.append("")
    lines.append("Actions:")
    for x in (rec.get("actions") or []):
        lines.append(f"- {x}")

    _write_txt(txt_latest, "\n".join(lines).strip() + "\n")
    _write_txt(txt_stamped, "\n".join(lines).strip() + "\n")

    return {
        "json_latest": str(json_latest),
        "txt_latest": str(txt_latest),
        "json_stamped": str(json_stamped),
        "txt_stamped": str(txt_stamped),
    }

