"""
nuclear_decision_card.py

Commander-grade decision card for nuclear/ISR watch contexts.

Design goals (Week-1 hardening):
- Never crash under missing/partial data
- Explicit ambiguity handling + confidence
- Clear recommendations + bounded language
- Safe outputs (synthetic-friendly)
- Writes latest + stamped artifacts

Public API:
- build_decision_card(...)
- write_decision_card(...)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


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


def _confidence_band(trust_score: float, degraded: bool, missing_signals: int) -> str:
    """
    Simple, bounded confidence rubric.
    We want consistent commander language, not vibes.
    """
    base = trust_score
    if degraded:
        base -= 10
    base -= min(20, missing_signals * 5)

    if base >= 85:
        return "HIGH"
    if base >= 70:
        return "MEDIUM"
    if base >= 55:
        return "LOW"
    return "VERY_LOW"


def _risk_band(risk_score: float) -> str:
    if risk_score >= 85:
        return "SEVERE"
    if risk_score >= 65:
        return "ELEVATED"
    if risk_score >= 40:
        return "GUARDED"
    return "NORMAL"


def _derive_missing_signals(
    *,
    comms_state: Optional[str],
    radiation_usv: Optional[float],
    seismic_mag: Optional[float],
    ems_state: Optional[str],
) -> int:
    missing = 0
    if comms_state is None:
        missing += 1
    if radiation_usv is None:
        missing += 1
    if seismic_mag is None:
        missing += 1
    if ems_state is None:
        missing += 1
    return missing


def build_decision_card(
    *,
    trust_score: Any,
    risk_score: Any,
    alerts: Optional[Dict[str, Any]] = None,
    degraded: bool = False,
    scenario: str = "Synthetic / Training",
    comms_state: Optional[str] = None,
    radiation_usv: Optional[Any] = None,
    seismic_mag: Optional[Any] = None,
    ems_state: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a commander-ready decision card object.
    """

    trust = _coerce_float(trust_score, 0.0)
    risk = _coerce_float(risk_score, 0.0)
    a = _norm_alerts(alerts)

    rad = None if radiation_usv is None else _coerce_float(radiation_usv, 0.0)
    mag = None if seismic_mag is None else _coerce_float(seismic_mag, 0.0)

    missing = _derive_missing_signals(
        comms_state=comms_state,
        radiation_usv=rad,
        seismic_mag=mag,
        ems_state=ems_state,
    )

    confidence = _confidence_band(trust, degraded, missing)
    risk_band = _risk_band(risk)

    # bounded, commander language – never overclaim
    ambiguity_flags = []
    if degraded:
        ambiguity_flags.append("DEGRADED_OPS")
    if missing > 0:
        ambiguity_flags.append("MISSING_SIGNALS")
    if trust < 70:
        ambiguity_flags.append("LOW_TRUST")
    if a["crit"] > 0:
        ambiguity_flags.append("CRIT_ALERTS_PRESENT")

    key_judgment = (
        "No immediate indicators of confirmed nuclear event."
        if risk < 65 and a["crit"] == 0
        else "Elevated indicators require increased scrutiny."
    )

    # action recommendations: always give next steps
    actions = []
    if confidence in {"VERY_LOW", "LOW"}:
        actions.append("Increase collection: restore missing sensors / verify data feed continuity.")
        actions.append("Run baseline vs injected validation to confirm system behavior is bounded.")
    if risk_band in {"ELEVATED", "SEVERE"} or a["crit"] > 0:
        actions.append("Escalate watch posture and notify duty leadership per local SOP.")
        actions.append("Cross-check independent sources; do not rely on single-domain indicators.")
    if not actions:
        actions.append("Maintain current watch posture; continue monitoring at normal cadence.")

    # what we know / don't know
    known = []
    unknown = []

    known.append(f"Trust score: {trust:.1f} (proxy)")
    known.append(f"Risk score: {risk:.1f} (proxy)")
    known.append(f"Alerts: crit={a['crit']}, high={a['high']}, attack_like={a['attack_like']}, anomaly={a['anomaly']}")

    if comms_state is not None:
        known.append(f"Comms state: {comms_state}")
    else:
        unknown.append("Comms state unavailable")

    if ems_state is not None:
        known.append(f"EMS state: {ems_state}")
    else:
        unknown.append("EMS state unavailable")

    if rad is not None:
        known.append(f"Radiation uSv (proxy): {rad:.2f}")
    else:
        unknown.append("Radiation uSv unavailable")

    if mag is not None:
        known.append(f"Seismic magnitude (proxy): {mag:.2f}")
    else:
        unknown.append("Seismic magnitude unavailable")

    card = {
        "generated_at_utc": _utc_now_iso(),
        "type": "NUCLEAR_DECISION_CARD",
        "scenario": scenario,
        "safe_notice": "This product may be generated from synthetic telemetry for training/demos.",
        "status": {
            "degraded": bool(degraded),
            "confidence": confidence,
            "risk_band": risk_band,
            "ambiguity_flags": ambiguity_flags,
        },
        "key_judgment": key_judgment,
        "recommendations": actions,
        "signals": {
            "trust_score": trust,
            "risk_score": risk,
            "alerts": a,
            "comms_state": comms_state,
            "ems_state": ems_state,
            "radiation_usv": rad,
            "seismic_mag": mag,
            "missing_signal_count": missing,
        },
        "knowns": known,
        "unknowns": unknown,
        "notes": notes or "",
    }

    return card


