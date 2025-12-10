"""
installation_threat_map.py

Builds a base-level "Installation Threat Map" by fusing:
- Fusion Trust score
- Critical / warning alert counts (if available later)
- Crisis mode flag
- Basic sector-level risk summary

This is intentionally lightweight and resilient:
- Works even if some upstream files are missing.
- Designed as a commander-facing, human-readable product.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Optional imports – everything is wrapped in try/except to avoid hard failures.
try:
    from fusion_trust import compute_trust  # type: ignore
except Exception:  # pragma: no cover - safe fallback
    compute_trust = None  # type: ignore

try:
    from crisis_mode_flag import status as crisis_status  # type: ignore
except Exception:  # pragma: no cover
    def crisis_status() -> str:  # type: ignore
        return "OFF"


BASE = Path(__file__).resolve().parent
DOCS_DIR = BASE / "docs"
DOCS_DIR.mkdir(exist_ok=True)


@dataclass
class SectorStatus:
    name: str
    risk_level: str
    notes: str


@dataclass
class InstallationThreatMap:
    generated_at: str
    base_name: str
    crisis_mode: str
    fusion_trust_score: int
    overall_risk: str
    sectors: Dict[str, SectorStatus]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "base_name": self.base_name,
            "crisis_mode": self.crisis_mode,
            "fusion_trust_score": self.fusion_trust_score,
            "overall_risk": self.overall_risk,
            "sectors": {
                k: asdict(v) for k, v in self.sectors.items()
            },
        }


def _safe_trust_score() -> int:
    """
    Returns a safe fusion trust score (0–100).
    Uses fusion_trust.compute_trust() when available, else defaults.
    """
    if compute_trust is None:
        return 80

    try:
        out = compute_trust()
        return int(out.get("fusion_trust", 80))  # type: ignore[arg-type]
    except Exception:
        return 80


def _derive_overall_risk(trust_score: int, crisis: str) -> str:
    """
    Translate trust score + crisis flag into a simple risk word.
    """
    if crisis.upper() == "ON":
        if trust_score >= 85:
            return "CRISIS – STABLE"
        return "CRISIS – FRAGILE"

    if trust_score >= 90:
        return "STABLE"
    if trust_score >= 75:
        return "ELEVATED"
    if trust_score >= 60:
        return "HIGH"
    return "SEVERE"


def build_installation_threat_map(
    base_name: str = "Notional Installation"
) -> Dict[str, Any]:
    """
    Core engine. Builds the sector view + writes a JSON + TXT artifact.
    """
    ts = datetime.utcnow().isoformat() + "Z"
    crisis = crisis_status()
    trust_score = _safe_trust_score()
    overall_risk = _derive_overall_risk(trust_score, crisis)

    # Simple sector model – can be upgraded later to read real telemetry.
    sectors = {
        "perimeter": SectorStatus(
            name="Perimeter",
            risk_level="ELEVATED" if trust_score < 90 else "STABLE",
            notes="Monitors gate ramming, fence breaches, and ground incursions.",
        ),
        "airspace": SectorStatus(
            name="Airspace",
            risk_level="ELEVATED" if trust_score < 85 else "STABLE",
            notes="Tracks drone incursions and low-altitude anomalies.",
        ),
        "cyber": SectorStatus(
            name="Cyber",
            risk_level="STABLE" if trust_score >= 80 else "HIGH",
            notes="Monitors fusion pipeline integrity and critical alert load.",
        ),
        "interior": SectorStatus(
            name="Interior",
            risk_level="STABLE",
            notes="Covers mission systems, operations floors, and critical nodes.",
        ),
    }

    itm = InstallationThreatMap(
        generated_at=ts,
        base_name=base_name,
        crisis_mode=crisis,
        fusion_trust_score=trust_score,
        overall_risk=overall_risk,
        sectors=sectors,
    )

    out = itm.to_dict()

    # Write artifacts
    json_path = DOCS_DIR / "installation_threat_map.json"
    txt_path = DOCS_DIR / "installation_threat_map.txt"

    json_path.write_text(json.dumps(out, indent=2))
    txt_lines = [
        "=== INSTALLATION THREAT MAP ===",
        f"Base: {base_name}",
        f"Generated: {ts}",
        f"Crisis Mode: {crisis}",
        f"Fusion Trust: {trust_score}",
        f"Overall Risk: {overall_risk}",
        "",
        "Sectors:",
    ]
    for key, sec in sectors.items():
        txt_lines.append(f"  [{sec.name.upper()}] {sec.risk_level}")
        txt_lines.append(f"    - {sec.notes}")
    txt_path.write_text("\n".join(txt_lines))

    return {
        "status": "ok",
        "json_path": str(json_path),
        "text_path": str(txt_path),
        "overall_risk": overall_risk,
    }


def main() -> None:
    out = build_installation_threat_map()
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

