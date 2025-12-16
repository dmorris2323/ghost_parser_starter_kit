from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

REQ = [
    Path("docs/briefs/commander_brief_latest.txt"),
    Path("docs/briefs/week3_operator_summary_latest.txt"),
    Path("docs/briefs/legal_case_snapshot_latest.txt"),
    Path("docs/briefs/legal_case_snapshot_stress_latest.json"),
]

OUT_DIR = Path("docs") / "validation"

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _stamp() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")

def run_week3_demo_pack_gate(context: str = "week3_demo_pack") -> Dict[str, Any]:
    missing: List[str] = []
    for p in REQ:
        try:
            if not p.exists():
                missing.append(str(p))
        except Exception:
            missing.append(str(p))

    verdict = "PASS" if not missing else "FAIL"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    latest = OUT_DIR / "week3_demo_pack_gate_latest.json"
    stamped = OUT_DIR / f"week3_demo_pack_gate_{_stamp()}.json"

    res = {
        "generated_at_utc": _utc_now_iso(),
        "context": context,
        "verdict": verdict,
        "missing": missing,
        "latest": str(latest),
        "stamped": str(stamped),
    }

    latest.write_text(json.dumps(res, indent=2), encoding="utf-8")
    stamped.write_text(json.dumps(res, indent=2), encoding="utf-8")
    return res

def main() -> int:
    res = run_week3_demo_pack_gate()
    print(json.dumps(res, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

