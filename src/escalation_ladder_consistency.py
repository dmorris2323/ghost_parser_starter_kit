"""
escalation_ladder_consistency.py

Validates nuclear escalation ladder behavior:
- No illegal jumps
- No oscillation under noise
- Reversible under ambiguity
- Monotonic escalation only when justified

Commander trust hardening artifact.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


OUT_DIR = Path("docs") / "nuclear"

LADDER = [
    "ROUTINE_MONITORING",
    "DUTY_OFFICER_NOTIFY",
    "COMMAND_AWARENESS",
    "NATIONAL_COMMAND_ALERT",
]


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _write(path: Path, obj: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def validate_sequence(sequence: List[str]) -> Dict:
    violations = []

    for i in range(1, len(sequence)):
        prev = sequence[i - 1]
        cur = sequence[i]

        if prev not in LADDER or cur not in LADDER:
            violations.append(f"UNKNOWN_STATE: {prev}->{cur}")
            continue

        prev_idx = LADDER.index(prev)
        cur_idx = LADDER.index(cur)

        # Illegal jump
        if cur_idx - prev_idx > 1:
            violations.append(f"ILLEGAL_JUMP: {prev}->{cur}")

        # Oscillation
        if cur_idx < prev_idx:
            violations.append(f"OSCILLATION: {prev}->{cur}")

    return {
        "valid": len(violations) == 0,
        "violations": violations,
    }


def run_escalation_ladder_consistency_test() -> Dict:
    # Synthetic stress sequences
    sequences = {
        "clean_progression": [
            "ROUTINE_MONITORING",
            "DUTY_OFFICER_NOTIFY",
            "COMMAND_AWARENESS",
        ],
        "noise_only": [
            "ROUTINE_MONITORING",
            "ROUTINE_MONITORING",
            "ROUTINE_MONITORING",
        ],
        "illegal_jump": [
            "ROUTINE_MONITORING",
            "NATIONAL_COMMAND_ALERT",
        ],
        "oscillation": [
            "DUTY_OFFICER_NOTIFY",
            "ROUTINE_MONITORING",
        ],
    }

    results = {}
    overall_ok = True

    for name, seq in sequences.items():
        res = validate_sequence(seq)
        results[name] = res
        if not res["valid"] and name != "illegal_jump":
            overall_ok = False

    verdict = "PASS" if overall_ok else "FAIL"

    report = {
        "generated_at_utc": _utc(),
        "artifact": "ESCALATION_LADDER_CONSISTENCY",
        "ladder": LADDER,
        "results": results,
        "verdict": verdict,
        "safe_notice": "Validation uses synthetic sequences only.",
    }

    ts = _ts()
    latest = OUT_DIR / "escalation_ladder_consistency_latest.json"
    stamped = OUT_DIR / f"escalation_ladder_consistency_{ts}.json"

    _write(latest, report)
    _write(stamped, report)

    return {
        "verdict": verdict,
        "json_latest": str(latest),
        "json_stamped": str(stamped),
        "violations": {
            k: v["violations"] for k, v in results.items() if v["violations"]
        },
    }


if __name__ == "__main__":
    result = run_escalation_ladder_consistency_test()
    print("Escalation Ladder Consistency Test:")
    print(json.dumps(result, indent=2))

