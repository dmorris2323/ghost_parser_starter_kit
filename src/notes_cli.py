#!/usr/bin/env python3

"""
notes_cli.py
-----------
A simple command-line tool to append timestamp-stamped notes into NOTES.txt
so Ghost can log progress quickly without opening a text editor.

Usage:
    python notes_cli.py "your log message here"
"""

import sys
from datetime import datetime
from pathlib import Path

# Locate NOTES.txt (relative to this src directory)
NOTES_PATH = Path(__file__).parent / "NOTES.txt"

def append_note(text: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n[{ts}] {text}\n"
    
    with open(NOTES_PATH, "a") as f:
        f.write(entry)

    print("\n📝 NOTE LOGGED:")
    print(entry)
    print("Stored in → NOTES.txt\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUsage: python notes_cli.py \"message\"\n")
        sys.exit(1)

    message = " ".join(sys.argv[1:])
    append_note(message)

