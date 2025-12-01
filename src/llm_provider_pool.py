"""
llm_provider_pool.py — Ghost Lantern Labs (Phase 2 AI-Independence)
-------------------------------------------------------------------

Stub implementations of multiple "providers" behind a common interface.

These are intentionally fake / local so that:
- GLL can run offline.
- We can prove provider switching and fallback without any external API.

Provider contract:
    engine.generate(prompt: str, **kwargs) -> dict with:
        {
            "provider": <name>,
            "mode": "simulation",
            "prompt": <prompt>,
            "response": <string>,
        }
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class BaseEngine:
    name: str

    def generate(self, prompt: str, **_: Any) -> Dict[str, Any]:
        raise NotImplementedError


@dataclass
class ProviderAEngine(BaseEngine):
    """
    Simulated 'Provider A' – could later map to Azure, OpenAI, etc.
    """

    def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        max_tokens = kwargs.get("max_tokens", 128)
        return {
            "provider": self.name,
            "mode": "simulation",
            "prompt": prompt,
            "response": f"[Provider A simulated answer; max_tokens={max_tokens}]",
        }


@dataclass
class ProviderBEngine(BaseEngine):
    """
    Simulated 'Provider B' – could later map to Anthropic, LM Studio, etc.
    """

    def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        temperature = kwargs.get("temperature", 0.2)
        return {
            "provider": self.name,
            "mode": "simulation",
            "prompt": prompt,
            "response": f"[Provider B simulated answer; temperature={temperature}]",
        }


@dataclass
class LocalRulesEngine(BaseEngine):
    """
    Local / offline rules-based engine (no external calls).

    This is the 'small brain' that should always be available, even if
    all cloud providers fail.
    """

    def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        # Minimal "analysis" based on keyword presence
        text = prompt.lower()
        tag = "general"

        if "dos" in text or "jamming" in text or "flood" in text:
            tag = "data_denial"
        elif "nuclear" in text or "icbm" in text or "golden dome" in text:
            tag = "nuclear_ems"
        elif "law" in text or "case" in text or "client" in text:
            tag = "legal"

        return {
            "provider": self.name,
            "mode": "local_rules",
            "prompt": prompt,
            "response": f"[Local rules classified this as: {tag}]",
        }


def build_engine(provider_name: str) -> BaseEngine:
    """Factory that returns the right engine instance."""
    key = provider_name.lower()

    if key == "provider_a":
        return ProviderAEngine(name="provider_a")
    if key == "provider_b":
        return ProviderBEngine(name="provider_b")
    if key == "local_rules":
        return LocalRulesEngine(name="local_rules")

    # Unknown provider → fallback to local rules
    return LocalRulesEngine(name="local_rules")

