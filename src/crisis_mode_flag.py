"""
crisis_mode_flag.py — Simple ON/OFF flag for Crisis Mode.

Backed by:
    data/crisis_mode.txt

Values:
    "ON" or "OFF"
"""

from pathlib import Path

FLAG_FILE = Path("data/crisis_mode.txt")


def enable() -> str:
    FLAG_FILE.parent.mkdir(parents=True, exist_ok=True)
    FLAG_FILE.write_text("ON")
    return "Crisis Mode: ON"


def disable() -> str:
    FLAG_FILE.parent.mkdir(parents=True, exist_ok=True)
    FLAG_FILE.write_text("OFF")
    return "Crisis Mode: OFF"


def status() -> str:
    if not FLAG_FILE.exists():
        return "OFF"
    return FLAG_FILE.read_text().strip() or "OFF"


if __name__ == "__main__":
    print("Current:", status())
    print("Enabling…")
    print(enable())
    print("Now:", status())

