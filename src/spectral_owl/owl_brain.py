"""
owl_brain.py — Spectral Owl reasoning engine

Upgrades:
- Analyze scored_output.csv for critical events
- Use LLM adapter for simple "thinking" tasks, offline-safe.
"""

import pandas as pd

from fusion_logger import log_event
from spectral_owl.llm_adapter import get_llm


def analyze_fusion(path: str = "scored_output.csv") -> str:
    """
    Core rule-based reasoning about the fusion output.

    Returns a short status string that other modules (CLI, mission brief,
    anti-DoS scan) can display.
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

    # Basic rule: anything with Score > 70 is "critical"
    if "Score" not in df.columns:
        result = "Fusion file missing Score column — cannot analyze."
        log_event("spectral_owl", "analysis_error", result)
        return result

    critical = df[df["Score"] > 70]

    if len(critical) == 0:
        result = "Situation stable — no high risk events."
    else:
        result = f"{len(critical)} critical event(s). Recommend operator review."

    log_event("spectral_owl", "analysis", result)
    return result


def think(task: str) -> str:
    """
    Simple entry point to show that Spectral Owl can 'think' about a task.

    Uses the DummyLocalEngine via llm_adapter, which is completely offline
    and vendor-independent.
    """
    engine = get_llm()
    prompt = f"Spectral Owl system task: {task}"
    response = engine.generate(prompt)
    log_event("spectral_owl", "think", task)
    return response

