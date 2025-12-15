"""
system_integrity_sentinel.py

GLL System Integrity Sentinel (SIS)
- Verifies core modules exist and import cleanly
- Verifies expected callable functions exist (best-effort / tolerant)
- Verifies key directories are writable
- Records and compares file hashes for critical paths (drift detection)
- Writes JSON + TXT reports to src/docs/integrity/

SAFE: local self-check only. No network. No destructive actions.
"""

from __future__ import annotations

import importlib
import json
import os
import time
import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ---------- Config (tight, conservative) ----------

CRITICAL_MODULES: List[str] = [
    # Core fusion + readiness + safety
    "fusion_ingest",
    "fusion_sanitizer",
    "fusion_scoring",
    "fusion_alerts",
    "commander_extract",
    "fusion_heat_index",
    "fusion_temporal_forecast",
    "fusion_trust",
    "operator_safety_layer",
    "operator_identity",
    "system_integrity_report",
    "gll_readiness",
    # Training/validation stack (synthetic)
    "synthetic_signal_generator",
    "pattern_injection_engine",
    "difficulty_scaling_engine",
    "training_curve_engine",
    "training_session_store",
    "scenario_engine",
    "instructor_rubric_autograder",
    "fusion_validation_harness",
    # SPS hardening layer (may be evolving)
    "sps_mutation_watcher",
    "sps_behavior_monitor",
]

# “Expected functions” are best-effort checks — modules may evolve; we tolerate missing.
EXPECTED_FUNCTIONS: Dict[str, List[str]] = {
    "fusion_trust": ["compute_trust", "compute_fusion_trust"],
    "operator_safety_layer": ["compute_osl", "compute_operator_safety_layer"],
    "operator_identity": ["get_operator", "read_operator", "operator_name"],
    "training_curve_engine": ["compute_training_curve"],
    "training_session_store": ["append_training_session", "load_sessions"],
    "scenario_engine": ["generate_scenario"],
    "difficulty_scaling_engine": ["normalize_difficulty"],
    "fusion_validation_harness": ["run_synthetic_fusion_validation"],
}

# Hash drift: the few files that must not “quietly” change without you knowing.
HASH_GLOBS: List[str] = [
    "ghost_cli.py",
    "fusion_trust.py",
    "operator_safety_layer.py",
    "crisis_mode_flag.py",
    "training_curve_engine.py",
    "difficulty_scaling_engine.py",
    "fusion_validation_harness.py",
    "synthetic_signal_generator.py",
    "pattern_injection_engine.py",
    "scenario_engine.py",
    "training_session_store.py",
]

# Output paths
INTEGRITY_DIR = Path("docs") / "integrity"
BASELINE_HASHES = INTEGRITY_DIR / "baseline_hashes.json"
JSON_OUT = INTEGRITY_DIR / "system_integrity_sentinel.json"
TXT_OUT = INTEGRITY_DIR / "system_integrity_sentinel.txt"


# ---------- Data structures ----------

@dataclass
class CheckItem:
    name: str
    status: str  # PASS / WARN / FAIL
    message: str
    details: Optional[Dict[str, Any]] = None


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _write_text(path: Path, text: str) -> None:
    _safe_mkdir(path.parent)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, obj: Any) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _try_import(module_name: str) -> Tuple[bool, str]:
    try:
        importlib.import_module(module_name)
        return True, "import_ok"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def _find_any_callable(mod: Any, names: List[str]) -> Tuple[bool, Optional[str]]:
    for n in names:
        if hasattr(mod, n) and callable(getattr(mod, n)):
            return True, n
    return False, None


def _check_modules() -> List[CheckItem]:
    items: List[CheckItem] = []
    for m in CRITICAL_MODULES:
        ok, msg = _try_import(m)
        if ok:
            items.append(CheckItem(name=f"module:{m}", status="PASS", message="Imported successfully."))
        else:
            items.append(CheckItem(name=f"module:{m}", status="FAIL", message=msg))
    return items


def _check_expected_functions() -> List[CheckItem]:
    items: List[CheckItem] = []
    for mod_name, fn_list in EXPECTED_FUNCTIONS.items():
        try:
            mod = importlib.import_module(mod_name)
            ok, chosen = _find_any_callable(mod, fn_list)
            if ok:
                items.append(CheckItem(
                    name=f"functions:{mod_name}",
                    status="PASS",
                    message=f"Found callable: {chosen}",
                    details={"expected": fn_list, "found": chosen},
                ))
            else:
                items.append(CheckItem(
                    name=f"functions:{mod_name}",
                    status="WARN",
                    message="No expected callable found (module may be mid-refactor).",
                    details={"expected": fn_list, "found": None},
                ))
        except Exception as e:
            items.append(CheckItem(
                name=f"functions:{mod_name}",
                status="FAIL",
                message=f"{type(e).__name__}: {e}",
                details={"expected": fn_list},
            ))
    return items


def _check_writable_dirs() -> List[CheckItem]:
    items: List[CheckItem] = []
    dirs = [
        Path("docs"),
        Path("docs") / "training",
        Path("docs") / "validation",
        Path("docs") / "synthetic",
        Path("docs") / "integrity",
    ]
    for d in dirs:
        try:
            _safe_mkdir(d)
            probe = d / f".write_probe_{int(time.time())}.tmp"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
            items.append(CheckItem(name=f"writable:{d.as_posix()}", status="PASS", message="Writable."))
        except Exception as e:
            items.append(CheckItem(name=f"writable:{d.as_posix()}", status="FAIL", message=f"{type(e).__name__}: {e}"))
    return items


