from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from legal_case_snapshot import build_legal_case_snapshot, write_legal_case_snapshot

OUT_DIR = Path("docs") / "briefs"

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _stamp() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")

def run_stress(runs: int = 25) -> Dict[str, Any]:
    """
    Stress harness:
    - inject bad inputs
    - must never crash
    - must produce bounded posture + ambiguity flags when inputs are bad
    """
    crashes = 0
    violations: List[str] = []

    test_cases = [
        # non-numeric fields
        dict(days_past_due="BAD_DATA", balance_usd="BAD_DATA", risk_score="BAD_DATA"),
        # missing everything important
        dict(debtor_or_defendant=None, jurisdiction=None, days_past_due=None, balance_usd=None, risk_score=None),
        # empty strings
        dict(debtor_or_defendant="", jurisdiction="", stage="", matter_name=""),
        # extreme values
        dict(days_past_due=9999, balance_usd=99999999, risk_score=99.9),
        # negative / weird
        dict(days_past_due=-5, balance_usd=-100, risk_score=-1),
        # red flags malformed
        dict(red_flags=",, , , one, two,,"),
        dict(red_flags=["", None, "  ", "FlagA"]),
    ]

    allowed_postures = {
        "ROUTINE_MONITORING",
        "DUTY_OFFICER_NOTIFY",
        "LEGAL_REVIEW_RECOMMENDED",
        "HOLD_ACTION_PENDING_REVIEW",
    }

    for i in range(runs):
        try:
            t = test_cases[i % len(test_cases)]
            snap = build_legal_case_snapshot(**t)
            paths = write_legal_case_snapshot(snap)

            posture = (((snap.get("assessment") or {}).get("recommended_posture")) or "").strip()
            if posture not in allowed_postures:
                violations.append(f"UNBOUNDED_POSTURE:{posture}")

            amb = (snap.get("assessment") or {}).get("ambiguity_flags") or []
            # if any critical inputs were missing/bad, we expect ambiguity flags
            if t.get("risk_score") in (None, "BAD_DATA") or t.get("balance_usd") in (None, "BAD_DATA") or t.get("days_past_due") in (None, "BAD_DATA"):
                if not amb:
                    violations.append("MISSING_AMBIGUITY_FLAGS")

            # ensure outputs exist
            if not Path(paths["txt_latest"]).exists():
                violations.append("MISSING_OUTPUT_TXT_LATEST")
            if not Path(paths["json_latest"]).exists():
                violations.append("MISSING_OUTPUT_JSON_LATEST")

        except Exception as e:
            crashes += 1
            violations.append(f"CRASH:{type(e).__name__}:{e}")

    verdict = "PASS" if crashes == 0 and not violations else "FAIL"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    latest = OUT_DIR / "legal_case_snapshot_stress_latest.json"
    stamped = OUT_DIR / f"legal_case_snapshot_stress_{_stamp()}.json"

    res = {
        "generated_at_utc": _utc_now_iso(),
        "verdict": verdict,
        "runs": runs,
        "crashes": crashes,
        "violations": violations,
        "latest": str(latest),
        "stamped": str(stamped),
    }

    latest.write_text(json.dumps(res, indent=2), encoding="utf-8")
    stamped.write_text(json.dumps(res, indent=2), encoding="utf-8")
    return res

def main() -> int:
    res = run_stress(runs=25)
    print(json.dumps(res, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

