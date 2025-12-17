from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from demo_lock import is_demo_locked, demo_lock_banner, enforce_demo_lock

BRIEFS_DIR = Path("docs") / "briefs"
VALIDATION_DIR = Path("docs") / "validation"

SRC_READINESS = VALIDATION_DIR / "week3_demo_readiness_gate_latest.json"
SRC_DEMO_PACK = VALIDATION_DIR / "week3_demo_pack_gate_latest.json"
SRC_FUSION_CORE = VALIDATION_DIR / "fusion_core_regression_latest.json"
SRC_OPERATOR_SUMMARY = BRIEFS_DIR / "week3_operator_summary_latest.txt"
SRC_LEGAL_SNAPSHOT = BRIEFS_DIR / "legal_case_snapshot_latest.txt"
SRC_COMMANDER_BRIEF = BRIEFS_DIR / "commander_brief_latest.txt"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _ensure_parent(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)


def _read_json_best_effort(p: Path) -> Optional[dict]:
    try:
        if not p.exists():
            return None
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _read_txt_best_effort(p: Path) -> str:
    try:
        if not p.exists():
            return ""
        return p.read_text(encoding="utf-8")
    except Exception:
        return ""


def _write_txt(p: Path, s: str) -> None:
    _ensure_parent(p)
    p.write_text(s, encoding="utf-8")


def _write_json(p: Path, obj: Any) -> None:
    _ensure_parent(p)
    p.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _presence_line(label: str, p: Path) -> str:
    return f"- {label}: {'OK' if p.exists() else 'MISSING'} ({p.as_posix()})"


