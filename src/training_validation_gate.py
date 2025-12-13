# src/training_validation_gate.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Any, Optional


@dataclass
class GateDecision:
    allowed: bool
    reason: str
    sis_status: str
    sps_status: str
    validation_verdict: str
    decided_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "sis_status": self.sis_status,
            "sps_status": self.sps_status,
            "validation_verdict": self.validation_verdict,
            "decided_at": self.decided_at,
        }


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def decide_training_gate(
    *,
    sis_status: Optional[str],
    sps_status: Optional[str],
    validation_verdict: Optional[str],
) -> GateDecision:
    """
    Rule set (simple + strict):
      - SIS must be GREEN
      - SPS must be GREEN
      - validation verdict must be PASS or WARN
    Any missing status => NOT allowed (fail closed).
    """
    sis = (sis_status or "UNKNOWN").strip().upper()
    sps = (sps_status or "UNKNOWN").strip().upper()
    vv = (validation_verdict or "UNKNOWN").strip().upper()

    if sis != "GREEN":
        return GateDecision(False, f"SIS not GREEN (got {sis})", sis, sps, vv, _utc_now())
    if sps != "GREEN":
        return GateDecision(False, f"SPS not GREEN (got {sps})", sis, sps, vv, _utc_now())
    if vv not in ("PASS", "WARN"):
        return GateDecision(False, f"Validation verdict not PASS/WARN (got {vv})", sis, sps, vv, _utc_now())

    return GateDecision(True, "Session accepted (gates satisfied).", sis, sps, vv, _utc_now())


def summarize_gate(gate: GateDecision) -> str:
    if gate.allowed:
        return f"✅ ALLOWED — {gate.reason} | SIS={gate.sis_status} SPS={gate.sps_status} VALID={gate.validation_verdict}"
    return f"⛔ BLOCKED — {gate.reason} | SIS={gate.sis_status} SPS={gate.sps_status} VALID={gate.validation_verdict}"

