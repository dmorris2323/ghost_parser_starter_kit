"""
llm_phase2_probe.py — Ghost Lantern Labs (Phase 2 Probe)
--------------------------------------------------------

Quick probe script to prove that:
- GLL_LLM_PROVIDER switches the active provider.
- The adapter uses that provider first in the fallback chain.

Usage examples (from src/):

    python llm_phase2_probe.py

    GLL_LLM_PROVIDER=provider_b python llm_phase2_probe.py

    GLL_LLM_PROVIDER=local_rules python llm_phase2_probe.py
"""

from __future__ import annotations

import os

from llm_config import describe_llm_config
from llm_phase2_adapter import run_llm_with_fallback


def main():
    print("=== LLM Phase 2 Probe ===")
    print("Raw env GLL_LLM_PROVIDER:", os.getenv("GLL_LLM_PROVIDER"))
    print("")
    print(describe_llm_config())
    print("")

    prompt = "Classify this prompt for Golden Dome and nuclear early warning relevance."
    result = run_llm_with_fallback(prompt, max_tokens=32, temperature=0.3)

    print("Providers tried:", ", ".join(result["provider_tried"]))
    print("Final provider:", result["final_provider"])
    print("Result payload:")
    print(result["result"])


if __name__ == "__main__":
    main()

