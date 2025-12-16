"""
prebrief_trust_consistency.py

Command-trust consistency gate for prebrief trust annotations.

Goal:
- No crashes
- Violations list is explicit
- Verdict is deterministic:
    PASS if violations_count == 0
    FAIL otherwise

Outputs:
- docs/nuclear/prebrief_trust_consistency_latest.json
- docs/nuclear/prebrief_trust_consistency_latest.txt
- stamped copies with timestamp
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


OUT_DIR = Path("docs") / "nuclear"
ANNOTATIONS_LATEST = Path("docs") / "briefs" / "prebrief_trust_annotations_latest.json"


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


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        if not path.exists():
            return {}
        raw = json.loads(path.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except Exception:
        return {}


def _coerce_list(x: Any) -> List[str]:
    if isinstance(x, list):
        return [str(i) for i in x]
    return []


def _extract_bounded_lists(annotations: Dict[str, Any]) -> Tuple[List[str], List[str], List[str]]:
    """
    Support both older/newer shapes.
    Prefer:
      annotations["bounded"]
      annotations["cannot_say"]
      annotations["unknowns"]
    Fallbacks:
      annotations["what_we_can_say"], ["what_we_cannot_say"], ["unknowns"]
    """
    bounded = _coerce_list(annotations.get("bounded") or annotations.get("what_we_can_say") or [])
    cannot = _coerce_list(annotations.get("cannot_say") or annotations.get("what_we_cannot_say") or [])
    unknowns = _coerce_list(annotations.get("unknowns") or [])
    return bounded, cannot, unknowns


def _validate(annotations: Dict[str, Any]) -> List[str]:
    """
    Keep checks simple and stable.
    This is a commander-trust gate: require the prebrief to explicitly state bounded + probabilistic under ambiguity.
    """
    violations: List[str] = []

    if not annotations:
        return ["MISSING_ANNOTATIONS_JSON"]

    trust_posture = annotations.get("trust_posture") or {}
    ambiguity_flags = trust_posture.get("ambiguity_flags") or []
    degraded = bool(trust_posture.get("degraded", False))

    bounded, cannot, unknowns = _extract_bounded_lists(annotations)

    # Under degraded OR ambiguity, we must have explicit bounded language.
    expect_ambiguity = bool(degraded) or (isinstance(ambiguity_flags, list) and len(ambiguity_flags) > 0)

    if expect_ambiguity:
        must_include_any = [
            "probabilistic",
            "bounded",
            "operator judgment",
        ]
        blob = " ".join(bounded + cannot + unknowns).lower()

        for token in must_include_any:
            if token not in blob:
                violations.append(f"MISSING_REQUIRED_TOKEN:{token}")

    # Must not claim certainty under ambiguity.
    if expect_ambiguity:
        forbidden = ["certain", "confirmed", "guaranteed", "definitive"]
        blob = " ".join(bounded).lower()
        for token in forbidden:
            if token in blob:
                violations.append(f"FORBIDDEN_CERTAINTY_TOKEN:{token}")

    return violations


def _render_txt(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("Prebrief Trust Consistency")
    lines.append(f"generated_at_utc: {report.get('generated_at_utc')}")
    lines.append(f"verdict: {report.get('verdict')}")
    lines.append(f"crashes: {report.get('crashes')}")
    lines.append(f"violations: {report.get('violations_count')}")
    lines.append("")
    if report.get("violations"):
        lines.append("Violation items:")
        for v in report["violations"][:50]:
            lines.append(f"- {v}")
    else:
        lines.append("No violations.")
    return "\n".join(lines) + "\n"


def main() -> None:
    ts = _ts()
    latest_json = OUT_DIR / "prebrief_trust_consistency_latest.json"
    latest_txt = OUT_DIR / "prebrief_trust_consistency_latest.txt"
    stamped_json = OUT_DIR / f"prebrief_trust_consistency_{ts}.json"
    stamped_txt = OUT_DIR / f"prebrief_trust_consistency_{ts}.txt"

    crashes = 0
    violations: List[str] = []

    try:
        annotations = _load_json(ANNOTATIONS_LATEST)
        violations = _validate(annotations)
    except Exception as e:
        crashes = 1
        violations = [f"CRASH:{e.__class__.__name__}:{e}"]

    verdict = "PASS" if crashes == 0 and len(violations) == 0 else "FAIL"

    report: Dict[str, Any] = {
        "generated_at_utc": _utc_now_iso(),
        "safe_notice": "This report is generated from synthetic telemetry and is safe for training/demos.",
        "inputs": {
            "annotations_latest_path": str(ANNOTATIONS_LATEST),
        },
        "verdict": verdict,
        "crashes": crashes,
        "violations_count": len(violations),
        "violations": violations,
        "paths": {
            "json_latest": str(latest_json),
            "txt_latest": str(latest_txt),
            "json_stamped": str(stamped_json),
            "txt_stamped": str(stamped_txt),
        },
    }

    _write_json(latest_json, report)
    _write_txt(latest_txt, _render_txt(report))
    _write_json(stamped_json, report)
    _write_txt(stamped_txt, _render_txt(report))

    print("Prebrief trust consistency written:")
    print(json.dumps(report["paths"], indent=2))
    print(f"Verdict: {verdict}")


if __name__ == "__main__":
    main()

