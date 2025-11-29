"""
threat_memory_summary.py

Turns raw threat memory into human-intel output:

• top recurring anomalies
• DoS frequency & spike detection
• summary sections for operator briefing
"""

from .threat_memory import load_events, count_by_type


def build_summary(limit=50) -> str:
    events = load_events()
    freq = count_by_type()

    lines = []
    lines.append("===== THREAT MEMORY SUMMARY =====")
    lines.append(f"Total recorded anomalies: {len(events)}")
    lines.append("")

    # Top recurring threat categories
    lines.append("Top recurring threat types:")
    for event, count in sorted(freq.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"  • {event}: {count} occurrences")
    lines.append("")

    # Recent selection
    lines.append(f"Most recent {min(len(events), limit)} events:")
    for e in events[-limit:]:
        lines.append(f"  [{e['severity']}] {e['event_type']} — {e['details']}")

    lines.append("\nSummary complete.\n")
    return "\n".join(lines)

