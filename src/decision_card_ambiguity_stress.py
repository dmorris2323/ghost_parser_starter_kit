"""
decision_card_ambiguity_stress.py

Hardening test: Decision card must remain commander-safe under ambiguity:
- missing signals
- degraded ops
- noisy EMS / comms uncertainty
- alert pressure

Success criteria (PASS):
- card builds for every test case (no crash)
- status.confidence is never HIGH when ambiguity exists
- ambiguity_flags present when degraded/missing signals exist
- escalation posture is present
- “bounded language” is used (no absolute certainty phrasing)

Outputs:
- docs/nuclear/ambiguity_stress_latest.json
- docs/nuclear/ambiguity_stress_latest.txt
- docs/nuclear/ambiguity_stress_<timestamp>.json
- docs/nuclear/ambiguity_stress_<timestamp>.txt
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


OUT_DIR = Path("docs") / "nuclear"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, obj: Any) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _write_txt(path: Path, text: str) -> None:
    _safe_mkdir(path.parent)
    path.write_text(text, encoding="utf-8")


ABSOLUTE_PHRASES = [
    "confirmed",
    "we know",
    "certain",
    "definitive",
    "guaranteed",
    "no doubt",
    "is a nuclear event",
    "this is nuclear",
    "launch confirmed",
]


def _contains_absolute_language(text: str) -> bool:
    t = (text or "").lower()
    return any(p in t for p in ABSOLUTE_PHRASES)


def _get(d: Dict[str, Any], path: List[str], default: Any = None) -> Any:
    cur: Any = d
    for k in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
    return cur if cur is not None else default


def _as_str(x: Any) -> str:
    try:
        return str(x)
    except Exception:
        return ""


def _build_cases() -> List[Dict[str, Any]]:
    """
    Generates a matrix of cases focused on ambiguous inputs.
    IMPORTANT: We always supply trust_score and risk_score so the card logic
    isn’t implicitly defaulting to zero unless it intentionally caps/bounds.
    """
    base_alerts = [
        {"crit": 0, "high": 0, "anomaly": 2},
        {"crit": 0, "high": 2, "anomaly": 12},
        {"crit": 1, "high": 5, "anomaly": 24},
    ]

    cases: List[Dict[str, Any]] = []
    for degraded in [False, True]:
        for comms_state in [None, "OK", "NOISY", "DEGRADED"]:
            for ems_state in [None, "CLEAR", "NOISY"]:
                for seismic_mag in [None, 2.1, 4.7]:
                    for radiation_usv in [None, 0.08, 0.35]:
                        for alerts in base_alerts:
                            # Define “ambiguity exists” conditions
                            missing = (comms_state is None) or (ems_state is None) or (seismic_mag is None) or (radiation_usv is None)
                            ambiguous = degraded or missing or (comms_state in {"NOISY", "DEGRADED"}) or (ems_state == "NOISY")

                            trust_score = 82 if not ambiguous else 78
                            risk_score = 18 if not ambiguous else 48

                            cases.append({
                                "degraded": degraded,
                                "comms_state": comms_state,
                                "ems_state": ems_state,
                                "seismic_mag": seismic_mag,
                                "radiation_usv": radiation_usv,
                                "alerts": alerts,
                                "trust_score": trust_score,
                                "risk_score": risk_score,
                                "expect_ambiguity": ambiguous,
                            })
    return cases


def _validate_card(card: Dict[str, Any], expect_ambiguity: bool) -> List[str]:
    violations: List[str] = []

    confidence = _get(card, ["status", "confidence"], "")
    ambiguity_flags = _get(card, ["status", "ambiguity_flags"], [])
    posture = _get(card, ["escalation", "posture"], None)

    # Escalation posture must exist
    if posture is None:
        violations.append("MISSING_ESCALATION_POSTURE")

    # If ambiguity is expected, confidence MUST NOT be HIGH
    if expect_ambiguity:
        if _as_str(confidence).upper() == "HIGH":
            violations.append("AMBIGUITY_HAS_HIGH_CONFIDENCE")
        if not isinstance(ambiguity_flags, list) or len(ambiguity_flags) == 0:
            violations.append("AMBIGUITY_MISSING_FLAGS")

    # Bounded language checks across key narrative fields (if present)
    narrative_fields = [
        _get(card, ["narrative"], ""),
        _get(card, ["what_we_can_say"], ""),
        _get(card, ["bounded_statement"], ""),
        _get(card, ["assessment"], ""),
    ]
    for idx, text in enumerate(narrative_fields):
        if isinstance(text, str) and text.strip():
            if _contains_absolute_language(text):
                violations.append(f"ABSOLUTE_LANGUAGE_FIELD_{idx}")

    return violations


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        from nuclear_decision_card import build_decision_card  # type: ignore
    except Exception as e:
        print(f"ImportError: nuclear_decision_card.build_decision_card: {e.__class__.__name__}: {e}")
        return

    cases = _build_cases()
    results: List[Dict[str, Any]] = []
    violations_total: List[Dict[str, Any]] = []
    crash_count = 0

    for i, c in enumerate(cases):
        try:
            card = build_decision_card(
                trust_score=c["trust_score"],
                risk_score=c["risk_score"],
                alerts=c["alerts"],
                degraded=c["degraded"],
                comms_state=c["comms_state"],
                radiation_usv=c["radiation_usv"],
                seismic_mag=c["seismic_mag"],
                ems_state=c["ems_state"],
            )
        except Exception as e:
            crash_count += 1
            violations_total.append({
                "case_index": i,
                "type": "CRASH",
                "error": f"{e.__class__.__name__}: {e}",
                "case": c,
            })
            continue

        v = _validate_card(card, expect_ambiguity=bool(c["expect_ambiguity"]))
        results.append({
            "case_index": i,
            "case": c,
            "confidence": _get(card, ["status", "confidence"], None),
            "risk_band": _get(card, ["status", "risk_band"], None),
            "posture": _get(card, ["escalation", "posture"], None),
            "ambiguity_flags": _get(card, ["status", "ambiguity_flags"], None),
            "violations": v,
        })
        if v:
            violations_total.append({
                "case_index": i,
                "type": "VIOLATIONS",
                "violations": v,
                "case": c,
            })

    verdict = "PASS" if (crash_count == 0 and len(violations_total) == 0) else "FAIL"

    report = {
        "generated_at_utc": _utc_now_iso(),
        "verdict": verdict,
        "total_cases": len(cases),
        "crashes": crash_count,
        "violations": len(violations_total),
        "violation_items": violations_total[:200],  # cap to keep file readable
        "summary": {
            "notes": [
                "This is synthetic ambiguity stress. It validates bounded outputs, not real nuclear truth.",
                "PASS requires: no crashes + no violations across the ambiguity matrix.",
            ]
        },
    }

    json_latest = OUT_DIR / "ambiguity_stress_latest.json"
    txt_latest = OUT_DIR / "ambiguity_stress_latest.txt"
    json_stamped = OUT_DIR / f"ambiguity_stress_{_ts()}.json"
    txt_stamped = OUT_DIR / f"ambiguity_stress_{_ts()}.txt"

    _write_json(json_latest, report)
    _write_json(json_stamped, report)

    txt = []
    txt.append("Ambiguity Stress Test")
    txt.append(f"generated_at_utc: {report['generated_at_utc']}")
    txt.append(f"verdict: {verdict}")
    txt.append(f"total_cases: {len(cases)}")
    txt.append(f"crashes: {crash_count}")
    txt.append(f"violations: {len(violations_total)}")
    if violations_total:
        txt.append("\nTop violation items (first 25):")
        for item in violations_total[:25]:
            txt.append(json.dumps(item, indent=2))
    _write_txt(txt_latest, "\n".join(txt))
    _write_txt(txt_stamped, "\n".join(txt))

    print("Ambiguity stress written:")
    print(f"  json_latest: {json_latest}")
    print(f"  txt_latest: {txt_latest}")
    print(f"  json_stamped: {json_stamped}")
    print(f"  txt_stamped: {txt_stamped}")
    print(f"Verdict: {verdict}, violations={len(violations_total)}")


if __name__ == "__main__":
    main()

