#!/usr/bin/env python3
"""
sps_mutation_watcher.py

Ghost Lantern Labs – Self-Preservation Shield (SPS) – Module 2
--------------------------------------------------------------

Purpose:
    Track file-level changes to the GLL codebase between runs to detect
    unexpected mutations, missing modules, or suspicious zero-byte files.

    This module:
        - Walks the src/ tree and records .py files.
        - Builds a snapshot with path, size, mtime, and sha256 hash.
        - Compares the current snapshot with the last snapshot (if any).
        - Reports:
            • new_files
            • removed_files
            • changed_files
            • zero_byte_files
            • critical_file_alerts

    Outputs:
        - docs/sps_file_snapshot.json      (latest snapshot)
        - docs/sps_mutation_report.json    (diff + narrative)
        - docs/sps_mutation_report.txt     (human-readable)

    Safety:
        - READ-ONLY with respect to source files.
        - Writes only into docs/.
        - No network calls.
"""

import os
import json
import hashlib
from typing import Any, Dict, List
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
DOCS_DIR = os.path.join(BASE_DIR, "docs")

SNAPSHOT_PATH = os.path.join(DOCS_DIR, "sps_file_snapshot.json")
REPORT_JSON = os.path.join(DOCS_DIR, "sps_mutation_report.json")
REPORT_TXT = os.path.join(DOCS_DIR, "sps_mutation_report.txt")


def _ensure_docs_dir() -> None:
    os.makedirs(DOCS_DIR, exist_ok=True)


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _normalized_rel_path(path: str) -> str:
    return os.path.relpath(path, REPO_ROOT).replace(os.sep, "/")


def build_current_snapshot() -> Dict[str, Dict[str, Any]]:
    """
    Walk the src/ tree and capture .py files with basic metadata.
    Returns a dict keyed by normalized relative path.
    """
    snapshot: Dict[str, Dict[str, Any]] = {}

    for root, dirs, files in os.walk(BASE_DIR):
        for name in files:
            if not name.endswith(".py"):
                continue
            full_path = os.path.join(root, name)
            try:
                stat = os.stat(full_path)
            except FileNotFoundError:
                continue

            rel_path = _normalized_rel_path(full_path)
            size = stat.st_size
            mtime = stat.st_mtime
            try:
                digest = _sha256_file(full_path) if size > 0 else ""
            except Exception:
                digest = ""

            snapshot[rel_path] = {
                "rel_path": rel_path,
                "size_bytes": size,
                "mtime": mtime,
                "sha256": digest,
            }

    return snapshot


