# Ghost Lantern Labs — AI-Independence Phase 3 Design

**Status:** DESIGN ONLY (implementation targeted for Day 80–90).  
**Owner:** Ghost (Dexter)  
**Context:** Phase 1 (contract) and Phase 2 (multi-provider adapter) are complete.

---

## 1. Phase 3 Goal

Move from “we can swap providers” to:

- **Degraded-mode aware**: GLL always knows if it's in primary, fallback, or local-only mode.
- **Error-resilient**: Provider failures are logged, classified, and don’t break analysis.
- **Offline-first**: Local / rules / on-device path is treated as a *first-class* option, not a backup hack.

This matches real-world ISR and Golden Dome resilience:
- Cloud optional.
- Local analysis mandatory.
- Fallback must be graceful and visible to the operator.

---

## 2. Desired Behavior (End-State for Phase 3)

### 2.1 LLM call contract returns mode + health

Every LLM call should return something like:

```json
{
  "provider_tried": ["provider_a", "provider_b", "local_rules"],
  "final_provider": "local_rules",
  "degraded_mode": true,
  "degraded_reason": "all cloud providers failed; local_rules in use",
  "result": {
    "provider": "local_rules",
    "mode": "local_rules",
    "prompt": "...",
    "response": "[Local rules classified this as: nuclear_ems]"
  },
  "errors": [
    "provider_a: timeout",
    "provider_b: HTTP 500"
  ]
}

