"""
nuclear_decision_card.py

Commander-safe nuclear decision card (TRAINING / SAFE)
- Produces a bounded, ambiguity-aware "decision card" from synthetic metrics.
- Caps escalation posture under ambiguity (prevents over-escalation when inputs are missing/degraded/contested).
- Writes latest + stamped JSON/TXT artifacts.

Outputs:
- docs/decision_cards/nuclear_decision_card_latest.json
- docs/decision_cards/nuclear_decision_card_latest.txt
- docs/decision_cards/nuclear_decision_card_<timestamp>.json
- docs/decision_cards/nuclear_decision_card_<timestamp>.txt
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


DECISION_DIR = Path("docs") / "decision_cards"


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


def _coerce_float(x: Any, default: float = 0.0) -> float:
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default


def _normalize_alerts(alerts: Optional[Dict[str, Any]]) -> Dict[str, int]:
    a = alerts or {}

    def _i(v: Any) -> int:
        try:
            return int(v)
        except Exception:
            return 0

    crit = _i(a.get("crit", 0))
    high = _i(a.get("high", 0))
    anomaly = _i(a.get("anomaly", 0))
    attack_like = _i(a.get("attack_like", 0))
    total = _i(a.get("total", crit + high + anomaly + attack_like))
    return {
        "total": total,
        "crit": crit,
        "high": high,
        "anomaly": anomaly,
        "attack_like": attack_like,
    }


def _risk_band(risk_score: float) -> str:
    # Bounded bands (do not imply certainty)
    if risk_score >= 80:
        return "SEVERE"
    if risk_score >= 60:
        return "ELEVATED"
    if risk_score >= 40:
        return "GUARDED"
    if risk_score >= 20:
        return "WATCH"
    return "BASELINE"


def _confidence_label(*, trust_score: Optional[float], degraded: bool, ambiguity_flags: list[str]) -> str:
    # Conservative confidence heuristic.
    if degraded or ambiguity_flags:
        return "LOW"
    if trust_score is None:
        return "LOW"
    if trust_score >= 90:
        return "HIGH"
    if trust_score >= 75:
        return "MEDIUM"
    return "LOW"


def _fmt_metric(value: Optional[float], *, ambiguity_flags: list[str]) -> str:
    """
    Avoid producing fake numeric certainty under ambiguity.
    If we are missing signals or in contested conditions, treat 0.0 as potentially "unknown"
    (many pipelines default missing to 0).
    """
    if value is None:
        return "UNKNOWN"
    if ambiguity_flags and abs(float(value)) < 1e-9:
        return "UNKNOWN"
    return f"{float(value):.2f}"


def _bounded_statement(
    *,
    posture: str,
    confidence: str,
    risk_band: str,
    trust_score: Optional[float],
    risk_score: Optional[float],
    ambiguity_flags: list[str],
) -> list[str]:
    trust_txt = _fmt_metric(trust_score, ambiguity_flags=ambiguity_flags)
    risk_txt = _fmt_metric(risk_score, ambiguity_flags=ambiguity_flags)

    lines = [
        f"System posture is {posture} with confidence={confidence}.",
        f"Risk is assessed in a bounded band (risk_score={risk_txt}).",
        f"Trust is bounded (trust_score={trust_txt}); interpretation remains probabilistic.",
    ]
    if ambiguity_flags:
        lines.append(f"Ambiguity flags: {', '.join(ambiguity_flags)}.")
    return lines


def _call_recommend_escalation_flex(
    *,
    trust_score: float,
    risk_score: float,
    alerts: Dict[str, int],
    degraded: bool,
    ambiguity_flags: list[str],
) -> Dict[str, Any]:
    """
    recommend_escalation() has been refactored a few times in your repo.
    This wrapper calls it safely across common signatures.
    """
    try:
        from escalation_ladder import recommend_escalation  # type: ignore
    except Exception as e:
        return {
            "posture": "DUTY_OFFICER_NOTIFY",
            "confidence": "LOW",
            "reason": f"Escalation engine unavailable: {e.__class__.__name__}: {e}",
        }

    attempts: list[Tuple[Dict[str, Any], str]] = [
        (
            {
                "trust_score": trust_score,
                "risk_score": risk_score,
                "alerts": alerts,
                "degraded": degraded,
                "ambiguity_flags": ambiguity_flags,
            },
            "trust,risk,alerts,degraded,ambiguity_flags",
        ),
        (
            {"trust_score": trust_score, "risk_score": risk_score, "alerts": alerts, "degraded": degraded},
            "trust,risk,alerts,degraded",
        ),
        (
            {"trust_score": trust_score, "risk_score": risk_score, "alerts": alerts},
            "trust,risk,alerts",
        ),
        (
            {"trust_score": trust_score, "risk_score": risk_score},
            "trust,risk",
        ),
    ]

    last_err: Optional[Exception] = None
    for kwargs, _sig in attempts:
        try:
            res = recommend_escalation(**kwargs)  # type: ignore
            if isinstance(res, dict):
                return res
            posture = getattr(res, "posture", None)
            conf = getattr(res, "confidence", None)
            reason = getattr(res, "reason", None) or getattr(res, "reasoning", None)
            return {
                "posture": posture or "DUTY_OFFICER_NOTIFY",
                "confidence": conf or "LOW",
                "reason": reason or "",
            }
        except Exception as e:
            last_err = e

    return {
        "posture": "DUTY_OFFICER_NOTIFY",
        "confidence": "LOW",
        "reason": f"Escalation engine call failed: {last_err.__class__.__name__}: {last_err}",
    }


def _dedupe_flags(flags: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for f in flags:
        if f and f not in seen:
            out.append(f)
            seen.add(f)
    return out


def build_decision_card(
    *,
    trust_score: Optional[float],
    risk_score: Optional[float],
    alerts: Optional[Dict[str, Any]] = None,
    degraded: bool = False,
    comms_state: Optional[str] = None,
    radiation_usv: Optional[float] = None,
    seismic_mag: Optional[float] = None,
    ems_state: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build the commander-safe decision card.

    Under ambiguity (missing/degraded/contested):
    - Confidence is LOW
    - Escalation posture is capped to DUTY_OFFICER_NOTIFY
    """
    a = _normalize_alerts(alerts)

    trust = None if trust_score is None else _coerce_float(trust_score, 0.0)
    risk = None if risk_score is None else _coerce_float(risk_score, 0.0)

    ambiguity_flags: list[str] = []

    # Core degraded flag
    if degraded:
        ambiguity_flags.append("DEGRADED_OPS")

    # Missing signals
    if comms_state is None:
        ambiguity_flags.append("MISSING_COMMS_STATE")
    if radiation_usv is None:
        ambiguity_flags.append("MISSING_RADIATION_uSv")
    if seismic_mag is None:
        ambiguity_flags.append("MISSING_SEISMIC_MAG")
    if ems_state is None:
        ambiguity_flags.append("MISSING_EMS_STATE")

    # Contested/noisy environment flags (THIS is what your stress expects)
    if ems_state is not None:
        ems_u = str(ems_state).upper().strip()
        if ems_u in {"NOISY", "JAMMED", "CONTESTED", "DEGRADED"}:
            ambiguity_flags.append("EMS_CONTESTED")

    if comms_state is not None:
        comms_u = str(comms_state).upper().strip()
        if comms_u not in {"OK", "UP", "NORMAL"}:
            ambiguity_flags.append("COMMS_CONTESTED")

    # Alert context can imply ambiguity even when sensors exist (bounded)
    if a.get("anomaly", 0) > 0 or a.get("attack_like", 0) > 0:
        ambiguity_flags.append("ALERT_ANOMALY_CONTEXT")

    # Aggregate missing
    if any(flag.startswith("MISSING_") for flag in ambiguity_flags):
        ambiguity_flags.append("MISSING_SIGNALS")

    ambiguity_flags = _dedupe_flags(ambiguity_flags)

    confidence = _confidence_label(trust_score=trust, degraded=degraded, ambiguity_flags=ambiguity_flags)
    band = _risk_band(risk if risk is not None else 0.0)

    escalation = _call_recommend_escalation_flex(
        trust_score=trust if trust is not None else 0.0,
        risk_score=risk if risk is not None else 0.0,
        alerts=a,
        degraded=degraded,
        ambiguity_flags=ambiguity_flags,
    )

    posture = str(escalation.get("posture", "DUTY_OFFICER_NOTIFY"))

    # 🔒 Escalation cap under ambiguity (hard safety)
    if ambiguity_flags and posture not in {"ROUTINE_MONITORING", "DUTY_OFFICER_NOTIFY"}:
        posture = "DUTY_OFFICER_NOTIFY"

    card: Dict[str, Any] = {
        "generated_at": _utc_now_iso(),
        "safe_notice": "Synthetic decision-support output (training/demo). Not real missile telemetry.",
        "inputs": {
            "trust_score": trust_score,
            "risk_score": risk_score,
            "alerts": a,
            "degraded": degraded,
            "comms_state": comms_state,
            "radiation_usv": radiation_usv,
            "seismic_mag": seismic_mag,
            "ems_state": ems_state,
        },
        "status": {
            "degraded": degraded,
            "confidence": confidence,
            "risk_band": band,
            "ambiguity_flags": ambiguity_flags,
        },
        "escalation": {
            "posture": posture,
            "reason": escalation.get("reason") or escalation.get("reasoning") or "",
            "confidence": escalation.get("confidence", confidence),
        },
        "what_we_can_say": _bounded_statement(
            posture=posture,
            confidence=confidence,
            risk_band=band,
            trust_score=trust,
            risk_score=risk,
            ambiguity_flags=ambiguity_flags,
        ),
    }

    return card


