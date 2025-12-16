"""
nuclear_status_summary.py

Week-1 Nuclear Hardening Module:
- Produce a commander-readable "Nuclear Status Summary" from latest artifacts
- Bound statements under ambiguity/degraded inputs
- Write latest + stamped artifacts to docs/nuclear/

Inputs (best-effort):
- docs/decision_cards/nuclear_decision_card_latest.json
- docs/nuclear/prelaunch_watchboard_latest.json
- docs/briefs/prebrief_trust_annotations_latest.json

Outputs:
- docs/nuclear/nuclear_status_summary_latest.json
- docs/nuclear/nuclear_status_summary_latest.txt
- docs/nuclear/nuclear_status_summary_<timestamp>.json
- docs/nuclear/nuclear_status_summary_<timestamp>.txt
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


NUCLEAR_DIR = Path("docs") / "nuclear"
DECISION_CARD_LATEST = Path("docs") / "decision_cards" / "nuclear_decision_card_latest.json"
WATCHBOARD_LATEST = Path("docs") / "nuclear" / "prelaunch_watchboard_latest.json"
PREFBRIEF_LATEST = Path("docs") / "briefs" / "prebrief_trust_annotations_latest.json"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_read_json(path: Path) -> Dict[str, Any]:
    try:
        if not path.exists():
            return {"_missing": True, "_path": str(path)}
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"_error": f"{e.__class__.__name__}: {e}", "_path": str(path)}


def _safe_write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _safe_write_txt(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _as_int(x: Any, default: int = 0) -> int:
    try:
        return int(x)
    except Exception:
        return default


def _as_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _bounded_statement(
    *,
    posture: str,
    confidence: str,
    risk_band: str,
    trust_score: float,
    risk_score: float,
    ambiguity_flags: List[str],
) -> List[str]:
    # Bounded language only. No certainty claims.
    lines = []
    lines.append(f"- System posture is {posture} with confidence={confidence}.")
    lines.append(f"- Risk is assessed in a bounded band (risk_band={risk_band}, risk_score={risk_score:.2f}).")
    lines.append(f"- Trust is bounded (trust_score={trust_score:.2f}); interpretation remains probabilistic.")
    if ambiguity_flags:
        lines.append(f"- Ambiguity present: {', '.join(sorted(set(ambiguity_flags)))}.")
    return lines


def build_nuclear_status_summary() -> Dict[str, Any]:
    card = _safe_read_json(DECISION_CARD_LATEST)
    wb = _safe_read_json(WATCHBOARD_LATEST)
    pb = _safe_read_json(PREFBRIEF_LATEST)

    # Extract decision card fields (best-effort)
    status = card.get("status", {}) if isinstance(card.get("status", {}), dict) else {}
    escalation = card.get("escalation", {}) if isinstance(card.get("escalation", {}), dict) else {}

    posture = str(escalation.get("posture", "DUTY_OFFICER_NOTIFY"))
    confidence = str(escalation.get("confidence", status.get("confidence", "LOW")))
    risk_band = str(status.get("risk_band", "UNKNOWN"))

    ambiguity_flags = status.get("ambiguity_flags", [])
    if not isinstance(ambiguity_flags, list):
        ambiguity_flags = []

    trust_score = _as_float(card.get("trust_score", status.get("trust_score", 0.0)), 0.0)
    risk_score = _as_float(card.get("risk_score", status.get("risk_score", 0.0)), 0.0)

    alerts = card.get("alerts", card.get("inputs", {}).get("alerts", {}))
    if not isinstance(alerts, dict):
        alerts = {}
    alert_pack = {
        "crit": _as_int(alerts.get("crit", 0)),
        "high": _as_int(alerts.get("high", 0)),
        "anomaly": _as_int(alerts.get("anomaly", 0)),
    }

    degraded = bool(status.get("degraded", False))

    summary = {
        "report_version": 1,
        "generated_at_utc": _utc_now_iso(),
        "safe_notice": "Synthetic/training artifacts only. Bounded language. No real-world sensor claims.",
        "inputs": {
            "decision_card_path": str(DECISION_CARD_LATEST),
            "watchboard_path": str(WATCHBOARD_LATEST),
            "prebrief_path": str(PREFBRIEF_LATEST),
            "missing_inputs": {
                "decision_card": bool(card.get("_missing") or card.get("_error")),
                "watchboard": bool(wb.get("_missing") or wb.get("_error")),
                "prebrief": bool(pb.get("_missing") or pb.get("_error")),
            },
        },
        "status": {
            "posture": posture,
            "confidence": confidence,
            "risk_band": risk_band,
            "degraded": degraded,
            "alerts": alert_pack,
            "ambiguity_flags": sorted(set([str(x) for x in ambiguity_flags])),
            "trust_score": trust_score,
            "risk_score": risk_score,
        },
        "what_we_can_say": _bounded_statement(
            posture=posture,
            confidence=confidence,
            risk_band=risk_band,
            trust_score=trust_score,
            risk_score=risk_score,
            ambiguity_flags=[str(x) for x in ambiguity_flags],
        ),
        # Keep raw references minimal but useful
        "references": {
            "decision_card_status": status if isinstance(status, dict) else {},
            "watchboard_meta": wb.get("meta", wb.get("report_meta", {})) if isinstance(wb, dict) else {},
            "prebrief_meta": pb.get("meta", pb.get("report_meta", {})) if isinstance(pb, dict) else {},
        },
    }
    return summary


def write_nuclear_status_summary(summary: Dict[str, Any]) -> Dict[str, str]:
    NUCLEAR_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _ts()

    json_latest = NUCLEAR_DIR / "nuclear_status_summary_latest.json"
    txt_latest = NUCLEAR_DIR / "nuclear_status_summary_latest.txt"
    json_stamped = NUCLEAR_DIR / f"nuclear_status_summary_{stamp}.json"
    txt_stamped = NUCLEAR_DIR / f"nuclear_status_summary_{stamp}.txt"

    _safe_write_json(json_latest, summary)
    _safe_write_json(json_stamped, summary)
    _safe_write_txt(txt_latest, _render_txt(summary))
    _safe_write_txt(txt_stamped, _render_txt(summary))

    return {
        "json_latest": str(json_latest),
        "txt_latest": str(txt_latest),
        "json_stamped": str(json_stamped),
        "txt_stamped": str(txt_stamped),
    }


def _render_txt(summary: Dict[str, Any]) -> str:
    s = summary.get("status", {})
    lines = []
    lines.append("Nuclear Status Summary (Training)")
    lines.append(f"generated_at_utc: {summary.get('generated_at_utc')}")
    lines.append("")
    lines.append(f"posture: {s.get('posture')}")
    lines.append(f"confidence: {s.get('confidence')}")
    lines.append(f"risk_band: {s.get('risk_band')}")
    lines.append(f"degraded: {s.get('degraded')}")
    lines.append(f"alerts: crit={s.get('alerts', {}).get('crit')} high={s.get('alerts', {}).get('high')} anomaly={s.get('alerts', {}).get('anomaly')}")
    lines.append(f"trust_score: {s.get('trust_score')}")
    lines.append(f"risk_score: {s.get('risk_score')}")
    af = s.get("ambiguity_flags", [])
    lines.append(f"ambiguity_flags: {', '.join(af) if af else 'NONE'}")
    lines.append("")
    lines.append("What we can say (bounded):")
    for l in summary.get("what_we_can_say", []):
        lines.append(l)
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    summary = build_nuclear_status_summary()
    paths = write_nuclear_status_summary(summary)
    print("Nuclear status summary written:")
    print(json.dumps(paths, indent=2))


if __name__ == "__main__":
    main()

