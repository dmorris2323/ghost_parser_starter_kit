"""
synthetic_signal_generator.py

Day 68 — Synthetic Signal Generator (SAFE)
Creates fake-but-structured ISR/cyber fusion telemetry bundles for testing/training.

Now supports Pattern Injection (Module 2):
  - pattern_id: e.g. "CYBER_LOTL", "EMS_BURST_NOISE", "CROSS_DOMAIN_CONFUSION"

Outputs:
  - src/docs/synthetic/synthetic_fusion_bundle.json
  - src/docs/synthetic/synthetic_fusion_bundle_<timestamp>.json
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _docs_dir() -> Path:
    return _repo_root() / "src" / "docs"


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _utc_iso(ts: Optional[datetime] = None) -> str:
    ts = ts or datetime.utcnow()
    return ts.isoformat()


def _stamp() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


DIFFICULTY_PRESETS: Dict[str, Dict[str, Any]] = {
    "BEGINNER": {
        "duration_minutes": 30,
        "event_count": 40,
        "noise": 0.15,
        "anomaly_rate": 0.08,
        "attack_rate": 0.03,
        "dropout_rate": 0.02,
        "latency_spike_rate": 0.03,
        "confidence_floor": 0.65,
    },
    "INTERMEDIATE": {
        "duration_minutes": 45,
        "event_count": 60,
        "noise": 0.22,
        "anomaly_rate": 0.14,
        "attack_rate": 0.06,
        "dropout_rate": 0.04,
        "latency_spike_rate": 0.06,
        "confidence_floor": 0.55,
    },
    "ADVANCED": {
        "duration_minutes": 60,
        "event_count": 80,
        "noise": 0.28,
        "anomaly_rate": 0.20,
        "attack_rate": 0.10,
        "dropout_rate": 0.06,
        "latency_spike_rate": 0.10,
        "confidence_floor": 0.45,
    },
    "ADVERSARIAL": {
        "duration_minutes": 75,
        "event_count": 110,
        "noise": 0.35,
        "anomaly_rate": 0.28,
        "attack_rate": 0.18,
        "dropout_rate": 0.10,
        "latency_spike_rate": 0.16,
        "confidence_floor": 0.35,
    },
}


@dataclass
class SyntheticEvent:
    ts_utc: str
    domain: str
    sensor: str
    metric: str
    value: float
    severity: str
    anomaly: bool
    attack_like: bool
    note: str


def _severity_from_score(x: float) -> str:
    if x >= 85:
        return "CRIT"
    if x >= 70:
        return "HIGH"
    if x >= 50:
        return "MED"
    return "LOW"


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _randn(rng: random.Random) -> float:
    u1 = max(1e-9, rng.random())
    u2 = max(1e-9, rng.random())
    import math
    z0 = (-2.0 * math.log(u1)) ** 0.5 * math.cos(2.0 * math.pi * u2)
    return z0


def _mk_sensor(domain: str, idx: int) -> str:
    return f"SYN_{domain}_{idx:02d}"


def _base_value(domain: str) -> float:
    return {
        "OPTICAL": 35.0,
        "EMS": 30.0,
        "CYBER": 25.0,
        "SEISMIC": 20.0,
        "RADIATION": 15.0,
        "COMMS": 28.0,
        "LATENCY": 18.0,
    }.get(domain, 25.0)


def _metric_for(domain: str) -> str:
    return {
        "OPTICAL": "optical_activity",
        "EMS": "ems_noise_index",
        "CYBER": "cyber_event_rate",
        "SEISMIC": "seismic_disturbance",
        "RADIATION": "radiation_uSv_index",
        "COMMS": "comms_state_index",
        "LATENCY": "sensor_latency_ms_index",
    }.get(domain, "metric")


def _note_for(domain: str, anomaly: bool, attack_like: bool) -> str:
    if attack_like:
        return f"{domain}: synthetic attack-like pattern present (training-safe)."
    if anomaly:
        return f"{domain}: synthetic anomaly spike (training-safe)."
    return f"{domain}: nominal synthetic telemetry."


def _choose_domain(rng: random.Random) -> str:
    domains = ["OPTICAL", "EMS", "CYBER", "SEISMIC", "RADIATION", "COMMS", "LATENCY"]
    weights = [1.0, 1.2, 1.3, 0.9, 0.8, 1.1, 1.0]
    r = rng.random() * sum(weights)
    acc = 0.0
    for d, w in zip(domains, weights):
        acc += w
        if r <= acc:
            return d
    return "CYBER"


def _maybe_dropout(rng: random.Random, dropout_rate: float) -> bool:
    return rng.random() < dropout_rate


def _generate_events(difficulty: str, seed: Optional[int] = None) -> List[SyntheticEvent]:
    diff = DIFFICULTY_PRESETS.get(difficulty.upper(), DIFFICULTY_PRESETS["INTERMEDIATE"])
    rng = random.Random(seed)

    start = datetime.utcnow()
    duration = timedelta(minutes=int(diff["duration_minutes"]))
    end = start + duration

    event_count = int(diff["event_count"])
    noise = float(diff["noise"])
    anomaly_rate = float(diff["anomaly_rate"])
    attack_rate = float(diff["attack_rate"])
    dropout_rate = float(diff["dropout_rate"])
    latency_spike_rate = float(diff["latency_spike_rate"])
    confidence_floor = float(diff["confidence_floor"])

    events: List[SyntheticEvent] = []
    sensors = {d: [_mk_sensor(d, i) for i in range(1, 4)] for d in ["OPTICAL", "EMS", "CYBER", "SEISMIC", "RADIATION", "COMMS", "LATENCY"]}

    for _ in range(event_count):
        frac = rng.random()
        ts = start + (end - start) * frac

        domain = _choose_domain(rng)
        sensor = rng.choice(sensors[domain])
        metric = _metric_for(domain)

        base = _base_value(domain)
        v = base + (_randn(rng) * 12.0 * noise)

        anomaly = rng.random() < anomaly_rate
        attack_like = rng.random() < attack_rate

        if domain == "LATENCY":
            if rng.random() < latency_spike_rate:
                v += rng.uniform(25.0, 60.0)
                anomaly = True
            v = _clamp(v, 0.0, 100.0)

        if domain == "CYBER" and attack_like:
            v += rng.uniform(30.0, 65.0)
            anomaly = True
            v = _clamp(v, 0.0, 100.0)

        if domain == "EMS" and attack_like:
            v += rng.uniform(20.0, 55.0)
            anomaly = True
            v = _clamp(v, 0.0, 100.0)

        if domain == "COMMS" and anomaly:
            v += rng.uniform(15.0, 45.0)
            v = _clamp(v, 0.0, 100.0)

        if domain in ("SEISMIC", "RADIATION") and anomaly:
            v += rng.uniform(10.0, 40.0)
            v = _clamp(v, 0.0, 100.0)

        if domain == "OPTICAL" and anomaly:
            v += rng.uniform(12.0, 45.0)
            v = _clamp(v, 0.0, 100.0)

        if _maybe_dropout(rng, dropout_rate):
            continue

        severity = _severity_from_score(v)

        confidence_penalty = 0.0
        if anomaly:
            confidence_penalty += 0.12
        if attack_like:
            confidence_penalty += 0.18
        confidence_penalty += noise * 0.15
        confidence = _clamp(1.0 - confidence_penalty, confidence_floor, 0.98)

        note = _note_for(domain, anomaly, attack_like)
        events.append(
            SyntheticEvent(
                ts_utc=_utc_iso(ts),
                domain=domain,
                sensor=sensor,
                metric=metric,
                value=round(_clamp(v, 0.0, 100.0), 3),
                severity=severity,
                anomaly=bool(anomaly),
                attack_like=bool(attack_like),
                note=(note + f" (confidence={confidence:.2f})").strip(),
            )
        )

    events.sort(key=lambda e: e.ts_utc)
    return events


def build_synthetic_fusion_bundle(
    difficulty: str = "INTERMEDIATE",
    seed: Optional[int] = None,
    pattern_id: Optional[str] = None,
    pattern_seed: Optional[int] = None,
    write: bool = True,
) -> Dict[str, Any]:
    difficulty = difficulty.upper().strip()
    if difficulty not in DIFFICULTY_PRESETS:
        difficulty = "INTERMEDIATE"

    events = _generate_events(difficulty=difficulty, seed=seed)

    total = len(events)
    anomaly_count = sum(1 for e in events if e.anomaly)
    attack_count = sum(1 for e in events if e.attack_like)
    crit_count = sum(1 for e in events if e.severity == "CRIT")

    domains = sorted({e.domain for e in events})
    domain_counts: Dict[str, int] = {d: sum(1 for e in events if e.domain == d) for d in domains}

    bundle: Dict[str, Any] = {
        "bundle_version": 2,
        "generated_at": _utc_iso(),
        "difficulty": difficulty,
        "seed": seed,
        "safe_notice": "Synthetic training telemetry only. Contains no real-world sensitive meaning.",
        "stats": {
            "total_events": total,
            "anomaly_events": anomaly_count,
            "attack_like_events": attack_count,
            "crit_events": crit_count,
            "domains": domains,
            "domain_counts": domain_counts,
        },
        "injections": [],
        "events": [asdict(e) for e in events],
    }

    # Optional Pattern Injection (Module 2)
    if pattern_id:
        try:
            from pattern_injection_engine import inject_pattern
            bundle, injected = inject_pattern(
                bundle=bundle,
                pattern_id=str(pattern_id),
                difficulty=difficulty,
                seed=pattern_seed if pattern_seed is not None else seed,
            )
            bundle["pattern_requested"] = str(pattern_id).upper()
            bundle["pattern_seed"] = pattern_seed if pattern_seed is not None else seed
        except Exception as e:
            # Non-fatal: preserve base bundle and record error
            bundle["pattern_requested"] = str(pattern_id).upper()
            bundle["pattern_seed"] = pattern_seed if pattern_seed is not None else seed
            bundle["pattern_error"] = f"{type(e).__name__}: {e}"

    if write:
        out_dir = _docs_dir() / "synthetic"
        _safe_mkdir(out_dir)
        latest = out_dir / "synthetic_fusion_bundle.json"
        stamped = out_dir / f"synthetic_fusion_bundle_{_stamp()}.json"

        latest.write_text(json.dumps(bundle, indent=2))
        stamped.write_text(json.dumps(bundle, indent=2))

        bundle["paths"] = {"latest": str(latest), "stamped": str(stamped)}

    return bundle


def write_synthetic_bundle(
    difficulty: str = "INTERMEDIATE",
    seed: Optional[int] = None,
    pattern_id: Optional[str] = None,
    pattern_seed: Optional[int] = None,
) -> Dict[str, str]:
    bundle = build_synthetic_fusion_bundle(
        difficulty=difficulty,
        seed=seed,
        pattern_id=pattern_id,
        pattern_seed=pattern_seed,
        write=True,
    )
    paths = bundle.get("paths", {})
    return {
        "json_path": paths.get("latest", ""),
        "stamped_path": paths.get("stamped", ""),
        "difficulty": bundle.get("difficulty", ""),
        "total_events": str(bundle.get("stats", {}).get("total_events", 0)),
        "pattern_requested": str(bundle.get("pattern_requested", "")),
    }


if __name__ == "__main__":
    # Example: injected cross-domain confusion
    res = write_synthetic_bundle(difficulty="ADVERSARIAL", seed=99, pattern_id="CROSS_DOMAIN_CONFUSION", pattern_seed=99)
    print("Synthetic fusion bundle written:")
    print(f"  JSON: {res['json_path']}")
    print(f"  Stamped: {res['stamped_path']}")
    print(f"  Difficulty: {res['difficulty']}")
    print(f"  Total events: {res['total_events']}")
    if res.get("pattern_requested"):
        print(f"  Pattern: {res['pattern_requested']}")

