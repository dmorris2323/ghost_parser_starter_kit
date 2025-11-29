"""
operator_snapshot.py

Builds a single text snapshot of GLL's current operational state.

Pulls from:
  - qa_summary.txt
  - critical_alerts.csv
  - daily_report.txt
  - Spectral Owl analysis
  - Cloud sync health
  - Threat memory stats

Outputs:
  - operator_snapshot.txt   (human-readable, commander-facing)
"""

from pathlib import Path
import csv

from spectral_owl.owl_brain import analyze_fusion
from spectral_owl.threat_memory import count_by_type, load_events
from cloud.azure_ingest import cloud_sync_health_check

SNAPSHOT_FILE = Path("operator_snapshot.txt")


def _read_file_text(path: Path, default: str = "N/A") -> str:
    if not path.exists():
        return default
    content = path.read_text(encoding="utf-8").strip()
    return content if content else default


def _count_critical_alerts() -> int:
    path = Path("critical_alerts.csv")
    if not path.exists():
        return 0

    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return sum(1 for _ in reader)


def _summarize_threat_memory() -> str:
    events = load_events()
    freq = count_by_type()
    total = len(events)
    if total == 0:
        return "No threat memory events recorded."

    parts = [f"{event}: {count}" for event, count in sorted(freq.items(), key=lambda x: x[1], reverse=True)]
    return f"{total} events total. Top patterns: " + "; ".join(parts)


def build_operator_snapshot() -> str:
    """
    Build and write the operator snapshot, return the text.
    """
    # QA summary
    qa_text = _read_file_text(Path("qa_summary.txt"), default="No QA summary found.")

    # Daily report
    daily_text = _read_file_text(Path("daily_report.txt"), default="No daily report found.")

    # Critical alerts count
    critical_count = _count_critical_alerts()

    # Owl analysis
    owl_result = analyze_fusion("scored_output.csv")

    # Threat memory overview
    threat_memory_summary = _summarize_threat_memory()

    # Cloud sync health
    cloud_health = cloud_sync_health_check()

    lines = []
    lines.append("======================================")
    lines.append(" GHOST LANTERN LABS — OPERATOR SNAPSHOT")
    lines.append("======================================\n")

    lines.append("1) PIPELINE & QA STATUS")
    lines.append("--------------------------------------")
    lines.append(qa_text)
    lines.append("")

    lines.append("2) ALERT STATUS")
    lines.append("--------------------------------------")
    lines.append(f"Critical alerts in current run: {critical_count}")
    lines.append("")

    lines.append("3) SPECTRAL OWL ASSESSMENT")
    lines.append("--------------------------------------")
    lines.append(str(owl_result))
    lines.append("")

    lines.append("4) THREAT MEMORY SUMMARY")
    lines.append("--------------------------------------")
    lines.append(threat_memory_summary)
    lines.append("")

    lines.append("5) CLOUD SYNC HEALTH")
    lines.append("--------------------------------------")
    lines.append(str(cloud_health))
    lines.append("")

    lines.append("6) DAILY REPORT (LAST RUN)")
    lines.append("--------------------------------------")
    lines.append(daily_text)
    lines.append("")

    snapshot_text = "\n".join(lines)
    SNAPSHOT_FILE.write_text(snapshot_text, encoding="utf-8")
    return snapshot_text

