# src/training_validation_gate.py
"""
training_validation_gate.py

Gate enforcement wrapper for training sessions.

Rule:
- A session may be logged regardless.
- It only counts toward AGI if SIS+SPS PRE and POST gates are GREEN.

We DO NOT import this from training_session_store to avoid circular imports.
Apps call this, then append_session().
"""

from __future__ import annotations

from typing import Any, Dict, Tuple


def _extract_status(gate_result: Dict[str, Any]) -> str:
    """
    Normalize a status string from gate result.
    We accept common keys but default to GREEN when a gate returns normally.
    """
    for k in ("overall_status", "status", "gate_status", "osl_status"):
        v = gate_result.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip().upper()
    return "GREEN"


def run_training_session_gates() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """
    Run PRE + POST gates for a training session append workflow.

    Returns:
      pre_gate: dict (or error dict)
      post_gate: dict (or error dict)
      decision: dict {counted_for_agi: bool, reason: [..], pre_status, post_status}
    """
    decision = {
        "counted_for_agi": False,
        "reason": [],
        "pre_status": "UNKNOWN",
        "post_status": "UNKNOWN",
    }

    # Import here (lazy) so this module doesn't break on import path quirks.
    from gll_run_gates import run_gates  # type: ignore

    # ---- PRE GATE ----
    try:
        pre_gate = run_gates(
            gate_type="PRE",
            context="training_session_append",
            update_baselines=False,
        )
        pre_status = _extract_status(pre_gate)
        decision["pre_status"] = pre_status
    except Exception as e:
        pre_gate = {"status": "FAIL", "error": f"{e.__class__.__name__}: {e}"}
        decision["pre_status"] = "FAIL"
        decision["reason"].append(f"PRE gate failed: {e.__class__.__name__}: {e}")

    # ---- POST GATE ----
    try:
        post_gate = run_gates(
            gate_type="POST",
            context="training_session_append",
            update_baselines=False,
        )
        post_status = _extract_status(post_gate)
        decision["post_status"] = post_status
    except Exception as e:
        post_gate = {"status": "FAIL", "error": f"{e.__class__.__name__}: {e}"}
        decision["post_status"] = "FAIL"
        decision["reason"].append(f"POST gate failed: {e.__class__.__name__}: {e}")

    # ---- COUNTING POLICY ----
    pre_ok = decision["pre_status"] in {"GREEN", "PASS"}
    post_ok = decision["post_status"] in {"GREEN", "PASS"}

    if pre_ok and post_ok:
        decision["counted_for_agi"] = True
        decision["reason"].append("PRE+POST gates GREEN — session counted toward AGI.")
    else:
        decision["counted_for_agi"] = False
        if not pre_ok:
            decision["reason"].append(f"PRE gate not GREEN ({decision['pre_status']}) — session NOT counted.")
        if not post_ok:
            decision["reason"].append(f"POST gate not GREEN ({decision['post_status']}) — session NOT counted.")

    return pre_gate, post_gate, decision

