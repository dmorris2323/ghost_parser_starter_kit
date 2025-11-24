#!/usr/bin/env python3
"""
ghost_cli.py

Simple operator menu for Ghost Lantern Labs.

Options:
  1) Run full QA validation (qa_validator.run_all)
  2) Show last 20 lines of fusion_ops_log.csv
  3) Exit
"""

from pathlib import Path

from qa_validator import run_all as qa_run_all
from fusion_logger import LOG_FILE


def tail_file(path: Path, n: int = 20) -> None:
    """Print last n lines of a file, if it exists."""
    if not path.exists():
        print(f"⚠️ Log file not found: {path}")
        return

    with path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    print(f"\n--- Last {min(n, len(lines))} lines of {path.name} ---")
    for line in lines[-n:]:
        print(line.rstrip())
    print("--- end of log ---\n")


def main() -> None:
    print("GLL OPERATOR CONSOLE — ghost_cli")
    print("================================")
    print("1) Run full QA validation")
    print("2) Show last 20 lines of fusion_ops_log.csv")
    print("3) Exit")
    choice = input("Select option (1/2/3): ").strip()

    if choice == "1":
        qa_run_all()
    elif choice == "2":
        log_path = Path(LOG_FILE)
        tail_file(log_path, n=20)
    else:
        print("👋 Exiting ghost_cli.")


if __name__ == "__main__":
    main()

