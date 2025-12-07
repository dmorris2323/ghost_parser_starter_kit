"""
operator_identity.py — Track the active human operator.

Backed by config/operator.txt
"""

from pathlib import Path

FILE = Path("config/operator.txt")


def get_identity() -> str:
    if FILE.exists():
        text = FILE.read_text().strip()
        return text or "Unknown Operator"
    return "Unknown Operator"


def set_identity(name: str) -> str:
    FILE.parent.mkdir(parents=True, exist_ok=True)
    FILE.write_text(name.strip() or "Unknown Operator")
    return f"Operator set to: {get_identity()}"


if __name__ == "__main__":
    print("Current operator:", get_identity())
    print(set_identity("Ghost"))
    print("Updated operator:", get_identity())

