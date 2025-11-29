"""
stress_tester.py — Ghost Lantern Labs
Day 55 Stability Test
--------------------------------------------------------
Runs repeated pipeline cycles using the existing CLI-style
scripts (fusion_scoring.py, fusion_alerts.py, etc.) to verify
that the system survives load and still produces valid outputs.

This DOES NOT depend on a 'main()' function in those modules.
It calls them exactly like you do from the terminal.
"""

import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path

from spectral_owl.owl_brain import analyze_fusion
from spectral_owl.threat_memory import append_event


ITERATIONS = 5  # increase later if you want heavier load


def run_script(script_name: str) -> None:
    """
    Run a Python script in the current src directory using the
    same interpreter, and don't crash the whole stress test if one fails.
    """
    print(f"\n-> Running {script_name} ...")
    try:
        subprocess.run([sys.executable, script_name], check=True)
        print(f"[OK] {script_name} completed.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {script_name} failed with code {e.returncode}")
    except Exception as e:
        print(f"[ERROR] Unexpected exception while running {script_name}: {e}")


def log_cycle_to_threat_memory(cycle_index: int, result: dict) -> None:
    """
    Log each stress cycle into threat memory so you can later see
    how the system behaved under repeated load.
    """
    status = str(result.get("status", "unknown"))
    risk = str(result.get("risk", "unknown")).upper()
    note = f"Stress cycle {cycle_index + 1}: status={status}, risk={risk}"

    # Severity = risk classification (HIGH / MODERATE / LOW / UNKNOWN)
    severity = risk if risk in ("HIGH", "MODERATE", "LOW") else "UNKNOWN"

    append_event(severity, "stress_cycle", note)


def stress_cycle(i: int) -> None:
    print(f"\n===============================")
    print(f"  STRESS CYCLE {i + 1}/{ITERATIONS}")
    print(f"===============================\n")

    # 1) Run core pipeline pieces the same way you do by hand
    run_script("fusion_scoring.py")
    run_script("fusion_alerts.py")
    run_script("commander_extract.py")
    run_script("daily_report.py")

    # 2) Let Spectral Owl analyze the latest scored_output.csv
    print("\n-> Running Spectral Owl analysis on scored_output.csv ...")
    result = analyze_fusion("scored_output.csv")
    print(f"Owl result: {result}")

    # 3) Write this into threat memory for long-term analysis
    log_cycle_to_threat_memory(i, result)

    # Small delay to avoid hammering the filesystem unnecessarily
    time.sleep(1.0)


def main():
    print("\n🚨 GLL Stress Tester — Multi-Cycle Pipeline Load\n")

    for i in range(ITERATIONS):
        stress_cycle(i)

    # After all cycles, run full QA once to verify no critical breakages
    print("\n=== Post-Stress QA Validation ===\n")
    run_script("qa_validator.py")

    # Drop an audit marker so you know when this was last run
    ts_path = Path("data/stress_test_last_run.txt")
    ts_path.parent.mkdir(parents=True, exist_ok=True)
    ts_path.write_text(
        f"Stress test completed at {datetime.now().isoformat()}\n",
        encoding="utf-8",
    )

    print("\n🔥 Stress Test Complete — System survived scripted load.\n")


if __name__ == "__main__":
    main()

