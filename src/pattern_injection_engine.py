"""
pattern_injection_engine.py

Module 2 — Pattern Injection Engine (SAFE)
Injects training-safe "adversary patterns" into synthetic fusion telemetry bundles.

Key points:
- This is synthetic-only. No real-world missile telemetry. No real targeting logic.
- Patterns are generic cyber/EMS/comms behaviors used for training and testing resilience.
- Designed to be deterministic with seed and repeatable for regression tests.

Used by:
- synthetic_signal_generator.py (optional injection)
- fusion_validation_harness.py (reports injected patterns and expected effects)
"""

from __future__ import annotations

import random
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class InjectedPattern:
    pattern_id: str
    label: str
    domains: List[str]
    intensity: float          # 0.0–1.0
    expected_effects: List[str]
    injected_events: int


# SAFE, generic pattern catalog
PATTERN_CATALOG: Dict[str, Dict[str, Any]] = {
    "CYBER_LOTL": {
        "label": "Cyber LOTL Pressure",
        "domains": ["CYBER"],
        "expected_effects": [
            "Increase cyber_event_rate spikes",
            "Increase attack_like count",
            "Reduce trust proxy slightly under stress",
        ],
    },
    "EMS_BURST_NOISE": {
        "label": "EMS Burst Noise",
        "domains": ["EMS"],
        "expected_effects": [
            "Increase ems_noise_index spikes",
            "Increase anomaly count",
            "Potential comms degradation co-movement",
        ],
    },
    "COMMS_DEGRADE": {
        "label": "Comms Degradation",
        "domains": ["COMMS"],
        "expected_effects": [
            "Increase comms_state_index anomalies",
            "Increase latency follow-on risk if enabled",
        ],
    },
    "LATENCY_SPIKE": {
        "label": "Latency Spike Wave",
        "domains": ["LATENCY"],
        "expected_effects": [
            "Increase sensor_latency_ms_index spikes",
            "Decrease confidence notes under stress",
        ],
    },
    "CROSS_DOMAIN_CONFUSION": {
        "label": "Cross-Domain Confusion",
        "domains": ["EMS", "COMMS", "CYBER"],
        "expected_effects": [
            "Multiple domains spike within a short window",
            "Higher volatility and alert pressure",
        ],
    },
}


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _safe_choice(rng: random.Random, items: List[str]) -> str:
    return items[int(rng.random() * len(items))] if items else ""


def _safe_intensity(level: str) -> float:
    """
    Difficulty-to-intensity mapping. Kept simple and stable.
    """
    lvl = level.upper().strip()
    if lvl == "BEGINNER":
        return 0.35
    if lvl == "INTERMEDIATE":
        return 0.55
    if lvl == "ADVANCED":
        return 0.75
    if lvl == "ADVERSARIAL":
        return 0.92
    return 0.55


def list_available_patterns() -> List[Dict[str, Any]]:
    out = []
    for pid, meta in PATTERN_CATALOG.items():
        out.append(
            {
                "pattern_id": pid,
                "label": meta.get("label", pid),
                "domains": meta.get("domains", []),
                "expected_effects": meta.get("expected_effects", []),
            }
        )
    return sorted(out, key=lambda x: x["pattern_id"])


