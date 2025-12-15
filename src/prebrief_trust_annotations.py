"""
prebrief_trust_annotations.py

Commander-trust artifact for Week-1 Nuclear/AFTAC hardening.

Purpose:
- Convert latest nuclear decision card + escalation ladder into a pre-brief packet:
  * What we can say (bounded claims)
  * What we cannot say (forbidden claims)
  * Known unknowns / ambiguity drivers
  * What we need next (collection tasks)
  * Comms language to use (no over-claiming)

Inputs (best-effort; safe if missing):
- docs/decision_cards/nuclear_decision_card_latest.json
- docs/nuclear/escalation_ladder_latest.json

Outputs:
- docs/briefs/prebrief_trust_annotations_latest.json
- docs/briefs/prebrief_trust_annotations_latest.txt
- docs/briefs/prebrief_trust_annotations_<timestamp>.json
- docs/briefs/prebrief_trust_annotations_<timestamp>.txt
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


DECISION_CARD_LATEST = Path("docs") / "decision_cards" / "nuclear_decision_card_latest.json"
ESCALATION_LATEST = Path("docs") / "nuclear" / "escalation_ladder_latest.json"
BRIEFS_DIR = Path("docs") / "briefs"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        if not path.exists():
            return {}
        raw = path.read_text(encoding="utf-8")
        obj = json.loads(raw)
        if isinstance(obj, dict):
            return obj
        return {}
    except Exception:
        return {}


def _write_json(path: Path, obj: Any) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _write_txt(path: Path, text: str) -> None:
    _safe_mkdir(path.parent)
    path.write_text(text, encoding="utf-8")


def _coerce_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _coerce_int(x: Any, default: int = 0) -> int:
    try:
        return int(x)
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


def _extract_signals(card: Dict[str, Any]) -> Dict[str, Any]:
    sig = card.get("signals") or {}
    if not isinstance(sig, dict):
        sig = {}
    # missing count is already computed inside decision card (if present)
    return {
        "comms_state": sig.get("comms_state", None),
        "ems_state": sig.get("ems_state", None),
        "radiation_usv": sig.get("radiation_usv", None),
        "seismic_mag": sig.get("seismic_mag", None),
        "missing_signal_count": _coerce_int(sig.get("missing_signal_count", 0)),
    }


def _compose_claims(
    *,
    trust_score: float,
    risk_score: float,
    confidence: str,
    degraded: bool,
    alerts: Dict[str, int],
    missing_signal_count: int,
    posture: str,
) -> Dict[str, List[str]]:
    """
    Bounded language rules.
    """
    can_say: List[str] = []
    cannot_say: List[str] = []

    # Baseline safe claims
    can_say.append(f"System posture is {posture} with confidence={confidence}.")
    can_say.append(f"Risk is assessed in a bounded band (risk_score={risk_score:.2f}).")
    can_say.append(f"Trust is bounded (trust_score={trust_score:.2f}); interpretation remains probabilistic.")

    if degraded or missing_signal_count > 0:
        can_say.append("Operating under degraded/ambiguous conditions; prioritizing verification and signal restoration.")

    # Alerts framing
    if alerts["crit"] > 0:
        can_say.append("CRIT-level alerts present; immediate verification and escalation per SOP is warranted.")
    elif alerts["high"] > 0:
        can_say.append(f"HIGH-level alert pressure present (high={alerts['high']}); treat as a watch condition pending corroboration.")
    else:
        can_say.append("No CRIT alerts present; escalation is driven by bounded risk + corroboration, not single indicators.")

    # Forbidden claims
    cannot_say.append("We confirm a real-world event occurred (not supported by this product).")
    cannot_say.append("This is a confirmed launch/detonation/attack (requires independent confirmation).")
    cannot_say.append("Single-source certainty (no single signal is treated as proof).")

    if degraded or missing_signal_count > 0:
        cannot_say.append("We have complete sensor coverage (we do not).")
        cannot_say.append("We can assign attribution or intent from degraded signals alone.")

    if alerts["crit"] == 0 and risk_score < 65:
        cannot_say.append("This requires leadership notification solely due to ambiguity (ambiguity triggers collection posture first).")

    return {"claims_allowed": can_say, "claims_forbidden": cannot_say}


def _compose_unknowns_and_tasks(
    *,
    signals: Dict[str, Any],
    ambiguity_flags: List[str],
    degraded: bool,
    posture: str,
) -> Dict[str, List[str]]:
    unknowns: List[str] = []
    tasks: List[str] = []

    missing = _coerce_int(signals.get("missing_signal_count", 0))
    if degraded:
        unknowns.append("Degraded operations mode active; signal quality may be reduced.")
    if missing > 0:
        unknowns.append(f"Missing signals detected (count={missing}); domain confidence is reduced.")

    for f in ambiguity_flags:
        unknowns.append(f"Ambiguity flag: {f}")

    # Collection tasks keyed to posture
    tasks.append("Run baseline vs injected validation and review delta_vs_baseline for expected directional changes.")
    tasks.append("Verify sensor health and pipeline integrity (SIS+SPS).")

    if signals.get("comms_state") is None:
        tasks.append("Restore COMMS state telemetry or corroborate via independent comms monitoring.")
    if signals.get("radiation_usv") is None:
        tasks.append("Restore radiation telemetry; verify sensor calibration and data freshness.")
    if signals.get("seismic_mag") is None:
        tasks.append("Restore seismic magnitude telemetry; verify timing alignment and noise floor.")
    if signals.get("ems_state") is None:
        tasks.append("Restore EMS state telemetry; verify interference/noise classification.")

    if posture in {"HEIGHTENED_COLLECTION", "DUTY_OFFICER_NOTIFY", "CRISIS_ACTION_TEAM"}:
        tasks.append("Perform a second-analyst review before any narrative is briefed upward.")
        tasks.append("Prepare an update window/timebox for next check-in (avoid continuous escalation without new data).")

    return {"known_unknowns": unknowns, "collection_tasks": tasks}


def build_prebrief_trust_annotations() -> Dict[str, Any]:
    card = _read_json(DECISION_CARD_LATEST)
    esc = _read_json(ESCALATION_LATEST)

    status = card.get("status") or {}
    if not isinstance(status, dict):
        status = {}

    alerts = _norm_alerts(card.get("alerts") if isinstance(card.get("alerts"), dict) else (card.get("inputs") or {}).get("alerts"))
    signals = _extract_signals(card)

    trust_score = _coerce_float((card.get("inputs") or {}).get("trust_score", status.get("trust_score", 0.0)), 0.0)
    risk_score = _coerce_float((card.get("inputs") or {}).get("risk_score", status.get("risk_score", 0.0)), 0.0)
    degraded = bool((card.get("inputs") or {}).get("degraded", status.get("degraded", False)))

    confidence = str(status.get("confidence", "UNKNOWN")).upper()
    risk_band = str(status.get("risk_band", "UNKNOWN")).upper()
    ambiguity_flags = status.get("ambiguity_flags") or []
    if not isinstance(ambiguity_flags, list):
        ambiguity_flags = []

    # posture is authoritative from decision card (it already uses escalation ladder)
    posture = "UNKNOWN"
    esc_block = card.get("escalation") or {}
    if isinstance(esc_block, dict):
        posture = str(esc_block.get("posture", "UNKNOWN"))
        cap_applied = bool((esc_block.get("rationale") or {}).get("cap_applied", False))
    else:
        cap_applied = False

    claims = _compose_claims(
        trust_score=trust_score,
        risk_score=risk_score,
        confidence=confidence,
        degraded=degraded,
        alerts=alerts,
        missing_signal_count=_coerce_int(signals.get("missing_signal_count", 0)),
        posture=posture,
    )

    unk = _compose_unknowns_and_tasks(
        signals=signals,
        ambiguity_flags=[str(x) for x in ambiguity_flags],
        degraded=degraded,
        posture=posture,
    )

    comms_language = [
        "Use bounded language: 'assess', 'indicates', 'suggests', 'requires verification'.",
        "Separate observation from inference (what we saw vs what it might mean).",
        "State what would change our posture (specific signals or corroboration).",
    ]
    if cap_applied:
        comms_language.append("Ambiguity cap applied: posture limited to collection until risk/crit thresholds are met.")

    report = {
        "generated_at_utc": _utc_now_iso(),
        "type": "PREBRIEF_TRUST_ANNOTATIONS",
        "safe_notice": "May be generated from synthetic telemetry for training/demos.",
        "sources": {
            "decision_card_latest": str(DECISION_CARD_LATEST),
            "escalation_ladder_latest": str(ESCALATION_LATEST),
        },
        "summary": {
            "posture": posture,
            "confidence": confidence,
            "risk_band": risk_band,
            "degraded": degraded,
            "cap_applied": cap_applied,
            "alerts": alerts,
            "missing_signal_count": _coerce_int(signals.get("missing_signal_count", 0)),
        },
        "signals": signals,
        "annotations": {
            **claims,
            **unk,
            "recommended_comms_language": comms_language,
        },
    }

    return report


def write_prebrief(report: Dict[str, Any]) -> Dict[str, str]:
    _safe_mkdir(BRIEFS_DIR)
    stamped = _ts()

    json_latest = BRIEFS_DIR / "prebrief_trust_annotations_latest.json"
    txt_latest = BRIEFS_DIR / "prebrief_trust_annotations_latest.txt"
    json_stamped = BRIEFS_DIR / f"prebrief_trust_annotations_{stamped}.json"
    txt_stamped = BRIEFS_DIR / f"prebrief_trust_annotations_{stamped}.txt"

    _write_json(json_latest, report)
    _write_json(json_stamped, report)

    s = report.get("summary") or {}
    a = (s.get("alerts") or {})
    lines: List[str] = []
    lines.append("GLL — PRE-BRIEF TRUST ANNOTATIONS (LATEST)")
    lines.append(f"Generated (UTC): {report.get('generated_at_utc','')}")
    lines.append("")
    lines.append("Snapshot:")
    lines.append(f"- Posture: {s.get('posture','')}")
    lines.append(f"- Confidence: {s.get('confidence','')}")
    lines.append(f"- Risk Band: {s.get('risk_band','')}")
    lines.append(f"- Degraded: {s.get('degraded', False)}")
    lines.append(f"- Cap Applied: {s.get('cap_applied', False)}")
    lines.append(
        f"- Alerts: crit={a.get('crit',0)} high={a.get('high',0)} "
        f"attack_like={a.get('attack_like',0)} anomaly={a.get('anomaly',0)}"
    )
    lines.append(f"- Missing Signals: {s.get('missing_signal_count',0)}")
    lines.append("")

    ann = (report.get("annotations") or {})
    lines.append("What we can say (bounded):")
    for x in (ann.get("claims_allowed") or []):
        lines.append(f"- {x}")
    lines.append("")
    lines.append("What we cannot say:")
    for x in (ann.get("claims_forbidden") or []):
        lines.append(f"- {x}")
    lines.append("")
    lines.append("Known unknowns / ambiguity:")
    for x in (ann.get("known_unknowns") or []):
        lines.append(f"- {x}")
    if len((ann.get("known_unknowns") or [])) == 0:
        lines.append("- None flagged.")
    lines.append("")
    lines.append("Collection tasks (next steps):")
    for x in (ann.get("collection_tasks") or []):
        lines.append(f"- {x}")
    lines.append("")
    lines.append("Comms language:")
    for x in (ann.get("recommended_comms_language") or []):
        lines.append(f"- {x}")

    txt = "\n".join(lines).strip() + "\n"
    _write_txt(txt_latest, txt)
    _write_txt(txt_stamped, txt)

    return {
        "json_latest": str(json_latest),
        "txt_latest": str(txt_latest),
        "json_stamped": str(json_stamped),
        "txt_stamped": str(txt_stamped),
    }


if __name__ == "__main__":
    rep = build_prebrief_trust_annotations()
    paths = write_prebrief(rep)
    print("Pre-brief trust annotations written:")
    for k, v in paths.items():
        print(f"  {k}: {v}")
    print("Posture:", (rep.get("summary") or {}).get("posture"))
    print("Cap applied:", (rep.get("summary") or {}).get("cap_applied", False))

