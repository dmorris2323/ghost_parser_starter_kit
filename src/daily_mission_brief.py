"""
daily_mission_brief.py — Text Mission Brief for Ghost Lantern Labs

Builds a commander-style daily brief that summarizes:
- System status
- Pipeline health
- Sensor readiness & reliability
- Threat memory snapshot
- Cross-sensor validation (if available)
"""

from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
DOCS = BASE / "docs"
DOCS.mkdir(exist_ok=True)


def load_text(path: Path, label: str | None = None) -> list[str]:
    """Load a text file if it exists, else return a placeholder line."""
    if not path.exists():
        if label:
            return [f"[{label}] No data available."]
        return []
    text = path.read_text().strip()
    if not text:
        if label:
            return [f"[{label}] File was empty."]
        return []
    lines = text.splitlines()
    if label:
        return [f"=== {label} ==="] + lines + [""]
    return lines + [""]


def build_mission_brief() -> str:
    lines: list[str] = []

    # Header
    lines.append("GHOST LANTERN LABS — DAILY MISSION BRIEF")
    lines.append("----------------------------------------")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("")

    # Active profile (if available)
    try:
        from profile_config import get_active_profile

        prof = get_active_profile()
        display_name = getattr(prof, "display_name", None) or getattr(
            prof, "name", "UNKNOWN_PROFILE"
        )
        domain = getattr(prof, "domain", "unknown-domain")
        lines.append(f"Active Profile: {display_name}  (domain: {domain})")
    except Exception:
        lines.append("Active Profile: UNKNOWN (profile_config error)")
    lines.append("")

    # System / pipeline summary (text files produced by other tools)
    lines += load_text(BASE / "system_status_dashboard.txt", "SYSTEM STATUS")
    lines += load_text(BASE / "pipeline_health.txt", "PIPELINE HEALTH")
    lines += load_text(BASE / "sensor_health_report.txt", "SENSOR HEALTH")

    # Threat memory snapshot
    threat_summary_path = DOCS / "threat_memory_summary_day56.txt"
    if not threat_summary_path.exists():
        threat_summary_path = DOCS / "threat_memory_doctrine_report.txt"
    lines += load_text(threat_summary_path, "THREAT MEMORY SNAPSHOT")

    # Sensor reliability
    reliability_report = DOCS / "reliability_report.txt"
    lines += load_text(reliability_report, "SENSOR RELIABILITY")

    # Cross-sensor validation
    cross_sensor_report = DOCS / "cross_sensor_report.txt"
    lines += load_text(cross_sensor_report, "CROSS-SENSOR VALIDATION")

    # AI / LLM status (optional)
    try:
        from llm_phase2_adapter import describe_active_provider

        lines.append("=== AI / LLM ENGINE STATUS ===")
        lines.append(describe_active_provider())
        lines.append("")
    except Exception:
        pass

    return "\n".join(lines)


def write_daily_brief() -> Path:
    text = build_mission_brief()
    out_path = DOCS / "daily_mission_brief.txt"
    out_path.write_text(text)
    print(f"[OK] Daily mission brief written → {out_path}")
    return out_path


if __name__ == "__main__":
    write_daily_brief()

