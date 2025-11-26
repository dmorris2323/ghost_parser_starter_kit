"""
llm_adapter.py — AI-Independence v1
Spectral Owl LLM adapter / brain socket.

This module defines a minimal interface (LLMEngine) that ANY future
language model must implement in order to plug into Ghost Lantern Labs.

Right now it ships with a DummyLocalEngine so GLL does NOT depend on
any real LLM service.
"""

from dataclasses import dataclass
from typing import Protocol, Optional

from fusion_logger import log_event


class LLMEngine(Protocol):
    """
    Contract for any language model used by GLL.

    Any concrete engine (cloud, local, self-hosted) must implement:
      - generate(prompt, max_tokens=...)
      - summarize(text, max_tokens=...)
    """

    def generate(self, prompt: str, max_tokens: int = 256) -> str:
        ...

    def summarize(self, text: str, max_tokens: int = 128) -> str:
        ...


@dataclass
class DummyLocalEngine:
    """
    A very simple offline stub.

    It doesn't call any real AI. It just echoes prompts in a structured way.
    This guarantees that Spectral Owl can run without network or vendor
    dependence during development and in denied environments.
    """

    name: str = "dummy-local"

    def generate(self, prompt: str, max_tokens: int = 256) -> str:
        truncated = prompt[:max_tokens]
        msg = f"[{self.name}] (offline stub) {truncated}"
        log_event("llm_adapter", "generate", f"len={len(prompt)}")
        return msg

    def summarize(self, text: str, max_tokens: int = 128) -> str:
        truncated = text.strip()
        if len(truncated) > max_tokens:
            truncated = truncated[:max_tokens] + "..."
        msg = f"[{self.name}] summary: {truncated}"
        log_event("llm_adapter", "summarize", f"len={len(text)}")
        return msg


# Internal singleton reference so the rest of GLL doesn't care
_default_engine: Optional[LLMEngine] = None


def get_llm() -> LLMEngine:
    """
    Return the default LLM engine.

    Today: DummyLocalEngine (no external dependency).
    Tomorrow: could be swapped for a real offline or cloud model
    without touching fusion or CLI code.
    """
    global _default_engine

    if _default_engine is None:
        _default_engine = DummyLocalEngine()

    return _default_engine


def set_llm(engine: LLMEngine) -> None:
    """
    Allow tests or future configuration to inject a different engine.
    """
    global _default_engine
    _default_engine = engine
    log_event("llm_adapter", "engine_set", str(type(engine)))

