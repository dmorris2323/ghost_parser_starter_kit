"""
escalation_ladder.py

Week-1 Nuclear/AFTAC Hardening:
- Monotonic, bounded escalation posture
- No illegal multi-step jumps in a single evaluation
- No oscillation (hysteresis) unless conditions are clean + stable

This is a training/safety policy layer. It is NOT real-world warning logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


POSTURE_ORDER = [
    "ROUTINE_MONITORING",
    "DUTY_OFFICER_NOTIFY",
    "UNIT_COMMANDER_ALERT",
    "WING_COMMANDER_ALERT",
    "NATIONAL_COMMAND_ALERT",
]
_POSTURE_INDEX = {p: i for i, p in enumerate(POSTURE_ORDER)}


def _clamp_posture(p: str) -> str:
    if p not in _POSTURE_INDEX:
        return "ROUTINE_MONITORING"
    return p


def _max_posture(a: str, b: str) -> str:
    a = _clamp_posture(a)
    b = _clamp_posture(b)
    return a if _POSTURE_INDEX[a] >= _POSTURE_INDEX[b] else b


def _min_posture(a: str, b: str) -> str:
    a = _clamp_posture(a)
    b = _clamp_posture(b)
    return a if _POSTURE_INDEX[a] <= _POSTURE_INDEX[b] else b


def _step_toward(prev: str, target: str, max_steps: int) -> str:
    prev = _clamp_posture(prev)
    target = _clamp_posture(target)
    pi = _POSTURE_INDEX[prev]
    ti = _POSTURE_INDEX[target]
    if ti <= pi:
        return target
    step = min(max_steps, ti - pi)
    return POSTURE_ORDER[pi + step]


def _risk_to_posture(risk_score: float) -> str:
    # Conservative banding. Tune only with evidence + tests.
    if risk_score >= 85:
        return "NATIONAL_COMMAND_ALERT"
    if risk_score >= 70:
        return "WING_COMMANDER_ALERT"
    if risk_score >= 55:
        return "UNIT_COMMANDER_ALERT"
    if risk_score >= 35:
        return "DUTY_OFFICER_NOTIFY"
    return "ROUTINE_MONITORING"


def _confidence_norm(conf: Optional[str]) -> str:
    if not conf:
        return "UNKNOWN"
    c = str(conf).strip().upper()
    if c in {"LOW", "MEDIUM", "HIGH"}:
        return c
    return "UNKNOWN"


@dataclass(frozen=True)
class EscalationResult:
    posture: str
    cap_applied: bool
    allowed_jump_steps: int
    deescalation_blocked: bool
    reasons: Dict[str, Any]


def compute_posture(
    *,
    trust_score: float,
    risk_score: float,
    confidence: Optional[str],
    degraded: bool,
    ambiguity_flags: Optional[list],
    previous_posture: Optional[str] = None,
) -> EscalationResult:
    """
    Compute posture with hardening controls.

    Rules:
    - Base posture derived from risk_score.
    - If degraded or confidence LOW/UNKNOWN or ambiguity exists -> cap at DUTY_OFFICER_NOTIFY (bounded statement).
    - Limit escalation per step to at most +2 posture levels (jump limiter).
    - Prevent oscillation: do not de-escalate unless conditions are clean (HIGH confidence, not degraded, no ambiguity).
    """

    prev = _clamp_posture(previous_posture or "ROUTINE_MONITORING")
    conf = _confidence_norm(confidence)
    flags = ambiguity_flags or []
    has_ambiguity = len(flags) > 0

    base = _risk_to_posture(float(risk_score))
    cap_applied = False

    # --- Cap logic (bounded under ambiguity / degraded / low confidence) ---
    cap_posture = "DUTY_OFFICER_NOTIFY"
    if degraded or conf in {"LOW", "UNKNOWN"} or has_ambiguity:
        capped = _min_posture(base, cap_posture)
        cap_applied = (capped != base)
        target = capped
    else:
        target = base

    # --- Jump limiter (no ROUTINE→NATIONAL in one step) ---
    # max_steps=2 means: ROUTINE→UNIT max in a single evaluation
    allowed_jump_steps = 2

    # Emergency override is intentionally strict
    emergency_override = (
        (not degraded)
        and (conf == "HIGH")
        and (not has_ambiguity)
        and (float(risk_score) >= 95.0)
        and (float(trust_score) >= 85.0)
    )
    if emergency_override:
        allowed_jump_steps = 4  # allow full jump only under strict override

    # Apply step limiter for upward moves
    stepped = _step_toward(prev, target, allowed_jump_steps)

    # --- Anti-oscillation / hysteresis ---
    # Default: do not de-escalate unless conditions are clean
    clean_for_deescalation = (
        (not degraded)
        and (conf == "HIGH")
        and (not has_ambiguity)
        and (float(risk_score) < 25.0)
        and (float(trust_score) >= 70.0)
    )

    deescalation_blocked = False
    if _POSTURE_INDEX[stepped] < _POSTURE_INDEX[prev] and not clean_for_deescalation:
        stepped = prev
        deescalation_blocked = True

    reasons: Dict[str, Any] = {
        "inputs": {
            "trust_score": float(trust_score),
            "risk_score": float(risk_score),
            "confidence": conf,
            "degraded": bool(degraded),
            "ambiguity_flags": list(flags),
            "previous_posture": prev,
        },
        "base_posture": base,
        "target_posture": target,
        "step_limited_posture": stepped,
        "cap_posture": cap_posture,
        "emergency_override": emergency_override,
        "clean_for_deescalation": clean_for_deescalation,
    }

    return EscalationResult(
        posture=stepped,
        cap_applied=cap_applied,
        allowed_jump_steps=allowed_jump_steps,
        deescalation_blocked=deescalation_blocked,
        reasons=reasons,
    )

