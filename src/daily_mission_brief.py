"""
daily_mission_brief.py

Builds the text daily mission brief for Ghost Lantern Labs.
This version includes:

- Operator name
- Crisis mode
- Pipeline health
- Sensor readiness
- Sensor reliability summary (if available)
- Reliability trend (if available)
- Owl confidence (simple sample)
- Fusion Trust Score
- Operator Safety Layer (OSL)
- Sensor latency report
"""

from pathlib import Path
import json

# Core health + status
from pipeline_health import evaluate_pipeline_health
from sensor_readiness_brief import build_readiness_brief

# Higher-level trust and safety layers
from fusion_trust import compute_trust
from operator_safety_layer import compute_osl

# Crisis + operator identity
from crisis_mode_flag import status as crisis_status
from operator_identity import get_identity

# Sensor latency block
from sensor_latency import compute_latency_report

# Optional imports wrapped in try/except so nothing breaks if missing
try:
    from reliability_trend import compute_trend
except ImportError:
    compute_trend = None

try:
    from sensor_reliability import compute_reliability_report  # if you have it
except ImportError:
    compute_reliability_report = None

try:
    from spectral_owl.owl_confidence import compute_confidence
except ImportError:
    compute_confidence = None


OUTPUT_TXT = Path("docs/daily_mission_brief.txt")


def build_mission_brief() -> str:
    """
    Build the full text mission brief as a single string.
    """
    lines = []

    # Header
    lines.append("=== GHOST LANTERN LABS — DAILY MISSION BRIEF ===")
    lines.append(f"Operator: {get_identity()}")
    lines.append(f"Crisis Mode: {crisis_status()}")
    lines.append("")

    # Pipeline health
    try:
        health = evaluate_pipeline_health()
        lines.append("=== PIPELINE HEALTH ===")
        lines.append(json.dumps(health, indent=2))
        lines.append("")
    except Exception as e:
        lines.append("=== PIPELINE HEALTH ===")
        lines.append(f"[ERROR] Pipeline health failed: {e}")
        lines.append("")

    # Sensor readiness brief
    try:
        readiness = build_readiness_brief()
        lines.append("=== SENSOR READINESS BRIEF ===")
        lines.append(readiness)
        lines.append("")
    except Exception as e:
        lines.append("=== SENSOR READINESS BRIEF ===")
        lines.append(f"[ERROR] Sensor readiness failed: {e}")
        lines.append("")

    # Sensor reliability (if function exists)
    if compute_reliability_report is not None:
        try:
            rel = compute_reliability_report()
            lines.append("=== SENSOR RELIABILITY SUMMARY ===")
            lines.append(json.dumps(rel, indent=2))
            lines.append("")
        except Exception as e:
            lines.append("=== SENSOR RELIABILITY SUMMARY ===")
            lines.append(f"[ERROR] Reliability summary failed: {e}")
            lines.append("")

    # Reliability trend (if module exists)
    if compute_trend is not None:
        try:
            trend = compute_trend()
            lines.append("=== RELIABILITY TREND ===")
            lines.append(json.dumps(trend, indent=2))
            lines.append("")
        except Exception as e:
            lines.append("=== RELIABILITY TREND ===")
            lines.append(f"[ERROR] Reliability trend failed: {e}")
            lines.append("")

    # Owl confidence (simple sample – safe even if no real data)
    lines.append("=== OWL CONFIDENCE ===")
    if compute_confidence is not None:
        try:
            sample = {"critical_alerts": 0, "warning_alerts": 0, "avg_reliability": 92.0}
            conf = compute_confidence(sample)
            lines.append(f"Sample confidence: {conf} (crit=0, warnings=0, avg_rel=92.0)")
        except Exception as e:
            lines.append(f"[ERROR] Owl confidence failed: {e}")
    else:
        lines.append("Owl confidence model not available.")
    lines.append("")

    # Crisis mode (already printed at top, but keep explicit section)
    lines.append("=== CRISIS MODE ===")
    lines.append(crisis_status())
    lines.append("")

    # Fusion Trust Score
    lines.append("=== FUSION TRUST SCORE ===")
    try:
        ts = compute_trust()
        lines.append(json.dumps(ts, indent=2))
    except Exception as e:
        lines.append(f"[ERROR] Fusion trust computation failed: {e}")
    lines.append("")

    # Operator Safety Layer
    lines.append("=== OPERATOR SAFETY LAYER ===")
    try:
        osl = compute_osl()
        lines.append(json.dumps(osl, indent=2))
    except Exception as e:
        lines.append(f"[ERROR] Operator Safety Layer failed: {e}")
    lines.append("")

    # === SENSOR LATENCY REPORT ===
    lines.append("=== SENSOR LATENCY ===")
    try:
        lat = compute_latency_report()
        lines.append(json.dumps(lat, indent=2))
    except Exception as e:
        lines.append(f"[ERROR] Sensor latency report failed: {e}")
    lines.append("")

    return "\n".join(lines)


def write_daily_brief() -> str:
    """
    Build and write the daily mission brief to docs/daily_mission_brief.txt.
    Returns the brief text.
    """
    text = build_mission_brief()
    OUTPUT_TXT.parent.mkdir(exist_ok=True, parents=True)
    OUTPUT_TXT.write_text(text)
    return text


if __name__ == "__main__":
    out = write_daily_brief()
    print(out)

