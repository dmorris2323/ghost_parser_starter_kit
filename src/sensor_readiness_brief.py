"""
sensor_readiness_brief.py

Builds a combined SENSOR READINESS + basic profile info + reliability snapshot.

Depends on:
- manifest_health.run_manifest_health()
- (optional) sensor_profile_loader.load_profile()
- sensor_reliability.compute_reliability_scores()
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from manifest_health import run_manifest_health
from sensor_reliability import compute_reliability_scores, ascii_bar

# sensor_profile_loader is optional – we degrade gracefully if it doesn't exist.
try:
    from sensor_profile_loader import load_profile  # type: ignore
except ImportError:
    load_profile = None  # type: ignore


def build_readiness_brief() -> str:
    """
    Returns a multi-line string summarizing:
    - Sensor manifest health (enabled/disabled)
    - Known sensor profiles (if available)
    - Reliability scores per sensor (from sensor_reliability)
    """
    mh = run_manifest_health()
    reliability_map = compute_reliability_scores()

    enabled = mh.get("enabled", []) or []
    disabled = mh.get("disabled", []) or []
    missing = mh.get("missing_from_manifest", []) or []
    unknown = mh.get("unknown_sensors", []) or []

    lines: List[str] = []
    lines.append("=== SENSOR READINESS OVERVIEW ===")
    lines.append(f"Total sensors in manifest: {mh.get('total', len(enabled) + len(disabled))}")
    lines.append(f"Enabled: {len(enabled)}")
    lines.append(f"Disabled: {len(disabled)}")

    if missing:
        lines.append(f"Missing in manifest: {', '.join(sorted(missing))}")
    if unknown:
        lines.append(f"Unknown sensors: {', '.join(sorted(unknown))}")
    lines.append("")

    # Detail per enabled sensor
    for name in sorted(enabled):
        lines.append(f"[{name.upper()}]")

        # Optional profile block
        prof = None
        if load_profile is not None:
            try:
                prof = load_profile(name)
            except Exception:
                prof = None

        if prof:
            desc = prof.get("description") or "No description"
            warn = prof.get("warning_threshold")
            crit = prof.get("critical_threshold")
            lines.append(f"  Desc: {desc}")
            if warn is not None and crit is not None:
                lines.append(f"  Warn: {warn}  Critical: {crit}")

        # Reliability block
        rel = reliability_map.get(name)
        if rel:
            bar = ascii_bar(rel.reliability)
            lines.append(f"  Reliability: {bar}  {rel.reliability:5.1f}%  ({rel.projected_window})")
            if rel.last_seen:
                lines.append(f"  Last seen: {rel.last_seen}")
        else:
            lines.append("  Reliability: [no data]")

        lines.append("")

    # Disabled sensors at the end
    if disabled:
        lines.append("=== DISABLED SENSORS ===")
        for name in sorted(disabled):
            lines.append(f"- {name}")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    print(build_readiness_brief())

