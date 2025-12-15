"""
sps_mutation_guard.py

SPS Mutation Guard
- Watches for suspicious/undesired changes in the repo (local filesystem)
- Produces an allowlist-based drift report without blocking development
- Can be used as a pre-run / post-run sanity gate for training + validation

Design intent:
- Detect "quiet sabotage" (unexpected changes to critical code paths)
- Detect accidental regressions (file moved/duplicated, surprise new files)
- Track changes in a lightweight, audit-friendly way

SAFE: local scanning only. No network. No destructive actions.
"""

from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


GUARD_DIR = Path("docs") / "integrity"
BASELINE = GUARD_DIR / "mutation_guard_baseline.json"
JSON_OUT = GUARD_DIR / "sps_mutation_guard.json"
TXT_OUT = GUARD_DIR / "sps_mutation_guard.txt"

# Where code is allowed to live (transitional duplicates tolerated).
ALLOWED_ROOTS = [
    Path("src"),
    Path("src") / "apps" / "gui",
    Path("apps") / "gui",  # transitional mirror (you’ve got duplicates today)
    Path("apps"),
]

# Paths we never care about (noise)
IGNORE_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
}

IGNORE_SUFFIXES = {
    ".pyc", ".pyo", ".pyd",
    ".DS_Store",
    ".log",
}

CRITICAL_FILES = [
    Path("src") / "ghost_cli.py",
    Path("src") / "fusion_trust.py",
    Path("src") / "operator_safety_layer.py",
    Path("src") / "training_curve_engine.py",
    Path("src") / "difficulty_scaling_engine.py",
    Path("src") / "fusion_validation_harness.py",
]

MAX_FILE_MB = 2  # don’t hash huge artifacts; this is a code integrity tool


@dataclass
class Finding:
    level: str  # INFO / WARN / FAIL
    category: str
    message: str
    details: Optional[Dict[str, Any]] = None


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _is_ignored(path: Path) -> bool:
    parts = set(path.parts)
    if parts & IGNORE_DIRS:
        return True
    if path.suffix in IGNORE_SUFFIXES:
        return True
    return False


def _iter_code_files() -> List[Path]:
    files: List[Path] = []
    for root in ALLOWED_ROOTS:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if _is_ignored(p):
                continue
            # Track python + markdown + json as "integrity relevant"
            if p.suffix.lower() in {".py", ".md", ".json", ".html", ".txt"}:
                # Skip large artifacts
                try:
                    if p.stat().st_size > MAX_FILE_MB * 1024 * 1024:
                        continue
                except Exception:
                    continue
                files.append(p)
    return sorted(set(files))


def _snapshot() -> Dict[str, str]:
    snap: Dict[str, str] = {}
    for p in _iter_code_files():
        try:
            snap[str(p)] = _sha256_file(p)
        except Exception:
            snap[str(p)] = "HASH_ERROR"
    return snap


