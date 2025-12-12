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

def read_crisis_mode() -> str:
    """
    Stable API for other modules (validation harness, dashboards, briefs).
    Returns "ON" or "OFF".
    """
    try:
        # If your module already has a canonical file path, reuse it.
        # Otherwise fall back to config/crisis_mode.txt (common pattern).
        from pathlib import Path
        base = Path(__file__).resolve().parent
        candidates = [
            base / "config" / "crisis_mode.txt",
            base.parent / "config" / "crisis_mode.txt",
            base / "crisis_mode.txt",
        ]
        for p in candidates:
            if p.exists():
                v = p.read_text().strip().upper()
                return "ON" if v in {"ON", "TRUE", "1", "YES"} else "OFF"
    except Exception:
        pass
    return "OFF"

