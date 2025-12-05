"""
spectral_value_snapshot_day61.py

Builds a consolidated "value snapshot" for GLL as of Day 61.
This is meant to support:
- personal tracking,
- investor / sponsor conversations,
- SBIR / pitch prep.

Outputs:
    docs/gll_value_snapshot_day61.txt
    docs/gll_value_snapshot_day61.json
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
OUT_TXT = DOCS_DIR / "gll_value_snapshot_day61.txt"
OUT_JSON = DOCS_DIR / "gll_value_snapshot_day61.json"


def _safe_compute_reliability(notes: List[str]) -> Dict[str, Any]:
    try:
        from sensor_reliability import compute_reliability_all  # type: ignore
        rel = compute_reliability_all()
        return rel
    except Exception as exc:  # noqa: BLE001
        notes.append(f"Reliability: fallback used ({exc})")
        return {"avg_reliability": 90.0, "sensors": {}}


def _safe_build_readiness(notes: List[str]) -> Dict[str, Any]:
    try:
        from golden_dome_readiness_report import build_readiness_report  # type: ignore
        rd = build_readiness_report()
        return rd
    except Exception as exc:  # noqa: BLE001
        notes.append(f"Readiness: fallback used ({exc})")
        return {"label": "UNKNOWN", "path": "N/A"}


def _safe_get_profile(notes: List[str]) -> Dict[str, Any]:
    try:
        from profile_config import get_active_profile  # type: ignore

        profile = get_active_profile()
        return {
            "key": getattr(profile, "key", "unknown_profile"),
            "display_name": getattr(profile, "display_name", "Unknown Profile"),
        }
    except Exception as exc:  # noqa: BLE001
        notes.append(f"Profile: fallback used ({exc})")
        return {"key": "unknown_profile", "display_name": "Unknown Profile"}


def _safe_sbir_note(notes: List[str]) -> Dict[str, Any]:
    try:
        from golden_dome_sbir_note import build_sbir_note  # type: ignore

        sb = build_sbir_note()
        return {"path": sb.get("path", "N/A")}
    except Exception as exc:  # noqa: BLE001
        notes.append(f"SBIR note: not available ({exc})")
        return {"path": "N/A"}


def _safe_day61_sitrep(notes: List[str]) -> Dict[str, Any]:
    try:
        from day61_sitrep_builder import build_day61_sitrep  # type: ignore

        st = build_day61_sitrep()
        return {"path": st.get("path", "N/A")}
    except Exception as exc:  # noqa: BLE001
        notes.append(f"Day 61 SITREP: not available ({exc})")
        return {"path": "N/A"}


def _safe_demo_manifest(notes: List[str]) -> Dict[str, Any]:
    try:
        from demo_deck_manifest import build_demo_deck_manifest  # type: ignore

        dm = build_demo_deck_manifest()
        return {"path": dm.get("path", "N/A")}
    except Exception as exc:  # noqa: BLE001
        notes.append(f"Demo deck manifest: not available ({exc})")
        return {"path": "N/A"}


def build_value_snapshot() -> Dict[str, Any]:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    notes: List[str] = []

    profile = _safe_get_profile(notes)
    reliability = _safe_compute_reliability(notes)
    readiness = _safe_build_readiness(notes)
    sbir_note = _safe_sbir_note(notes)
    sitrep = _safe_day61_sitrep(notes)
    demo_manifest = _safe_demo_manifest(notes)

    avg_rel = reliability.get("avg_reliability", 90.0)
    readiness_label = readiness.get("label", "UNKNOWN")

    # === Editable valuation assumptions ===
    assumed_hours_total = 180  # adjust if you want more precision
    assumed_hourly_rate = 350  # notional cleared ISR/cyber-engineer blended rate
    engineering_value = assumed_hours_total * assumed_hourly_rate

    snapshot: Dict[str, Any] = {
        "snapshot_date": datetime.utcnow().isoformat() + "Z",
        "day_index": 61,
        "profile": profile,
        "reliability": reliability,
        "golden_dome_readiness": readiness_label,
        "golden_dome_readiness_report": readiness.get("path", "N/A"),
        "sbir_note": sbir_note,
        "day61_sitrep": sitrep,
        "demo_deck_manifest": demo_manifest,
        "valuation_assumptions": {
            "assumed_hours_total": assumed_hours_total,
            "assumed_hourly_rate_usd": assumed_hourly_rate,
        },
        "notional_engineering_value_usd": engineering_value,
        "notes": notes,
    }

    # Write TXT
    lines: List[str] = []
    lines.append("GLL VALUE SNAPSHOT — DAY 61")
    lines.append("")
    lines.append(f"Snapshot UTC: {snapshot['snapshot_date']}")
    lines.append(f"Day Index:    {snapshot['day_index']}")
    lines.append("")
    lines.append("Active Profile:")
    lines.append(f"  - Key:   {profile['key']}")
    lines.append(f"  - Name:  {profile['display_name']}")
    lines.append("")
    lines.append("Reliability:")
    lines.append(f"  - Average: {avg_rel:.2f}%")
    if reliability.get("sensors"):
        for name, val in sorted(reliability["sensors"].items()):
            lines.append(f"  - {name}: {val:.2f}%")
    else:
        lines.append("  - Sensor breakdown not available (fallback).")
    lines.append("")
    lines.append("Golden Dome Readiness:")
    lines.append(f"  - Label:   {readiness_label}")
    lines.append(f"  - Report:  {snapshot['golden_dome_readiness_report']}")
    lines.append("")
    lines.append("Key Artifacts:")
    lines.append(f"  - SBIR Note:     {sbir_note['path']}")
    lines.append(f"  - Day 61 SITREP: {sitrep['path']}")
    lines.append(f"  - Demo Manifest: {demo_manifest['path']}")
    lines.append("")
    lines.append("Notional Engineering Value (Edit These Assumptions):")
    lines.append(f"  - Total Hours (assumed): {assumed_hours_total}")
    lines.append(f"  - Hourly Rate (assumed): ${assumed_hourly_rate:,}/hr")
    lines.append(f"  - Implied Engineering Value: ${engineering_value:,}")
    lines.append("")
    if notes:
        lines.append("Notes / Fallbacks:")
        for n in notes:
            lines.append(f"  - {n}")
        lines.append("")
    else:
        lines.append("Notes / Fallbacks:")
        lines.append("  - All core inputs loaded without fallback.")
        lines.append("")

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    OUT_JSON.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    return snapshot


if __name__ == "__main__":
    snap = build_value_snapshot()
    print("GLL value snapshot written:")
    print(f"  TXT : {OUT_TXT}")
    print(f"  JSON: {OUT_JSON}")
    print(
        f"  Implied engineering value: "
        f"${snap['notional_engineering_value_usd']:,}"
    )

