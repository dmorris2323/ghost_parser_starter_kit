"""
operator_identity.py — Track who is currently running GLL.

Backed by:
    config/operator.txt
"""

from pathlib import Path

OP_FILE = Path("config/operator.txt")


def get_identity() -> str:
    if OP_FILE.exists():
        return OP_FILE.read_text().strip() or "Unknown Operator"
    return "Unknown Operator"


def set_identity(name: str) -> str:
    OP_FILE.parent.mkdir(parents=True, exist_ok=True)
    OP_FILE.write_text(name.strip() or "Unknown Operator")
    return f"Operator set to: {get_identity()}"


if __name__ == "__main__":
    print(set_identity("Ghost"))
    print("Current operator:", get_identity())

