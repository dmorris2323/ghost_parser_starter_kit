#!/usr/bin/env python3
"""
Owl Explain Gate — Hardening validator for Spectral Owl "Explain" functions.

- Validates explain_* functions exist and return bounded, UI-safe sections.
- Emits docs/validation/owl_explain_gate_latest.json (+ stamped).
- Exits non-zero on FAIL (use in orchestrators / CI / demo gates).

This is a "contractor-grade" safety gate:
if the Explain layer drifts, your demo must fail loudly.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


# -----------------------------
# Paths
# -----------------------------
_THIS_FILE = Path(__file__).resolve()
SRC_DIR = _THIS_FILE.parent
REPO_ROOT = SRC_DIR.parent
DOCS_DIR = REPO_ROOT / "docs"
VALIDATION_DIR = DOCS_DIR / "validation"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stamp_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _ensure_dirs() -> None:
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)


def _bootstrap_import_path() -> None:
    """
    Ensure imports work whether user runs:
      - python src/owl_explain_gate.py
      - python -m src.owl_explain_gate (rare)
    """
    # Add repo root and src directory to sys.path
    # so imports like `from src...` and `import spectral_owl_explain` can work.
    for p in [str(REPO_ROOT), str(SRC_DIR)]:
        if p not in sys.path:
            sys.path.insert(0, p)


def _try_import_explain_module():
    """
    Prefer src.spectral_owl_explain; fall back to spectral_owl_explain.
    This makes the gate resilient to how you’ve wired imports in Streamlit.
    """
    errors = []
    try:
        import importlib

        m = importlib.import_module("src.spectral_owl_explain")
        return m, "src.spectral_owl_explain"
    except Exception as e:
        errors.append(f"src.spectral_owl_explain import failed: {e!r}")

    try:
        import importlib

        m = importlib.import_module("spectral_owl_explain")
        return m, "spectral_owl_explain"
    except Exception as e:
        errors.append(f"spectral_owl_explain import failed: {e!r}")

    raise ImportError(" | ".join(errors))


# -----------------------------
# Gate rules
# -----------------------------
EXPECTED_ORDER = [
    "headline",
    "summary",
    "confidence",
    "recommended_posture",
    "what_we_know",
    "what_we_do_not_know",
    "assumptions",
    "uncertainties",
    "operator_actions",
    "notice",
]

# Minimum required keys for a "valid explain pack"
MIN_REQUIRED_KEYS = {
    "summary",
    "confidence",
    "recommended_posture",
    "what_we_know",
    "what_we_do_not_know",
    "notice",
}


def _is_ui_safe_value(v: Any) -> bool:
    """
    Bounded UI-safe types only.
    - str, int, float, bool, None
    - list[str] or list of primitives
    - dict[str, primitive] (shallow)
    """
    if v is None:
        return True
    if isinstance(v, (str, int, float, bool)):
        return True

    if isinstance(v, list):
        # Keep lists bounded to primitives
        return all(isinstance(x, (str, int, float, bool)) or x is None for x in v)

    if isinstance(v, dict):
        # Shallow dict only: keys must be str, values primitive/None
        if not all(isinstance(k, str) for k in v.keys()):
            return False
        return all(isinstance(x, (str, int, float, bool)) or x is None for x in v.values())

    return False


def _validate_explain_pack(name: str, pack: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    Returns: (ok, violations, normalized_pack)
    normalized_pack keeps only expected keys (in expected order) + any extras at the end.
    """
    violations: List[str] = []

    if not isinstance(pack, dict):
        return False, [f"{name}: explain output is not a dict (got {type(pack).__name__})"], {}

    # Must not be empty
    if not pack:
        violations.append(f"{name}: explain output is empty dict")

    # Required keys present
    missing = sorted(list(MIN_REQUIRED_KEYS - set(pack.keys())))
    if missing:
        violations.append(f"{name}: missing required keys: {missing}")

    # UI-safe values only
    unsafe = []
    for k, v in pack.items():
        if not isinstance(k, str):
            unsafe.append(f"non-string key: {k!r}")
            continue
        if not _is_ui_safe_value(v):
            unsafe.append(f"{k}: unsafe type {type(v).__name__}")
    if unsafe:
        violations.append(f"{name}: contains non-UI-safe values: {unsafe}")

    # Confidence sanity (optional, but useful)
    conf = pack.get("confidence")
    if isinstance(conf, str):
        allowed = {"LOW", "MEDIUM", "HIGH", "UNKNOWN"}
        if conf.strip().upper() not in allowed:
            violations.append(f"{name}: confidence not in {sorted(allowed)} (got {conf!r})")

    # Normalize pack for display & deterministic output ordering
    normalized: Dict[str, Any] = {}
    for k in EXPECTED_ORDER:
        if k in pack:
            normalized[k] = pack[k]
    # append extras (but keep stable order)
    for k in sorted([k for k in pack.keys() if k not in normalized]):
        normalized[k] = pack[k]

    ok = len(violations) == 0
    return ok, violations, normalized