def _build_hash_snapshot() -> Dict[str, str]:
    snap: Dict[str, str] = {}
    base = Path(".")
    for g in HASH_GLOBS:
        p = base / g
        if p.exists() and p.is_file():
            snap[str(p)] = _sha256_file(p)
        else:
            snap[str(p)] = "MISSING"
    return snap


def _check_hash_drift() -> CheckItem:
    _safe_mkdir(INTEGRITY_DIR)
    current = _build_hash_snapshot()

    if not BASELINE_HASHES.exists():
        _write_json(BASELINE_HASHES, {"generated_at": _utc_now_iso(), "hashes": current})
        return CheckItem(
            name="hash_drift",
            status="WARN",
            message="Baseline hashes created (first run). Re-run to detect drift.",
            details={"baseline_path": str(BASELINE_HASHES)},
        )

    try:
        baseline_obj = json.loads(BASELINE_HASHES.read_text(encoding="utf-8"))
        baseline = baseline_obj.get("hashes", {})
    except Exception as e:
        return CheckItem(
            name="hash_drift",
            status="FAIL",
            message=f"Failed to read baseline hashes: {type(e).__name__}: {e}",
            details={"baseline_path": str(BASELINE_HASHES)},
        )

    changed: Dict[str, Dict[str, str]] = {}
    for path_str, cur_hash in current.items():
        base_hash = baseline.get(path_str, "MISSING")
        if cur_hash != base_hash:
            changed[path_str] = {"baseline": base_hash, "current": cur_hash}

    if not changed:
        return CheckItem(name="hash_drift", status="PASS", message="No drift detected.", details={"count": 0})

    # Drift detected: warn (not fail) — you might have intentionally upgraded modules.
    return CheckItem(
        name="hash_drift",
        status="WARN",
        message="Drift detected in critical files. Confirm changes are intentional; update baseline if approved.",
        details={"count": len(changed), "changed": changed, "baseline_path": str(BASELINE_HASHES)},
    )


def _grade(items: List[CheckItem]) -> Tuple[str, int, int, int]:
    p = sum(1 for i in items if i.status == "PASS")
    w = sum(1 for i in items if i.status == "WARN")
    f = sum(1 for i in items if i.status == "FAIL")

    if f > 0:
        return "FAIL", p, w, f
    if w > 0:
        return "WARN", p, w, f
    return "PASS", p, w, f


def run_system_integrity_sentinel(update_baseline: bool = False) -> Dict[str, Any]:
    """
    Run all integrity checks and write reports.

    update_baseline=True will overwrite baseline_hashes.json with current snapshot
    ONLY after you reviewed drift and approve it.
    """
    _safe_mkdir(INTEGRITY_DIR)

    checks: List[CheckItem] = []
    checks.extend(_check_modules())
    checks.extend(_check_expected_functions())
    checks.extend(_check_writable_dirs())
    checks.append(_check_hash_drift())

    overall, p, w, f = _grade(checks)

    report: Dict[str, Any] = {
        "report_version": 1,
        "generated_at": _utc_now_iso(),
        "status": overall,
        "counts": {"pass": p, "warn": w, "fail": f, "total": len(checks)},
        "safe_notice": "Local integrity check only. No network. No destructive actions.",
        "checks": [asdict(c) for c in checks],
        "paths": {
            "json": str(JSON_OUT),
            "txt": str(TXT_OUT),
            "baseline_hashes": str(BASELINE_HASHES),
        },
        "recommendations": [
            "If FAIL: freeze feature work, fix imports/functions, re-run sentinel.",
            "If WARN: review drift and missing optional functions; proceed cautiously.",
            "After intentional upgrades: run with update_baseline=True to accept drift.",
        ],
    }

    _write_json(JSON_OUT, report)
    _write_text(TXT_OUT, _render_txt(report))

    if update_baseline:
        snap = _build_hash_snapshot()
        _write_json(BASELINE_HASHES, {"generated_at": _utc_now_iso(), "hashes": snap})
        report["baseline_updated"] = True
        _write_json(JSON_OUT, report)
        _write_text(TXT_OUT, _render_txt(report))

    return report


def _render_txt(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("GLL SYSTEM INTEGRITY SENTINEL (SIS)")
    lines.append("=" * 40)
    lines.append(f"Generated: {report.get('generated_at')}")
    lines.append(f"Status:    {report.get('status')}")
    c = report.get("counts", {})
    lines.append(f"Counts:    PASS={c.get('pass')} WARN={c.get('warn')} FAIL={c.get('fail')} TOTAL={c.get('total')}")
    lines.append("")
    lines.append("Key Notes:")
    lines.append(f"- Baseline hashes: {report.get('paths', {}).get('baseline_hashes')}")
    if report.get("baseline_updated"):
        lines.append("- Baseline updated: YES")
    lines.append("")
    lines.append("Checks:")
    for item in report.get("checks", []):
        name = item.get("name")
        status = item.get("status")
        msg = item.get("message")
        lines.append(f"  [{status}] {name} — {msg}")
    lines.append("")
    lines.append("Recommendations:")
    for r in report.get("recommendations", []):
        lines.append(f"  - {r}")
    lines.append("")
    lines.append("Outputs:")
    lines.append(f"  JSON: {report.get('paths', {}).get('json')}")
    lines.append(f"  TXT:  {report.get('paths', {}).get('txt')}")
    return "\n".join(lines)


if __name__ == "__main__":
    out = run_system_integrity_sentinel(update_baseline=False)
    print(json.dumps(out, indent=2))

