"""
notes_merge_doc_notes.py — Ghost Lantern Labs
---------------------------------------------
Merges any docs/*day*_notes.md files into NOTES.txt, then (optionally)
you can delete the originals manually once you’re satisfied.

Behavior:
- Finds all files matching docs/*day*_notes.md
- For each file, appends a clear section block into NOTES.txt:
    ===== Imported from docs/<filename> =====
    <file contents>

- Does NOT delete the original files (you decide when to clean up).
"""

from pathlib import Path
from datetime import datetime
import glob

ROOT = Path(__file__).resolve().parent
DOCS_DIR = ROOT / "docs"
NOTES_FILE = ROOT / "NOTES.txt"


def merge_doc_notes():
    pattern = str(DOCS_DIR / "*day*_notes.md")
    files = sorted(glob.glob(pattern))

    if not files:
        print(f"[WARN] No files matching {pattern}")
        return

    if not NOTES_FILE.exists():
        NOTES_FILE.write_text("", encoding="utf-8")

    merged_count = 0
    with NOTES_FILE.open("a", encoding="utf-8") as notes:
        notes.write("\n")
        notes.write("===== NOTES MERGE SESSION =====\n")
        notes.write(f"Timestamp (UTC): {datetime.utcnow().isoformat()}\n")
        notes.write("----------------------------------------\n\n")

        for filepath in files:
            p = Path(filepath)
            content = p.read_text(encoding="utf-8").strip()
            notes.write(f"===== Imported from {p.as_posix()} =====\n")
            notes.write(content)
            notes.write("\n\n")
            merged_count += 1

    print(f"[OK] Merged {merged_count} doc note file(s) into {NOTES_FILE}")


def main():
    merge_doc_notes()


if __name__ == "__main__":
    main()

