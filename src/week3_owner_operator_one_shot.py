from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

# Best-effort import
try:
    from week3_shari_demo_packet import run_week3_shari_demo_packet
except Exception as e:  # pragma: no cover
    raise SystemExit(f"ERROR: cannot import week3_shari_demo_packet: {type(e).__name__}:{e}")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    """
    Week-3 Owner-Operator One-Shot:
    - Runs week3_shari_demo_packet (regen + readiness gate)
    - Prints a small, stable JSON summary
    """
    res = run_week3_shari_demo_packet(strict=True)

    outputs = res.get("outputs", {}) if isinstance(res, dict) else {}
    verdict = res.get("verdict", "UNKNOWN") if isinstance(res, dict) else "UNKNOWN"

    summary: Dict[str, Any] = {
        "generated_at_utc": _utc_now_iso(),
        "context": "week3_owner_operator_one_shot",
        "verdict": verdict,
        "outputs": outputs,
        "next_actions": [
            "Open checklist_latest and follow the 3-minute flow.",
            "If verdict != PASS, open readiness_gate_head in week3_shari_demo_packet_latest.json for violations.",
        ],
    }

    print(json.dumps(summary, indent=2))

    # Convenience: print checklist text path if present
    checklist = outputs.get("checklist_latest")
    if checklist and Path(checklist).exists():
        print(f"\nOPEN THIS FIRST:\n{checklist}")

    return 0 if str(verdict).upper() == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())

