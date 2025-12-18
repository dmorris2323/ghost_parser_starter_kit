# src/week3_demo_freeze_gate.py
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from demo_freeze_loader import load_demo_freeze_manifest, is_demo_safe


REPO_ROOT = Path(__file__).resolve().parent.parent
VALIDATION_DIR = REPO_ROOT / "docs" / "validation"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(p: Path, obj: Dict[str, Any]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _write_txt(p: Path, lines: List[str]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_week3_demo_freeze_gate() -> Dict[str, Any]:
    manifest = load_demo_freeze_manifest()
    demo_safe = is_demo_safe(manifest)

    violations: List[str] = []
    if not demo_safe:
        violations.append("DEMO_SAFE_FALSE")

    out: Dict[str, Any] = {
        "generated_at_utc": _utc_now_iso(),
        "context": "week3_demo_freeze_gate",
        "verdict": "PASS" if len(violations) == 0 else "FAIL",
        "violations": violations,
        "required_missing": [],
        "demo_safe": demo_safe,
        "mode": (manifest.get("mode") or "").strip(),
        "loaded_from": manifest.get("_loaded_from", "UNKNOWN"),
        "manifest_demo_safe_value": manifest.get("demo_safe"),
        "banner_len": len((manifest.get("required_banner_text") or "").strip()),
    }

    latest_json = VALIDATION_DIR / "week3_demo_freeze_gate_latest.json"
    latest_txt = VALIDATION_DIR / "week3_demo_freeze_gate_latest.txt"

    txt_lines: List[str] = []
    txt_lines.append(f"Verdict: {out['verdict']}")
    txt_lines.append("WEEK-3 DEMO FREEZE GATE")
    txt_lines.append(f"generated_at_utc: {out['generated_at_utc']}")
    txt_lines.append(f"demo_safe: {out['demo_safe']}")
    txt_lines.append(f"mode: {out['mode']}")
    txt_lines.append(f"loaded_from: {out['loaded_from']}")
    txt_lines.append(f"manifest demo_safe value: {out['manifest_demo_safe_value']}")
    txt_lines.append(f"banner_len: {out['banner_len']}")
    txt_lines.append("")
    if violations:
        txt_lines.append("Violations:")
        for v in violations:
            txt_lines.append(f"- {v}")

    _write_json(latest_json, out)
    _write_txt(latest_txt, txt_lines)

    return {
        "latest_json": str(latest_json),
        "latest_txt": str(latest_txt),
        "verdict": out["verdict"],
        "violations": out["violations"],
        "required_missing": out["required_missing"],
    }


def main() -> int:
    res = run_week3_demo_freeze_gate()
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

