# src/training_validation_gate.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class GateDecision:
    ok: bool
    reason: str
    sis: str
    sps: str
    validation: str


def decide_training_gate(sis_status: str, sps_status: str, validation_verdict: str) -> GateDecision:
    sis = (sis_status or "UNKNOWN").upper().strip()
    sps = (sps_status or "UNKNOWN").upper().strip()
    val = (validation_verdict or "UNKNOWN").upper().strip()

    if sis != "GREEN":
        return GateDecision(False, f"SIS not GREEN ({sis})", sis, sps, val)
    if sps != "GREEN":
        return GateDecision(False, f"SPS not GREEN ({sps})", sis, sps, val)

    # Validation can be PASS or WARN. FAIL blocks.
    if val not in {"PASS", "WARN"}:
        return GateDecision(False, f"Validation not PASS/WARN ({val})", sis, sps, val)

    return GateDecision(True, "All gates GREEN; validation PASS/WARN.", sis, sps, val)


def summarize_gate(g: GateDecision) -> str:
    return f"{'GREEN' if g.ok else 'BLOCKED'} | SIS={g.sis} SPS={g.sps} VAL={g.validation} | {g.reason}"


def gate_to_dict(g: GateDecision) -> Dict[str, str]:
    return {"ok": str(g.ok), "reason": g.reason, "sis": g.sis, "sps": g.sps, "validation": g.validation}

