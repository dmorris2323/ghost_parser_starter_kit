"""
daily_mission_brief.py

Ghost Lantern Labs – Daily Mission Brief (Text)

This file builds a consolidated text brief that can be:
- Saved as docs/daily_mission_brief.txt
- Fed into mission_brief_html.py
- Viewed in CLI or GUI

Sections:
- Header + timestamp
- Pipeline health (if available)
- Operator snapshot (if available)
- Sensor readiness + reliability
- Threat memory summary (if available)

All external module calls are wrapped so that:
- If a module returns a dict, we stringify it.
- If a module throws, we log a WARN line instead of crashing.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List

from sensor_readiness_brief import build_readiness_brief
from sensor_reliability import build_reliability_report_text

# Optional imports – all wrapped in try/except to avoid crashes.
try:
    from pipeline_health import evaluate_pipeline_health
except ImportError:
    evaluate_pipeline_health = None  # type: ignore

try:
    from operator_snapshot import build_operator_snapshot
except ImportError:
    build_operator_snapshot = None  # type: ignore

try:
    from spectral_owl.threat_memory_summary import build_summary as build_threat_summary
except ImportError:
    build_threat_summary = None  # type: ignore


BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "docs"


def _section_header(title: str) -> str:
    return f"=== {title.upper()} ==="


def _stringify(value) -> str:
    """
    Ensure any value becomes a clean string for appending to the brief.
    - dict → repr()
    - other → str()
    """
    if isinstance(value, dict):
        return repr(value)
    return str(value)


def build_mission_brief() -> str:
    now = datetime.now()
    lines: List[str] = []

    # Header
    lines.append("Ghost Lantern Labs – Daily Mission Brief")
    lines.append(now.strftime("Generated: %Y-%m-%d %H:%M:%S"))
    lines.append("")
    lines.append(_section_header("System Overview"))
    lines.append("GLL is running as an offline-capable fusion + AI ISR platform.")
    lines.append("")

    # Pipeline health
    lines.append(_section_header("Pipeline Health"))
    if evaluate_pipeline_health is not None:
        try:
            summary = evaluate_pipeline_health()
            lines.append(_stringify(summary))
        except Exception as e:
            lines.append(f"[WARN] Pipeline health check failed: {e}")
    else:
        lines.append("[INFO] pipeline_health module not available.")
    lines.append("")

    # Operator snapshot
    lines.append(_section_header("Operator Snapshot"))
    if build_operator_snapshot is not None:
        try:
            snapshot_text = build_operator_snapshot()
            lines.append(_stringify(snapshot_text))
        except Exception as e:
            lines.append(f"[WARN] Operator snapshot failed: {e}")
    else:
        lines.append("[INFO] operator_snapshot module not available.")
    lines.append("")

    # Sensor readiness + reliability
    lines.append(_section_header("Sensor Readiness & Reliability"))
    try:
        readiness = build_readiness_brief()
        lines.append(_stringify(readiness))
    except Exception as e:
        lines.append(f"[WARN] Sensor readiness section failed: {e}")
    lines.append("")

    lines.append(_section_header("Sensor Reliability Detail"))
    try:
        rel_report = build_reliability_report_text()
        lines.append(_stringify(rel_report))
    except Exception as e:
        lines.append(f"[WARN] Reliability report failed: {e}")
    lines.append("")

    # Threat memory
    lines.append(_section_header("Threat Memory Snapshot"))
    if build_threat_summary is not None:
        try:
            t_summary = build_threat_summary()
            lines.append(_stringify(t_summary))
        except Exception as e:
            lines.append(f"[WARN] Threat memory summary failed: {e}")
    else:
        lines.append("[INFO] threat_memory_summary not available.")
    lines.append("")

    return "\n".join(lines)


def write_daily_brief(path: Path | None = None) -> Path:
    """
    Write the mission brief to docs/daily_mission_brief.txt
    and return the Path.
    """
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    if path is None:
        path = DOCS_DIR / "daily_mission_brief.txt"

    text = build_mission_brief()
    path.write_text(text, encoding="utf-8")
    return path


if __name__ == "__main__":
    out = write_daily_brief()
    print(f"[OK] Daily mission brief written → {out}")