@dataclass
class GateResult:
    verdict: str
    crashes: int
    violations: List[str]
    checks: Dict[str, Any]
    artifacts: Dict[str, str]


def run_owl_explain_gate(strict: bool = True) -> GateResult:
    """
    strict=True: any violation => FAIL (recommended for demos)
    strict=False: violations => WARN but still PASS (not recommended)
    """
    _ensure_dirs()
    _bootstrap_import_path()

    generated_at_utc = _utc_now_iso()

    crashes = 0
    violations: List[str] = []

    checks: Dict[str, Any] = {
        "generated_at_utc": generated_at_utc,
        "context": "owl_explain_gate",
        "strict": bool(strict),
        "module_import": {"ok": False, "module": None, "error": None},
        "functions": {},
    }

    # Import module
    try:
        m, module_name = _try_import_explain_module()
        checks["module_import"]["ok"] = True
        checks["module_import"]["module"] = module_name
    except Exception as e:
        crashes += 1
        checks["module_import"]["error"] = repr(e)
        violations.append(f"IMPORT_FAIL: {repr(e)}")
        # can't proceed
        verdict = "FAIL"
        artifacts = _write_outputs(generated_at_utc, verdict, crashes, violations, checks)
        return GateResult(verdict=verdict, crashes=crashes, violations=violations, checks=checks, artifacts=artifacts)

    # Expected functions
    fn_specs = [
        ("explain_installation_threat_map", "installation_threat_map"),
        ("explain_commander_brief", "commander_brief"),
        ("explain_legal_snapshot", "legal_snapshot"),
    ]

    for fn_name, tag in fn_specs:
        fn_info: Dict[str, Any] = {
            "present": False,
            "ok": False,
            "violations": [],
            "keys": [],
        }

        try:
            fn = getattr(m, fn_name)
            fn_info["present"] = True
        except Exception as e:
            crashes += 1
            fn_info["violations"].append(f"MISSING_FUNCTION: {repr(e)}")
            violations.append(f"{fn_name}: missing")
            checks["functions"][tag] = fn_info
            continue

        # Execute function
        try:
            pack = fn()  # expected: Dict[str, Any]
            if isinstance(pack, dict):
                fn_info["keys"] = list(pack.keys())
            ok, vios, normalized = _validate_explain_pack(fn_name, pack)
            fn_info["ok"] = ok
            fn_info["violations"] = vios
            fn_info["normalized_preview"] = {k: normalized.get(k) for k in EXPECTED_ORDER if k in normalized}
            if not ok:
                violations.extend([f"{fn_name}: {x}" for x in vios])
        except Exception as e:
            crashes += 1
            fn_info["violations"].append(f"EXEC_FAIL: {repr(e)}")
            violations.append(f"{fn_name}: EXEC_FAIL {repr(e)}")

        checks["functions"][tag] = fn_info

    if crashes > 0:
        verdict = "FAIL"
    elif violations and strict:
        verdict = "FAIL"
    elif violations and not strict:
        verdict = "WARN"
    else:
        verdict = "PASS"

    artifacts = _write_outputs(generated_at_utc, verdict, crashes, violations, checks)
    return GateResult(verdict=verdict, crashes=crashes, violations=violations, checks=checks, artifacts=artifacts)


def _write_outputs(
    generated_at_utc: str,
    verdict: str,
    crashes: int,
    violations: List[str],
    checks: Dict[str, Any],
) -> Dict[str, str]:
    """
    Writes latest + stamped JSON.
    """
    _ensure_dirs()
    stamp = _stamp_utc()

    payload = {
        "generated_at_utc": generated_at_utc,
        "context": "owl_explain_gate",
        "verdict": verdict,
        "crashes": crashes,
        "violations": violations,
        "checks": checks,
        "notice": "Assessment is probabilistic and bounded; operator judgment applies.",
    }

    latest = VALIDATION_DIR / "owl_explain_gate_latest.json"
    stamped = VALIDATION_DIR / f"owl_explain_gate_{stamp}.json"

    latest.write_text(json.dumps(payload, indent=2, sort_keys=False), encoding="utf-8")
    stamped.write_text(json.dumps(payload, indent=2, sort_keys=False), encoding="utf-8")

    return {
        "latest_json": str(latest),
        "stamped_json": str(stamped),
    }


def main() -> int:
    strict = True
    # Optional env override (handy when debugging)
    if os.getenv("OWL_EXPLAIN_GATE_STRICT", "1").strip() in {"0", "false", "False"}:
        strict = False

    r = run_owl_explain_gate(strict=strict)

    print(json.dumps(
        {
            "generated_at_utc": r.checks.get("generated_at_utc"),
            "context": "owl_explain_gate",
            "strict": bool(r.checks.get("strict", True)),
            "verdict": r.verdict,
            "crashes": r.crashes,
            "violations": r.violations,
            "artifacts": r.artifacts,
        },
        indent=2
    ))

    return 0 if r.verdict in {"PASS", "WARN"} else 2


if __name__ == "__main__":
    raise SystemExit(main())

