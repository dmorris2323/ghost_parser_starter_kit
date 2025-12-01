"""
system_metrics_rollup.py — Ghost Lantern Labs
---------------------------------------------
Aggregates key system metrics into a single machine-readable
snapshot for dashboards, briefs, or automated health checks.

Pulls from:
  - qa_summary.txt
  - pipeline_health.txt (if present)
  - critical_alerts.csv
  - threat_memory.csv
  - bad_data_quarantine.csv
  - cloud_sync_health_check() (live)
  - data/stress_test_last_run.txt (if present)

Outputs:
  - system_metrics.json
  - system_metrics.txt   (human-readable)
"""

import json
import csv
from pathlib import Path
from typing import Dict, Any

from pipeline_health import evaluate_pipeline_health
from cloud.azure_ingest import cloud_sync_health_check
from spectral_owl.threat_memory import load_events


def parse_qa_summary(path: Path) -> Dict[str, int]:
    if not path.exists():
        return {"passed": 0, "failed": 0}

    text = path.read_text(encoding="utf-8").splitlines()
    passed = 0
    failed = 0
    for line in text:
        line = line.strip()
        if line.startswith("[PASS]"):
            passed += 1
        elif line.startswith("[FAIL]"):
            failed += 1
    return {"passed": passed, "failed": failed}


def count_csv_rows(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f)
        # skip header row if present
        try:
            header = next(reader)
        except StopIteration:
            return 0
        return sum(1 for _ in reader)


def load_stress_timestamp(path: Path) -> str:
    if not path.exists():
        return "never"
    return path.read_text(encoding="utf-8").strip()


def build_system_metrics() -> Dict[str, Any]:
    # QA
    qa_stats = parse_qa_summary(Path("qa_summary.txt"))

    # Pipeline health (this also recomputes and writes pipeline_health.txt)
    health = evaluate_pipeline_health()

    # Threat memory
    threat_events = load_events()
    threat_total = len(threat_events)

    # Bad-data quarantine
    bad_data_quarantine_count = count_csv_rows(Path("bad_data_quarantine.csv"))

    # Critical alerts
    critical_alerts = count_csv_rows(Path("critical_alerts.csv"))

    # Cloud sync (live)
    cloud_health = cloud_sync_health_check()

    # Stress test last run
    stress_last_run = load_stress_timestamp(Path("data/stress_test_last_run.txt"))

    metrics = {
        "qa": {
            "passed": qa_stats["passed"],
            "failed": qa_stats["failed"],
        },
        "pipeline_health": {
            "score": health["score"],
            "status": health["status"],
            "qa_passed": health["qa_passed"],
            "qa_failed": health["qa_failed"],
            "critical_alerts": health["critical_alerts"],
        },
        "threat_memory": {
            "total_events": threat_total,
        },
        "bad_data": {
            "quarantined_rows": bad_data_quarantine_count,
        },
        "alerts": {
            "critical_alerts": critical_alerts,
        },
        "cloud": {
            "health": cloud_health,
        },
        "stress_test": {
            "last_run": stress_last_run,
        },
    }

    return metrics


def write_outputs(metrics: Dict[str, Any]) -> None:
    # JSON version
    json_path = Path("system_metrics.json")
    json_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    # Human-readable text
    lines = []
    lines.append("======================================")
    lines.append(" GHOST LANTERN LABS — SYSTEM METRICS")
    lines.append("======================================")
    lines.append("")
    lines.append(f"QA: {metrics['qa']['passed']} passed, {metrics['qa']['failed']} failed")
    lines.append(
        f"Pipeline Health: {metrics['pipeline_health']['score']}/100 "
        f"({metrics['pipeline_health']['status']})"
    )
    lines.append(
        f"Critical Alerts (current): {metrics['alerts']['critical_alerts']}"
    )
    lines.append(
        f"Threat Memory Events (total): {metrics['threat_memory']['total_events']}"
    )
    lines.append(
        f"Bad Data Quarantined Rows: {metrics['bad_data']['quarantined_rows']}"
    )
    lines.append("")
    lines.append(f"Cloud Health: {metrics['cloud']['health']}")
    lines.append(f"Last Stress Test Run: {metrics['stress_test']['last_run']}")
    lines.append("")

    txt_path = Path("system_metrics.txt")
    txt_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    metrics = build_system_metrics()
    write_outputs(metrics)
    print("[OK] System metrics written to system_metrics.json and system_metrics.txt")


if __name__ == "__main__":
    main()

