"""
crisis_mode_flag.py — Global crisis mode flag for GLL.

Stores a simple ON/OFF state in data/crisis_mode.txt.
"""

from pathlib import Path

FILE = Path("data/crisis_mode.txt")


def enable():
    FILE.parent.mkdir(parents=True, exist_ok=True)
    FILE.write_text("ON")
    return "Crisis Mode: ENABLED"


def disable():
    FILE.parent.mkdir(parents=True, exist_ok=True)
    FILE.write_text("OFF")
    return "Crisis Mode: DISABLED"


def status():
    if not FILE.exists():
        return "OFF"
    return FILE.read_text().strip() or "OFF"


if __name__ == "__main__":
    print("Current:", status())
    print(enable())
    print("Now:", status())
    print(disable())
    print("Final:", status())

