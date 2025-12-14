"""
shared_gate_utils.py

Small helpers to make gate failures readable in Streamlit UIs without
changing core gate logic.

Goal:
- PRE/POST gate RuntimeError stays "hard" in engines
- UI catches and renders it as an operator-friendly signal
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


_GATE_PATH_RE = re.compile(r"See\s+(?P<path>docs\/[^\s]+)\s+and\s+fix", re.IGNORECASE)


@dataclass(frozen=True)
class GateFailureInfo:
    gate_type: str
    context: str
    report_path: Optional[str]
    message: str


def parse_gate_runtime_error(exc: Exception) -> Optional[GateFailureInfo]:
    """
    Parse the RuntimeError thrown by run_gates() into structured info.

    Example engine message:
    "GLL PRE-GATE FAIL for context 'fusion_validation_harness'. See docs/integrity/run_gate_pre_fusion_validation_harness_20251212_152520.txt and fix integrity before running."
    """
    msg = str(exc) if exc is not None else ""
    if "GLL" not in msg or "GATE FAIL" not in msg:
        return None

    gate_type = "UNKNOWN"
    if "PRE-GATE FAIL" in msg:
        gate_type = "PRE"
    elif "POST-GATE FAIL" in msg:
        gate_type = "POST"

    context = "UNKNOWN"
    m_ctx = re.search(r"context\s+'([^']+)'", msg, re.IGNORECASE)
    if m_ctx:
        context = m_ctx.group(1).strip()

    report_path = None
    m_path = _GATE_PATH_RE.search(msg)
    if m_path:
        report_path = m_path.group("path").strip()

    return GateFailureInfo(
        gate_type=gate_type,
        context=context,
        report_path=report_path,
        message=msg.strip(),
    )