def build_week3_demo_narrative(context: str = "week3_demo_narrative") -> Dict[str, Any]:
    """
    Builds a commander-safe narrative script for the Shari demo.
    Never crashes. Best-effort reads only.
    """
    generated_at = _utc_now_iso()

    readiness = _read_json_best_effort(SRC_READINESS) or {}
    demo_pack = _read_json_best_effort(SRC_DEMO_PACK) or {}
    fusion_core = _read_json_best_effort(SRC_FUSION_CORE) or {}

    readiness_verdict = readiness.get("verdict", "UNKNOWN")
    demo_pack_verdict = demo_pack.get("verdict", "UNKNOWN")
    fusion_core_verdict = fusion_core.get("verdict", "UNKNOWN")

    # “Headlines” from existing text artifacts (best effort)
    op_summary_head = _read_txt_best_effort(SRC_OPERATOR_SUMMARY).strip().splitlines()[:6]
    legal_head = _read_txt_best_effort(SRC_LEGAL_SNAPSHOT).strip().splitlines()[:18]
    commander_head = _read_txt_best_effort(SRC_COMMANDER_BRIEF).strip().splitlines()[:28]

    # Demo lock info (read-only, safe)
    lock_info = enforce_demo_lock(context) if is_demo_locked() else {"demo_lock": False}

    narrative_lines: List[str] = []
    narrative_lines.append("WEEK-3 DEMO NARRATIVE (COMMANDER-SAFE)")
    narrative_lines.append(f"generated_at_utc: {generated_at}")
    narrative_lines.append(f"context: {context}")
    narrative_lines.append("")
    narrative_lines.append("MISSION: Show a locked, read-only GLL demo that feels like a real command center.")
    narrative_lines.append("RULE: No baselines updated. No training. No mutation. Operator judgment applies.")
    narrative_lines.append("")

    narrative_lines.append("=== 0) OPENING (10 seconds) ===")
    narrative_lines.append("“This is Ghost Lantern Labs — a fusion platform designed to output bounded, operator-safe products.”")
    narrative_lines.append("“Today’s demo is demo-locked: read-only, no learning, no changes.”")
    narrative_lines.append("")

    narrative_lines.append("=== 1) READINESS STATUS (10 seconds) ===")
    narrative_lines.append(f"- Demo Readiness Gate: {readiness_verdict}")
    narrative_lines.append(f"- Demo Pack Gate: {demo_pack_verdict}")
    narrative_lines.append(f"- Fusion Core Regression: {fusion_core_verdict}")
    narrative_lines.append("")

    narrative_lines.append("=== 2) OPERATOR SUMMARY (10 seconds) ===")
    if op_summary_head:
        narrative_lines.append("Read:")
        for ln in op_summary_head:
            narrative_lines.append(f"  {ln}")
    else:
        narrative_lines.append("Operator summary is missing; proceed with commander brief + legal snapshot.")
    narrative_lines.append("")

    narrative_lines.append("=== 3) COMMANDER BRIEF (20–30 seconds) ===")
    narrative_lines.append("Goal: bounded posture + what changed/why/known/unknown/recommendation.")
    if commander_head:
        narrative_lines.append("Preview (first lines):")
        for ln in commander_head:
            narrative_lines.append(f"  {ln}")
    else:
        narrative_lines.append("Commander brief missing; regenerate via orchestrator/command_brief_exporter.")
    narrative_lines.append("")

    narrative_lines.append("=== 4) SHARI HOOK — LEGAL SNAPSHOT (20 seconds) ===")
    narrative_lines.append("Goal: show a familiar domain output (collections-style snapshot) with ambiguity flags and posture.")
    if legal_head:
        narrative_lines.append("Preview (first lines):")
        for ln in legal_head:
            narrative_lines.append(f"  {ln}")
    else:
        narrative_lines.append("Legal snapshot missing; regenerate via legal_case_snapshot.py.")
    narrative_lines.append("")

    narrative_lines.append("=== 5) WHAT THIS PROVES (10 seconds) ===")
    narrative_lines.append("- The system can generate multiple mission products from the same “truth layer” artifacts.")
    narrative_lines.append("- Everything is bounded, operator-safe, and resilient to missing inputs.")
    narrative_lines.append("- Demo lock prevents accidental learning or mutation during a stakeholder demo.")
    narrative_lines.append("")

    narrative_lines.append("=== 6) CLOSE (5 seconds) ===")
    narrative_lines.append("“This is a controlled demo. In real ops, products are still bounded; operator judgment remains mandatory.”")
    narrative_lines.append("Assessment is probabilistic and bounded; operator judgment applies.")
    narrative_lines.append("")

    narrative_lines.append("=== PRESENCE CHECKS (for you, not for the demo) ===")
    narrative_lines.append(_presence_line("week3_demo_readiness_gate_latest.json", SRC_READINESS))
    narrative_lines.append(_presence_line("week3_demo_pack_gate_latest.json", SRC_DEMO_PACK))
    narrative_lines.append(_presence_line("fusion_core_regression_latest.json", SRC_FUSION_CORE))
    narrative_lines.append(_presence_line("week3_operator_summary_latest.txt", SRC_OPERATOR_SUMMARY))
    narrative_lines.append(_presence_line("commander_brief_latest.txt", SRC_COMMANDER_BRIEF))
    narrative_lines.append(_presence_line("legal_case_snapshot_latest.txt", SRC_LEGAL_SNAPSHOT))

    if is_demo_locked():
        narrative_lines.append("")
        narrative_lines.append(demo_lock_banner())

    result: Dict[str, Any] = {
        "generated_at_utc": generated_at,
        "context": context,
        "readiness_verdict": readiness_verdict,
        "demo_pack_verdict": demo_pack_verdict,
        "fusion_core_verdict": fusion_core_verdict,
        "paths": {
            "latest_txt": str(BRIEFS_DIR / "week3_demo_narrative_latest.txt"),
        },
        "notes": [
            "Commander-safe, bounded narrative for stakeholder demo.",
            "Read-only: no baselines updated. No training. No mutation.",
        ],
    }
    result.update(lock_info)
    return {"text": "\n".join(narrative_lines) + "\n", "json": result}


def write_week3_demo_narrative() -> Dict[str, str]:
    payload = build_week3_demo_narrative()
    txt = payload["text"]
    res = payload["json"]

    latest_txt = BRIEFS_DIR / "week3_demo_narrative_latest.txt"
    stamped_txt = BRIEFS_DIR / f"week3_demo_narrative_{_stamp()}.txt"
    latest_json = BRIEFS_DIR / "week3_demo_narrative_latest.json"
    stamped_json = BRIEFS_DIR / f"week3_demo_narrative_{_stamp()}.json"

    _write_txt(latest_txt, txt)
    _write_txt(stamped_txt, txt)
    _write_json(latest_json, res)
    _write_json(stamped_json, res)

    return {
        "txt_latest": str(latest_txt),
        "txt_stamped": str(stamped_txt),
        "json_latest": str(latest_json),
        "json_stamped": str(stamped_json),
    }


def main() -> int:
    out = write_week3_demo_narrative()
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

