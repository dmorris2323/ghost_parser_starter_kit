# src/gll_status_probe.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _read_text(path: Path) -> Optional[str]:
    try:
        return path.read_text(errors="ignore")
    except Exception:
        return None


def probe_latest_status(repo_root: Optional[Path] = None) -> Dict[str, str]:
    """
    Best-effort probe for:
      - SIS (system integrity)
      - SPS (behavior/integrity)
      - Validation (fusion validation harness)

    Returns: {"sis": "...", "sps": "...", "validation": "..."} where values are:
      GREEN/YELLOW/RED or PASS/WARN/FAIL or UNKNOWN
    """
    if repo_root is None:
        # This file is under src/, so repo root is parent of src
        repo_root = Path(__file__).resolve().parents[1]

    docs = repo_root / "src" / "docs"
    out: Dict[str, str] = {"sis": "UNKNOWN", "sps": "UNKNOWN", "validation": "UNKNOWN"}

    # --- SIS: look for a system integrity report text
    # You’ve been generating run_gate_pre_* files and integrity outputs. We treat "GREEN" if file contains "GREEN".
    integrity_dir = docs / "integrity"
    if integrity_dir.exists():
        # pick newest matching text files
        candidates = sorted(integrity_dir.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
        for p in candidates[:8]:
            txt = _read_text(p) or ""
            if "SIS" in txt or "SYSTEM INTEGRITY" in txt or "INTEGRITY" in txt:
                if "GREEN" in txt:
                    out["sis"] = "GREEN"
                    break
                if "RED" in txt:
                    out["sis"] = "RED"
                    break
                if "YELLOW" in txt:
                    out["sis"] = "YELLOW"
                    break

    # --- SPS: look for SPS behavior/integrity report
    # (You’ve been writing SPS behavioral integrity monitor outputs.)
    sps_dir = docs / "sps"
    if sps_dir.exists():
        candidates = sorted(sps_dir.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
        for p in candidates[:8]:
            txt = _read_text(p) or ""
            if "GREEN" in txt:
                out["sps"] = "GREEN"
                break
            if "RED" in txt:
                out["sps"] = "RED"
                break
            if "YELLOW" in txt:
                out["sps"] = "YELLOW"
                break

    # --- Validation: read latest fusion validation report json if present
    validation_dir = docs / "validation"
    report = validation_dir / "fusion_validation_report.json"
    if report.exists():
        data = _read_json(report) or {}
        verdict = (data.get("verdict") or {}).get("status")
        if isinstance(verdict, str) and verdict.strip():
            out["validation"] = verdict.strip().upper()

    return out

