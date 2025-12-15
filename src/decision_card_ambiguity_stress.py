"""
decision_card_ambiguity_stress.py

Week-1 hardening:
- Stress-test nuclear decision card posture under ambiguity
- Generate a matrix of scenarios (missing signals/degraded/alerts)
- Verify escalation ladder does not over-escalate when risk<65 and crit==0
- Write artifacts for command trust

Outputs:
- docs/nuclear/ambiguity_stress_latest.json
- docs/nuclear/ambiguity_stress_latest.txt
- docs/nuclear/ambiguity_stress_<timestamp>.json
- docs/nuclear/ambiguity_stress_<timestamp>.txt
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from nuclear_decision_card import build_decision_card


NUCLEAR_DIR = Path("docs") / "nuclear"


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


def _scenario_rows() -> List[Dict[str, Any]]:
    """
    Matrix design:
    - Keep primary case risk=48 (GUARDED) and no CRIT
    - Vary missing signals + degraded + high count
    - Ensure the cap holds: posture should not exceed HEIGHTENED_COLLECTION
    """
    base_alerts = {"crit": 0, "high": 3, "anomaly": 14, "attack_like": 0}

    rows: List[Dict[str, Any]] = []

    for degraded in [False, True]:
        for missing_profile in ["NONE_MISSING", "COMMS_MISSING", "RAD_MISSING", "MAG_MISSING", "ALL_MISSING"]:
            for high in [0, 1, 3, 5]:
                alerts = dict(base_alerts)
                alerts["high"] = high

                comms_state = "OK"
                radiation_usv = 0.12
                seismic_mag = 2.1
                ems_state = "OK"

                if missing_profile == "COMMS_MISSING":
                    comms_state = None
                elif missing_profile == "RAD_MISSING":
                    radiation_usv = None
                elif missing_profile == "MAG_MISSING":
                    seismic_mag = None
                elif missing_profile == "ALL_MISSING":
                    comms_state = None
                    radiation_usv = None
                    seismic_mag = None
                    ems_state = None

                rows.append(
                    {
                        "risk_score": 48,
                        "trust_score": 82,
                        "alerts": alerts,
                        "degraded": degraded,
                        "comms_state": comms_state,
                        "radiation_usv": radiation_usv,
                        "seismic_mag": seismic_mag,
                        "ems_state": ems_state,
                        "tag": f"risk48_trust82_{missing_profile}_degraded{degraded}_high{high}",
                    }
                )
    return rows


def run_ambiguity_stress() -> Dict[str, Any]:
    rows = _scenario_rows()

    results: List[Dict[str, Any]] = []
    violations: List[Dict[str, Any]] = []

    for r in rows:
        card = build_decision_card(
            trust_score=r["trust_score"],
            risk_score=r["risk_score"],
            alerts=r["alerts"],
            degraded=r["degraded"],
            comms_state=r["comms_state"],
            radiation_usv=r["radiation_usv"],
            seismic_mag=r["seismic_mag"],
            ems_state=r["ems_state"],
            scenario="Ambiguity Stress (SAFE)",
            notes="Matrix test for bounded escalation under ambiguity.",
        )

        posture = (card.get("escalation") or {}).get("posture", "UNKNOWN")
        cap_applied = ((card.get("escalation") or {}).get("rationale") or {}).get("cap_applied", False)

        item = {
            "tag": r["tag"],
            "inputs": {
                "risk_score": r["risk_score"],
                "trust_score": r["trust_score"],
                "alerts": r["alerts"],
                "degraded": r["degraded"],
                "missing_signal_count": (card.get("signals") or {}).get("missing_signal_count", 0),
            },
            "outputs": {
                "confidence": (card.get("status") or {}).get("confidence", "UNKNOWN"),
                "risk_band": (card.get("status") or {}).get("risk_band", "UNKNOWN"),
                "posture": posture,
                "cap_applied": bool(cap_applied),
                "ambiguity_flags": (card.get("status") or {}).get("ambiguity_flags", []),
            },
        }
        results.append(item)

        # rule we are enforcing in Week-1:
        # when risk < 65 and crit == 0, posture must not exceed HEIGHTENED_COLLECTION
        alerts = r["alerts"]
        if r["risk_score"] < 65 and int(alerts.get("crit", 0)) == 0:
            if posture in {"DUTY_OFFICER_NOTIFY", "CRISIS_ACTION_TEAM"}:
                violations.append(item)

    verdict = "PASS" if len(violations) == 0 else "FAIL"

    report = {
        "generated_at_utc": _utc_now_iso(),
        "type": "AMBIGUITY_STRESS_REPORT",
        "safe_notice": "Generated from synthetic/constructed inputs for training/demos.",
        "matrix_size": len(results),
        "verdict": verdict,
        "violations_count": len(violations),
        "violations": violations[:25],  # keep bounded
        "summary": {
            "rule": "If risk<65 and crit==0, posture must not exceed HEIGHTENED_COLLECTION.",
            "note": "Ambiguity should push collection/verification, not automatic notification.",
        },
        "samples": results[:15],
    }
    return report


def write_report(report: Dict[str, Any]) -> Dict[str, str]:
    _safe_mkdir(NUCLEAR_DIR)
    stamped = _ts()

    json_latest = NUCLEAR_DIR / "ambiguity_stress_latest.json"
    txt_latest = NUCLEAR_DIR / "ambiguity_stress_latest.txt"
    json_stamped = NUCLEAR_DIR / f"ambiguity_stress_{stamped}.json"
    txt_stamped = NUCLEAR_DIR / f"ambiguity_stress_{stamped}.txt"

    _write_json(json_latest, report)
    _write_json(json_stamped, report)

    lines: List[str] = []
    lines.append("GLL — AMBIGUITY STRESS REPORT (LATEST)")
    lines.append(f"Generated (UTC): {report.get('generated_at_utc','')}")
    lines.append(f"Verdict: {report.get('verdict','')}")
    lines.append(f"Matrix size: {report.get('matrix_size',0)}")
    lines.append(f"Violations: {report.get('violations_count',0)}")
    lines.append("")
    lines.append("Rule:")
    lines.append(f"- {report.get('summary',{}).get('rule','')}")
    lines.append("")
    if report.get("violations_count", 0) > 0:
        lines.append("Top violations (first 10):")
        for v in (report.get("violations") or [])[:10]:
            lines.append(f"- {v.get('tag','')} -> posture={v.get('outputs',{}).get('posture','')}")
    else:
        lines.append("No violations. Escalation remained bounded under ambiguity.")
    _write_txt(txt_latest, "\n".join(lines).strip() + "\n")
    _write_txt(txt_stamped, "\n".join(lines).strip() + "\n")

    return {
        "json_latest": str(json_latest),
        "txt_latest": str(txt_latest),
        "json_stamped": str(json_stamped),
        "txt_stamped": str(txt_stamped),
    }


if __name__ == "__main__":
    rep = run_ambiguity_stress()
    paths = write_report(rep)
    print("Ambiguity stress written:")
    for k, v in paths.items():
        print(f"  {k}: {v}")
    print(f"Verdict: {rep.get('verdict')}, violations={rep.get('violations_count')}")