def inject_pattern(
    bundle: Dict[str, Any],
    pattern_id: str,
    difficulty: str = "INTERMEDIATE",
    seed: Optional[int] = None,
) -> Tuple[Dict[str, Any], InjectedPattern]:
    """
    Injects a pattern into an existing synthetic bundle.

    Bundle format expected:
      bundle["events"] = list[dict] where each event has keys:
        - domain, value, severity, anomaly, attack_like, note

    We DO NOT depend on any other modules. If keys are missing, we guard safely.
    """
    if not isinstance(bundle, dict):
        raise ValueError("bundle must be dict")

    pid = pattern_id.upper().strip()
    if pid not in PATTERN_CATALOG:
        raise ValueError(f"Unknown pattern_id: {pattern_id}")

    rng = random.Random(seed)
    meta = PATTERN_CATALOG[pid]
    domains = list(meta.get("domains", []))
    intensity = _safe_intensity(difficulty)

    events: List[Dict[str, Any]] = list(bundle.get("events", []) or [])
    if not events:
        # no events to modify; return with zero injection
        injected = InjectedPattern(
            pattern_id=pid,
            label=meta.get("label", pid),
            domains=domains,
            intensity=float(intensity),
            expected_effects=list(meta.get("expected_effects", [])),
            injected_events=0,
        )
        _append_injection_metadata(bundle, injected)
        return bundle, injected

    # pick a subset to modify based on intensity
    # higher intensity modifies more events in the target domains
    candidate_idxs = [i for i, e in enumerate(events) if str(e.get("domain", "")).upper() in domains]
    if not candidate_idxs:
        injected = InjectedPattern(
            pattern_id=pid,
            label=meta.get("label", pid),
            domains=domains,
            intensity=float(intensity),
            expected_effects=list(meta.get("expected_effects", [])),
            injected_events=0,
        )
        _append_injection_metadata(bundle, injected)
        return bundle, injected

    # how many to inject
    base = max(3, int(len(candidate_idxs) * (0.10 + 0.35 * intensity)))
    inject_n = _clamp(base, 3, min(40, len(candidate_idxs)))
    inject_n = int(inject_n)

    chosen = rng.sample(candidate_idxs, k=inject_n)

    injected_events = 0
    for idx in chosen:
        e = events[idx]
        dom = str(e.get("domain", "")).upper()

        # adjust value upward in a domain-specific but safe way
        v = float(e.get("value", 0.0) or 0.0)

        bump = 0.0
        if dom == "CYBER":
            bump = rng.uniform(18.0, 55.0) * intensity
            e["attack_like"] = True
            e["anomaly"] = True
        elif dom == "EMS":
            bump = rng.uniform(15.0, 50.0) * intensity
            e["anomaly"] = True
        elif dom == "COMMS":
            bump = rng.uniform(12.0, 40.0) * intensity
            e["anomaly"] = True
        elif dom == "LATENCY":
            bump = rng.uniform(20.0, 65.0) * intensity
            e["anomaly"] = True
        else:
            bump = rng.uniform(10.0, 35.0) * intensity
            e["anomaly"] = True

        e["value"] = round(_clamp(v + bump, 0.0, 100.0), 3)

        # severity recalculation (simple and stable)
        e["severity"] = _severity_from_value(float(e["value"]))

        # note append (keep readable)
        note = str(e.get("note", ""))
        tag = f"[INJECT:{pid}]"
        if tag not in note:
            e["note"] = (note + " " + tag + " synthetic pattern injected.").strip()

        injected_events += 1

    # If cross-domain confusion, optionally "shadow inject" a small comms/latency co-move
    if pid == "CROSS_DOMAIN_CONFUSION":
        _shadow_inject(events, rng=rng, intensity=intensity)

    # write back and update bundle stats
    bundle["events"] = events
    _recompute_bundle_stats(bundle)

    injected = InjectedPattern(
        pattern_id=pid,
        label=meta.get("label", pid),
        domains=domains,
        intensity=float(intensity),
        expected_effects=list(meta.get("expected_effects", [])),
        injected_events=int(injected_events),
    )
    _append_injection_metadata(bundle, injected)

    return bundle, injected


def _severity_from_value(x: float) -> str:
    if x >= 85:
        return "CRIT"
    if x >= 70:
        return "HIGH"
    if x >= 50:
        return "MED"
    return "LOW"


def _shadow_inject(events: List[Dict[str, Any]], rng: random.Random, intensity: float) -> None:
    """
    Adds a small correlated disturbance to COMMS/LATENCY events to mimic confusion.
    """
    domains = {"COMMS", "LATENCY"}
    idxs = [i for i, e in enumerate(events) if str(e.get("domain", "")).upper() in domains]
    if not idxs:
        return
    k = max(2, int(min(12, len(idxs)) * (0.20 + 0.35 * intensity)))
    k = int(_clamp(k, 2, min(18, len(idxs))))
    chosen = rng.sample(idxs, k=k)
    for idx in chosen:
        e = events[idx]
        v = float(e.get("value", 0.0) or 0.0)
        bump = rng.uniform(8.0, 22.0) * intensity
        e["value"] = round(_clamp(v + bump, 0.0, 100.0), 3)
        e["anomaly"] = True
        e["severity"] = _severity_from_value(float(e["value"]))
        note = str(e.get("note", ""))
        tag = "[INJECT:CROSS_DOMAIN_CONFUSION]"
        if tag not in note:
            e["note"] = (note + " " + tag + " correlated disturbance.").strip()


def _recompute_bundle_stats(bundle: Dict[str, Any]) -> None:
    events = list(bundle.get("events", []) or [])
    total = len(events)
    anomaly = sum(1 for e in events if bool(e.get("anomaly", False)))
    attack = sum(1 for e in events if bool(e.get("attack_like", False)))
    crit = sum(1 for e in events if str(e.get("severity", "")).upper() == "CRIT")
    domains = sorted({str(e.get("domain", "")).upper() for e in events})
    domain_counts: Dict[str, int] = {}
    for d in domains:
        domain_counts[d] = sum(1 for e in events if str(e.get("domain", "")).upper() == d)

    if "stats" not in bundle or not isinstance(bundle["stats"], dict):
        bundle["stats"] = {}

    bundle["stats"].update(
        {
            "total_events": total,
            "anomaly_events": anomaly,
            "attack_like_events": attack,
            "crit_events": crit,
            "domains": domains,
            "domain_counts": domain_counts,
        }
    )


def _append_injection_metadata(bundle: Dict[str, Any], injected: InjectedPattern) -> None:
    if "injections" not in bundle or not isinstance(bundle["injections"], list):
        bundle["injections"] = []
    bundle["injections"].append(asdict(injected))

