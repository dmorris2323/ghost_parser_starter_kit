from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from demo_lock import is_demo_locked, demo_lock_banner, enforce_demo_lock


# ============================
# PATHS
# ============================

BRIEFS_DIR = Path("docs") / "briefs"
VALIDATION_DIR = Path("docs") / "validation"

SRC_COMMANDER_BRIEF_TXT = BRIEFS_DIR / "commander_brief_latest.txt"
SRC_OPERATOR_SUMMARY_TXT = BRIEFS_DIR / "week3_operator_summary_latest.txt"
SRC_LEGAL_SNAPSHOT_TXT = BRIEFS_DIR / "legal_case_snapshot_latest.txt"
SRC_MOBILE_MANIFEST_JSON = BRIEFS_DIR / "mobile_enjoy_manifest_latest.json"
SRC_DEMO_PACK_GATE_JSON = VALIDATION_DIR / "week3_demo_pack_gate_latest.json"
SRC_FUSION_CORE_REGRESSION_TXT = VALIDATION_DIR / "fusion_core_regression_latest.txt"

OUT_LATEST_TXT = BRIEFS_DIR / "week3_demo_narrative_latest.txt"
OUT_LATEST_JSON = BRIEFS_DIR / "week3_demo_narrative_latest.json"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_read_txt(path: Path) -> Optional[str]:
    try:
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def _safe_read_json(path: Path) -> Optional[dict]:
    try:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write_txt(path: Path, txt: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(txt, encoding="utf-8")


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _present(path: Path) -> Dict[str, Any]:
    return {"path": str(path), "present": path.exists()}


def _head(s: Optional[str], max_lines: int = 18) -> str:
    if not s:
        return "MISSING"
    lines = [ln.rstrip() for ln in s.splitlines()]
    return "\n".join(lines[:max_lines]).strip()


def _build_blocks() -> List[Dict[str, str]]:
    """
    The demo script. Keep it bounded and commander-safe.
    No claims of real-world attribution. No intent inference.
    """
    blocks: List[Dict[str, str]] = []

    blocks.append(
        {
            "title": "0) Opening (10 seconds)",
            "say": (
                "This is a DEMO-LOCKED Ghost Lantern Labs briefing.\n"
                "Read-only. No baselines updated. No training mutations.\n"
                "Assessment is probabilistic and bounded; operator judgment applies."
            ),
            "do": "Open docs/briefs/week3_demo_narrative_latest.txt and read section 1–2.",
        }
    )

    blocks.append(
        {
            "title": "1) Proof of Control (10 seconds)",
            "say": (
                "First: I prove stability.\n"
                "The Fusion Core Regression Gate confirms key subsystems run without breaking."
            ),
            "do": "Open docs/validation/fusion_core_regression_latest.txt and read verdict lines.",
        }
    )

    blocks.append(
        {
            "title": "2) Commander Brief (30 seconds)",
            "say": (
                "Next: the commander brief.\n"
                "It survives missing inputs and still outputs a bounded posture statement."
            ),
            "do": "Open docs/briefs/commander_brief_latest.txt and read sections 1–5 only.",
        }
    )

    blocks.append(
        {
            "title": "3) Operator Summary (10 seconds)",
            "say": (
                "This is the 10-second checkpoint.\n"
                "It answers: did the core gate pass, yes or no."
            ),
            "do": "Open docs/briefs/week3_operator_summary_latest.txt and read the verdict line.",
        }
    )

    blocks.append(
        {
            "title": "4) Shari Hook (30 seconds)",
            "say": (
                "Here’s the legal snapshot so a non-technical professional can instantly relate.\n"
                "It shows the same safety pattern: bounded risk, ambiguity flags, operator judgment."
            ),
            "do": "Open docs/briefs/legal_case_snapshot_latest.txt and read the posture + ambiguity flags.",
        }
    )

    blocks.append(
        {
            "title": "5) Mobile Enjoy Mode (15 seconds)",
            "say": (
                "This is the 'enjoy what we built' view.\n"
                "It lists the demo artifacts and provides previews. Still read-only."
            ),
            "do": "Open docs/briefs/mobile_enjoy_manifest_latest.json and show the 'previews' section.",
        }
    )

    blocks.append(
        {
            "title": "6) Close (10 seconds)",
            "say": (
                "That’s the demo: stable gates, bounded brief outputs, and a relatable legal snapshot.\n"
                "Next step is making it prettier (GUI polish) without weakening safety controls."
            ),
            "do": "Stop. Do not change baselines during the demo.",
        }
    )

    return blocks


def run_week3_demo_narrative(context: str = "week3_demo_narrative_control") -> Dict[str, Any]:
    """
    Generate Week-3 demo narrative artifact (TXT + JSON, latest + stamped).
    Must never crash.
    """
    generated_at_utc = _utc_now_iso()
    stamp = _stamp()

    commander_txt = _safe_read_txt(SRC_COMMANDER_BRIEF_TXT)
    operator_txt = _safe_read_txt(SRC_OPERATOR_SUMMARY_TXT)
    legal_txt = _safe_read_txt(SRC_LEGAL_SNAPSHOT_TXT)
    fusion_gate_txt = _safe_read_txt(SRC_FUSION_CORE_REGRESSION_TXT)
    mobile_manifest = _safe_read_json(SRC_MOBILE_MANIFEST_JSON)
    demo_pack_gate = _safe_read_json(SRC_DEMO_PACK_GATE_JSON)

    blocks = _build_blocks()

    # Simple “read this first” header
    lines: List[str] = []
    lines.append("WEEK-3 DEMO NARRATIVE (COMMANDER-SAFE)")
    lines.append(f"generated_at_utc: {generated_at_utc}")
    lines.append(f"context: {context}")
    lines.append("")

    if is_demo_locked():
        lines.append(demo_lock_banner())
        lines.append("")

    lines.append("WHAT THIS DEMO IS:")
    lines.append("- A bounded, read-only demonstration of stability + briefing outputs.")
    lines.append("- No real-world attribution. No intent inference. Demo-safe synthetic posture.")
    lines.append("")

    lines.append("WHAT YOU WILL SHOW (IN ORDER):")
    for i, b in enumerate(blocks, start=1):
        lines.append(f"{i}. {b['title']}")
    lines.append("")

    lines.append("DEMO SCRIPT (WHAT TO SAY / WHAT TO OPEN):")
    for b in blocks:
        lines.append("")
        lines.append(b["title"])
        lines.append("Say:")
        lines.append(b["say"])
        lines.append("Do:")
        lines.append(b["do"])

    # Best-effort previews so you can read without opening everything
    lines.append("")
    lines.append("BEST-EFFORT PREVIEWS (FOR QUICK REHEARSAL):")
    lines.append("")
    lines.append("Fusion Core Regression Gate (head):")
    lines.append(_head(fusion_gate_txt))
    lines.append("")
    lines.append("Commander Brief (head):")
    lines.append(_head(commander_txt))
    lines.append("")
    lines.append("Week-3 Operator Summary (head):")
    lines.append(_head(operator_txt))
    lines.append("")
    lines.append("Legal Case Snapshot (head):")
    lines.append(_head(legal_txt))

    # Envelope for JSON
    result: Dict[str, Any] = {
        "generated_at_utc": generated_at_utc,
        "context": context,
        "artifacts": {
            "fusion_core_regression_txt": _present(SRC_FUSION_CORE_REGRESSION_TXT),
            "commander_brief_txt": _present(SRC_COMMANDER_BRIEF_TXT),
            "operator_summary_txt": _present(SRC_OPERATOR_SUMMARY_TXT),
            "legal_case_snapshot_txt": _present(SRC_LEGAL_SNAPSHOT_TXT),
            "mobile_enjoy_manifest_json": _present(SRC_MOBILE_MANIFEST_JSON),
            "week3_demo_pack_gate_json": _present(SRC_DEMO_PACK_GATE_JSON),
        },
        "previews": {
            "fusion_core_regression_head": _head(fusion_gate_txt),
            "commander_brief_head": _head(commander_txt),
            "operator_summary_head": _head(operator_txt),
            "legal_case_snapshot_head": _head(legal_txt),
        },
        "mobile_manifest_present": bool(mobile_manifest is not None),
        "demo_pack_gate_present": bool(demo_pack_gate is not None),
        "blocks": blocks,
    }

    if is_demo_locked():
        result["demo_notice"] = demo_lock_banner()
        result.update(enforce_demo_lock(context))

    # Write outputs (latest + stamped)
    stamped_txt = BRIEFS_DIR / f"week3_demo_narrative_{stamp}.txt"
    stamped_json = BRIEFS_DIR / f"week3_demo_narrative_{stamp}.json"

    txt_out = "\n".join(lines).rstrip() + "\n"
    _write_txt(OUT_LATEST_TXT, txt_out)
    _write_txt(stamped_txt, txt_out)
    _write_json(OUT_LATEST_JSON, result)
    _write_json(stamped_json, result)

    return {
        "generated_at_utc": generated_at_utc,
        "context": context,
        "txt_latest": str(OUT_LATEST_TXT),
        "json_latest": str(OUT_LATEST_JSON),
        "txt_stamped": str(stamped_txt),
        "json_stamped": str(stamped_json),
        "demo_locked": bool(is_demo_locked()),
    }


def main() -> int:
    out = run_week3_demo_narrative()
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

