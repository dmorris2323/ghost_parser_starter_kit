"""
gll_scoreboard.py

Builds a high-level "scoreboard" for Ghost Lantern Labs:
- GLL readiness
- System integrity
- Fusion trust
- Operator Safety Layer
- Reliability trend

Outputs:
- docs/gll_scoreboard.json
- docs/gll_scoreboard.md
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


BASE = Path(__file__).resolve().parent
DOCS = BASE / "docs"
DOCS.mkdir(exist_ok=True)


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


@dataclass
class Scoreboard:
    generated_at: str
    readiness: Dict[str, Any]
    system_integrity: Dict[str, Any]
    fusion_trust: Dict[str, Any]
    operator_safety: Dict[str, Any]
    reliability_trend: Dict[str, Any]

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)


def _compute_readiness() -> Dict[str, Any]:
    try:
        from gll_readiness import compute_gll_readiness  # type: ignore
        return compute_gll_readiness()
    except Exception:
        data = _load_json(DOCS / "gll_readiness_status.json")
        if data is not None:
            return data
        return {"status": "unknown", "note": "No GLL readiness data available."}


def _compute_system_integrity() -> Dict[str, Any]:
    try:
        from system_integrity import compute_system_integrity  # type: ignore
        return compute_system_integrity()
    except Exception:
        data = _load_json(DOCS / "system_integrity_status.json")
        if data is not None:
            return data
        return {"status": "unknown", "note": "No system integrity data available."}


def _compute_fusion_trust() -> Dict[str, Any]:
    try:
        from fusion_trust import compute_trust  # type: ignore
        return compute_trust()
    except Exception:
        return {"status": "no_data", "note": "fusion_trust module not available."}


def _compute_operator_safety() -> Dict[str, Any]:
    try:
        from operator_safety_layer import compute_osl  # type: ignore
        return compute_osl()
    except Exception:
        return {"status": "no_data", "note": "operator_safety_layer module not available."}


def _compute_reliability_trend() -> Dict[str, Any]:
    try:
        from reliability_trend import compute_trend  # type: ignore
        return compute_trend()
    except Exception:
        return {"status": "no_data", "note": "reliability_trend module not available."}


def build_scoreboard() -> Dict[str, Any]:
    ts = datetime.now(timezone.utc).isoformat()

    sb = Scoreboard(
        generated_at=ts,
        readiness=_compute_readiness(),
        system_integrity=_compute_system_integrity(),
        fusion_trust=_compute_fusion_trust(),
        operator_safety=_compute_operator_safety(),
        reliability_trend=_compute_reliability_trend(),
    )

    data = asdict(sb)
    json_path = DOCS / "gll_scoreboard.json"
    md_path = DOCS / "gll_scoreboard.md"

    json_path.write_text(sb.to_json())

    md_lines = [
        "# Ghost Lantern Labs — Scoreboard",
        "",
        f"Generated at: {ts}",
        "",
        "## GLL Readiness",
        "```json",
        json.dumps(data["readiness"], indent=2),
        "```",
        "",
        "## System Integrity",
        "```json",
        json.dumps(data["system_integrity"], indent=2),
        "```",
        "",
        "## Fusion Trust",
        "```json",
        json.dumps(data["fusion_trust"], indent=2),
        "```",
        "",
        "## Operator Safety Layer",
        "```json",
        json.dumps(data["operator_safety"], indent=2),
        "```",
        "",
        "## Reliability Trend",
        "```json",
        json.dumps(data["reliability_trend"], indent=2),
        "```",
        "",
    ]
    md_path.write_text("\n".join(md_lines))

    return {
        "json_path": str(json_path),
        "md_path": str(md_path),
        "generated_at": ts,
    }


if __name__ == "__main__":
    out = build_scoreboard()
    print("=== GLL SCOREBOARD BUILT ===")
    print(json.dumps(out, indent=2))