def _load_baseline() -> Optional[Dict[str, Any]]:
    if not BASELINE.exists():
        return None
    try:
        return json.loads(BASELINE.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write_json(path: Path, obj: Any) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    _safe_mkdir(path.parent)
    path.write_text(text, encoding="utf-8")


def _critical_health(findings: List[Finding]) -> str:
    if any(f.level == "FAIL" for f in findings):
        return "FAIL"
    if any(f.level == "WARN" for f in findings):
        return "WARN"
    return "PASS"


def run_sps_mutation_guard(update_baseline: bool = False) -> Dict[str, Any]:
    """
    Run mutation guard.
    update_baseline=True sets the baseline to current snapshot (use after review).
    """
    _safe_mkdir(GUARD_DIR)

    current = _snapshot()
    base = _load_baseline()

    findings: List[Finding] = []

    # Baseline creation
    if base is None:
        _write_json(BASELINE, {"generated_at": _utc_now_iso(), "snapshot": current})
        findings.append(Finding(
            level="WARN",
            category="baseline",
            message="Baseline created (first run). Re-run to detect drift.",
            details={"baseline_path": str(BASELINE), "tracked_files": len(current)},
        ))
        status = _critical_health(findings)
        report = _build_report(status, findings, current, baseline=None)
        _write_json(JSON_OUT, report)
        _write_text(TXT_OUT, _render_txt(report))
        return report

    baseline_snapshot = base.get("snapshot", {})
    baseline_files: Set[str] = set(baseline_snapshot.keys())
    current_files: Set[str] = set(current.keys())

    added = sorted(current_files - baseline_files)
    removed = sorted(baseline_files - current_files)

    changed: Dict[str, Dict[str, str]] = {}
    for k in sorted(current_files & baseline_files):
        if current.get(k) != baseline_snapshot.get(k):
            changed[k] = {"baseline": baseline_snapshot.get(k), "current": current.get(k)}

    if added:
        findings.append(Finding(
            level="WARN",
            category="filesystem",
            message=f"New tracked files detected: {len(added)}",
            details={"added": added[:100]},
        ))
    if removed:
        findings.append(Finding(
            level="WARN",
            category="filesystem",
            message=f"Tracked files removed/moved: {len(removed)}",
            details={"removed": removed[:100]},
        ))
    if changed:
        findings.append(Finding(
            level="WARN",
            category="drift",
            message=f"Content drift detected in tracked files: {len(changed)}",
            details={"changed": dict(list(changed.items())[:50])},
        ))

    # Critical file presence + hash
    for cf in CRITICAL_FILES:
        if not cf.exists():
            findings.append(Finding(
                level="FAIL",
                category="critical",
                message=f"Critical file missing: {cf}",
                details={"path": str(cf)},
            ))
        else:
            findings.append(Finding(
                level="INFO",
                category="critical",
                message=f"Critical file present: {cf}",
                details={"path": str(cf)},
            ))

    status = _critical_health(findings)

    report = _build_report(status, findings, current, baseline={"path": str(BASELINE), "generated_at": base.get("generated_at")})

    if update_baseline:
        _write_json(BASELINE, {"generated_at": _utc_now_iso(), "snapshot": current})
        report["baseline_updated"] = True

    _write_json(JSON_OUT, report)
    _write_text(TXT_OUT, _render_txt(report))
    return report


def _build_report(status: str, findings: List[Finding], current_snapshot: Dict[str, str], baseline: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "report_version": 1,
        "generated_at": _utc_now_iso(),
        "status": status,
        "safe_notice": "Local drift/mutation report only. No network. No destructive actions.",
        "baseline": baseline,
        "counts": {
            "info": sum(1 for f in findings if f.level == "INFO"),
            "warn": sum(1 for f in findings if f.level == "WARN"),
            "fail": sum(1 for f in findings if f.level == "FAIL"),
            "total_findings": len(findings),
            "tracked_files": len(current_snapshot),
        },
        "findings": [asdict(f) for f in findings],
        "paths": {
            "json": str(JSON_OUT),
            "txt": str(TXT_OUT),
            "baseline": str(BASELINE),
        },
        "recommendations": [
            "If FAIL: stop feature work, restore missing critical files, re-run guard.",
            "If WARN: review drift list; accept changes only if intentional.",
            "After intentional refactors: rerun with update_baseline=True.",
        ],
    }


def _render_txt(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("SPS MUTATION GUARD")
    lines.append("=" * 28)
    lines.append(f"Generated: {report.get('generated_at')}")
    lines.append(f"Status:    {report.get('status')}")
    c = report.get("counts", {})
    lines.append(f"Findings:  INFO={c.get('info')} WARN={c.get('warn')} FAIL={c.get('fail')} TOTAL={c.get('total_findings')}")
    lines.append(f"Tracked files: {c.get('tracked_files')}")
    lines.append("")
    b = report.get("baseline") or {}
    if b:
        lines.append(f"Baseline: {b.get('path')} (generated {b.get('generated_at')})")
    else:
        lines.append("Baseline: created on first run.")
    if report.get("baseline_updated"):
        lines.append("Baseline updated: YES")
    lines.append("")
    lines.append("Findings:")
    for f in report.get("findings", []):
        lines.append(f"  [{f.get('level')}] {f.get('category')} — {f.get('message')}")
    lines.append("")
    lines.append("Outputs:")
    lines.append(f"  JSON: {report.get('paths', {}).get('json')}")
    lines.append(f"  TXT:  {report.get('paths', {}).get('txt')}")
    lines.append(f"  BASE: {report.get('paths', {}).get('baseline')}")
    return "\n".join(lines)


if __name__ == "__main__":
    out = run_sps_mutation_guard(update_baseline=False)
    print(json.dumps(out, indent=2))

