"""
mission_briefing.py
-------------------

Builds a compact text mission brief combining:

 - Pipeline health status
 - Fusion / threat status from Spectral Owl
 - Short threat snapshot for context

Used by:
 - ghost_cli.py (Option 8: Mission briefing)
 - daily_mission_brief.py (as CORE MISSION STATUS)
"""

from datetime import datetime
from typing import Dict, Any

from pipeline_health import evaluate_pipeline_health
from spectral_owl.owl_brain import analyze_fusion, threat_snapshot


def _format_pipeline_health(health: Dict[str, Any]) -> str:
    lines = []
    status = health.get("status", "unknown")
    lines.append(f"Pipeline status: {status}")

    missing = health.get("missing_outputs") or []
    if missing:
        lines.append(f"Missing outputs: {', '.join(missing)}")
    else:
        lines.append("Missing outputs: none")

    warnings = health.get("warnings") or []
    if warnings:
        lines.append("Warnings:")
        for w in warnings:
            lines.append(f"  - {w}")

    return "\n".join(lines)


def _format_fusion_status(fusion: Dict[str, Any]) -> str:
    lines = []
    status = fusion.get("status", "unknown")
    total = fusion.get("total_rows", 0)
    crit = fusion.get("critical_events", 0)
    rec = fusion.get("recommendation", "")

    lines.append(f"Fusion status: {status}")
    lines.append(f"Total fused rows: {total}")
    lines.append(f"Critical events: {crit}")
    if rec:
        lines.append(f"Recommendation: {rec}")

    msg = fusion.get("message")
    if msg:
        lines.append(f"Note: {msg}")

    return "\n".join(lines)


def build_mission_briefing() -> str:
    """
    Returns a multi-line mission brief string.
    """

    lines = []
    lines.append("=== GLL MISSION BRIEF ===")
    lines.append(f"Generated (UTC): {datetime.utcnow().isoformat()}")
    lines.append("")

    # Pipeline health
    try:
        health = evaluate_pipeline_health()
        lines.append(">>> PIPELINE HEALTH")
        lines.append(_format_pipeline_health(health))
    except Exception as e:
        lines.append(">>> PIPELINE HEALTH")
        lines.append(f"Error evaluating pipeline health: {e}")
    lines.append("")

    # Fusion / Spectral Owl
    try:
        fusion = analyze_fusion()
        lines.append(">>> FUSION / SPECTRAL OWL STATUS")
        lines.append(_format_fusion_status(fusion))
    except Exception as e:
        lines.append(">>> FUSION / SPECTRAL OWL STATUS")
        lines.append(f"Error analyzing fusion scores: {e}")
    lines.append("")

    # Threat snapshot (short form)
    try:
        lines.append(">>> THREAT SNAPSHOT (OWL MEMORY)")
        lines.append(threat_snapshot(max_events=3))
    except Exception as e:
        lines.append(">>> THREAT SNAPSHOT (OWL MEMORY)")
        lines.append(f"Error building threat snapshot: {e}")
    lines.append("")

    return "\n".join(lines)


def main():
    brief = build_mission_briefing()
    print(brief)


if __name__ == "__main__":
    main()

