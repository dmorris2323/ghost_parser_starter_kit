"""
nuclear_product_consistency_gate.py

Week-1 Nuclear Hardening Gate:
Validate that the three commander-trust products agree on core fields:

1) Decision Card (latest):
   docs/decision_cards/nuclear_decision_card_latest.json

2) Prelaunch Watchboard (latest):
   docs/nuclear/prelaunch_watchboard_latest.json

3) Prebrief Trust Annotations (latest):
   docs/briefs/prebrief_trust_annotations_latest.json

Checks (bounded, commander-trust):
- posture alignment
- confidence alignment
- risk_band alignment (when present)
- degraded alignment (when present)
- ambiguity_flags: ensure prebrief + watchboard include decision-card flags (subset check)

Outputs:
- docs/nuclear/nuclear_product_consistency_latest.json
- docs/nuclear/nuclear_product_consistency_latest.txt
- docs/nuclear/nuclear_product_consistency_<timestamp>.json  (stamped)
- docs/nuclear/nuclear_product_consistency_<timestamp>.txt   (stamped)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


OUT_DIR = Path("docs") / "nuclear"

DECISION_CARD_LATEST = Path("docs") / "decision_cards" / "nuclear_decision_card_latest.json"
WATCHBOARD_LATEST = Path("docs") / "nuclear" / "prelaunch_watchboard_latest.json"
PREBRIEF_LATEST = Path("docs") / "briefs" / "prebrief_trust_annotations_latest.json"


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"_missing": True, "_path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"_error": f"{e.__class__.__name__}: {e}", "_path": str(path)}


def _write_json(path: Path, obj: Any) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _write_txt(path: Path, text: str) -> None:
    _safe_mkdir(path.parent)
    path.write_text(text, encoding="utf-8")


def _as_str(x: Any, default: str = "") -> str:
    try:
        s = str(x)
        return s if s else default
    except Exception:
        return default


def _as_bool(x: Any, default: Optional[bool] = None) -> Optional[bool]:
    if x is None:
        return default
    if isinstance(x, bool):
        return x
    if isinstance(x, (int, float)):
        return bool(x)
    if isinstance(x, str):
        t = x.strip().lower()
        if t in {"true", "t", "yes", "y", "1"}:
            return True
        if t in {"false", "f", "no", "n", "0"}:
            return False
    return default


def _as_list(x: Any) -> List[str]:
    if x is None:
        return []
    if isinstance(x, list):
        out: List[str] = []
        for i in x:
            if i is None:
                continue
            out.append(_as_str(i))
        return [s for s in out if s]
    # if it’s a single string, treat as one item
    if isinstance(x, str) and x.strip():
        return [x.strip()]
    return []


@dataclass
class Extracted:
    posture: str = ""
    confidence: str = ""
    risk_band: str = ""
    degraded: Optional[bool] = None
    ambiguity_flags: List[str] = None

    def __post_init__(self) -> None:
        if self.ambiguity_flags is None:
            self.ambiguity_flags = []


def _extract_from_decision_card(card: Dict[str, Any]) -> Extracted:
    escalation = card.get("escalation", {}) if isinstance(card.get("escalation", {}), dict) else {}
    status = card.get("status", {}) if isinstance(card.get("status", {}), dict) else {}

    return Extracted(
        posture=_as_str(escalation.get("posture", "")),
        confidence=_as_str(status.get("confidence", card.get("confidence", ""))),
        risk_band=_as_str(status.get("risk_band", card.get("risk_band", ""))),
        degraded=_as_bool(status.get("degraded", card.get("degraded"))),
        ambiguity_flags=_as_list(status.get("ambiguity_flags", card.get("ambiguity_flags"))),
    )


def _extract_from_watchboard(wb: Dict[str, Any]) -> Extracted:
    # We accept either top-level fields or nested fields depending on evolution.
    # Try common placements; remain safe/bounded.
    escalation = wb.get("escalation", {}) if isinstance(wb.get("escalation", {}), dict) else {}
    status = wb.get("status", {}) if isinstance(wb.get("status", {}), dict) else {}
    trust_posture = wb.get("trust_posture", {}) if isinstance(wb.get("trust_posture", {}), dict) else {}

    posture = _as_str(
        escalation.get("posture")
        or trust_posture.get("posture")
        or status.get("posture")
        or wb.get("posture", "")
    )
    confidence = _as_str(
        trust_posture.get("confidence")
        or status.get("confidence")
        or wb.get("confidence", "")
    )
    risk_band = _as_str(
        trust_posture.get("risk_band")
        or status.get("risk_band")
        or wb.get("risk_band", "")
    )
    degraded = _as_bool(
        trust_posture.get("degraded")
        or status.get("degraded")
        or wb.get("degraded")
    )
    ambiguity_flags = _as_list(
        trust_posture.get("ambiguity_flags")
        or status.get("ambiguity_flags")
        or wb.get("ambiguity_flags")
    )

    return Extracted(
        posture=posture,
        confidence=confidence,
        risk_band=risk_band,
        degraded=degraded,
        ambiguity_flags=ambiguity_flags,
    )


def _extract_from_prebrief(pb: Dict[str, Any]) -> Extracted:
    tp = pb.get("trust_posture", {}) if isinstance(pb.get("trust_posture", {}), dict) else {}
    return Extracted(
        posture=_as_str(tp.get("posture", pb.get("posture", ""))),
        confidence=_as_str(tp.get("confidence", pb.get("confidence", ""))),
        risk_band=_as_str(tp.get("risk_band", pb.get("risk_band", ""))),
        degraded=_as_bool(tp.get("degraded", pb.get("degraded"))),
        ambiguity_flags=_as_list(tp.get("ambiguity_flags", pb.get("ambiguity_flags"))),
    )


def _render_txt(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("Nuclear Product Consistency Gate")
    lines.append(f"generated_at_utc: {report.get('generated_at_utc')}")
    lines.append(f"verdict: {report.get('verdict')}")
    lines.append("")
    lines.append("Inputs:")
    for k, v in (report.get("inputs") or {}).items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("Extracted (decision_card vs watchboard vs prebrief):")
    ex = report.get("extracted") or {}
    for label in ["decision_card", "watchboard", "prebrief"]:
        obj = ex.get(label) or {}
        lines.append(f"- {label}: posture={obj.get('posture')} confidence={obj.get('confidence')} risk_band={obj.get('risk_band')} degraded={obj.get('degraded')} ambiguity_flags={obj.get('ambiguity_flags')}")
    lines.append("")
    lines.append("Violations:")
    viols = report.get("violations") or []
    if not viols:
        lines.append("- none")
    else:
        for v in viols:
            lines.append(f"- {v}")
    return "\n".join(lines) + "\n"


def run_gate() -> Dict[str, Any]:
    decision = _read_json(DECISION_CARD_LATEST)
    watchboard = _read_json(WATCHBOARD_LATEST)
    prebrief = _read_json(PREBRIEF_LATEST)

    violations: List[str] = []

    # Missing / parse errors
    for name, blob in [("decision_card", decision), ("watchboard", watchboard), ("prebrief", prebrief)]:
        if blob.get("_missing"):
            violations.append(f"MISSING_INPUT:{name}")
        if blob.get("_error"):
            violations.append(f"BAD_JSON:{name}:{blob.get('_error')}")

    d = _extract_from_decision_card(decision)
    w = _extract_from_watchboard(watchboard)
    p = _extract_from_prebrief(prebrief)

    # Core alignment checks (posture/confidence are the most important)
    if d.posture and w.posture and d.posture != w.posture:
        violations.append(f"POSTURE_MISMATCH:decision_card={d.posture} watchboard={w.posture}")
    if d.posture and p.posture and d.posture != p.posture:
        violations.append(f"POSTURE_MISMATCH:decision_card={d.posture} prebrief={p.posture}")

    if d.confidence and w.confidence and d.confidence != w.confidence:
        violations.append(f"CONFIDENCE_MISMATCH:decision_card={d.confidence} watchboard={w.confidence}")
    if d.confidence and p.confidence and d.confidence != p.confidence:
        violations.append(f"CONFIDENCE_MISMATCH:decision_card={d.confidence} prebrief={p.confidence}")

    # Optional alignment: risk band + degraded (only if present on both)
    if d.risk_band and w.risk_band and d.risk_band != w.risk_band:
        violations.append(f"RISK_BAND_MISMATCH:decision_card={d.risk_band} watchboard={w.risk_band}")
    if d.risk_band and p.risk_band and d.risk_band != p.risk_band:
        violations.append(f"RISK_BAND_MISMATCH:decision_card={d.risk_band} prebrief={p.risk_band}")

    if (d.degraded is not None) and (w.degraded is not None) and (d.degraded != w.degraded):
        violations.append(f"DEGRADED_MISMATCH:decision_card={d.degraded} watchboard={w.degraded}")
    if (d.degraded is not None) and (p.degraded is not None) and (d.degraded != p.degraded):
        violations.append(f"DEGRADED_MISMATCH:decision_card={d.degraded} prebrief={p.degraded}")

    # Ambiguity flags: decision card flags must be present in watchboard + prebrief (subset)
    dc_flags = set([f for f in d.ambiguity_flags if f])
    wb_flags = set([f for f in w.ambiguity_flags if f])
    pb_flags = set([f for f in p.ambiguity_flags if f])

    missing_in_wb = sorted(list(dc_flags - wb_flags))
    missing_in_pb = sorted(list(dc_flags - pb_flags))

    if missing_in_wb:
        violations.append(f"AMBIGUITY_FLAGS_MISSING_IN_WATCHBOARD:{missing_in_wb}")
    if missing_in_pb:
        violations.append(f"AMBIGUITY_FLAGS_MISSING_IN_PREBRIEF:{missing_in_pb}")

    verdict = "PASS" if len(violations) == 0 else "FAIL"

    report: Dict[str, Any] = {
        "generated_at_utc": _utc_now_iso(),
        "verdict": verdict,
        "inputs": {
            "decision_card_latest": str(DECISION_CARD_LATEST),
            "watchboard_latest": str(WATCHBOARD_LATEST),
            "prebrief_latest": str(PREBRIEF_LATEST),
        },
        "extracted": {
            "decision_card": {
                "posture": d.posture,
                "confidence": d.confidence,
                "risk_band": d.risk_band,
                "degraded": d.degraded,
                "ambiguity_flags": d.ambiguity_flags,
            },
            "watchboard": {
                "posture": w.posture,
                "confidence": w.confidence,
                "risk_band": w.risk_band,
                "degraded": w.degraded,
                "ambiguity_flags": w.ambiguity_flags,
            },
            "prebrief": {
                "posture": p.posture,
                "confidence": p.confidence,
                "risk_band": p.risk_band,
                "degraded": p.degraded,
                "ambiguity_flags": p.ambiguity_flags,
            },
        },
        "violations": violations,
    }

    # Write outputs
    _safe_mkdir(OUT_DIR)
    json_latest = OUT_DIR / "nuclear_product_consistency_latest.json"
    txt_latest = OUT_DIR / "nuclear_product_consistency_latest.txt"

    stamped = _ts()
    json_stamped = OUT_DIR / f"nuclear_product_consistency_{stamped}.json"
    txt_stamped = OUT_DIR / f"nuclear_product_consistency_{stamped}.txt"

    _write_json(json_latest, report)
    _write_txt(txt_latest, _render_txt(report))
    _write_json(json_stamped, report)
    _write_txt(txt_stamped, _render_txt(report))

    print("Nuclear Product Consistency Gate:")
    print(json.dumps(
        {
            "verdict": verdict,
            "json_latest": str(json_latest),
            "txt_latest": str(txt_latest),
            "json_stamped": str(json_stamped),
            "txt_stamped": str(txt_stamped),
            "violations": violations,
        },
        indent=2,
    ))
    return report


def main() -> None:
    run_gate()


if __name__ == "__main__":
    main()

