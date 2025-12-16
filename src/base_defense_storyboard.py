"""
base_defense_storyboard.py

Week-2 Base Defense — Base Defense Storyboard

Goal:
- Flawless outputs without perfect inputs
- Standardized outputs to docs/base_defense (latest + stamped)
- Legacy compatibility outputs maintained in src/docs (JSON + TXT)

Outputs (standard):
- docs/base_defense/base_defense_storyboard_latest.json
- docs/base_defense/base_defense_storyboard_latest.txt
- docs/base_defense/base_defense_storyboard_<timestamp>.json
- docs/base_defense/base_defense_storyboard_<timestamp>.txt

Legacy outputs (back-compat):
- src/docs/base_defense_storyboard.json
- src/docs/base_defense_storyboard.txt
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


OUT_DIR = Path("docs") / "base_defense"
LEGACY_DIR = Path("src") / "docs"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, obj: Any) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _write_txt(path: Path, text: str) -> None:
    _safe_mkdir(path.parent)
    path.write_text(text, encoding="utf-8")


def _bounded_lines() -> List[str]:
    # These tokens are REQUIRED by Week-2 hardening posture (same spirit as nuclear prebrief rules)
    return [
        "Assessment is probabilistic and bounded; operator judgment applies.",
        "This storyboard summarizes security posture under incomplete or noisy inputs.",
        "Do not infer intent. Confirm with operator judgment and additional collection.",
    ]


def _render_txt(rpt: Dict[str, Any]) -> str:
    summary = rpt.get("summary", {}) if isinstance(rpt.get("summary", {}), dict) else {}
    posture = summary.get("posture", "ROUTINE_MONITORING")
    confidence = summary.get("confidence", "LOW")
    notes = rpt.get("notes", [])
    if not isinstance(notes, list):
        notes = []

    lines: List[str] = []
    lines.append("Base Defense Storyboard")
    lines.append(f"generated_at_utc: {rpt.get('generated_at_utc', _utc_now_iso())}")
    lines.append("")
    lines.append(f"posture: {posture}")
    lines.append(f"confidence: {confidence}")
    lines.append("")
    lines.append("Bounded guidance:")
    for b in _bounded_lines():
        lines.append(f"- {b}")
    lines.append("")
    if notes:
        lines.append("Notes:")
        for n in notes[:50]:
            lines.append(f"- {str(n)}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def build_base_defense_storyboard() -> Dict[str, Any]:
    """
    SAFE: This is a training/demo storyboard, not a real base-defense system.
    Keep it bounded, explain uncertainty, and require operator judgment.

    This function must not crash on missing inputs.
    """
    # Minimal, resilient default output.
    rpt: Dict[str, Any] = {
        "generated_at_utc": _utc_now_iso(),
        "safe_notice": "Synthetic / training-only artifact. Not real-world operational telemetry.",
        "summary": {
            "posture": "ROUTINE_MONITORING",
            "confidence": "LOW",
        },
        "bounded_statements": _bounded_lines(),
        "notes": [
            "If inputs are missing or noisy, maintain bounded posture and escalate only with operator judgment.",
        ],
    }
    return rpt


def write_base_defense_storyboard(rpt: Dict[str, Any]) -> Dict[str, str]:
    ts = _ts()

    json_latest = OUT_DIR / "base_defense_storyboard_latest.json"
    txt_latest = OUT_DIR / "base_defense_storyboard_latest.txt"
    json_stamped = OUT_DIR / f"base_defense_storyboard_{ts}.json"
    txt_stamped = OUT_DIR / f"base_defense_storyboard_{ts}.txt"

    legacy_json = LEGACY_DIR / "base_defense_storyboard.json"
    legacy_txt = LEGACY_DIR / "base_defense_storyboard.txt"

    _write_json(json_latest, rpt)
    _write_txt(txt_latest, _render_txt(rpt))
    _write_json(json_stamped, rpt)
    _write_txt(txt_stamped, _render_txt(rpt))

    # Legacy compatibility
    _write_json(legacy_json, rpt)
    _write_txt(legacy_txt, _render_txt(rpt))

    return {
        "json_latest": str(json_latest),
        "txt_latest": str(txt_latest),
        "json_stamped": str(json_stamped),
        "txt_stamped": str(txt_stamped),
        "legacy_json": str(legacy_json),
        "legacy_txt": str(legacy_txt),
    }


def main() -> None:
    rpt = build_base_defense_storyboard()
    paths = write_base_defense_storyboard(rpt)
    print(json.dumps(paths, indent=2))


if __name__ == "__main__":
    main()

