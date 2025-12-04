"""
Golden Dome Validator — GLL Mission Integrity Check
---------------------------------------------------
Runs a full ISR-grade validation cycle:

 - Sensor manifest status
 - Reliability scores
 - Cross-sensor agreement
 - AI-Independence health
 - Profile alignment
 - Threat memory stability
 - Fusion scoring presence
 - Minimap + SOS overlay presence

Outputs:
  docs/golden_dome_validation.txt
"""

from pathlib import Path
from datetime import datetime

from manifest_health import run_manifest_health
from sensor_reliability import compute_reliability_all
from cross_sensor_report import build_report
from llm_phase2_adapter import get_active_provider
from profile_config import get_active_profile
from spectral_owl.owl_memory import load_memory_log
from fusion_minimap import build_minimap
from spectral_sos_overlay import build_sos_overlay


OUT_PATH = Path("docs/golden_dome_validation.txt")


def build_validation():
    lines = []
    lines.append("=== GLL GOLDEN DOME VALIDATION REPORT ===")
    lines.append(f"Timestamp: {datetime.utcnow().isoformat()}Z")
    lines.append("")

    # Manifest
    mh = run_manifest_health()
    lines.append("=== SENSOR MANIFEST ===")
    lines.append(f"Total Sensors: {mh['total']}")
    lines.append(f"Enabled: {mh['enabled']}")
    lines.append(f"Disabled: {mh['disabled']}")
    lines.append("")

    # Reliability
    rel = compute_reliability_all()
    lines.append("=== SENSOR RELIABILITY ===")
    for k, v in rel.items():
        lines.append(f"{k.upper():10} — {v['score']}%  (last_ok={v['last_ok']})")
    lines.append("")

    # Cross-Sensor
    lines.append("=== CROSS-SENSOR AGREEMENT ===")
    csr = build_report()
    lines.append(csr["summary"])
    lines.append(f"Report saved: {csr['path']}")
    lines.append("")

    # AI Provider
    lines.append("=== AI ENGINE STATUS ===")
    provider = get_active_provider()
    lines.append(f"Provider: {provider}")
    lines.append("")

    # Profile
    p = get_active_profile()
    lines.append("=== ACTIVE PROFILE ===")
    lines.append(f"{p.key}  ({p.display_name})")
    lines.append("")

    # Threat Memory
    tm = load_memory_log()
    lines.append("=== THREAT MEMORY ===")
    lines.append(f"Events recorded: {len(tm)}")
    lines.append("")

    # Minimap
    lines.append("=== MINIMAP STATUS ===")
    mini = build_minimap()
    lines.append(f"Critical: {mini['map'].get('critical', 0)}%")
    lines.append(f"Warning : {mini['map'].get('warning', 0)}%")
    lines.append(f"Stable  : {mini['map'].get('stable', 0)}%")
    lines.append("")

    # SOS Overlay
    lines.append("=== SOS OVERLAY ===")
    sos = build_sos_overlay()
    lines.append(f"Status: {sos.get('status', 'unknown')}")
    lines.append("")

    OUT_PATH.write_text("\n".join(lines))
    return {"status": "ok", "path": str(OUT_PATH)}


if __name__ == "__main__":
    print(build_validation())

