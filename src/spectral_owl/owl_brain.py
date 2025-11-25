"""
owl_brain.py — Day 51
Simple reasoning engine based on fusion outputs.
"""

import pandas as pd
from fusion_logger import log_event

def analyze_fusion(path: str = "scored_output.csv") -> str:
    """Look at scored_output.csv and summarize the situation."""
    try:
        df = pd.read_csv(path)
    except Exception as e:
        msg = f"Could not read {path}: {e}"
        log_event("spectral_owl", "error", msg)
        return msg

    if df.empty:
        result = "No events to analyze."
        log_event("spectral_owl", "analysis", result)
        return result

    # Critical threshold: Score > 70
    critical = df[df["Score"] > 70]

    if len(critical) == 0:
        result = "Situation stable — no high risk events."
    else:
        result = f"{len(critical)} critical event(s). Recommend operator review."

    log_event("spectral_owl", "analysis", result)
    return result

def think(task: str) -> str:
    """
    Very simple 'thinking' stub for now.
    Later this will route tasks to real tools / models.
    """
    msg = f"[OWL] Thinking about: {task}"
    log_event("spectral_owl", "think", task)
    return msg