def _render_txt(card: Dict[str, Any]) -> str:
    s = card.get("status", {})
    sig = card.get("signals", {})
    alerts = (sig.get("alerts") or {})

    lines = []
    lines.append("GLL — NUCLEAR DECISION CARD")
    lines.append(f"Generated (UTC): {card.get('generated_at_utc', '')}")
    lines.append(f"Scenario: {card.get('scenario', '')}")
    lines.append("")
    lines.append(f"Confidence: {s.get('confidence','')}")
    lines.append(f"Risk Band:  {s.get('risk_band','')}")
    lines.append(f"Degraded:   {s.get('degraded', False)}")
    lines.append(f"Flags:      {', '.join(s.get('ambiguity_flags', []) or [])}")
    lines.append("")
    lines.append("Key Judgment:")
    lines.append(f"- {card.get('key_judgment','')}")
    lines.append("")
    lines.append("Signals (proxy):")
    lines.append(f"- Trust: {sig.get('trust_score', 0)}")
    lines.append(f"- Risk:  {sig.get('risk_score', 0)}")
    lines.append(
        f"- Alerts: crit={alerts.get('crit',0)} high={alerts.get('high',0)} "
        f"attack_like={alerts.get('attack_like',0)} anomaly={alerts.get('anomaly',0)}"
    )
    lines.append(f"- Missing signals: {sig.get('missing_signal_count', 0)}")
    lines.append("")
    lines.append("Recommendations:")
    for r in card.get("recommendations", []) or []:
        lines.append(f"- {r}")
    lines.append("")
    lines.append("Knowns:")
    for k in card.get("knowns", []) or []:
        lines.append(f"- {k}")
    lines.append("")
    lines.append("Unknowns:")
    for u in card.get("unknowns", []) or []:
        lines.append(f"- {u}")
    if card.get("notes"):
        lines.append("")
        lines.append("Notes:")
        lines.append(card.get("notes", ""))

    return "\n".join(lines).strip() + "\n"


def write_decision_card(card: Dict[str, Any]) -> Dict[str, str]:
    """
    Writes latest + stamped artifacts.
    """
    _safe_mkdir(DECISION_DIR)
    json_latest = DECISION_DIR / "nuclear_decision_card_latest.json"
    txt_latest = DECISION_DIR / "nuclear_decision_card_latest.txt"

    stamped = _ts()
    json_stamped = DECISION_DIR / f"nuclear_decision_card_{stamped}.json"
    txt_stamped = DECISION_DIR / f"nuclear_decision_card_{stamped}.txt"

    _write_json(json_latest, card)
    _write_json(json_stamped, card)
    _safe_mkdir(txt_latest.parent)
    txt_latest.write_text(_render_txt(card), encoding="utf-8")
    txt_stamped.write_text(_render_txt(card), encoding="utf-8")

    return {
        "json_latest": str(json_latest),
        "txt_latest": str(txt_latest),
        "json_stamped": str(json_stamped),
        "txt_stamped": str(txt_stamped),
    }

