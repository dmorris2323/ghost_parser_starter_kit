from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------
# Output paths (standard + legacy)
# ---------------------------------------------------------------------

OUT_DIR = Path("docs") / "briefs"
LEGACY_DIR = Path("src") / "docs"

LATEST_JSON = OUT_DIR / "legal_case_snapshot_latest.json"
LATEST_TXT = OUT_DIR / "legal_case_snapshot_latest.txt"

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _stamp() -> str:
    # Use UTC stamp like rest of stack
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")

def _safe_str(x: Any, default: str = "") -> str:
    try:
        if x is None:
            return default
        s = str(x).strip()
        return s if s else default
    except Exception:
        return default

def _safe_list(x: Any) -> List[str]:
    try:
        if x is None:
            return []
        if isinstance(x, list):
            out = []
            for item in x:
                out.append(_safe_str(item, default="").strip())
            return [z for z in out if z]
        # allow comma-separated string
        if isinstance(x, str):
            return [z.strip() for z in x.split(",") if z.strip()]
        return []
    except Exception:
        return []

def _bounded_posture(posture: str) -> str:
    # Legal + demo posture: keep it conservative
    allowed = {
        "ROUTINE_MONITORING",
        "DUTY_OFFICER_NOTIFY",
        "LEGAL_REVIEW_RECOMMENDED",
        "HOLD_ACTION_PENDING_REVIEW",
    }
    p = _safe_str(posture, "LEGAL_REVIEW_RECOMMENDED")
    return p if p in allowed else "LEGAL_REVIEW_RECOMMENDED"

def _risk_band(score: Optional[float]) -> str:
    # For Shari: simple and consistent
    try:
        if score is None:
            return "UNKNOWN"
        if score >= 80:
            return "HIGH"
        if score >= 50:
            return "MEDIUM"
        if score >= 0:
            return "LOW"
        return "UNKNOWN"
    except Exception:
        return "UNKNOWN"

def _safe_float(x: Any) -> Optional[float]:
    try:
        if x is None:
            return None
        if isinstance(x, (int, float)):
            return float(x)
        s = str(x).strip()
        if not s:
            return None
        return float(s)
    except Exception:
        return None

@dataclass
class LegalCaseInputs:
    case_type: str = "COLLECTIONS"
    matter_name: str = "Demo Matter"
    debtor_or_defendant: str = "UNKNOWN"
    jurisdiction: str = "UNKNOWN"
    stage: str = "PRE-SUIT"
    days_past_due: Optional[int] = None
    balance_usd: Optional[float] = None
    risk_score: Optional[float] = None
    red_flags: List[str] = None
    recommended_next_step: str = "Operator judgment applies; consult counsel."

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_type": self.case_type,
            "matter_name": self.matter_name,
            "debtor_or_defendant": self.debtor_or_defendant,
            "jurisdiction": self.jurisdiction,
            "stage": self.stage,
            "days_past_due": self.days_past_due,
            "balance_usd": self.balance_usd,
            "risk_score": self.risk_score,
            "red_flags": self.red_flags or [],
            "recommended_next_step": self.recommended_next_step,
        }

def build_legal_case_snapshot(
    case_type: str = "COLLECTIONS",
    matter_name: str = "Demo Matter",
    debtor_or_defendant: str = "UNKNOWN",
    jurisdiction: str = "UNKNOWN",
    stage: str = "PRE-SUIT",
    days_past_due: Any = None,
    balance_usd: Any = None,
    risk_score: Any = None,
    red_flags: Any = None,
    recommended_next_step: str = "",
    synthetic_notice: str = "This artifact is derived from synthetic inputs and is safe for training/demos.",
) -> Dict[str, Any]:
    """
    Commander-safe, Shari-friendly legal snapshot.
    Must never crash, even with bad inputs.
    """

    # sanitize
    case_type_s = _safe_str(case_type, "COLLECTIONS").upper()
    matter_name_s = _safe_str(matter_name, "Demo Matter")
    debtor_s = _safe_str(debtor_or_defendant, "UNKNOWN")
    juris_s = _safe_str(jurisdiction, "UNKNOWN")
    stage_s = _safe_str(stage, "PRE-SUIT").upper()

    # ints/floats
    dpd = None
    try:
        if days_past_due is not None and str(days_past_due).strip() != "":
            dpd = int(float(str(days_past_due).strip()))
    except Exception:
        dpd = None

    bal = _safe_float(balance_usd)
    rscore = _safe_float(risk_score)

    flags = _safe_list(red_flags)

    # ambiguity flags
    ambiguity: List[str] = []
    if dpd is None:
        ambiguity.append("MISSING_DAYS_PAST_DUE")
    if bal is None:
        ambiguity.append("MISSING_BALANCE_USD")
    if rscore is None:
        ambiguity.append("MISSING_RISK_SCORE")
    if debtor_s == "UNKNOWN":
        ambiguity.append("UNKNOWN_PARTY")
    if juris_s == "UNKNOWN":
        ambiguity.append("UNKNOWN_JURISDICTION")

    band = _risk_band(rscore)

    # posture: keep bounded and conservative
    posture = "LEGAL_REVIEW_RECOMMENDED"
    if band == "HIGH":
        posture = "HOLD_ACTION_PENDING_REVIEW"
    elif band in {"MEDIUM", "LOW"}:
        posture = "LEGAL_REVIEW_RECOMMENDED"

    posture = _bounded_posture(posture)

    if not recommended_next_step.strip():
        recommended_next_step = (
            "Assessment is probabilistic and bounded; operator judgment applies. "
            "Recommend reviewing account file, verifying jurisdiction, and confirming evidentiary posture "
            "before any escalation."
        )

    snapshot: Dict[str, Any] = {
        "generated_at_utc": _utc_now_iso(),
        "safe_notice": synthetic_notice,
        "domain": "LEGAL",
        "product": "legal_case_snapshot",
        "inputs": {
            "case_type": case_type_s,
            "matter_name": matter_name_s,
            "debtor_or_defendant": debtor_s,
            "jurisdiction": juris_s,
            "stage": stage_s,
            "days_past_due": dpd,
            "balance_usd": bal,
            "risk_score": rscore,
            "red_flags": flags,
        },
        "assessment": {
            "risk_band": band,
            "recommended_posture": posture,
            "recommended_next_step": recommended_next_step,
            "ambiguity_flags": ambiguity,
        },
        "what_we_can_say": [
            "This is a training/demo artifact derived from synthetic inputs.",
            f"Risk band is {band} (bounded).",
            f"Recommended posture is {posture} (bounded).",
            "Operator judgment applies; consult counsel before escalation.",
        ],
        "what_we_cannot_say": [
            "We do not infer real-world intent, liability, or outcome from this snapshot.",
            "We do not provide legal advice; this is an analytic training aid only.",
        ],
    }

    return snapshot

