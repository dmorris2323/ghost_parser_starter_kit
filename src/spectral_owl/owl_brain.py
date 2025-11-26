"""
owl_brain.py — Day 52
Reasoning engine for Spectral Owl:
- think(task): generic stub thinking
- analyze_fusion: looks at scored_output.csv
- analyze_quarantine: looks at bad_data_heatmap.csv for bad-data patterns
"""

from pathlib import Path

import pandas as pd

from fusion_logger import log_event

HEATMAP_FILE = Path("bad_data_heatmap.csv")


def think(task: str) -> str:
    """
    Simple "thinking" stub for now.
    """
    log_event("spectral_owl", "think", task)
    return f"[OWL] Thinking about: {task}"


def analyze_fusion(path: str = "scored_output.csv") -> str:
    """
    Look at scored_output.csv and give a simple threat summary.
    """
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

    if "Score" not in df.columns:
        result = "Scored output missing 'Score' column."
        log_event("spectral_owl", "analysis", result)
        return result

    critical = df[df["Score"] > 70]

    if len(critical) == 0:
        result = "Situation stable — no high risk events."
    else:
        result = f"{len(critical)} critical event(s). Recommend operator review."

    log_event("spectral_owl", "analysis", result)
    return result


def analyze_quarantine(path: Path = HEATMAP_FILE) -> str:
    """
    Read bad_data_heatmap.csv and summarize bad-data / possible flood patterns.
    """
    if not path.exists():
        msg = f"No bad_data_heatmap.csv found at {path}."
        log_event("spectral_owl", "quarantine_info", msg)
        return msg

    try:
        df = pd.read_csv(path)
    except Exception as e:
        msg = f"Could not read {path}: {e}"
        log_event("spectral_owl", "quarantine_error", msg)
        return msg

    if df.empty:
        result = "Quarantine heatmap is empty — no bad data patterns detected."
        log_event("spectral_owl", "quarantine_analysis", result)
        return result

    total = df["Count"].sum()
    top = df.sort_values("Count", ascending=False).head(3)

    top_strings = [
        f"{row['Quarantine_Reason']} @ {row['Time_Bucket']} -> {row['Count']}"
        for _, row in top.iterrows()
    ]
    top_summary = "; ".join(top_strings)

    if total < 10:
        severity = "low-level noise"
    elif total < 50:
        severity = "elevated bad-data activity"
    else:
        severity = "possible deliberate flood / spoofing pattern"

    result = (
        f"Quarantine total={total} rows ({severity}). "
        f"Top patterns: {top_summary}"
    )
    log_event("spectral_owl", "quarantine_analysis", result)
    return result


if __name__ == "__main__":
    # Tiny manual test hooks
    print(think("self-test"))
    print(analyze_fusion())
    print(analyze_quarantine())

