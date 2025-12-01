"""
llm_phase2_adapter.py — Ghost Lantern Labs (Phase 2 AI-Independence)
--------------------------------------------------------------------

This is the Phase 2 multi-provider adapter.

Responsibilities:
- Read active provider and fallback chain from llm_config.
- Build appropriate engine(s) from llm_provider_pool.
- Route a prompt through the chain until one "succeeds".
- Tag results with which provider actually answered.
- Provide a demo proving provider swap works.

This does NOT call real cloud APIs yet. All engines are local/simulated.
"""

from __future__ import annotations

from typing import Dict, Any, List

from llm_config import get_fallback_chain, describe_llm_config
from llm_provider_pool import build_engine


def run_llm_with_fallback(prompt: str, **kwargs: Any) -> Dict[str, Any]:
    """
    Execute LLM call with fallback.

    Returns:
        {
            "provider_tried": [list of provider names],
            "final_provider": <name>,
            "result": <engine_result_dict>,
        }
    """
    cfg = get_fallback_chain()
    tried: List[str] = []
    last_result: Dict[str, Any] | None = None

    for provider_name in cfg.fallback_chain:
        engine = build_engine(provider_name)
        tried.append(provider_name)
        try:
            result = engine.generate(prompt, **kwargs)
            # In a real environment we'd check for errors / HTTP codes, etc.
            last_result = result
            return {
                "provider_tried": tried,
                "final_provider": provider_name,
                "result": result,
            }
        except Exception as e:  # noqa: BLE001
            # Log and continue to next provider
            last_result = {
                "provider": provider_name,
                "mode": "error",
                "prompt": prompt,
                "response": f"Engine error: {e!r}",
            }
            continue

    # If all providers failed, return last_result (likely error from last engine)
    return {
        "provider_tried": tried,
        "final_provider": tried[-1] if tried else None,
        "result": last_result,
    }


def demo_provider_swap() -> None:
    """
    Run a small demo that:
    - Prints current config
    - Runs prompt through the fallback chain
    - Shows which provider answered
    """
    print("=== Phase 2 AI-Independence Demo ===")
    print(describe_llm_config())
    print("")

    prompt = "Summarize why data denial and jamming matter for ISR."

    result = run_llm_with_fallback(prompt, max_tokens=64, temperature=0.1)

    print("Providers tried:", ", ".join(result["provider_tried"]))
    print("Final provider:", result["final_provider"])
    print("Engine result dict:")
    print(result["result"])


if __name__ == "__main__":
    demo_provider_swap()

