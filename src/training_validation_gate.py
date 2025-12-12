# src/training_validation_gate.py
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, List


DOC_CANDIDATES = [
    # System integrity
    "src/docs/system_integrity_report.json",
    "src/docs/system_integrity_report.txt",
    "docs/system_integrity_report.json",
    "docs/system_integrity_report.txt",
    # SPS behavioral monitor outputs (if present)
    "src/docs/sps_behavior_report.json",
    "src/docs/sps_behavior_report.txt",
    "docs/sps_behavior_report.json",
    "docs/sps_behavior_report.txt",
    # OSL / trust outputs (optional)
    "src/docs/operator_safety_layer.json",
    "src/docs/operator_safety_layer.txt",
    "docs/operator_safety_layer.json",
    "docs/operator_safety_layer.txt",
    "src/docs/fusion_trust.json",
    "src/docs/fusion_trust.txt",
    "docs/fusion_trust.json",
    "docs/fusion_trust.txt",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_root() -> Path:
    # This file lives in src/, so repo root is parent
    return Path(__file__).resolve().parent.parent


def _try_read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _try_read_text(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None


def _find_first_existing(paths: List[str]) -> List[Path]:
    root = _repo_root()
    found: List[Path] = []
    for rel in paths:
        p = (root / rel).resolve()
        if p.exists() and p.is_file():
            found.append(p)
    return found


def _infer_pass_from_json(obj: Dict[str, Any]) -> Optional[bool]:
    """
    Attempts to infer PASS/FAIL from common JSON patterns.
    """
    # Common keys
    for key in ["status", "verdict", "result", "overall_status", "gate_status"]:
        if key in obj and isinstance(obj[key], str):
            v = obj[key].strip().upper()
            if v in ["PASS", "GREEN", "OK"]:
                return True
            if v in ["FAIL", "RED", "ERROR"]:
                return False

    # Nested patterns
    for key in ["system_integrity", "integrity", "sps", "osl", "fusion_trust"]:
        if key in obj and isinstance(obj[key], dict):
            inner = _infer_pass_from_json(obj[key])
            if inner is not None:
                return inner

    return None


def _infer_pass_from_text(txt: str) -> Optional[bool]:
    t = txt.upper()
    # Strong signals
    if "STATUS: PASS" in t or "VERDICT: PASS" in t or "PASS" in t and "FAIL" not in t:
        return True
    if "STATUS: FAIL" in t or "VERDICT: FAIL" in t or "FAIL" in t or "ERROR" in t:
        return False
    if "GREEN" in t and "RED" not in t:
        return True
    if "RED" in t:
        return False
    return None


@dataclass
class GateCheck:
    name: str
    file: Optional[str]
    observed: str
    passed: Optional[bool]


@dataclass
class GateVerdict:
    gate_version: int
    generated_at: str
    status: str  # PASS/WARN/FAIL
    counted_for_agi: bool
    message: str
    checks: List[GateCheck]
    files_seen: List[str]


def evaluate_training_gate(require_all_green: bool = True) -> GateVerdict:
    """
    Option B gate: read artifacts that already exist. No imports of fragile modules.
    Rule:
      - If we cannot find ANY integrity/monitoring files, gate is FAIL (not counted).
      - If we find files and can infer PASS/FAIL:
          - PASS => counted
          - FAIL => not counted
      - If inference is ambiguous (no clear PASS/FAIL):
          - WARN => not counted if require_all_green=True
    """
    files = _find_first_existing(DOC_CANDIDATES)
    files_seen = [str(p) for p in files]

    checks: List[GateCheck] = []

    if not files:
        return GateVerdict(
            gate_version=1,
            generated_at=_utc_now(),
            status="FAIL",
            counted_for_agi=False,
            message="No integrity/SPS/OSL artifacts found. Run system integrity + SPS monitor first.",
            checks=[],
            files_seen=[],
        )

    any_fail = False
    any_pass = False
    any_unknown = False

    for p in files:
        obs = ""
        passed: Optional[bool] = None

        if p.suffix.lower() == ".json":
            obj = _try_read_json(p)
            if obj is None:
                obs = "json_parse_error"
                passed = None
            else:
                obs = "json_ok"
                passed = _infer_pass_from_json(obj)
        else:
            txt = _try_read_text(p) or ""
            obs = "txt_ok" if txt else "txt_empty"
            passed = _infer_pass_from_text(txt) if txt else None

        checks.append(
            GateCheck(
                name=p.name,
                file=str(p),
                observed=obs,
                passed=passed,
            )
        )

        if passed is True:
            any_pass = True
        elif passed is False:
            any_fail = True
        else:
            any_unknown = True

    if any_fail:
        status = "FAIL"
        counted = False
        msg = "One or more integrity/SPS/OSL checks indicate FAIL/RED."
    else:
        if any_unknown:
            status = "WARN"
            counted = False if require_all_green else bool(any_pass)
            msg = "Integrity/SPS/OSL artifacts found but verdict ambiguous. Not counted (strict mode)."
        else:
            status = "PASS"
            counted = True
            msg = "All observed artifacts indicate PASS/GREEN."

    return GateVerdict(
        gate_version=1,
        generated_at=_utc_now(),
        status=status,
        counted_for_agi=counted,
        message=msg,
        checks=checks,
        files_seen=files_seen,
    )


def gate_to_dict(v: GateVerdict) -> Dict[str, Any]:
    return asdict(v)


if __name__ == "__main__":
    v = evaluate_training_gate(require_all_green=True)
    print(json.dumps(gate_to_dict(v), indent=2))

