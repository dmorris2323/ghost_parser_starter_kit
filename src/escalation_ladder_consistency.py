"""
escalation_ladder_consistency.py

Consistency test:
- Ensures ladder does NOT generate:
  - illegal jumps (ROUTINE->NATIONAL in one step)
  - oscillation (de-escalation without clean conditions)

Writes:
- docs/nuclear/escalation_ladder_consistency_latest.json
- docs/nuclear/escalation_ladder_consistency_<timestamp>.json
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from escalation_ladder import compute_posture, POSTURE_ORDER

OUT_DIR = Path("docs") / "nuclear"


def _ts() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _idx(posture: str) -> int:
    return POSTURE_ORDER.index(posture) if posture in POSTURE_ORDER else 0


def main() -> Dict[str, Any]:
    violations = {"illegal_jump": [], "oscillation": []}

    # We simulate a small sequence of evaluations.
    # The ladder must enforce safety constraints even when risk changes quickly.
    prev_posture = "ROUTINE_MONITORING"

    # Each tuple is:
    # (trust, risk, confidence, degraded, flags)
    test_sequence: List[Tuple[float, float, str, bool, List[str]]] = [
        # normal rise into DUTY
        (82, 40, "MEDIUM", False, []),
        # risk spike (should NOT jump to NATIONAL in one step)
        (82, 96, "HIGH", False, []),
        # degraded/ambiguous situation (cap should keep it bounded)
        (70, 80, "LOW", True, ["DEGRADED_OPS", "MISSING_SIGNALS"]),
        # risk drops but NOT clean enough to de-escalate (avoid oscillation)
        (75, 20, "MEDIUM", False, []),
        # now clean + stable (allow controlled de-escalation)
        (80, 10, "HIGH", False, []),
    ]

    history: List[Dict[str, Any]] = []

    for i, (trust, risk, conf, degraded, flags) in enumerate(test_sequence, start=1):
        res = compute_posture(
            trust_score=trust,
            risk_score=risk,
            confidence=conf,
            degraded=degraded,
            ambiguity_flags=flags,
            previous_posture=prev_posture,
        )

        cur = res.posture

        # Illegal jump check: ROUTINE->NATIONAL in one evaluation is forbidden
        if prev_posture == "ROUTINE_MONITORING" and cur == "NATIONAL_COMMAND_ALERT":
            violations["illegal_jump"].append(
                f"ILLEGAL_JUMP: {prev_posture}->{cur} at step {i}"
            )

        # Oscillation check: de-escalation without clean conditions
        if _idx(cur) < _idx(prev_posture) and not res.reasons.get("clean_for_deescalation", False):
            violations["oscillation"].append(
                f"OSCILLATION: {prev_posture}->{cur} at step {i}"
            )

        history.append(
            {
                "step": i,
                "prev_posture": prev_posture,
                "posture": cur,
                "cap_applied": res.cap_applied,
                "allowed_jump_steps": res.allowed_jump_steps,
                "deescalation_blocked": res.deescalation_blocked,
                "reasons": res.reasons,
            }
        )

        prev_posture = cur

    ok = (len(violations["illegal_jump"]) == 0 and len(violations["oscillation"]) == 0)
    verdict = "PASS" if ok else "FAIL"

    payload = {
        "generated_at_utc": datetime.utcnow().isoformat() + "Z",
        "verdict": verdict,
        "violations": violations,
        "history": history,
        "json_latest": str(OUT_DIR / "escalation_ladder_consistency_latest.json"),
        "json_stamped": str(OUT_DIR / f"escalation_ladder_consistency_{_ts()}.json"),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    latest = OUT_DIR / "escalation_ladder_consistency_latest.json"
    stamped = OUT_DIR / f"escalation_ladder_consistency_{_ts()}.json"
    _write_json(latest, payload)
    _write_json(stamped, payload)

    print("Escalation Ladder Consistency Test:")
    print(json.dumps({k: payload[k] for k in ["verdict", "json_latest", "json_stamped", "violations"]}, indent=2))
    return payload


if __name__ == "__main__":
    main()

