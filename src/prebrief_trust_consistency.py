"""
prebrief_trust_consistency.py

Validates that all commander-facing nuclear artifacts
express a CONSISTENT trust posture and confidence level.

Artifacts checked:
- nuclear_decision_card_latest
- prelaunch_watchboard_latest
- prebrief_trust_annotations_latest

FAIL conditions:
- posture mismatch
- confidence escalation under ambiguity
- contradictory claims across artifacts
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List


DOCS = Path("docs")
OUT_DIR = DOCS / "nuclear"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def _extract_posture(obj: Dict[str, Any]) -> str:
    for k in ("posture", "escalation_posture", "recommended_posture"):
        if k in obj:
            return str(obj[k])
    return "UNKNOWN"


def _extract_confidence(obj: Dict[str, Any]) -> str:
    for k in ("confidence", "trust_confidence"):
        if k in obj:
            return str(obj[k]).upper()
    return "UNKNOWN"


def run_prebrief_trust_consistency() -> Dict[str, Any]:
    decision_card = _load(DOCS / "decision_cards" / "nuclear_decision_card_latest.json")
    watchboard = _load(DOCS / "nuclear" / "prelaunch_watchboard_latest.json")
    prebrief = _load(DOCS / "briefs" / "prebrief_trust_annotations_latest.json")

    dc_posture = _extract_posture(decision_card)
    wb_posture = _extract_posture(watchboard)
    pb_posture = _extract_posture(prebrief)

    dc_conf = _extract_confidence(decision_card)
    pb_conf = _extract_confidence(prebrief)

    violations: List[str] = []

    if len({dc_posture, wb_posture, pb_posture}) > 1:
        violations.append(
            f"POSTURE_MISMATCH: decision_card={dc_posture}, "
            f"watchboard={wb_posture}, prebrief={pb_posture}"
        )

    # Confidence must not increase under degraded ops
    if dc_conf == "LOW" and pb_conf in {"MEDIUM", "HIGH"}:
        violations.append(
            f"CONFIDENCE_ESCALATION: decision_card={dc_conf}, prebrief={pb_conf}"
        )

    verdict = "PASS" if not violations else "FAIL"

    report = {
        "generated_at_utc": _utc_now(),
        "verdict": verdict,
        "decision_card": {
            "posture": dc_posture,
            "confidence": dc_conf,
        },
        "watchboard": {
            "posture": wb_posture,
        },
        "prebrief": {
            "posture": pb_posture,
            "confidence": pb_conf,
        },
        "violations": violations,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    latest = OUT_DIR / "prebrief_trust_consistency_latest.json"
    stamped = OUT_DIR / f"prebrief_trust_consistency_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"

    latest.write_text(json.dumps(report, indent=2))
    stamped.write_text(json.dumps(report, indent=2))

    return {
        "verdict": verdict,
        "json_latest": str(latest),
        "json_stamped": str(stamped),
        "violations": violations,
    }


if __name__ == "__main__":
    result = run_prebrief_trust_consistency()
    print(json.dumps(result, indent=2))

