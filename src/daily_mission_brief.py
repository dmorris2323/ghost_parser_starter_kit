"""
daily_mission_brief.py — Text mission brief for Ghost Lantern Labs.

Sections:
  - Pipeline health
  - Sensor readiness
  - Sensor reliability summary
  - Reliability trend
  - Owl confidence (fallback estimator)
  - Crisis Mode status
  - Operator identity
"""

from pathlib import Path
import json

from pipeline_health import evaluate_pipeline_health
from sensor_readiness_brief import build_readiness_brief
from sensor_reliability import compute_reliability_all
from reliability_trend import compute_trend
from spectral_owl.owl_confidence import compute_confidence
from crisis_mode_flag import status as crisis_status
from operator_identity import get_identity

BRIEF_TXT_PATH = Path("docs/daily_mission_brief.txt")


def build_mission_brief() -> str:
    lines: list[str] = []

    # Header
    lines.append("=== GHOST LANTERN LABS — DAILY MISSION BRIEF ===")
    lines.append(f"Operator: {get_identity()}")
    lines.append(f"Crisis Mode: {crisis_status()}")
    lines.append("")

    # 1) Pipeline Health
    try:
        health = evaluate_pipeline_health()
        lines.append("=== PIPELINE HEALTH ===")
        lines.append(json.dumps(health, indent=2))
        lines.append("")
    except Exception as e:
        lines.append("=== PIPELINE HEALTH ===")
        lines.append(f"Failed to evaluate pipeline health: {e}")
        lines.append("")

    # 2) Sensor Readiness
    try:
        lines.append("=== SENSOR READINESS BRIEF ===")
        readiness_text = build_readiness_brief()
        if isinstance(readiness_text, str):
            lines.append(readiness_text)
        else:
            lines.append(json.dumps(readiness_text, indent=2))
        lines.append("")
    except Exception as e:
        lines.append("=== SENSOR READINESS BRIEF ===")
        lines.append(f"Failed to build readiness brief: {e}")
        lines.append("")

    # 3) Sensor Reliability Summary
    reliability_summary = None
    try:
        lines.append("=== SENSOR RELIABILITY SUMMARY ===")
        reliability_summary = compute_reliability_all()
        lines.append(json.dumps(reliability_summary, indent=2))
        lines.append("")
    except Exception as e:
        lines.append("=== SENSOR RELIABILITY SUMMARY ===")
        lines.append(f"Failed to compute reliability: {e}")
        lines.append("")

    # 4) Reliability Trend
    try:
        lines.append("=== RELIABILITY TREND ===")
        trend = compute_trend()
        if isinstance(trend, (dict, list)):
            lines.append(json.dumps(trend, indent=2))
        else:
            lines.append(str(trend))
        lines.append("")
    except Exception as e:
        lines.append("=== RELIABILITY TREND ===")
        lines.append(f"Failed to compute reliability trend: {e}")
        lines.append("")

    # 5) Owl Confidence
    try:
        lines.append("=== OWL CONFIDENCE ===")
        # Derive rough counts from reliability_summary if available
        crit = 0
        warn = 0
        avg_rel = 90.0
        if isinstance(reliability_summary, dict):
            crit = reliability_summary.get("total_critical", 0) or 0
            warn = reliability_summary.get("total_warnings", 0) or 0
            avg_rel = reliability_summary.get("avg_reliability", 90.0) or 90.0
        sample = {
            "critical_alerts": crit,
            "warning_alerts": warn,
            "avg_reliability": avg_rel,
        }
        conf = compute_confidence(sample)
        lines.append(f"Sample confidence: {conf} (crit={crit}, warnings={warn}, avg_rel={avg_rel})")
        lines.append("")
    except Exception as e:
        lines.append("=== OWL CONFIDENCE ===")
        lines.append(f"Failed to compute Owl confidence: {e}")
        lines.append("")

    # 6) Crisis Mode status block (explicit)
    lines.append("=== CRISIS MODE ===")
    lines.append(crisis_status())
    lines.append("")

    return "\n".join(lines)


def write_daily_brief() -> str:
    BRIEF_TXT_PATH.parent.mkdir(parents=True, exist_ok=True)
    text = build_mission_brief()
    BRIEF_TXT_PATH.write_text(text)
    return str(BRIEF_TXT_PATH)


if __name__ == "__main__":
    path = write_daily_brief()
    print(f"Daily mission brief written to: {path}")

