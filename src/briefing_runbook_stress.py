from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _has_text(s: Any) -> bool:
    return isinstance(s, str) and len(s.strip()) > 0


def _bounded_posture(posture: str) -> bool:
    # Bound the runbook output to known safe postures only
    allowed = {
        "ROUTINE_MONITORING",
        "DUTY_OFFICER_NOTIFY",
        "SECURITY_FORCES_DISPATCH",
        "NATIONAL_COMMAND_ALERT",
    }
    return posture in allowed


@dataclass
class StressResult:
    generated_at_utc: str
    verdict: str
    runs: int
    crashes: int
    violations: List[str]


def run_stress(runs: int = 12) -> Dict[str, Any]:
    """
    Stress the one-shot entrypoint across multiple contexts.
    Requirements:
      - no crash
      - returns structured dict
      - if a posture is present anywhere in the one-shot products, it must be bounded
      - must include at least one readable text preview somewhere (commander brief OR consistency outputs)
    """
    from briefing_runbook import run_commander_brief_one_shot

    crashes = 0
    violations: List[str] = []

    for i in range(runs):
        # vary context a bit; do NOT update baselines
        ctx = f"day72_runbook_stress_{i}_{random.randint(1000, 9999)}"

        try:
            res = run_commander_brief_one_shot(context=ctx, update_baselines=False)
        except Exception as e:
            crashes += 1
            violations.append(f"CRASH:{type(e).__name__}:{e}")
            continue

        if not isinstance(res, dict):
            violations.append("NON_DICT_RESULT")
            continue

        # Look for any posture field we can find (best-effort)
        posture_candidates: List[str] = []
        npc = (res.get("nuclear_product_consistency") or {}).get("json_obj") or {}
        wb = (npc.get("inputs") or {}).get("watchboard") or {}
        # various possible locations depending on how your gate formats output
        for path in [
            ("npc", npc.get("posture")),
            ("npc", (npc.get("decision_card") or {}).get("escalation", {}).get("posture")),
            ("watchboard", wb.get("posture")),
        ]:
            if isinstance(path[1], str):
                posture_candidates.append(path[1])

        for p in posture_candidates:
            if not _bounded_posture(p):
                violations.append(f"UNBOUNDED_POSTURE:{p}")

        # Require at least one readable preview text
        brief_prev = (res.get("commander_brief") or {}).get("preview_txt")
        npc_prev = (res.get("nuclear_product_consistency") or {}).get("preview_txt")
        if not (_has_text(brief_prev) or _has_text(npc_prev)):
            violations.append("MISSING_TEXT_PREVIEW")

        # Gates should be dict-shaped even if they fail
        gates = res.get("gates")
        if not isinstance(gates, dict):
            violations.append("MISSING_GATES_DICT")

    verdict = "PASS" if (crashes == 0 and len(violations) == 0) else "FAIL"
    out = StressResult(
        generated_at_utc=_utc_now_iso(),
        verdict=verdict,
        runs=runs,
        crashes=crashes,
        violations=violations,
    ).__dict__

    # Write latest artifact (docs/nuclear is fine, but we’ll keep this under docs/briefs since it’s briefing surface)
    from pathlib import Path

    out_dir = Path("docs") / "briefs"
    out_dir.mkdir(parents=True, exist_ok=True)
    latest = out_dir / "briefing_runbook_stress_latest.json"
    stamped = out_dir / f"briefing_runbook_stress_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    latest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    stamped.write_text(json.dumps(out, indent=2), encoding="utf-8")

    return {
        "verdict": verdict,
        "latest": str(latest),
        "stamped": str(stamped),
        "crashes": crashes,
        "violations_count": len(violations),
    }


if __name__ == "__main__":
    print(json.dumps(run_stress(runs=12), indent=2))

