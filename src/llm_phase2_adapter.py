"""
llm_phase2_adapter.py

Phase 2 AI-Independence adapter for Spectral Owl.

Goals:
- Single place where ALL LLM calls flow through.
- Support multiple providers via env/config.
- Provide a robust run_llm_with_fallback() that never kills GLL.
- Always preserve an offline-safe local_rules path.

Exports:
- get_active_provider() -> str
- call_llm(provider: str, prompt: str) -> dict
- run_llm_with_fallback(prompt: str) -> dict
"""

from __future__ import annotations

import os
from typing import Any, Dict


# ---------------------------------------------------------------------------
# Provider selection
# ---------------------------------------------------------------------------

AVAILABLE_PROVIDERS = ("provider_a", "provider_b", "local_rules")


def get_active_provider() -> str:
    """
    Returns the currently selected provider based on env var GLL_LLM_PROVIDER.
    Defaults to 'local_rules' if unset or invalid.
    """
    env_val = os.getenv("GLL_LLM_PROVIDER", "").strip().lower()
    if env_val in AVAILABLE_PROVIDERS:
        return env_val
    return "local_rules"


# ---------------------------------------------------------------------------
# Core call function for each provider
# ---------------------------------------------------------------------------

def _call_provider_stub(name: str, prompt: str) -> Dict[str, Any]:
    """
    Stub implementation for remote providers.

    In a future phase, this is where you plug in:
      - Azure OpenAI
      - Other cloud vendors
      - On-prem APIs

    For now, it just simulates a structured response.
    """
    return {
        "provider": name,
        "completion": f"[{name} simulated completion] {prompt[:160]}",
        "mode": "simulated",
    }


def _call_local_rules(prompt: str) -> Dict[str, Any]:
    """
    Offline / local 'small brain' implementation.

    Uses spectral_owl.local_rules_engine if available.
    Never throws — always returns a best-effort completion.
    """
    try:
        from spectral_owl.local_rules_engine import run_local_rules
        text = run_local_rules(prompt)
    except Exception:
        text = f"[local_rules fallback] {prompt[:160]}"

    return {
        "provider": "local_rules",
        "completion": text,
        "mode": "local",
    }


def call_llm(provider: str, prompt: str) -> Dict[str, Any]:
    """
    Unified call interface for all providers.
    """
    provider = (provider or "").lower()

    if provider in ("provider_a", "provider_b"):
        return _call_provider_stub(provider, prompt)

    # default + explicit local
    return _call_local_rules(prompt)


# ---------------------------------------------------------------------------
# Fallback chain
# ---------------------------------------------------------------------------

def run_llm_with_fallback(prompt: str) -> Dict[str, Any]:
    """
    Main entry point for Spectral Owl.

    Behavior:
    - Try active provider (based on env / config).
    - If it fails or returns missing completion, walk a fallback chain:
        1) provider_a
        2) provider_b
        3) local_rules
    - Never raises: always returns a dict with at least:
        { "provider": str, "completion": str, "mode": str, ... }
    """
    primary = get_active_provider()

    # 1) Try primary
    result = None
    try:
        result = call_llm(primary, prompt)
    except Exception:
        result = None

    if _is_valid_result(result):
        result.setdefault("primary_provider", primary)
        return result

    # 2) Fallback chain, skipping the already-tried primary
    chain = [p for p in AVAILABLE_PROVIDERS if p != primary]

    for provider in chain:
        try:
            candidate = call_llm(provider, prompt)
        except Exception:
            candidate = None

        if _is_valid_result(candidate):
            candidate.setdefault("primary_provider", primary)
            candidate.setdefault("fallback_from", primary)
            candidate.setdefault("fallback_chain", chain)
            return candidate

    # 3) Last-resort emergency fallback
    return {
        "provider": "local_rules",
        "completion": f"[emergency fallback] {prompt[:200]}",
        "mode": "emergency",
        "primary_provider": primary,
        "fallback_chain": list(chain),
    }


def _is_valid_result(obj: Any) -> bool:
    """
    Accepts a result if it's a dict with a non-empty 'completion' string.
    """
    if not isinstance(obj, dict):
        return False
    comp = obj.get("completion")
    return isinstance(comp, str) and len(comp.strip()) > 0


# ---------------------------------------------------------------------------
# Simple probe for CLI/QA usage
# ---------------------------------------------------------------------------

def phase2_probe(summary: str) -> Dict[str, Any]:
    """
    Utility used by llm_phase2_probe.py or other diagnostics.

    Returns a small dict describing:
      - active provider
      - completion preview
      - mode
    """
    res = run_llm_with_fallback(summary)
    preview = res.get("completion", "")[:120]
    return {
        "active_provider": get_active_provider(),
        "used_provider": res.get("provider"),
        "mode": res.get("mode"),
        "preview": preview,
    }


if __name__ == "__main__":
    # Lightweight self-test
    test = phase2_probe("Test summary: 0 critical, 2 warnings, avg reliability 93%.")
    print(test)

