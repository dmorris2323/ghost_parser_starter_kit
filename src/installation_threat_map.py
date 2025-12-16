from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


OUT_DIR = Path("docs") / "base_defense"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LEGACY_DIR = Path("src") / "docs"
LEGACY_DIR.mkdir(parents=True, exist_ok=True)


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_float(val: Any, default: Optional[float] = None) -> Optional[float]:
    try:
        if val is None:
            return default
        return float(val)
    except Exception:
        return default


def _risk_band(score: float) -> str:
    if score >= 80:
        return "SEVERE"
    if score >= 50:
        return "ELEVATED"
    if score >= 25:
        return "GUARDED"
    return "LOW"


def build_installation_threat_map(
    zones: Optional[List[Dict[str, Any]]] = None,
    comms_state: Optional[str] = "OK",
    ems_state: Optional[str] = "OK",
    degraded: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Build a threat-map summary from zone risk inputs.
    Must survive missing/non-numeric inputs.
    """
    ambiguity_flags: List[str] = []
    unknowns: List[str] = []

    if zones is None:
        zones = []

    # degraded inference (best effort)
    if degraded is None:
        degraded = False
        if comms_state is None:
            degraded = True
            unknowns.append("comms_state")
        if ems_state is None:
            degraded = True
            unknowns.append("ems_state")

    # normalize zones safely
    zone_summaries: List[Dict[str, Any]] = []
    max_risk = 0.0

    if not zones:
        ambiguity_flags.append("NO_ZONES_PROVIDED")

    for z in zones:
        raw_score = z.get("risk", 0.0)
        score = _safe_float(raw_score)

        if score is None:
            ambiguity_flags.append("NON_NUMERIC_SENSOR_INPUT")
            score = 0.0

        score = max(0.0, min(100.0, float(score)))
        band = _risk_band(score)
        max_risk = max(max_risk, score)

        zone_summaries.append(
            {
                "zone": z.get("zone", "UNKNOWN"),
                "risk_score": round(score, 2),
                "risk_band": band,
                "notes": z.get("notes", "") or "",
            }
        )

    overall_band = _risk_band(max_risk)

    posture = "ROUTINE_MONITORING"
    if overall_band == "SEVERE":
        posture = "SECURITY_FORCES_DISPATCH"
    elif overall_band in {"ELEVATED", "GUARDED"}:
        posture = "DUTY_OFFICER_NOTIFY"

    # under ambiguity, cap posture (bounded)
    if ambiguity_flags and posture == "SECURITY_FORCES_DISPATCH":
        posture = "DUTY_OFFICER_NOTIFY"
        ambiguity_flags.append("ESCALATION_CAPPED_UNDER_AMBIGUITY")

    report: Dict[str, Any] = {
        "generated_at_utc": _utc_now_iso(),
        "inputs": {
            "zones_count": len(zones),
            "comms_state": comms_state,
            "ems_state": ems_state,
            "degraded": bool(degraded),
        },
        "summary": {
            "posture": posture,
            "overall_risk_band": overall_band,
            "max_risk_score": round(max_risk, 2),
        },
        "zones": zone_summaries,
        "unknowns": unknowns,
        "ambiguity_flags": ambiguity_flags,
        "what_we_can_say": [
            f"Posture is {posture} based on bounded zone risk.",
            f"Overall risk band is {overall_band} (max_risk_score={round(max_risk,2)}).",
        ],
        "what_we_cannot_say": [
            "Cannot infer adversary intent from this product.",
            "Cannot attribute causality without corroborating sensors and operator judgment.",
        ],
    }

    return report


def _write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _write_txt(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("Installation Threat Map")
    lines.append(f"generated_at_utc: {obj.get('generated_at_utc')}")
    lines.append(f"posture: {obj.get('summary', {}).get('posture')}")
    lines.append(f"overall_risk_band: {obj.get('summary', {}).get('overall_risk_band')}")
    lines.append(f"max_risk_score: {obj.get('summary', {}).get('max_risk_score')}")
    lines.append("")
    if obj.get("ambiguity_flags"):
        lines.append("ambiguity_flags:")
        for a in obj["ambiguity_flags"]:
            lines.append(f"- {a}")
        lines.append("")
    if obj.get("unknowns"):
        lines.append("unknowns:")
        for u in obj["unknowns"]:
            lines.append(f"- {u}")
        lines.append("")
    lines.append("zones:")
    for z in obj.get("zones", []):
        lines.append(
            f"- {z.get('zone')}: risk_score={z.get('risk_score')} band={z.get('risk_band')} notes={z.get('notes')}"
        )
    lines.append("")
    lines.append("what_we_can_say:")
    for w in obj.get("what_we_can_say", []):
        lines.append(f"- {w}")
    lines.append("")
    lines.append("what_we_cannot_say:")
    for w in obj.get("what_we_cannot_say", []):
        lines.append(f"- {w}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_installation_threat_map(report: Dict[str, Any]) -> Dict[str, str]:
    stamp = _utc_stamp()

    json_latest = OUT_DIR / "installation_threat_map_latest.json"
    txt_latest = OUT_DIR / "installation_threat_map_latest.txt"
    json_stamped = OUT_DIR / f"installation_threat_map_{stamp}.json"
    txt_stamped = OUT_DIR / f"installation_threat_map_{stamp}.txt"

    legacy_json = LEGACY_DIR / "installation_threat_map.json"
    legacy_txt = LEGACY_DIR / "installation_threat_map.txt"

    _write_json(json_latest, report)
    _write_txt(txt_latest, report)
    _write_json(json_stamped, report)
    _write_txt(txt_stamped, report)

    _write_json(legacy_json, report)
    _write_txt(legacy_txt, report)

    return {
        "json_latest": str(json_latest),
        "txt_latest": str(txt_latest),
        "json_stamped": str(json_stamped),
        "txt_stamped": str(txt_stamped),
        "legacy_json": str(legacy_json),
        "legacy_txt": str(legacy_txt),
    }


# --- REQUIRED ENTRYPOINTS FOR GATES ---

def run() -> Dict[str, str]:
    """
    Canonical callable entrypoint for regression gates.
    Uses safe defaults if no inputs are provided.
    """
    report = build_installation_threat_map(
        zones=[
            {"zone": "NORTH", "risk": 12.0, "notes": "Routine activity."},
            {"zone": "EAST", "risk": 27.5, "notes": "Minor anomalies."},
            {"zone": "SOUTH", "risk": 55.0, "notes": "Elevated signals; verify sensors."},
        ],
        comms_state="OK",
        ems_state="OK",
        degraded=False,
    )
    return write_installation_threat_map(report)


def main() -> None:
    paths = run()
    print(json.dumps(paths, indent=2))


if __name__ == "__main__":
    main()

