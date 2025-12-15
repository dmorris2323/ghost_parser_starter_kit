"""
escalation_ladder_consistency.py

Hardening test: Escalation ladder must not:
- make illegal jumps (e.g., ROUTINE_MONITORING -> NATIONAL_COMMAND_ALERT)
- oscillate (e.g., DUTY_OFFICER_NOTIFY -> ROUTINE_MONITORING) within a short run

This is a safety/credibility test: commander products must be stable and plausible.

Outputs:
- docs/nuclear/escalation_ladder_consistency_latest.json
- docs/nuclear/escalation_ladder_consistency_<timestamp>.json
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


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


def _load_ladder_map() -> Dict[str, int]:
    """
    Defines the allowed ordering for posture progression.
    If your escalation_ladder module uses different names, update ONLY here.
    """
    return {
        "ROUTINE_MONITORING": 0,
        "DUTY_OFFICER_NOTIFY": 1,
        "WATCH_FLOOR_ELEVATE": 2,
        "WING_COMMAND_POSTURE": 3,
        "NATIONAL_COMMAND_ALERT": 4,
    }


def _illegal_jump(prev: str, nxt: str, ladder: Dict[str, int]) -> bool:
    if prev not in ladder or nxt not in ladder:
        return False  # unknown labels are handled elsewhere
    return (ladder[nxt] - ladder[prev]) > 1


def _is_oscillation(prev: str, nxt: str, ladder: Dict[str, int]) -> bool:
    if prev not in ladder or nxt not in ladder:
        return False
    return ladder[nxt] < ladder[prev]


def _extract_reason_fields(res: Any) -> List[str]:
    """
    Your EscalationResult seems to have `reason` (singular).
    Older versions used `reasons` (plural).
    This function supports BOTH without crashing.
    """
    if res is None:
        return []

    # Prefer plural if present and is list-like
    if hasattr(res, "reasons"):
        val = getattr(res, "reasons")
        if isinstance(val, list):
            return [str(x) for x in val]
        if isinstance(val, str):
            return [val]

    # Fallback to singular
    if hasattr(res, "reason"):
        val = getattr(res, "reason")
        if isinstance(val, list):
            return [str(x) for x in val]
        if isinstance(val, str):
            return [val]

    return []


def _run_sequence() -> Dict[str, Any]:
    ladder = _load_ladder_map()

    try:
        # Your escalation module is the source of truth.
        from escalation_ladder import recommend_escalation  # type: ignore
    except Exception as e:
        return {
            "verdict": "FAIL",
            "error": f"ImportError: escalation_ladder.recommend_escalation: {e.__class__.__name__}: {e}",
            "violations": {"illegal_jump": [], "oscillation": [], "unknown_posture": []},
        }

    # Deterministic sequence of “inputs” that should not create illegal behavior.
    # We only care about posture transitions, not real-world data.
    test_vectors = [
        {"trust_score": 95, "risk_score": 10, "confidence": "HIGH", "degraded": False, "alerts": {"crit": 0, "high": 0, "anomaly": 0}},
        {"trust_score": 90, "risk_score": 25, "confidence": "MED", "degraded": False, "alerts": {"crit": 0, "high": 1, "anomaly": 4}},
        {"trust_score": 85, "risk_score": 48, "confidence": "LOW", "degraded": True,  "alerts": {"crit": 0, "high": 3, "anomaly": 14}},
        {"trust_score": 80, "risk_score": 55, "confidence": "LOW", "degraded": True,  "alerts": {"crit": 1, "high": 5, "anomaly": 20}},
        {"trust_score": 78, "risk_score": 60, "confidence": "LOW", "degraded": True,  "alerts": {"crit": 1, "high": 7, "anomaly": 28}},
    ]

    postures: List[str] = []
    reasons: List[List[str]] = []

    unknown_posture: List[str] = []

    for v in test_vectors:
        try:
            # We call using a “best-effort signature” that matches how you wired it earlier.
            # If your function has a different signature, adapt only this call.
            res = recommend_escalation(
                trust_score=v["trust_score"],
                risk_score=v["risk_score"],
                degraded=v["degraded"],
                confidence=v["confidence"],
                alerts=v["alerts"],
            )
        except TypeError:
            # Some versions don’t accept alerts/confidence; try a minimal call.
            res = recommend_escalation(
                trust_score=v["trust_score"],
                risk_score=v["risk_score"],
                degraded=v["degraded"],
            )
        except Exception as e:
            return {
                "verdict": "FAIL",
                "error": f"RuntimeError: recommend_escalation: {e.__class__.__name__}: {e}",
                "violations": {"illegal_jump": [], "oscillation": [], "unknown_posture": []},
            }

        # Support result shapes:
        # - dict with "posture"
        # - object with .posture
        posture = None
        if isinstance(res, dict):
            posture = res.get("posture") or res.get("recommended_posture")
        else:
            posture = getattr(res, "posture", None) or getattr(res, "recommended_posture", None)

        if posture is None:
            unknown_posture.append("MISSING_POSTURE")
            posture = "ROUTINE_MONITORING"

        posture = str(posture)
        if posture not in ladder:
            unknown_posture.append(posture)

        postures.append(posture)
        reasons.append(_extract_reason_fields(res))

    illegal: List[str] = []
    oscillation: List[str] = []

    for i in range(1, len(postures)):
        prev, nxt = postures[i - 1], postures[i]
        if _illegal_jump(prev, nxt, ladder):
            illegal.append(f"ILLEGAL_JUMP: {prev}->{nxt}")
        if _is_oscillation(prev, nxt, ladder):
            oscillation.append(f"OSCILLATION: {prev}->{nxt}")

    verdict = "PASS" if (not illegal and not oscillation and not unknown_posture) else "FAIL"

    return {
        "verdict": verdict,
        "generated_at_utc": _utc_now_iso(),
        "postures": postures,
        "reasons": reasons,
        "violations": {
            "illegal_jump": illegal,
            "oscillation": oscillation,
            "unknown_posture": unknown_posture,
        },
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    res = _run_sequence()

    latest = OUT_DIR / "escalation_ladder_consistency_latest.json"
    stamped = OUT_DIR / f"escalation_ladder_consistency_{_ts()}.json"

    _write_json(latest, res)
    _write_json(stamped, res)

    print("Escalation Ladder Consistency Test:")
    print(json.dumps(
        {
            "verdict": res.get("verdict"),
            "json_latest": str(latest),
            "json_stamped": str(stamped),
            "violations": res.get("violations", {}),
        },
        indent=2
    ))


if __name__ == "__main__":
    main()

