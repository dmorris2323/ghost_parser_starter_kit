"""
qa_validator.py

Central QA harness for Ghost Lantern Labs.

Runs a series of tests over the core pipeline modules and reports
pass/fail status for each, including the new Cloud Sync health check.
"""

import subprocess
import sys
from pathlib import Path

from cloud.azure_ingest import cloud_sync_health_check

PYTHON = sys.executable  # uses current Python interpreter


def run_subprocess(description, cmd):
    """
    Helper to run a subprocess and return (success, message).
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as e:
        return False, f"{description} crashed: {e}"

    if result.returncode != 0:
        return False, (
            f"{description} FAILED with code {result.returncode}\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )

    return True, f"{description} PASSED.\nSTDOUT:\n{result.stdout}"


# ---- Individual test wrappers ----
# These point directly at scripts in src/


def test_fusion_scoring():
    return run_subprocess("fusion_scoring", [PYTHON, "fusion_scoring.py"])


def test_commander_extract():
    return run_subprocess("commander_extract", [PYTHON, "commander_extract.py"])


def test_heatmap_prep():
    return run_subprocess("heatmap_prep", [PYTHON, "heatmap_prep.py"])


def test_fusion_alerts():
    return run_subprocess("fusion_alerts", [PYTHON, "fusion_alerts.py"])


def test_daily_report():
    return run_subprocess("daily_report", [PYTHON, "daily_report.py"])


def test_spectral_owl():
    """
    Spectral Owl test:
    We import the module instead of running it as a script to avoid
    relative import issues inside owl_brain.py.
    """
    try:
        import spectral_owl.owl_brain as owl_brain  # noqa: F401
        return True, "Spectral Owl module import OK."
    except Exception as e:
        return False, f"Spectral Owl import failed: {e}"


def test_cloud_sync():
    """
    Verifies that the cloud simulation path is reachable and
    that the cloud config file is valid.
    """
    result = cloud_sync_health_check()
    status = result.get("status")

    if status not in ("ok", "warning"):
        return False, f"Cloud sync health FAILED: {result}"

    return True, f"Cloud sync health check OK: {result}"


TESTS = [
    ("fusion_scoring", test_fusion_scoring),
    ("commander_extract", test_commander_extract),
    ("heatmap_prep", test_heatmap_prep),
    ("fusion_alerts", test_fusion_alerts),
    ("daily_report", test_daily_report),
    ("spectral_owl", test_spectral_owl),
    ("cloud_sync", test_cloud_sync),
]


def run_all_tests():
    """
    Runs all registered tests and returns a summary dict.
    """
    summary = {
        "total": len(TESTS),
        "passed": 0,
        "failed": 0,
        "results": [],
    }

    for name, func in TESTS:
        ok, msg = func()
        if ok:
            summary["passed"] += 1
        else:
            summary["failed"] += 1

        summary["results"].append(
            {
                "name": name,
                "ok": ok,
                "message": msg,
            }
        )

    return summary


def _format_summary(summary):
    lines = []
    lines.append("=== QA VALIDATION SUMMARY ===")
    lines.append(f"Total tests: {summary['total']}")
    lines.append(f"Passed:      {summary['passed']}")
    lines.append(f"Failed:      {summary['failed']}")
    lines.append("")

    for result in summary["results"]:
        status = "PASS" if result["ok"] else "FAIL"
        lines.append(f"[{status}] {result['name']}")
        lines.append(result["message"])
        lines.append("-" * 40)

    return "\n".join(lines)


if __name__ == "__main__":
    summary = run_all_tests()
    report = _format_summary(summary)

    out_path = Path("qa_summary.txt")
    out_path.write_text(report, encoding="utf-8")

    print(report)

    sys.exit(0 if summary["failed"] == 0 else 1)

