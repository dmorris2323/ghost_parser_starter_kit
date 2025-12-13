"""
training_policy.py

Rules for:
- whether a session "counts toward AGI"
- difficulty logging rules (lightweight)
- gate enforcement (SIS+SPS)

No imports from training_curve_engine or feedback engine.
"""

from __future__ import annotations

from typing import Any, Dict


def gate_is_green(gate_report: Dict[str, Any]) -> bool:
    """
    Normalize multiple gate schemas.
    We treat GREEN/PASS as allowed. Everything else => not counted.
    """
    if not isinstance(gate_report, dict):
        return False

    # Common patterns
    status = str(gate_report.get("overall_status") or gate_report.get("status") or "").upper()
    if status in {"GREEN", "PASS"}:
        return True

    # Sometimes nested
    sis = gate_report.get("sis", {}) if isinstance(gate_report.get("sis"), dict) else {}
    sps = gate_report.get("sps", {}) if isinstance(gate_report.get("sps"), dict) else {}

    sis_status = str(sis.get("status") or sis.get("overall_status") or "").upper()
    sps_status = str(sps.get("status") or sps.get("overall_status") or "").upper()

    # If either explicitly fails, not green
    if sis_status in {"RED", "FAIL"} or sps_status in {"RED", "FAIL"}:
        return False

    # If both look green-ish, allow
    if sis_status in {"GREEN", "PASS"} and sps_status in {"GREEN", "PASS"}:
        return True

    return False


def apply_gate_enforcement_to_session(
    *,
    session: Dict[str, Any],
    pre_gate: Dict[str, Any] | None,
    post_gate: Dict[str, Any] | None,
) -> Dict[str, Any]:
    """
    Adds:
      session["gates"] = {"pre":..., "post":...}
      session["counts_toward_agi"] = True/False
    Rule:
      counts only if BOTH pre and post are GREEN/PASS.
    """
    s = dict(session) if isinstance(session, dict) else {}
    gates = {
        "pre": pre_gate or {},
        "post": post_gate or {},
    }
    s["gates"] = gates

    pre_ok = gate_is_green(gates["pre"])
    post_ok = gate_is_green(gates["post"])

    s["counts_toward_agi"] = bool(pre_ok and post_ok)
    return s

