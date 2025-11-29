"""
attack_replay.py — reproduce 🦠 hostile data into pipeline

Allows you to take stored adversarial rows and push them
back into the system to test if defenses improved.
"""

import pandas as pd
from fusion_sanitizer import sanitize
from attack_memory import recall_attacks


def replay(limit: int = 10) -> str:
    df = recall_attacks(limit)
    if df.empty:
        return "⚠ No past attacks stored — replay skipped."

    clean = sanitize(df)
    clean.to_csv("replayed_attack.csv", index=False)
    return f"Replayed {len(clean)} stored hostile samples into replayed_attack.csv"

