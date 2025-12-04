"""
owl_router.py — Spectral Owl Routing Logic
Phase 2 + Phase 3 Fallback Integration
"""

from pathlib import Path
import json

from spectral_fallback_tree import build_fallback_response
from spectral_owl.owl_brain_phase2 import analyze_fusion
from llm_phase2_adapter import run_llm_query
from spectral_owl.owl_memory import load_memory_log


def route_to_owl(summary: dict) -> dict:
    """
    Core router for Spectral Owl.
    Tries LLM → If fails, returns fallback logic.
    """

    # Attempt full AI reasoning
    try:
        result = run_llm_query(summary)
    except Exception:
        result = None

    # If provider output fails → fallback
    if not result or "completion" not in result:
        return build_fallback_response(summary)

    # Normal successful path
    return {
        "mode": "ai",
        "completion": result["completion"],
        "inputs_used": summary,
    }


def owl_analyze(summary: dict) -> dict:
    """
    Wrapper for GUI + CLI tools.
    """

    try:
        intel = analyze_fusion(summary)
    except Exception:
        intel = {"status": "analysis_failed"}

    routed = route_to_owl(summary)

    return {
        "analysis": intel,
        "owl_output": routed
    }


# If manually executed for tests
if __name__ == "__main__":
    sample = {
        "critical_alerts": 0,
        "warning_alerts": 2,
        "avg_reliability": 93.2
    }
    print(owl_analyze(sample))