def write_decision_card(card: Dict[str, Any]) -> Dict[str, str]:
    _safe_mkdir(DECISION_DIR)
    stamped = _ts()

    json_latest = DECISION_DIR / "nuclear_decision_card_latest.json"
    txt_latest = DECISION_DIR / "nuclear_decision_card_latest.txt"

    json_stamped = DECISION_DIR / f"nuclear_decision_card_{stamped}.json"
    txt_stamped = DECISION_DIR / f"nuclear_decision_card_{stamped}.txt"

    _write_json(json_latest, card)
    _write_json(json_stamped, card)
    _write_txt(txt_latest, _render_txt(card))
    _write_txt(txt_stamped, _render_txt(card))

    return {
        "json_latest": str(json_latest),
        "txt_latest": str(txt_latest),
        "json_stamped": str(json_stamped),
        "txt_stamped": str(txt_stamped),
    }


def _render_txt(card: Dict[str, Any]) -> str:
    esc = card.get("escalation", {}) if isinstance(card.get("escalation"), dict) else {}
    status = card.get("status", {}) if isinstance(card.get("status"), dict) else {}
    what = card.get("what_we_can_say", [])
    if not isinstance(what, list):
        what = [str(what)]

    lines: list[str] = []
    lines.append("GLL Nuclear Decision Card (SAFE/TRAINING)")
    lines.append(f"Generated: {card.get('generated_at', '')}")
    lines.append("")
    lines.append(f"Posture: {esc.get('posture', 'DUTY_OFFICER_NOTIFY')}")
    lines.append(f"Confidence: {status.get('confidence', 'LOW')}")
    lines.append(f"Risk band: {status.get('risk_band', 'BASELINE')}")
    lines.append("")

    flags = status.get("ambiguity_flags", [])
    if isinstance(flags, list) and flags:
        lines.append("Ambiguity flags:")
        for f in flags:
            lines.append(f"  - {f}")
        lines.append("")

    reason = esc.get("reason", "")
    if reason:
        lines.append("Escalation reason (bounded):")
        lines.append(f"  {reason}")
        lines.append("")

    lines.append("What we can say (bounded):")
    for w in what:
        lines.append(f"- {w}")

    return "\n".join(lines)