def _load_previous_snapshot() -> Dict[str, Dict[str, Any]]:
    if not os.path.exists(SNAPSHOT_PATH):
        return {}
    try:
        with open(SNAPSHOT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {}
        normalized: Dict[str, Dict[str, Any]] = {}
        for k, v in data.items():
            if isinstance(v, dict) and "rel_path" in v:
                normalized[k] = v
        return normalized
    except Exception:
        return {}


def compare_snapshots(
    prev: Dict[str, Dict[str, Any]],
    curr: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Compare two snapshots and produce change lists.
    """
    prev_keys = set(prev.keys())
    curr_keys = set(curr.keys())

    new_files = sorted(curr_keys - prev_keys)
    removed_files = sorted(prev_keys - curr_keys)
    common = prev_keys & curr_keys

    changed_files: List[str] = []
    zero_byte_files: List[str] = []

    for k in common:
        p = prev[k]
        c = curr[k]
        if p.get("size_bytes") != c.get("size_bytes") or p.get("sha256") != c.get("sha256"):
            changed_files.append(k)

    for k, meta in curr.items():
        if meta.get("size_bytes", 0) == 0:
            zero_byte_files.append(k)

    # Critical file monitoring
    critical_rel_paths = [
        "src/ghost_cli.py",
        "src/spectral_dashboard_api.py",
        "src/fusion_ingest.py",
        "src/fusion_scoring.py",
        "src/fusion_alerts.py",
        "src/daily_mission_brief.py",
        "src/mission_brief_html.py",
        "src/golden_dome_daily_watch.py",
        "src/nuclear_decision_card.py",
        "src/treaty_evidence_bundle.py",
        "src/installation_threat_map.py",
        "src/sensor_outage_predictor.py",
        "src/distributed_readiness_snapshot.py",
        "src/perimeter_incident_report.py",
        "src/base_defense_storyboard.py",
        "src/sps_guardrail_engine.py",
        "src/sps_mutation_watcher.py",
    ]

    critical_alerts: List[str] = []
    for path in critical_rel_paths:
        if path not in curr:
            critical_alerts.append(f"CRITICAL: {path} is missing in current snapshot.")
        elif path in prev and (
            prev[path].get("size_bytes") != curr[path].get("size_bytes")
            or prev[path].get("sha256") != curr[path].get("sha256")
        ):
            critical_alerts.append(f"CRITICAL: {path} has changed since last snapshot.")

    return {
        "new_files": new_files,
        "removed_files": removed_files,
        "changed_files": sorted(changed_files),
        "zero_byte_files": sorted(zero_byte_files),
        "critical_alerts": critical_alerts,
    }


def build_mutation_report() -> Dict[str, Any]:
    """
    Orchestrator:
        - Load previous snapshot.
        - Build current snapshot.
        - Compute diff (if previous exists).
        - Persist current snapshot as new baseline.
    """
    _ensure_docs_dir()
    prev_snapshot = _load_previous_snapshot()
    curr_snapshot = build_current_snapshot()
    diff = compare_snapshots(prev_snapshot, curr_snapshot) if prev_snapshot else None

    report: Dict[str, Any] = {
        "title": "Ghost Lantern Labs – SPS Module 2 – Mutation Watcher Report",
        "repo_root": REPO_ROOT,
        "docs_dir": DOCS_DIR,
        "snapshot_paths": {
            "previous": SNAPSHOT_PATH if prev_snapshot else None,
            "current": SNAPSHOT_PATH,
        },
        "previous_snapshot_present": bool(prev_snapshot),
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "current_file_count": len(curr_snapshot),
    }

    if not prev_snapshot:
        report["mode"] = "BASELINE_CREATED"
        report["message"] = (
            "No previous snapshot found. Created initial SPS file snapshot. "
            "Future runs will compare against this baseline."
        )
        report["diff"] = {
            "new_files": [],
            "removed_files": [],
            "changed_files": [],
            "zero_byte_files": [
                p for p, meta in curr_snapshot.items()
                if meta.get('size_bytes', 0) == 0
            ],
            "critical_alerts": [],
        }
    else:
        report["mode"] = "DIFF"
        report["message"] = (
            "Compared current snapshot to previous SPS baseline. "
            "Review changes carefully and reconcile with git history."
        )
        report["diff"] = diff

    report["snapshot"] = curr_snapshot

    with open(SNAPSHOT_PATH, "w", encoding="utf-8") as f_snap:
        json.dump(curr_snapshot, f_snap, indent=2)

    return report


def _format_text_report(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("Ghost Lantern Labs – Self-Preservation Shield (SPS)")
    lines.append("Module 2 – Mutation Watcher Report")
    lines.append("=" * 72)
    lines.append("")
    lines.append(f"Repo root: {report.get('repo_root')}")
    lines.append(f"Docs dir : {report.get('docs_dir')}")
    lines.append(f"Mode     : {report.get('mode')}")
    lines.append(f"Message  : {report.get('message')}")
    lines.append(f"Generated: {report.get('generated_at')}")
    lines.append(f"Files in current snapshot: {report.get('current_file_count')}")
    lines.append("")

    diff = report.get("diff", {}) or {}
    lines.append("1) Summary of Changes")
    lines.append("-" * 30)
    lines.append(f"New files       : {len(diff.get('new_files', []))}")
    lines.append(f"Removed files   : {len(diff.get('removed_files', []))}")
    lines.append(f"Changed files   : {len(diff.get('changed_files', []))}")
    lines.append(f"Zero-byte files : {len(diff.get('zero_byte_files', []))}")
    lines.append("")
    lines.append("Critical Alerts:")
    critical_alerts = diff.get("critical_alerts", [])
    if critical_alerts:
        for alert in critical_alerts:
            lines.append(f"  - {alert}")
    else:
        lines.append("  - None.")
    lines.append("")

    if diff.get("new_files"):
        lines.append("2) New Files (not present in previous snapshot)")
        lines.append("-" * 48)
        for p in diff["new_files"]:
            lines.append(f"  - {p}")
        lines.append("")

    if diff.get("removed_files"):
        lines.append("3) Removed Files")
        lines.append("-" * 24)
        for p in diff["removed_files"]:
            lines.append(f"  - {p}")
        lines.append("")

    if diff.get("changed_files"):
        lines.append("4) Changed Files (size or hash)")
        lines.append("-" * 34)
        for p in diff["changed_files"]:
            lines.append(f"  - {p}")
        lines.append("")

    if diff.get("zero_byte_files"):
        lines.append("5) Zero-Byte Files")
        lines.append("-" * 22)
        for p in diff["zero_byte_files"]:
            lines.append(f"  - {p}")
        lines.append("")

    lines.append("6) How to Use This Report")
    lines.append("-" * 30)
    lines.append("  - Treat unexpected changes, missing files, or zero-byte modules as red flags.")
    lines.append("  - Cross-check with git history to confirm whether changes were intentional.")
    lines.append("  - For critical alerts, restore from a known-good commit before running GLL.")
    lines.append("")
    lines.append("This report is suitable for:")
    lines.append("  - Internal self-preservation checks")
    lines.append("  - Tech School / training discussions about safe AI-assisted development")
    lines.append("  - AFWERX/SBIR demonstrations of GLL's tamper-awareness capabilities")
    lines.append("")

    return "\n".join(lines)


def write_mutation_report() -> Dict[str, Any]:
    _ensure_docs_dir()
    report = build_mutation_report()

    with open(REPORT_JSON, "w", encoding="utf-8") as f_json:
        json.dump(report, f_json, indent=2)

    text = _format_text_report(report)
    with open(REPORT_TXT, "w", encoding="utf-8") as f_txt:
        f_txt.write(text)

    return {
        "json_path": REPORT_JSON,
        "txt_path": REPORT_TXT,
        "report": report,
    }


if __name__ == "__main__":
    result = write_mutation_report()
    print("SPS Mutation Watcher report written:")
    print(f"  JSON: {result['json_path']}")
    print(f"  TXT:  {result['txt_path']}")

