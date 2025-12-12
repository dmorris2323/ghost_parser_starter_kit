# src/training_validation_gate.py
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


@dataclass
class TrainingGate:
    status: str               # PASS / FAIL
    counted_for_agi: bool
    message: str
    details: Dict[str, Any]


def _safe_call(fn, default=None):
    try:
        return fn()
    except Exception as e:
        return default, str(e)


def evaluate_training_gate(require_all_green: bool = True) -> TrainingGate:
    """
    Gate logic:
    - Prefer existing SIS/SPS/OSL modules if present.
    - If modules missing, degrade safely to FAIL when require_all_green=True.
    """
    details: Dict[str, Any] = {}

    # Operator Safety Layer
    osl_ok = False
    try:
        import operator_safety_layer as osl_mod  # type: ignore

        fn = None
        for cand in ("compute_osl", "compute_operator_safety_layer", "evaluate_osl"):
            if hasattr(osl_mod, cand):
                fn = getattr(osl_mod, cand)
                break
        if fn:
            res = fn()
            details["operator_safety_layer"] = res
            # Accept common fields
            status = str((res or {}).get("osl_status") or (res or {}).get("status") or "").upper()
            osl_ok = status in ("GREEN", "PASS", "OK")
        else:
            details["operator_safety_layer_error"] = "MissingFunction"
    except Exception as e:
        details["operator_safety_layer_error"] = str(e)

    # System Integrity (SIS)
    sis_ok = False
    try:
        import system_integrity_report as sis_mod  # type: ignore

        fn = None
        for cand in ("generate_system_integrity_report", "run_system_integrity", "build_system_integrity"):
            if hasattr(sis_mod, cand):
                fn = getattr(sis_mod, cand)
                break
        if fn:
            res = fn()
            details["system_integrity"] = res
            # Heuristic: accept if no "FAIL"/"RED" flags
            txt = str(res).upper()
            sis_ok = ("FAIL" not in txt) and ("RED" not in txt)
        else:
            details["system_integrity_error"] = "MissingFunction"
    except Exception as e:
        details["system_integrity_error"] = str(e)

    # SPS (mutation / behavioral checks)
    sps_ok = False
    try:
        import sps_behavior_monitor as sps_b  # type: ignore

        fn = None
        for cand in ("write_behavior_report", "run_behavior_monitor", "behavior_scan"):
            if hasattr(sps_b, cand):
                fn = getattr(sps_b, cand)
                break
        if fn:
            res = fn()
            details["sps_behavior"] = res
            txt = str(res).upper()
            sps_ok = ("FAIL" not in txt) and ("RED" not in txt)
        else:
            details["sps_behavior_error"] = "MissingFunction"
    except Exception as e:
        details["sps_behavior_error"] = str(e)

    all_ok = osl_ok and sis_ok and sps_ok
    if require_all_green:
        status = "PASS" if all_ok else "FAIL"
        counted = bool(all_ok)
    else:
        # permissive: count if at least OSL is green
        status = "PASS" if osl_ok else "FAIL"
        counted = bool(osl_ok)

    msg = "GREEN gate satisfied." if counted else "Gate not satisfied. Fix integrity posture before counting training."
    return TrainingGate(status=status, counted_for_agi=counted, message=msg, details=details)


def gate_to_dict(g: TrainingGate) -> Dict[str, Any]:
    return asdict(g)

