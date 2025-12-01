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

NEW (Module 1):
- Integrates offline_mode_flag to mark when we are in
  a degraded/offline-like state (e.g., using local_rules or
  not using the primary provider).

This does NOT change the public return structure of
run_llm_with_fallback(...) so existing callers remain valid:
    {
        "provider_tried": [...],
        "final_provider": <name>,
        "result": <engine_result_dict>,
    }
"""

from __future__ import annotations

from typing import Dict, Any, List

from llm_config import get_fallback_chain, describe_llm_config
from llm_provider_pool import build_engine
from offline_mode_flag import set_offline_mode, set_online_mode


def run_llm_with_fallback(prompt: str, **kwargs: Any) -> Dict[str, Any]:
    """
    Execute LLM call with fallback.

    Returns:
        {
            "provider_tried": [list of provider names],
            "final_provider": <name>,
            "result": <engine_result_dict>,
        }

    Side effect (Module 1):
        - Writes offline_status.txt via offline_mode_flag:
          * NORMAL_OPERATION if primary provider was used successfully.
          * OFFLINE_OR_DEGRADED if we fell back to another provider or
            ended up on local_rules.
    """
    cfg = get_fallback_chain()
    tried: List[str] = []
    last_result: Dict[str, Any] | None = None
    final_provider: str | None = None

    for provider_name in cfg.fallback_chain:
        engine = build_engine(provider_name)
        tried.append(provider_name)
        try:
            result = engine.generate(prompt, **kwargs)
            last_result = result
            final_provider = provider_name
            break
        except Exception as e:  # noqa: BLE001
            # Log last error-like result locally; we still continue to next provider.
            last_result = {
                "provider": provider_name,
                "mode": "error",
                "prompt": prompt,
                "response": f"Engine error: {e!r}",
            }
            final_provider = provider_name
            continue

    if last_result is None:
        # Nothing succeeded and no result recorded.
        final_provider = None
        last_result = {
            "provider": None,
            "mode": "error",
            "prompt": prompt,
            "response": "No providers available or all failed without result.",
        }

    # Decide offline/degraded mode.
    primary = cfg.fallback_chain[0] if cfg.fallback_chain else None

    if final_provider == "local_rules":
        # Strong signal that we're in a local-only / offline-like path.
        set_offline_mode(
            "local_rules in use; treating this as offline/degraded analysis path."
        )
    elif primary is not None and final_provider != primary:
        # We did not use the primary provider even though it's in the chain.
        set_offline_mode(
            f"Primary provider '{primary}' not used; fell back to '{final_provider}'."
        )
    else:
        # We used the primary provider or there is no clear primary.
        set_online_mode()

    return {
        "provider_tried": tried,
        "final_provider": final_provider,
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