def _render_txt(snapshot: Dict[str, Any]) -> str:
    inp = snapshot.get("inputs", {}) or {}
    a = snapshot.get("assessment", {}) or {}
    flags = a.get("ambiguity_flags", []) or []

    lines = [
        "LEGAL CASE SNAPSHOT (DEMO / TRAINING)",
        f"generated_at_utc: {snapshot.get('generated_at_utc', '')}",
        "",
        f"Matter: {inp.get('matter_name', 'Demo Matter')}",
        f"Type: {inp.get('case_type', 'COLLECTIONS')} | Stage: {inp.get('stage', 'PRE-SUIT')}",
        f"Party: {inp.get('debtor_or_defendant', 'UNKNOWN')} | Jurisdiction: {inp.get('jurisdiction', 'UNKNOWN')}",
        f"Days Past Due: {inp.get('days_past_due', None)} | Balance (USD): {inp.get('balance_usd', None)}",
        f"Risk Score: {inp.get('risk_score', None)} | Risk Band: {a.get('risk_band', 'UNKNOWN')}",
        "",
        f"Recommended posture: {a.get('recommended_posture', 'LEGAL_REVIEW_RECOMMENDED')}",
        f"Next step: {a.get('recommended_next_step', 'Operator judgment applies.')}",
        "",
        "Ambiguity flags:",
    ]
    if flags:
        for f in flags:
            lines.append(f"- {f}")
    else:
        lines.append("- None")

    lines.append("")
    lines.append("NOTICE: Assessment is probabilistic and bounded; operator judgment applies.")
    return "\n".join(lines)

def write_legal_case_snapshot(snapshot: Dict[str, Any]) -> Dict[str, str]:
    """
    Write standard latest + stamped AND legacy src/docs copies.
    """

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LEGACY_DIR.mkdir(parents=True, exist_ok=True)

    stamped_json = OUT_DIR / f"legal_case_snapshot_{_stamp()}.json"
    stamped_txt = OUT_DIR / f"legal_case_snapshot_{_stamp()}.txt"

    txt = _render_txt(snapshot)

    # Standard (repo-friendly)
    LATEST_JSON.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    LATEST_TXT.write_text(txt, encoding="utf-8")
    stamped_json.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    stamped_txt.write_text(txt, encoding="utf-8")

    # Legacy (backward compatible)
    legacy_json = LEGACY_DIR / "legal_case_snapshot.json"
    legacy_txt = LEGACY_DIR / "legal_case_snapshot.txt"
    legacy_json.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    legacy_txt.write_text(txt, encoding="utf-8")

    return {
        "json_latest": str(LATEST_JSON),
        "txt_latest": str(LATEST_TXT),
        "json_stamped": str(stamped_json),
        "txt_stamped": str(stamped_txt),
        "legacy_json": str(legacy_json),
        "legacy_txt": str(legacy_txt),
    }

def main() -> int:
    # Sensible demo defaults (collections)
    snap = build_legal_case_snapshot(
        case_type="COLLECTIONS",
        matter_name="Code 116 Collections Demo",
        debtor_or_defendant="JOHN DOE (Synthetic)",
        jurisdiction="GA",
        stage="DEMAND LETTER",
        days_past_due=62,
        balance_usd=3487.22,
        risk_score=57,
        red_flags=["Partial payment history", "Address mismatch"],
        recommended_next_step="Send demand letter + validate debtor identity; prep suit package if non-response in 10–14 days.",
    )
    paths = write_legal_case_snapshot(snap)
    print(json.dumps(paths, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

