"""
run_history_logger.py — Ghost Lantern Labs
------------------------------------------
Reads qa_summary.txt and optional pipeline_health.txt, and appends a row
to data/run_history.csv for each QA run.

Fields:
  timestamp_utc, qa_total_tests, qa_passed, qa_failed, pipeline_health_snippet
"""

from pathlib import Path
from datetime import datetime
import csv

QA_SUMMARY = Path("qa_summary.txt")
PIPELINE_HEALTH = Path("pipeline_health.txt")
RUN_HISTORY = Path("data/run_history.csv")


def parse_qa_summary(path: Path):
    total = passed = failed = None
    if not path.exists():
        return total, passed, failed

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("Total tests:"):
            try:
                total = int(line.split(":")[1].strip())
            except ValueError:
                pass
        elif line.startswith("Passed:"):
            try:
                passed = int(line.split(":")[1].strip())
            except ValueError:
                pass
        elif line.startswith("Failed:"):
            try:
                failed = int(line.split(":")[1].strip())
            except ValueError:
                pass
    return total, passed, failed


def read_pipeline_snippet(path: Path, max_len: int = 200) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8").strip().replace("\n", " | ")
    return text[:max_len]


def ensure_header(path: Path):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "timestamp_utc",
                    "qa_total_tests",
                    "qa_passed",
                    "qa_failed",
                    "pipeline_health_snippet",
                ]
            )


def append_run():
    total, passed, failed = parse_qa_summary(QA_SUMMARY)
    snippet = read_pipeline_snippet(PIPELINE_HEALTH)
    ts = datetime.utcnow().isoformat()

    ensure_header(RUN_HISTORY)

    with RUN_HISTORY.open("a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([ts, total, passed, failed, snippet])


def main():
    append_run()
    print(f"[OK] Appended QA run to {RUN_HISTORY}")


if __name__ == "__main__":
    main()

