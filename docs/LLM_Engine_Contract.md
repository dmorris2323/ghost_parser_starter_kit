# GLL LLM Engine Contract (Spectral Owl Interface)

This document defines how **any** Large Language Model must behave to work inside Ghost Lantern Labs.

The goal: you can replace the AI engine without rewriting GLL.

---

## 1. Core Concept

GLL talks to **one thing**:

`LLMEngine`

This is an interface (a “contract”) that defines what functions the AI must provide.

Everything else — ChatGPT, local LLM, another vendor — is just an implementation of that engine.

---

## 2. Required Capabilities

Any `LLMEngine` used by GLL must provide:

### 2.1 Text Generation

Basic text completion / reasoning.

Python-style:

```python
response = engine.generate(prompt: str, max_tokens: int = 256) -> str

