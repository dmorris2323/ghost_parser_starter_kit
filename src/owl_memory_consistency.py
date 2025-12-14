# src/owl_memory_consistency.py
"""
owl_memory_consistency.py

Memory consistency checker for Spectral Owl.
This is a hardening tool: it does NOT require a specific memory backend.

It checks:
- critical training artifacts exist
- latest validation report exists
- crisis mode file is parseable
- optional: owl memory file presence (if used)

Outputs:
- docs/integrity/owl_memory_consistency.json
- docs/integrity/owl_memory_consistency_<timestamp>.json
- docs/integrity/owl_memory_consistency.txt
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


INTEGRITY_DIR = Path("docs") / "integrity"


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


def _exists(path: Path) -> bool:
    return path.exists() and path.is_file()


def run_owl_memory_consistency_check() -> Dict[str, Any]:
    """
    Returns a dict report and writes it to docs/integrity/.
    """
    # Known artifacts in your repo so far
    candidates = {
        "training_curve_latest": Path("src") / "docs" / "training" / "training_curve_latest.json",
        "training_feedback_latest": Path("src") / "docs" / "training" / "training_feedback_latest.json",
        "validation_latest": Path("src") / "docs" / "validation" / "fusion_validation_report.json",
        "crisis_mode": Path("docs") / "integrity" / "crisis_mode.json",
    }

    # Optional (if you later standardize owl memory storage)
    optional = {
        "owl_memory_optional": Path("docs") / "owl" / "owl_memory.json",
    }

    issues: List[str] = []
    present: Dict[str, bool] = {}

    for k, p in candidates.items():
        present[k] = _exists(p)
        if not present[k]:
            issues.append(f"Missing required artifact: {k} -> {p}")

    for k, p in optional.items():
        present[k] = _exists(p)  # optional, no issue if missing

    # Parse checks (only if present)
    parse_ok = True
    parse_errors: List[str] = []

    for k in ["training_curve_latest", "training_feedback_latest", "validation_latest", "crisis_mode"]:
        p = candidates[k]
        if _exists(p):
            try:
                json.loads(p.read_text(encoding="utf-8"))
            except Exception as e:
                parse_ok = False
                parse_errors.append(f"Parse error for {k}: {e.__class__.__name__}: {e}")

    status = "PASS" if (len(issues) == 0 and parse_ok) else "FAIL"

    report = {
        "report": "owl_memory_consistency",
        "generated_at": _utc_now_iso(),
        "status": status,
        "present": present,
        "issues": issues,
        "parse_ok": parse_ok,
        "parse_errors": parse_errors,
        "recommendations": [
            "If FAIL: fix missing artifacts first, then rerun check.",
            "Keep crisis_mode_flag stable; many systems depend on it.",
            "Standardize owl memory path later (post-Day 100 sprint) if needed.",
        ],
        "paths_checked": {k: str(v) for k, v in {**candidates, **optional}.items()},
    }

    stamped = INTEGRITY_DIR / f"owl_memory_consistency_{_ts()}.json"
    latest = INTEGRITY_DIR / "owl_memory_consistency.json"
    txt = INTEGRITY_DIR / "owl_memory_consistency.txt"

    _write_json(latest, report)
    _write_json(stamped, report)

    lines = [
        "OBASI / SPECTRAL OWL — MEMORY CONSISTENCY CHECK",
        f"Status: {status}",
        f"Generated: {report['generated_at']}",
        "",
        "Required artifacts:",
    ]
    for k in candidates:
        lines.append(f"- {k}: {'OK' if present[k] else 'MISSING'} ({candidates[k]})")

    if parse_errors:
        lines.append("")
        lines.append("Parse errors:")
        lines.extend([f"- {e}" for e in parse_errors])

    if issues:
        lines.append("")
        lines.append("Issues:")
        lines.extend([f"- {i}" for i in issues])

    _write_txt(txt, "\n".join(lines) + "\n")

    return report


if __name__ == "__main__":
    r = run_owl_memory_consistency_check()
    print(json.dumps(r, indent=2))

