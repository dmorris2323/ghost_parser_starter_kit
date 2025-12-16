# src/week3_operator_summary.py
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


IN_PATH = Path("docs") / "validation" / "fusion_core_regression_latest.json"
OUT_DIR = Path("docs") / "briefs"
OUT_LATEST = OUT_DIR / "week3_operator_summary_latest.txt"


@dataclass(frozen=True)
class SummaryResult:
    verdict: str
    txt_latest: str
    txt_stamped: str


def _utc_now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json_best_effort(path: Path) -> Optional[Dict[str, Any]]:
    try:
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _safe_get(d: Optional[Dict[str, Any]], key: str, default: Any = None) -> Any:
    if not isinstance(d, dict):
        return default
    return d.get(key, default)


def _as_str(val: Any, default: str = "") -> str:
    try:
        if val is None:
            return default
        s = str(val)
        return s if s.strip() else default
    except Exception:
        return default


def _build_validated_list(report: Optional[Dict[str, Any]]) -> list[str]:
    """
    Best-effort inference of what's validated based on the gate JSON shape.
    Never fails; never speculates.
    """
    items: list[str] = []
    checks = _safe_get(report, "checks", {})
    if isinstance(checks, dict):
        for k, v in checks.items():
            # The gate seems to record PASS/FAIL per check; accept strings or dicts.
            status = None
            if isinstance(v, str):
                status = v
            elif isinstance(v, dict):
                status = v.get("status") or v.get("verdict") or v.get("ok")
            status_s = _as_str(status, "").upper()

            if status_s == "PASS" or status is True:
                # Map known keys to operator-friendly phrases
                if "FUSION_VALIDATION" in k:
                    items.append("Fusion validation (core pipeline validated)")
                elif "DEGRADED_FUSION_VALIDATION" in k:
                    items.append("Degraded fusion validation (bounded behavior under degraded ops)")
                elif "COMMANDER_BRIEF" in k:
                    items.append("Commander brief generation (best-effort briefing output)")
                elif "BASEDEF_SENSOR_OUTAGE" in k:
                    items.append("Base Defense: Sensor Outage Predictor artifact intact")
                elif "BASEDEF_INSTALLATION_THREAT_MAP" in k:
                    items.append("Base Defense: Installation Threat Map artifact intact")
                elif "BASEDEF_PERIMETER_INCIDENT" in k:
                    items.append("Base Defense: Perimeter Incident Report artifact intact")
                elif "BASEDEF_STORYBOARD" in k:
                    items.append("Base Defense: Base Defense Storyboard artifact intact")
                elif "GATES_PRE" in k:
                    items.append("Integrity gates PRE (SIS/SPS produced)")
                elif "GATES_POST" in k:
                    items.append("Integrity gates POST (SIS/SPS produced)")
                else:
                    items.append(f"{k} (PASS)")

    # De-dup while preserving order
    seen = set()
    deduped: list[str] = []
    for it in items:
        if it not in seen:
            seen.add(it)
            deduped.append(it)
    return deduped


def _render_summary(report: Optional[Dict[str, Any]]) -> tuple[str, str]:
    """
    Returns (verdict, text_summary). Never crashes.
    """
    # Default conservative posture if anything is missing
    verdict = "UNKNOWN"
    try:
        v = _safe_get(report, "verdict", None)
        if isinstance(v, str) and v.strip():
            verdict = v.strip().upper()
    except Exception:
        verdict = "UNKNOWN"

    crashes = _safe_get(report, "crashes", None)
    crashes_s = ""
    try:
        if isinstance(crashes, int):
            crashes_s = str(crashes)
        elif crashes is not None:
            crashes_s = _as_str(crashes, "")
    except Exception:
        crashes_s = ""

    generated_at = _as_str(_safe_get(report, "generated_at_utc", None), "")
    if not generated_at:
        generated_at = _utc_now_iso()

    validated = _build_validated_list(report)

    # Commander-safe, bounded language (no speculation)
    lines: list[str] = []
    lines.append("WEEK-3 OPERATOR SUMMARY")
    lines.append(f"generated_at_utc: {generated_at}")
    if crashes_s:
        lines.append(f"crashes: {crashes_s}")
    lines.append("")
    lines.append(f"Overall Status: {verdict}")
    lines.append("")

    lines.append("Validated (best-effort):")
    if validated:
        for it in validated[:12]:
            lines.append(f"- {it}")
    else:
        lines.append("- No validated items could be confirmed (artifact missing or unreadable).")
    lines.append("")

    lines.append("Did NOT Observe (bounded claims):")
    if verdict == "PASS":
        lines.append("- No gate-reported crashes in the regression run.")
        lines.append("- No missing required artifacts reported by the regression gate.")
        lines.append("- No unbounded escalation beyond defined postures reported by this gate.")
    else:
        lines.append("- Cannot assert absence of failure modes because overall status is not PASS.")
        lines.append("- Treat outputs as provisional until regression gate is PASS.")
    lines.append("")

    lines.append("Unknowns / Requires Judgment:")
    lines.append("- Synthetic / training artifacts only (no live adversary telemetry implied).")
    lines.append("- Intent, causality, and attribution are not inferred from these products.")
    lines.append("- Operator judgment is required before escalation beyond DUTY_OFFICER_NOTIFY.")
    lines.append("")

    lines.append("Recommended Operator Posture:")
    if verdict == "PASS":
        lines.append("CONTINUE HARDENING (safe to proceed to next Week-3 module).")
    elif verdict == "FAIL":
        lines.append("HOLD (fix regression failures before advancing).")
    else:
        lines.append("HOLD (unable to confirm regression status).")

    return verdict, "\n".join(lines).rstrip() + "\n"


def write_week3_operator_summary() -> SummaryResult:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    report = _read_json_best_effort(IN_PATH)
    verdict, text = _render_summary(report)

    stamped = OUT_DIR / f"week3_operator_summary_{_utc_now_stamp()}.txt"

    # Best-effort writes (never crash)
    try:
        OUT_LATEST.write_text(text, encoding="utf-8")
    except Exception:
        pass
    try:
        stamped.write_text(text, encoding="utf-8")
    except Exception:
        pass

    return SummaryResult(
        verdict=verdict,
        txt_latest=str(OUT_LATEST),
        txt_stamped=str(stamped),
    )


def main() -> int:
    res = write_week3_operator_summary()
    # Keep CLI output machine-friendly
    print(
        json.dumps(
            {
                "verdict": res.verdict,
                "txt_latest": res.txt_latest,
                "txt_stamped": res.txt_stamped,
                "source_json": str(IN_PATH),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

