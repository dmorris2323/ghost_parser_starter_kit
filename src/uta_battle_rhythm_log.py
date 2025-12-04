from pathlib import Path
from datetime import datetime
import sys


BASE = Path(__file__).parent
DOCS = BASE / "docs"
LOG_FILE = DOCS / "uta_battle_rhythm_log.txt"


def log_uta_entry(
    day: str = "Day 60",
    tech_block: str = "20x sprint",
    note: str = ""
) -> Path:
    """
    Append a single UTA / drill-day entry to docs/uta_battle_rhythm_log.txt.

    Format:
      2025-12-04T19:32:10 | Day 60 | tech=20x sprint | note=Finished reliability + Golden Dome work
    """
    DOCS.mkdir(exist_ok=True)
    ts = datetime.now().isoformat(timespec="seconds")
    cleaned_note = note.strip()

    line = f"{ts} | {day} | tech={tech_block}"
    if cleaned_note:
        line += f" | note={cleaned_note}"

    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

    return LOG_FILE


if __name__ == "__main__":
    # Allow quick notes via CLI args:
    #   python uta_battle_rhythm_log.py "UTA Day 1 – finished 20x + module 42–43"
    _note = " ".join(sys.argv[1:]).strip()

    if not _note:
        try:
            _note = input("Short note for today (UTA / drills / focus): ").strip()
        except EOFError:
            _note = ""

    path = log_uta_entry(note=_note)
    print(f"UTA battle rhythm entry appended → {path}")

