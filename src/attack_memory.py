"""
attack_memory.py — Persistent adversarial evolution memory

Stores patterns of hostile/noisy telemetry so GLL can learn,
compare future attacks, and replay them later for testing.
"""

import pandas as pd
import os

MEMORY_FILE = "attack_memory.csv"


def store_attack(rows: list[dict]) -> None:
    """Append hostile event patterns to persistent memory."""
    df = pd.DataFrame(rows)

    if os.path.exists(MEMORY_FILE):
        old = pd.read_csv(MEMORY_FILE)
        df = pd.concat([old, df], ignore_index=True)

    df.to_csv(MEMORY_FILE, index=False)
    return f"Stored {len(rows)} hostile rows."



def recall_attacks(limit: int = 10) -> pd.DataFrame:
    """Return last N recorded attack patterns."""
    if not os.path.exists(MEMORY_FILE):
        return pd.DataFrame()

    return pd.read_csv(MEMORY_FILE).tail(limit)

