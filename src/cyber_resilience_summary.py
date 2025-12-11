#!/usr/bin/env python3
"""
cyber_resilience_summary.py

Ghost Lantern Labs – Cyber Fusion Resilience Summary
----------------------------------------------------

Purpose:
    Generate a unified cyber-resilience summary for GLL that covers:

        - Ingest / DoS stress (anti_dos_guard)
        - Cloud / Azure ingest readiness (azure_ingest_adapter)

    Outputs:
        - docs/cyber_resilience_summary.json
        - docs/cyber_resilience_summary.txt

    This is read-only with respect to the fusion pipeline and configs.
    It is safe to run at any time as a status/check-up tool.
"""

import json
import os
from typing import Any, Dict, List

from anti_dos_guard import analyze_dos_surface
from azure_ingest_adapter import inspect_azure_config


BASE_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(BASE_DIR, "docs")

SUMMARY_JSON = os.path.join(DOCS_DIR, "cyber_resilience_summary.json")
SUMMARY_TXT = os.path.join(DOCS_DIR, "cyber_resilience_summary.txt")


def _ensure_docs_dir() -> None:
    os.makedirs(DOCS_DIR, exist_ok=True)


def build_cyber_resilience_summary() -> Dict[str, Any]:
    """
    Build the combined resilience summary payload.
    """
    dos = analyze_dos_surface()
    azure = inspect_azure_config()

    return {
        "title": "Ghost Lantern Labs – Cyber Fusion Resilience Summary",
        "dos_analysis": dos,
        "azure_ingest_status": azure,
    }


def _format_text(summary: Dict[str, Any]) -> str:
    """
    Produce a human-readable text version of the cyber resilience summary.
    """
    lines: List[str] = []
    lines.append("Ghost Lantern Labs – Cyber Fusion Resilience Summary")
    lines.append("=" * 64)
    lines.append("")

    dos = summary.get("dos_analysis", {}) or {}
    azure = summary.get("azure_ingest_status", {}) or {}

    # DoS / ingest stress section
    lines.append("1) Ingest / DoS Stress Analysis")
    lines.append("-" * 40)
    lines.append(f"Status: {dos.get('status', 'UNKNOWN')}")
    if dos.get("message"):
        lines.append(f"Message: {dos.get('message')}")
    lines.append(f"Total events: {dos.get('total_events', 0)}")
    lines.append(f"Unique sensors: {dos.get('unique_sensors', 0)}")
    lines.append(f"Time span (minutes): {dos.get('time_span_minutes')}")
    lines.append(f"Avg events/minute: {dos.get('avg_events_per_minute')}")
    lines.append(f"Burst level: {dos.get('burst_level')}")
    lines.append("")
    lines.append("Findings:")
    for f in dos.get("findings", []):
        lines.append(f"  - {f}")
    lines.append("")
    lines.append("Recommendations:")
    for r in dos.get("recommendations", []):
        lines.append(f"  - {r}")
    lines.append("")

    # Azure / cloud ingest section
    lines.append("2) Azure / Cloud Ingest Readiness")
    lines.append("-" * 40)
    lines.append(f"Status: {azure.get('status', 'UNKNOWN')}")
    if azure.get("message"):
        lines.append(f"Message: {azure.get('message')}")
    lines.append(f"Config path: {azure.get('config_path')}")
    lines.append(f"Enabled: {azure.get('enabled')}")
    lines.append(f"Mode: {azure.get('mode')}")
    lines.append("")
    issues = azure.get("issues", [])
    if issues:
        lines.append("Config Issues:")
        for issue in issues:
            lines.append(f"  - {issue}")
    else:
        lines.append("Config Issues: None noted.")
    lines.append("")

    storage = azure.get("storage_account", {}) or {}
    event_hub = azure.get("event_hub", {}) or {}

    lines.append("Storage Account (if applicable):")
    lines.append(f"  - Name: {storage.get('name')}")
    lines.append(f"  - Container: {storage.get('container')}")
    lines.append("")
    lines.append("Event Hub (if applicable):")
    lines.append(f"  - Namespace: {event_hub.get('namespace')}")
    lines.append(f"  - Name: {event_hub.get('name')}")
    lines.append("")

    lines.append("3) Next Steps (High-Level)")
    lines.append("-" * 40)

    # High-level guidance based on combined view
    burst = (dos.get("burst_level") or "NO_DATA").upper()
    azure_status = (azure.get("status") or "UNKNOWN").upper()

    if burst in ("MEDIUM", "HIGH"):
        lines.append(
            "  - Treat ingest behavior as an active cyber-resilience concern; "
            "plan rate limits and ingest playbooks as you harden GLL."
        )
    else:
        lines.append(
            "  - Current ingest behavior does not show clear DoS signs, "
            "but you should still plan for rate-limiting and burst handling."
        )

    if azure_status == "READY":
        lines.append(
            "  - Azure ingest is configured and marked ready – next step is controlled, "
            "non-production tests feeding GLL's fusion_ingest from cloud telemetry."
        )
    elif azure_status == "PARTIAL":
        lines.append(
            "  - Azure ingest has partial configuration; tighten missing fields before "
            "attempting any real cloud integration."
        )
    else:
        lines.append(
            "  - Azure ingest has not been configured yet – this is acceptable at this phase. "
            "Use the provided template when you're ready to attach cloud sources."
        )

    lines.append("")
    lines.append("This document is suitable for: cyber/ISR design reviews, "
                 "training briefs, or early-stage investor / SBIR conversations about GLL's resilience posture.")
    lines.append("")

    return "\n".join(lines)


def write_cyber_resilience_summary() -> Dict[str, Any]:
    """
    Build and write the summary to JSON and TXT files.
    """
    _ensure_docs_dir()
    summary = build_cyber_resilience_summary()

    with open(SUMMARY_JSON, "w", encoding="utf-8") as f_json:
        json.dump(summary, f_json, indent=2)

    text = _format_text(summary)
    with open(SUMMARY_TXT, "w", encoding="utf-8") as f_txt:
        f_txt.write(text)

    return {
        "json_path": SUMMARY_JSON,
        "txt_path": SUMMARY_TXT,
        "summary": summary,
    }


if __name__ == "__main__":
    result = write_cyber_resilience_summary()
    print("Cyber Resilience Summary written:")
    print(f"  JSON: {result['json_path']}")
    print(f"  TXT:  {result['txt_path']}")

