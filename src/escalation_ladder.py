"""
escalation_ladder.py

Week-1 Nuclear/AFTAC Hardening:
Escalation posture logic that is:
- bounded
- anti-oscillation
- anti-illegal-jump
- ambiguity-aware

IMPORTANT:
This file provides both the newer API (compute_posture)
AND backward-compatible function names used by older modules:
- recommend_escalation
- write_escalation_artifacts

So nothing else breaks.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


OUT_DIR = Path("docs") / "nuclear"


POSTURE_ORDER = [
    "ROUTINE_MONITORING",
    "DUTY_OFFICER_NOTIFY",
    "UNIT_COMMANDER_ALERT",
    "REGIONAL_COMMAND_ALERT",
    "NATIONAL_COMMAND_ALERT",
]

POSTURE_INDEX = {p: i for i, p in enumerate(POSTURE_ORDER)}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, obj: Any) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _coerce_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _clamp_posture(p: str) -> str:
    p = str(p or "").strip().upper()
    if p in POSTURE_INDEX:
        return p
    return "ROUTINE_MONITORING"


def _step_up(p: str, steps: int = 1) -> str:
    i = POSTURE_INDEX[_clamp_posture(p)]
    j = min(i + max(0, int(steps)), len(POSTURE_ORDER) - 1)
    return POSTURE_ORDER[j]


@dataclass(frozen=True)
class EscalationResult:
    posture: str
    cap_applied: bool
    allowed_jump_steps: int
    deescalation_blocked: bool
    reason: List[str]


def compute_posture(
    *,
    trust_score: float,
    risk_score: float,
    confidence: str,
    degraded: bool,
    ambiguity_flags: Optional[List[str]] = None,
    previous_posture: Optional[str] = None,
) -> EscalationResult:
    """
    Primary (new) API.

    Inputs are bounded proxies (synthetic-safe).
    Output posture must never jump illegally and must avoid oscillation.

    Rules:
    - Base posture from risk banding
    - Confidence LOW/UNKNOWN limits escalation (cap)
    - Degraded/ambiguity blocks rapid de-escalation (anti-oscillation)
    - Max jump up per cycle is limited (anti-illegal-jump)
    """
    t = _coerce_float(trust_score, 0.0)
    r = _coerce_float(risk_score, 0.0)
    conf = str(confidence or "UNKNOWN").upper().strip()
    prev = _clamp_posture(previous_posture) if previous_posture else "ROUTINE_MONITORING"
    flags = ambiguity_flags if isinstance(ambiguity_flags, list) else []
    flags_s = [str(x) for x in flags]

    reason: List[str] = []
    allowed_jump_steps = 1

    # Base posture from risk score (bounded thresholds)
    if r >= 80:
        base = "REGIONAL_COMMAND_ALERT"
        reason.append("risk>=80 => base=REGIONAL_COMMAND_ALERT")
    elif r >= 60:
        base = "UNIT_COMMANDER_ALERT"
        reason.append("risk>=60 => base=UNIT_COMMANDER_ALERT")
    elif r >= 35:
        base = "DUTY_OFFICER_NOTIFY"
        reason.append("risk>=35 => base=DUTY_OFFICER_NOTIFY")
    else:
        base = "ROUTINE_MONITORING"
        reason.append("risk<35 => base=ROUTINE_MONITORING")

    # If trust is very low, bias away from extreme postures
    if t < 40 and base in {"REGIONAL_COMMAND_ALERT", "NATIONAL_COMMAND_ALERT"}:
        base = "UNIT_COMMANDER_ALERT"
        reason.append("trust<40 => downgrade base to UNIT_COMMANDER_ALERT")

    # Cap escalation if confidence is LOW/UNKNOWN or degraded ops / ambiguity
    cap_applied = False
    if conf in {"LOW", "UNKNOWN"} or degraded or "DEGRADED_OPS" in flags_s or "MISSING_SIGNALS" in flags_s:
        if base in {"UNIT_COMMANDER_ALERT", "REGIONAL_COMMAND_ALERT", "NATIONAL_COMMAND_ALERT"} and r < 85:
            base = "DUTY_OFFICER_NOTIFY"
            cap_applied = True
            reason.append("cap applied due to low confidence/degraded/ambiguity (risk<85)")

    target = base

    # Allow slightly larger jump only when risk is extreme
    if r >= 90:
        allowed_jump_steps = 2
        reason.append("risk>=90 => allow 2-step jump")

    # Prevent illegal jumps
    if POSTURE_INDEX[target] > POSTURE_INDEX[prev] + allowed_jump_steps:
        target = _step_up(prev, allowed_jump_steps)
        reason.append(f"illegal jump prevented => limited to +{allowed_jump_steps} step(s)")

    # Anti-oscillation: if degraded or ambiguity present, do not step down this run
    deescalation_blocked = False
    if degraded or flags_s:
        if POSTURE_INDEX[target] < POSTURE_INDEX[prev]:
            target = prev
            deescalation_blocked = True
            reason.append("de-escalation blocked due to degraded/ambiguity")

    return EscalationResult(
        posture=_clamp_posture(target),
        cap_applied=cap_applied,
        allowed_jump_steps=int(allowed_jump_steps),
        deescalation_blocked=bool(deescalation_blocked),
        reason=reason,
    )


# ---------------------------------------------------------------------
# Backward-compatible API expected by nuclear_decision_card.py
# ---------------------------------------------------------------------

def recommend_escalation(**kwargs: Any) -> Dict[str, Any]:
    """
    Back-compat wrapper.

    Older callers may pass extra fields (alerts, comms_state, etc.).
    We accept them and only use what we need.

    Expected commonly:
      trust_score, risk_score, confidence, degraded, ambiguity_flags, previous_posture, alerts
    """
    trust_score = kwargs.get("trust_score", 0.0)
    risk_score = kwargs.get("risk_score", 0.0)
    confidence = kwargs.get("confidence", "UNKNOWN")
    degraded = bool(kwargs.get("degraded", False))
    ambiguity_flags = kwargs.get("ambiguity_flags", None)
    previous_posture = kwargs.get("previous_posture", None)

    # We tolerate alerts but do not rely on its structure here.
    # If you want alert-driven escalation later, we’ll add it explicitly
    # with tests—NOT ad-hoc.
    res = compute_posture(
        trust_score=_coerce_float(trust_score, 0.0),
        risk_score=_coerce_float(risk_score, 0.0),
        confidence=str(confidence),
        degraded=degraded,
        ambiguity_flags=ambiguity_flags if isinstance(ambiguity_flags, list) else None,
        previous_posture=str(previous_posture) if previous_posture else None,
    )

    return {
        "posture": res.posture,
        "cap_applied": res.cap_applied,
        "allowed_jump_steps": res.allowed_jump_steps,
        "deescalation_blocked": res.deescalation_blocked,
        "reason": list(res.reason),
    }


def write_escalation_artifacts(escalation: Dict[str, Any]) -> Dict[str, str]:
    """
    Back-compat artifact writer used by older code.
    Writes latest + stamped JSON.
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = _ts()

    json_latest = OUT_DIR / "escalation_ladder_latest.json"
    json_stamped = OUT_DIR / f"escalation_ladder_{ts}.json"

    payload = {
        "generated_at": _utc_now_iso(),
        "safe_notice": "Synthetic-safe escalation artifacts for training/demos.",
        "escalation": escalation,
    }

    _write_json(json_latest, payload)
    _write_json(json_stamped, payload)

    return {
        "json_latest": str(json_latest),
        "json_stamped": str(json_stamped),
    }

