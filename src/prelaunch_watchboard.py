"""
prelaunch_watchboard.py

Week-1 Nuclear/AFTAC Hardening (SAFE):
Produces a commander-facing "pre-launch watchboard" from *synthetic* / training telemetry.

Design goals:
- Bounded statements only (no overclaiming)
- Explicit unknowns/missing signals
- Clear posture + confidence under ambiguity
- Collection/validation next steps (training-safe)

Outputs:
- docs/nuclear/prelaunch_watchboard_latest.json
- docs/nuclear/prelaunch_watchboard_latest.txt
- stamped versions with timestamp
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from nuclear_decision_card import build_decision_card
from escalation_ladder import compute_posture


OUT_DIR = Path("docs") / "nuclear"


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


def _norm_alerts(alerts: Optional[Dict[str, Any]]) -> Dict[str, int]:
    a = alerts or {}
    def _i(x: Any) -> int:
        try:
            return int(x)
        except Exception:
            return 0
    return {
        "crit": _i(a.get("crit", 0)),
        "high": _i(a.get("high", 0)),
        "attack_like": _i(a.get("attack_like", 0)),
        "anomaly": _i(a.get("anomaly", 0)),
        "total": _i(a.get("total", 0)),
    }


def _missing_flags(
    *,
    comms_state: Optional[str],
    radiation_usv: Optional[float],
    seismic_mag: Optional[float],
    ems_state: Optional[str],
) -> List[str]:
    flags: List[str] = []
    if comms_state is None:
        flags.append("MISSING_COMMS_STATE")
    if radiation_usv is None:
        flags.append("MISSING_RADIATION_USV")
    if seismic_mag is None:
        flags.append("MISSING_SEISMIC_MAG")
    if ems_state is None:
        flags.append("MISSING_EMS_STATE")
    return flags


def _bounded_statements(card: Dict[str, Any], posture: str) -> List[str]:
    st: List[str] = []
    status = card.get("status", {}) if isinstance(card.get("status"), dict) else {}
    conf = status.get("confidence", "UNKNOWN")
    risk_band = status.get("risk_band", "UNKNOWN")
    degraded = bool(status.get("degraded", False))
    amb = status.get("ambiguity_flags", [])
    amb = amb if isinstance(amb, list) else []

    # Always bounded, always probability language.
    st.append(f"System posture is {posture} with confidence={conf}.")
    st.append(f"Risk is assessed in a bounded band (risk_band={risk_band}).")

    if degraded or amb:
        st.append("Interpretation remains probabilistic due to degraded operations and/or ambiguity flags.")
    else:
        st.append("Interpretation remains probabilistic; no single indicator is decisive.")

    if amb:
        st.append(f"Ambiguity flags present: {', '.join([str(x) for x in amb])}.")

    return st


def _cannot_say(card: Dict[str, Any]) -> List[str]:
    status = card.get("status", {}) if isinstance(card.get("status"), dict) else {}
    amb = status.get("ambiguity_flags", [])
    amb = amb if isinstance(amb, list) else []
    missing = []
    for f in amb:
        if str(f).startswith("MISSING_"):
            missing.append(str(f).replace("MISSING_", "").lower())

    cannot: List[str] = []
    if missing:
        cannot.append("Cannot assert signal-specific conclusions due to missing inputs: " + ", ".join(missing) + ".")
    cannot.append("Cannot infer intent; this product only summarizes bounded risk/trust posture from synthetic telemetry.")
    return cannot


def _next_actions(card: Dict[str, Any]) -> List[str]:
    # Training-safe “collection actions” (generic, non-sensitive)
    status = card.get("status", {}) if isinstance(card.get("status"), dict) else {}
    amb = status.get("ambiguity_flags", [])
    amb = amb if isinstance(amb, list) else []

    actions: List[str] = []
    if "MISSING_SIGNALS" in amb:
        actions.append("Request missing sensor inputs (training-safe): comms_state, radiation_usv, seismic_mag, ems_state.")
    if "DEGRADED_OPS" in amb:
        actions.append("Re-run validation at INTERMEDIATE baseline (no injection) to confirm bounded behavior.")
    actions.append("Run ambiguity stress + escalation consistency checks to prevent posture instability.")
    actions.append("If posture persists ≥ UNIT_COMMANDER_ALERT for 2 consecutive cycles, trigger an operator review session.")
    return actions


def build_prelaunch_watchboard(
    *,
    trust_score: float,
    risk_score: float,
    alerts: Optional[Dict[str, Any]] = None,
    degraded: bool = False,
    comms_state: Optional[str] = None,
    radiation_usv: Optional[float] = None,
    seismic_mag: Optional[float] = None,
    ems_state: Optional[str] = None,
    previous_posture: Optional[str] = None,
) -> Dict[str, Any]:
    alerts_n = _norm_alerts(alerts)

    # Decision card is the nucleus of bounded posture under ambiguity
    card = build_decision_card(
        trust_score=trust_score,
        risk_score=risk_score,
        alerts={"crit": alerts_n["crit"], "high": alerts_n["high"], "anomaly": alerts_n["anomaly"]},
        degraded=degraded,
        comms_state=comms_state,
        radiation_usv=radiation_usv,
        seismic_mag=seismic_mag,
        ems_state=ems_state,
    )

    status = card.get("status", {}) if isinstance(card.get("status"), dict) else {}
    confidence = status.get("confidence", "UNKNOWN")
    ambiguity_flags = status.get("ambiguity_flags", [])
    ambiguity_flags = ambiguity_flags if isinstance(ambiguity_flags, list) else []
    ambiguity_flags = list(ambiguity_flags) + _missing_flags(
        comms_state=comms_state,
        radiation_usv=radiation_usv,
        seismic_mag=seismic_mag,
        ems_state=ems_state,
    )

    # Escalation ladder hardened (monotonic, capped, anti-oscillation)
    esc = compute_posture(
        trust_score=trust_score,
        risk_score=risk_score,
        confidence=confidence,
        degraded=degraded,
        ambiguity_flags=ambiguity_flags,
        previous_posture=previous_posture,
    )

    watchboard = {
        "generated_at": _utc_now_iso(),
        "safe_notice": "This watchboard is generated from synthetic telemetry and is safe for training/demos.",
        "inputs": {
            "trust_score": float(trust_score),
            "risk_score": float(risk_score),
            "alerts": alerts_n,
            "degraded": bool(degraded),
            "signals": {
                "comms_state": comms_state,
                "radiation_usv": radiation_usv,
                "seismic_mag": seismic_mag,
                "ems_state": ems_state,
            },
            "previous_posture": previous_posture,
        },
        "decision_card": card,
        "escalation": {
            "posture": esc.posture,
            "cap_applied": esc.cap_applied,
            "allowed_jump_steps": esc.allowed_jump_steps,
            "deescalation_blocked": esc.deescalation_blocked,
        },
        "brief": {
            "what_we_can_say": _bounded_statements(card, esc.posture),
            "what_we_cannot_say": _cannot_say(card),
            "unknowns": list(sorted(set([f for f in ambiguity_flags if str(f).startswith("MISSING_")]))),
            "recommended_next_actions": _next_actions(card),
        },
    }
    return watchboard


def write_prelaunch_watchboard(wb: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = _ts()

    json_latest = OUT_DIR / "prelaunch_watchboard_latest.json"
    txt_latest = OUT_DIR / "prelaunch_watchboard_latest.txt"
    json_stamped = OUT_DIR / f"prelaunch_watchboard_{ts}.json"
    txt_stamped = OUT_DIR / f"prelaunch_watchboard_{ts}.txt"

    _write_json(json_latest, wb)
    _write_json(json_stamped, wb)
    _write_txt(txt_latest, render_watchboard_txt(wb))
    _write_txt(txt_stamped, render_watchboard_txt(wb))

    return {
        "json_latest": str(json_latest),
        "txt_latest": str(txt_latest),
        "json_stamped": str(json_stamped),
        "txt_stamped": str(txt_stamped),
    }


def render_watchboard_txt(wb: Dict[str, Any]) -> str:
    esc = wb.get("escalation", {}) if isinstance(wb.get("escalation"), dict) else {}
    brief = wb.get("brief", {}) if isinstance(wb.get("brief"), dict) else {}
    card = wb.get("decision_card", {}) if isinstance(wb.get("decision_card"), dict) else {}
    status = card.get("status", {}) if isinstance(card.get("status"), dict) else {}

    lines: List[str] = []
    lines.append("GLL PRE-LAUNCH WATCHBOARD (TRAINING SAFE)")
    lines.append("=" * 46)
    lines.append(f"Generated: {wb.get('generated_at')}")
    lines.append(f"Posture: {esc.get('posture')}  |  Confidence: {status.get('confidence')}  |  Risk band: {status.get('risk_band')}")
    lines.append(f"Degraded: {status.get('degraded')}  |  Cap applied: {esc.get('cap_applied')}  |  De-escalation blocked: {esc.get('deescalation_blocked')}")
    lines.append("")
    lines.append("WHAT WE CAN SAY (BOUNDED):")
    for s in brief.get("what_we_can_say", []) or []:
        lines.append(f"- {s}")
    lines.append("")
    lines.append("WHAT WE CANNOT SAY:")
    for s in brief.get("what_we_cannot_say", []) or []:
        lines.append(f"- {s}")
    lines.append("")
    lines.append("UNKNOWNS / MISSING:")
    for u in brief.get("unknowns", []) or []:
        lines.append(f"- {u}")
    lines.append("")
    lines.append("RECOMMENDED NEXT ACTIONS:")
    for a in brief.get("recommended_next_actions", []) or []:
        lines.append(f"- {a}")
    lines.append("")
    return "\n".join(lines)

