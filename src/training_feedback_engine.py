"""
training_feedback_engine.py

Generates a "next best training step" recommendation.
- Recorded, not enforced.

Writes:
- src/docs/training/training_feedback_latest.json
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from operator_certification_engine import compute_certification, highest_certified_track
from training_policy import normalize_difficulty


FEEDBACK_PATH = Path("src") / "docs" / "training" / "training_feedback_latest.json"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def write_latest_feedback(feedback: Dict[str, Any]) -> str:
    _safe_mkdir(FEEDBACK_PATH.parent)
    FEEDBACK_PATH.write_text(json.dumps(feedback, indent=2), encoding="utf-8")
    return str(FEEDBACK_PATH)


def recommend_next_training(
    *,
    training_curve: Dict[str, Any],
    current_difficulty: str,
    validation_verdict: str,
    sessions: list[dict] | None = None,
) -> Dict[str, Any]:
    """
    training_curve: output of compute_training_curve()
    current_difficulty: e.g. BEGINNER/INTERMEDIATE/ADVANCED/ADVERSARIAL
    validation_verdict: PASS/WARN/FAIL/UNKNOWN
    sessions: optional list of sessions for certification computation
    """
    cur = normalize_difficulty(current_difficulty)
    verdict = str(validation_verdict or "UNKNOWN").upper().strip()

    agi = float(training_curve.get("AGI", 0.0) or 0.0)
    slope = float(training_curve.get("improvement_slope", 0.0) or 0.0)
    vol = float(training_curve.get("volatility_index", 0.0) or 0.0)

    cert = compute_certification(sessions or [])
    top = highest_certified_track(cert)  # MUST be string
    top = str(top or "NONE").upper().strip()

    # Default recommendation
    next_diff = cur
    pattern = "NONE"
    rationale = []

    if verdict == "FAIL":
        next_diff = "INTERMEDIATE"
        pattern = "NONE"
        rationale.append("Validation FAIL: stabilize baseline before adding adversary stress.")
    elif verdict == "WARN":
        next_diff = cur
        pattern = "CROSS_DOMAIN_CONFUSION"
        rationale.append("Validation WARN: keep difficulty but practice controlled injection.")
    else:
        # PASS/UNKNOWN
        if slope < 0 and vol > 10:
            next_diff = "INTERMEDIATE"
            pattern = "NONE"
            rationale.append("Negative slope + volatility: consolidate fundamentals and reduce variance.")
        else:
            # Step up only if certified allows it
            if top in {"NONE"}:
                next_diff = "BEGINNER"
                rationale.append("Not certified yet: build a clean GREEN streak at BEGINNER.")
            elif top == "BEGINNER":
                next_diff = "INTERMEDIATE"
                rationale.append("Beginner certified: step to INTERMEDIATE with stable GREEN sessions.")
            elif top == "INTERMEDIATE":
                next_diff = "ADVANCED"
                rationale.append("Intermediate certified: step to ADVANCED with fewer misses.")
            elif top == "ADVANCED":
                next_diff = "ADVERSARIAL"
                pattern = "CROSS_DOMAIN_CONFUSION"
                rationale.append("Advanced certified: move to ADVERSARIAL with injection training.")
            else:
                next_diff = "ADVERSARIAL"
                pattern = "CROSS_DOMAIN_CONFUSION"
                rationale.append("Top track: maintain adversarial readiness and pattern discipline.")

    recommendation = {
        "generated_at": _utc_now_iso(),
        "current_difficulty": cur,
        "certified_track": top,
        "validation_verdict": verdict,
        "metrics": {
            "AGI": agi,
            "improvement_slope": slope,
            "volatility_index": vol,
        },
        "recommendation": {
            "next_difficulty": next_diff,
            "pattern": pattern,
        },
        "rationale": rationale,
    }
    return recommendation

