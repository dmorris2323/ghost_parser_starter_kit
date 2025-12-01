"""
llm_config.py — Ghost Lantern Labs (Phase 2 AI-Independence)
------------------------------------------------------------

Central configuration for LLM providers.

- Reads environment variable: GLL_LLM_PROVIDER
- Defines available providers (provider_a, provider_b, local_rules)
- Exposes:
    get_active_provider()
    get_fallback_chain()
    describe_llm_config()
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class LLMConfig:
    active: str
    fallback_chain: List[str]


# Supported logical provider names (stubs for now)
SUPPORTED_PROVIDERS = ["provider_a", "provider_b", "local_rules"]

DEFAULT_ACTIVE = "provider_a"
DEFAULT_FALLBACK_CHAIN = ["provider_a", "provider_b", "local_rules"]


def get_active_provider() -> str:
    """Return the configured active provider (or default)."""
    env_val = os.getenv("GLL_LLM_PROVIDER", "").strip().lower()
    if env_val in SUPPORTED_PROVIDERS:
        return env_val
    return DEFAULT_ACTIVE


def get_fallback_chain() -> LLMConfig:
    """
    Return the active + fallback chain.

    Right now the chain is static, but in the future this can be
    loaded from a config file (JSON/YAML) or command-line arguments.
    """
    active = get_active_provider()

    chain = []
    for name in DEFAULT_FALLBACK_CHAIN:
        if name not in chain:
            chain.append(name)

    if active in chain:
        # Move active to front
        chain = [active] + [n for n in chain if n != active]
    else:
        chain.insert(0, active)

    return LLMConfig(active=active, fallback_chain=chain)


def describe_llm_config() -> str:
    cfg = get_fallback_chain()
    return (
        "LLM Config:\n"
        f"  Active provider: {cfg.active}\n"
        f"  Fallback chain: {', '.join(cfg.fallback_chain)}\n"
        f"  Supported providers: {', '.join(SUPPORTED_PROVIDERS)}"
    )


if __name__ == "__main__":
    print(describe_llm_config())

