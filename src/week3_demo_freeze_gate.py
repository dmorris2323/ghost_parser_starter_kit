# src/week3_demo_freeze_gate.py
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from demo_freeze_loader import load_demo_freeze_manifest, is_demo_safe


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


_THIS = Path(__file__).resolve()
SRC_DIR = _THIS.parent
REPO_ROOT = SRC_DIR.parent

VALIDATION_DIR = REPO_ROOT / "docs" / "validation"


def _write_json(p: Path, obj: Dict[str, Any]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _write_txt(p: Path, lines: List[str]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _exists(rel: str) -> bool:
    return (REPO_ROOT / rel).exists()


def _read_text(rel: str, limit: int = 12000) -> str:
    p = REPO_ROOT / rel
    if not p.exists():
        return ""
    s = p.read_text(encoding="utf-8", errors="replace")
    return s[:limit]


def run_week3_demo_freeze_gate(strict: bool = True) -> Dict[str, Any]:
    manifest = load_demo_freeze_manifest()
    demo_safe = is_demo_safe(manifest)
    banner = str(manifest.get("required_banner_text", "")).strip()

    required_files = list(manifest.get("required_files", [])) if isinstance(manifest.get("required_files"), list) else []
    optional_files = list(manifest.get("optional_files", [])) if isinstance(manifest.get("optional_files"), list) else []

    violations: List[str] = []

    if manifest.get("mode") != "DEMO_FREEZE":
        violations.append("MODE_NOT_DEMO_FREEZE")
    if not demo_safe:
        violations.append("DEMO_SAFE_FALSE")
    if not banner:
        violations.append("BANNER_TEXT_MISSING")

    missing_required: List[str] = []
    for rel in required_files:
        if not _exists(rel):
            missing_required.append(rel)
    if missing_required:
        violations.append("REQUIRED_FILES_MISSING")

    # Banner enforcement in key text outputs (only if demo_safe true)
    banner_checks: List[str] = []
    banner_ok_all = True
    if demo_safe and banner:
        key_txt = [
            "docs/briefs/commander_brief_latest.txt",
            "docs/briefs/legal_case_snapshot_latest.txt",
            "docs/briefs/week3_operator_summary_latest.txt",
            "docs/briefs/week3_demo_narrative_latest.txt",
        ]
        for rel in key_txt:
            txt = _read_text(rel)
            ok = banner in txt
            banner_checks.append(f"- {rel}: {'OK' if ok else 'MISSING_BANNER'}")
            if not ok:
                banner_ok_all = False
        if not banner_ok_all:
            violations.append("BANNER_NOT_PRESENT_IN_KEY_TXT")

    verdict = "PASS" if len(violations) == 0 else "FAIL"

    out = {
        "generated_at_utc": _utc_now_iso(),
        "context": "week3_demo_freeze_gate",
        "strict": bool(strict),
        "verdict": verdict,
        "demo_safe": demo_safe,
        "manifest_mode": manifest.get("mode"),
        "required_missing": missing_required,
        "optional_present": [rel for rel in optional_files if _exists(rel)],
        "violations": violations,
        "banner_checks": banner_checks,
        "manifest_path": "docs/demo/demo_freeze_manifest.json",
    }

    # write latest artifacts
    latest_json = VALIDATION_DIR / "week3_demo_freeze_gate_latest.json"
    latest_txt = VALIDATION_DIR / "week3_demo_freeze_gate_latest.txt"

    lines: List[str] = []
    lines.append(f"Verdict: {verdict}")
    lines.append("WEEK-3 DEMO FREEZE GATE")
    lines.append(f"generated_at_utc: {out['generated_at_utc']}")
    lines.append(f"demo_safe: {demo_safe}")
    lines.append(f"mode: {out.get('manifest_mode')}")
    lines.append("")
    if missing_required:
        lines.append("Missing required files:")
        for m in missing_required:
            lines.append(f"- {m}")
        lines.append("")
    if banner_checks:
        lines.append("Banner checks:")
        lines.extend(banner_checks)
        lines.append("")
    if violations:
        lines.append("Violations:")
        for v in violations:
            lines.append(f"- {v}")
        lines.append("")
    else:
        lines.append("No violations.")

    _write_json(latest_json, out)
    _write_txt(latest_txt, lines)

    return {
        "latest_json": str(latest_json),
        "latest_txt": str(latest_txt),
        "verdict": verdict,
        "violations": violations,
        "required_missing": missing_required,
    }


def main() -> int:
    res = run_week3_demo_freeze_gate(strict=True)
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

