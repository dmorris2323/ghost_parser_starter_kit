"""
installation_threat_map.py

Week-2 Base Defense — Installation Threat Map (HARDENED)

Goals:
- Flawless outputs without perfect inputs
- No crashes on bad/missing/non-numeric sensor inputs
- Standardized outputs to docs/base_defense (latest + stamped)
- Legacy compatibility writes to src/docs (json/txt)

Outputs:
- docs/base_defense/installation_threat_map_latest.json
- docs/base_defense/installation_threat_map_latest.txt
- docs/base_defense/installation_threat_map_<timestamp>.json
- docs/base_defense/installation_threat_map_<timestamp>.txt
- src/docs/installation_threat_map.json
- src/docs/installation_threat_map.txt
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


OUT_DIR = Path("docs") / "base_defense"
LEGACY_DIR = Path("src") / "docs"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _write_json(p: Path, obj: Any) -> None:
    _safe_mkdir(p.parent)
    p.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _write_txt(p: Path, text: str) -> None:
    _safe_mkdir(p.parent)
    p.write_text(text, encoding="utf-8")


def _safe_float(val: Any, default: Optional[float] = None) -> Optional[float]:
    """
    Convert val to float safely.
    Returns default (None by default) if conversion fails.
    """
    try:
        if val is None:
            return default
        return float(val)
    except Exception:
        return default


def _risk_band(score: float) -> str:
    """
    Bounded banding for base defense risk.
    """
    s = max(0.0, min(100.0, float(score)))
    if s >= 80:
        return "SEVERE"
    if s >= 55:
        return "ELEVATED"
    if s >= 30:
        return "GUARDED"
    return "LOW"


def build_installation_threat_map(
    zones: Optional[List[Dict[str, Any]]] = None,
    comms_state: Optional[str] = "OK",
    include_legacy_writes: bool = True,
) -> Dict[str, Any]:
    """
    Build a commander-friendly installation threat map from synthetic inputs.

    zones format (training proxy):
      [{"zone":"NORTH","risk":12.3,"notes":"..."}]

    Hardening behavior:
    - Non-numeric risk => treated as 0.0 and flagged
    - Missing comms_state => degraded=True and unknowns includes comms_state
    - Missing zones => treated as empty list
    """
    # Always initialize these locals FIRST (fixes your NameError)
    ambiguity_flags: List[str] = []
    unknowns: List[str] = []
    degraded = False

    # Degraded if comms missing/unknown
    if comms_state is None:
        degraded = True
        unknowns.append("comms_state")
        ambiguity_flags.append("MISSING_COMMS_STATE")
        comms_state_str = "UNKNOWN"
    else:
        comms_state_str = str(comms_state)

    zones = zones or []
    if not isinstance(zones, list):
        zones = []
        ambiguity_flags.append("ZONES_NOT_A_LIST")

    # Aggregate zone risks safely
    zone_summaries: List[Dict[str, Any]] = []
    max_risk = 0.0

    for idx, z in enumerate(zones):
        if not isinstance(z, dict):
            ambiguity_flags.append("NON_DICT_ZONE_ITEM")
            continue

        raw_score = z.get("risk", 0.0)
        score_opt = _safe_float(raw_score, default=None)

        if score_opt is None:
            # This is exactly the pattern you asked about: safe parse + ambiguity flag
            ambiguity_flags.append("NON_NUMERIC_SENSOR_INPUT")
            score = 0.0
        else:
            score = max(0.0, min(100.0, float(score_opt)))

        band = _risk_band(score)
        max_risk = max(max_risk, score)

        zone_summaries.append(
            {
                "zone": str(z.get("zone", f"ZONE_{idx}") or f"ZONE_{idx}"),
                "risk_score": round(score, 2),
                "risk_band": band,
                "notes": str(z.get("notes", "") or ""),
                "raw_risk": raw_score,
            }
        )

    overall_band = _risk_band(max_risk)

    # Bounded posture logic
    posture = "ROUTINE_MONITORING"
    if overall_band == "SEVERE":
        posture = "SECURITY_FORCES_DISPATCH"
    elif overall_band in {"ELEVATED", "GUARDED"}:
        posture = "DUTY_OFFICER_NOTIFY"

    report: Dict[str, Any] = {
        "generated_at_utc": _utc_now_iso(),
        "safe_notice": "This artifact is derived from synthetic telemetry and is safe for training/demos.",
        "inputs": {
            "comms_state": comms_state_str,
            "zones_count": len(zones),
        },
        "status": {
            "degraded": degraded,
            "comms_state": comms_state_str,
        },
        "summary": {
            "overall_risk_band": overall_band,
            "max_risk_score": round(max_risk, 2),
            "recommended_posture": posture,
        },
        "ambiguity_flags": ambiguity_flags,
        "unknowns": unknowns,
        "zones": zone_summaries,
    }

    # Write outputs (standard + stamped)
    ts = _ts()
    json_latest = OUT_DIR / "installation_threat_map_latest.json"
    txt_latest = OUT_DIR / "installation_threat_map_latest.txt"
    json_stamped = OUT_DIR / f"installation_threat_map_{ts}.json"
    txt_stamped = OUT_DIR / f"installation_threat_map_{ts}.txt"

    _write_json(json_latest, report)
    _write_json(json_stamped, report)
    _write_txt(txt_latest, _render_txt(report))
    _write_txt(txt_stamped, _render_txt(report))

    # Legacy writes (backward compatible)
    legacy_json = LEGACY_DIR / "installation_threat_map.json"
    legacy_txt = LEGACY_DIR / "installation_threat_map.txt"
    if include_legacy_writes:
        _write_json(legacy_json, report)
        _write_txt(legacy_txt, _render_txt(report))

    return {
        "json_latest": str(json_latest),
        "txt_latest": str(txt_latest),
        "json_stamped": str(json_stamped),
        "txt_stamped": str(txt_stamped),
        "legacy_json": str(legacy_json),
        "legacy_txt": str(legacy_txt),
    }


def _render_txt(report: Dict[str, Any]) -> str:
    summary = report.get("summary", {})
    status = report.get("status", {})
    flags = report.get("ambiguity_flags", []) or []
    unknowns = report.get("unknowns", []) or []
    zones = report.get("zones", []) or []

    lines: List[str] = []
    lines.append("INSTALLATION THREAT MAP (TRAINING)")
    lines.append(f"generated_at_utc: {report.get('generated_at_utc')}")
    lines.append(f"degraded: {status.get('degraded')}")
    lines.append(f"comms_state: {status.get('comms_state')}")
    lines.append("")
    lines.append("SUMMARY")
    lines.append(f"- overall_risk_band: {summary.get('overall_risk_band')}")
    lines.append(f"- max_risk_score: {summary.get('max_risk_score')}")
    lines.append(f"- recommended_posture: {summary.get('recommended_posture')}")
    lines.append("")

    if flags:
        lines.append("AMBIGUITY FLAGS")
        for f in flags:
            lines.append(f"- {f}")
        lines.append("")

    if unknowns:
        lines.append("UNKNOWNS")
        for u in unknowns:
            lines.append(f"- {u}")
        lines.append("")

    lines.append("ZONES")
    if not zones:
        lines.append("- (none)")
    else:
        for z in zones:
            lines.append(
                f"- {z.get('zone')}: risk_score={z.get('risk_score')} band={z.get('risk_band')} notes={z.get('notes')}"
            )

    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    # Default run with a tiny synthetic set
    sample = [
        {"zone": "NORTH", "risk": 12.5, "notes": "Routine patrols."},
        {"zone": "EAST", "risk": 61.0, "notes": "Repeated fence alarms."},
        {"zone": "SOUTH", "risk": "BAD_DATA", "notes": "Sensor glitch."},
    ]
    paths = build_installation_threat_map(zones=sample, comms_state="OK")
    print(json.dumps(paths, indent=2))

