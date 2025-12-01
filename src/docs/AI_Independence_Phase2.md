# Ghost Lantern Labs — AI-Independence Phase 2

## Status

**Date:** Day 57 — Monday, Dec 1, 2025  
**Phase:** 2 (Multi-provider adapter + config switch)

Phase 2 core requirements:

- Implement real adapter stubs for at least 2 providers.
- Add a config switch (e.g., GLL_LLM_PROVIDER).
- Route all LLM calls for this phase through one clean adapter.
- Prove provider swap works in a simple demo.

## What Was Implemented

### 1. Central LLM Config (`llm_config.py`)

- Reads env var: `GLL_LLM_PROVIDER`
- Defines:
  - Supported providers: `provider_a`, `provider_b`, `local_rules`
  - Default active provider: `provider_a`
  - Fallback chain: `[provider_a, provider_b, local_rules]`
- Exposes:
  - `get_active_provider()`
  - `get_fallback_chain()`
  - `describe_llm_config()`

### 2. Provider Pool (`llm_provider_pool.py`)

Stub engines behind a common interface:

- `ProviderAEngine`
  - Simulated cloud model A.
  - Returns structured dict with `"provider": "provider_a"`.

- `ProviderBEngine`
  - Simulated cloud model B.
  - Returns structured dict with `"provider": "provider_b"`.

- `LocalRulesEngine`
  - Fully local, offline rules-based engine.
  - Classifies prompt into:
    - `data_denial`
    - `nuclear_ems`
    - `legal`
    - `general`

These engines can later be wired to **real** APIs or local models
without changing the rest of GLL.

### 3. Phase 2 Adapter (`llm_phase2_adapter.py`)

- Reads the fallback chain from `llm_config`.
- For a given prompt:
  - Iterates through providers in the chain.
  - Calls `build_engine(provider_name).generate(prompt, **kwargs)`.
  - Returns:
    - `provider_tried`
    - `final_provider`
    - `result` (engine payload dict)
- Includes `demo_provider_swap()` for simple one-command demo.

### 4. Probe Script (`llm_phase2_probe.py`)

Proves that provider switching works:

Examples:

```bash
python llm_phase2_probe.py
GLL_LLM_PROVIDER=provider_b python llm_phase2_probe.py
GLL_LLM_PROVIDER=local_rules python llm_phase2_probe.py

