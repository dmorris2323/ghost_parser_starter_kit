from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> Dict[str, Any]:
    """
    Consistency check for the operator one-shot:
      - commander brief latest exists and includes the 5 required sections
      - nuclear product consistency latest exists and verdict is present (PASS/FAIL accepted)
      - prebrief annotations latest exists and contains bounded language tokens
    """

    briefs_dir = Path("docs") / "briefs"
    nuclear_dir = Path("docs") / "nuclear"

    commander_txt = briefs_dir / "commander_brief_latest.txt"
    prebrief_txt = briefs_dir / "prebrief_trust_annotations_latest.txt"
    npc_json = nuclear_dir / "nuclear_product_consistency_latest.json"

    violations = []

    # commander brief structure
    if not commander_txt.exists():
        violations.append("MISSING:commander_brief_latest.txt")
    else:
        txt = commander_txt.read_text(encoding="utf-8", errors="replace")
        required_headers = [
            "1. What changed:",
            "2. Why it matters:",
            "3. What we know:",
            "4. What we do NOT know:",
            "5. Recommended posture:",
        ]
        for h in required_headers:
            if h not in txt:
                violations.append(f"MISSING_BRIEF_SECTION:{h}")

    # nuclear product consistency
    if not npc_json.exists():
        violations.append("MISSING:nuclear_product_consistency_latest.json")
    else:
        try:
            d = _read_json(npc_json)
            # verdict may live at top-level
            if "verdict" not in d:
                violations.append("MISSING_FIELD:npc.verdict")
        except Exception as e:
            violations.append(f"CRASH_READ_NPC:{type(e).__name__}:{e}")

    # prebrief bounded language
    if not prebrief_txt.exists():
        violations.append("MISSING:prebrief_trust_annotations_latest.txt")
    else:
        t = prebrief_txt.read_text(encoding="utf-8", errors="replace").lower()
        for token in ["probabilistic", "bounded", "operator judgment"]:
            if token not in t:
                violations.append(f"MISSING_REQUIRED_TOKEN:{token}")

    verdict = "PASS" if len(violations) == 0 else "FAIL"

    out = {
        "generated_at_utc": _utc_now_iso(),
        "verdict": verdict,
        "violations": violations,
        "inputs": {
            "commander_txt": str(commander_txt),
            "prebrief_txt": str(prebrief_txt),
            "npc_json": str(npc_json),
        },
    }

    out_dir = Path("docs") / "briefs"
    out_dir.mkdir(parents=True, exist_ok=True)

    latest = out_dir / "briefing_runbook_consistency_latest.json"
    stamped = out_dir / f"briefing_runbook_consistency_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    stamped.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(json.dumps({"verdict": verdict, "latest": str(latest), "stamped": str(stamped)}, indent=2))
    return out


if __name__ == "__main__":
    main()

