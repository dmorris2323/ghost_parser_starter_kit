"""
auto_retry_runner.py — GLL
--------------------------
Runs qa_validator.py and, if there are failures, re-runs it once
to see if errors are transient.
"""

import subprocess
import sys
from pathlib import Path


def run_qa() -> str:
    result = subprocess.run(
        [sys.executable, "qa_validator.py"],
        capture_output=True,
        text=True,
    )
    output = result.stdout + "\n" + result.stderr
    Path("auto_retry_last_qa.log").write_text(output, encoding="utf-8")
    return output


def main():
    print("[INFO] Running QA (first pass)...")
    output1 = run_qa()

    if "[FAIL]" not in output1:
        print("[OK] All tests passed on first run.")
        return

    print("[WARN] Failures detected. Running QA again (retry)...")
    output2 = run_qa()

    if "[FAIL]" in output2:
        print("[FAIL] QA still failing after retry. See auto_retry_last_qa.log.")
    else:
        print("[OK] QA passed on retry. See auto_retry_last_qa.log.")


if __name__ == "__main__":
    main()

