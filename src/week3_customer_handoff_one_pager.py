# src/week3_customer_handoff_one_pager.py
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]

BRIEFS_DIR = ROOT / "docs" / "briefs"
VALIDATION_DIR = ROOT / "docs" / "validation"
PACKAGES_DIR = ROOT / "docs" / "packages"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _read_text_best_effort(p: Path) -> Optional[str]:
    try:
        if not p.exists():
            return None
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None


def _read_json_best_effort(p: Path) -> Optional[dict]:
    try:
        if not p.exists():
            return None
        return json.loads(p.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def _tail_lines(text: str, n: int = 80) -> str:
    lines = (text or "").splitlines()
    if len(lines) <= n:
        return "\n".join(lines)
    return "\n".join(lines[-n:])


def _demo_lock_state() -> Dict[str, Any]:
    """
    Best-effort demo lock state (never crashes).
    """
    state: Dict[str, Any] = {"module_present": False, "demo_locked": False, "banner": None}
    try:
        # If your demo_lock module exists, use it.
        from demo_lock import is_demo_locked, demo_lock_banner  # type: ignore

        state["module_present"] = True
        state["demo_locked"] = bool(is_demo_locked())
        if state["demo_locked"]:
            state["banner"] = str(demo_lock_banner())
        return state
    except Exception:
        return state


def write_week3_customer_handoff_one_pager(
    context: str = "week3_customer_handoff_one_pager",
) -> Dict[str, Any]:
    """
    Generates a commander-safe, customer-facing handoff one-pager for Week-3 demo packaging.
    Writes:
      - docs/packages/week3_customer_handoff_one_pager_latest.md
      - docs/packages/week3_customer_handoff_one_pager_latest.txt
      - stamped versions
    Must never crash.
    """
    PACKAGES_DIR.mkdir(parents=True, exist_ok=True)

    demo_lock = _demo_lock_state()

    # Canonical Week-3 demo artifacts (best effort)
    p_orchestrator = BRIEFS_DIR / "week3_demo_orchestrator_latest.json"
    p_readiness = VALIDATION_DIR / "week3_demo_readiness_gate_latest.json"
    p_mobile_manifest = BRIEFS_DIR / "mobile_enjoy_manifest_latest.json"
    p_operator_summary = BRIEFS_DIR / "week3_operator_summary_latest.txt"
    p_legal_txt = BRIEFS_DIR / "legal_case_snapshot_latest.txt"
    p_legal_json = BRIEFS_DIR / "legal_case_snapshot_latest.json"
    p_commander_txt = BRIEFS_DIR / "commander_brief_latest.txt"
    p_commander_json = BRIEFS_DIR / "commander_brief_latest.json"
    p_demo_narrative_txt = BRIEFS_DIR / "week3_demo_narrative_latest.txt"
    p_demo_narrative_json = BRIEFS_DIR / "week3_demo_narrative_latest.json"
    p_fusion_reg_json = VALIDATION_DIR / "fusion_core_regression_latest.json"
    p_fusion_reg_txt = VALIDATION_DIR / "fusion_core_regression_latest.txt"
    p_demo_pack_gate = VALIDATION_DIR / "week3_demo_pack_gate_latest.json"

    # Optional operator log
    p_notes = ROOT / "NOTES.txt"

    orchestrator = _read_json_best_effort(p_orchestrator) or {}
    readiness = _read_json_best_effort(p_readiness) or {}
    mobile_manifest = _read_json_best_effort(p_mobile_manifest) or {}
    legal_json = _read_json_best_effort(p_legal_json) or {}
    commander_json = _read_json_best_effort(p_commander_json) or {}
    demo_narrative_json = _read_json_best_effort(p_demo_narrative_json) or {}

    notes_tail = None
    notes_txt = _read_text_best_effort(p_notes)
    if notes_txt:
        notes_tail = _tail_lines(notes_txt, n=120)

    # Safe fields
    orchestrator_verdict = orchestrator.get("verdict", "UNKNOWN")
    readiness_verdict = readiness.get("verdict", "UNKNOWN")
    demo_pack_verdict = (_read_json_best_effort(p_demo_pack_gate) or {}).get("verdict", "UNKNOWN")

    commander_posture = None
    try:
        commander_posture = (commander_json.get("sections") or {}).get("recommended_posture")
    except Exception:
        commander_posture = None

    legal_posture = legal_json.get("recommended_posture")

    # IMPORTANT: valuation/revenue are NOT asserted as facts here. This is a handoff doc.
    valuation_note = (
        "Valuation: Internal working estimate only (non-financial, non-binding). "
        "Do not represent as audited or market-validated."
    )

    # Build one-pager content (MD + TXT)
    generated = _utc_now_iso()
    stamp = _stamp()

    md_lines = []
    md_lines.append("# GLL Week-3 Demo — Customer Handoff (One-Pager)")
    md_lines.append("")
    md_lines.append(f"- generated_at_utc: `{generated}`")
    md_lines.append(f"- context: `{context}`")
    md_lines.append("")
    md_lines.append("## 1) What this is")
    md_lines.append(
        "A **demo-safe, read-only** package of Ghost Lantern Labs (GLL) Week-3 artifacts designed for a short stakeholder demo: "
        "commander brief, operator summary, legal snapshot (“Shari Hook”), readiness gates, and a mobile manifest."
    )
    md_lines.append("")
    md_lines.append("## 2) Demo safety and constraints")
    if demo_lock.get("demo_locked"):
        md_lines.append("✅ **DEMO MODE ACTIVE (READ ONLY)**")
        md_lines.append("")
        md_lines.append("```")
        md_lines.append(demo_lock.get("banner") or "DEMO MODE ACTIVE — READ ONLY")
        md_lines.append("```")
    else:
        md_lines.append("⚠️ Demo lock not detected. If this is for a stakeholder demo, enable demo lock before presenting.")
    md_lines.append("")
    md_lines.append("## 3) Current demo status (best effort)")
    md_lines.append(f"- Orchestrator verdict: **{orchestrator_verdict}**")
    md_lines.append(f"- Readiness gate verdict: **{readiness_verdict}**")
    md_lines.append(f"- Demo pack gate verdict: **{demo_pack_verdict}**")
    if commander_posture:
        md_lines.append(f"- Commander recommended posture (from brief): **{commander_posture}**")
    if legal_posture:
        md_lines.append(f"- Legal snapshot recommended posture: **{legal_posture}**")
    md_lines.append("")
    md_lines.append("## 4) What to show in the demo (2–5 minutes)")
    md_lines.append("1. **Week-3 demo narrative** (sets expectations and scope).")
    md_lines.append("2. **Commander brief (bounded, safe language)** — what changed / why it matters / what we know / what we don’t.")
    md_lines.append("3. **Legal case snapshot (“Shari Hook”)** — fast hook she understands instantly.")
    md_lines.append("4. **Operator summary** — 10-second PASS signal.")
    md_lines.append("5. **Readiness gate** — shows we do not demo if a required marker is missing.")
    md_lines.append("")
    md_lines.append("## 5) How to run (local)")
    md_lines.append("From repo root:")
    md_lines.append("")
    md_lines.append("```bash")
    md_lines.append("python src/week3_demo_orchestrator.py")
    md_lines.append("cat docs/briefs/week3_shari_demo_packet_latest.txt")
    md_lines.append("cat docs/briefs/commander_brief_latest.txt | head -n 60")
    md_lines.append("cat docs/briefs/legal_case_snapshot_latest.txt")
    md_lines.append("```")
    md_lines.append("")
    md_lines.append("Optional mobile-friendly bundle paths:")
    md_lines.append("")
    md_lines.append("```bash")
    md_lines.append("cat docs/briefs/mobile_enjoy_manifest_latest.json")
    md_lines.append("```")
    md_lines.append("")
    md_lines.append("## 6) What’s included (key files)")
    md_lines.append("")
    def _present(p: Path) -> str:
        return "OK" if p.exists() else "MISSING"

    table = [
        ("week3_demo_orchestrator_latest.json", str(p_orchestrator.relative_to(ROOT)), _present(p_orchestrator)),
        ("week3_demo_readiness_gate_latest.json", str(p_readiness.relative_to(ROOT)), _present(p_readiness)),
        ("mobile_enjoy_manifest_latest.json", str(p_mobile_manifest.relative_to(ROOT)), _present(p_mobile_manifest)),
        ("commander_brief_latest.txt", str(p_commander_txt.relative_to(ROOT)), _present(p_commander_txt)),
        ("legal_case_snapshot_latest.txt", str(p_legal_txt.relative_to(ROOT)), _present(p_legal_txt)),
        ("week3_operator_summary_latest.txt", str(p_operator_summary.relative_to(ROOT)), _present(p_operator_summary)),
        ("week3_demo_narrative_latest.txt", str(p_demo_narrative_txt.relative_to(ROOT)), _present(p_demo_narrative_txt)),
        ("fusion_core_regression_latest.txt", str(p_fusion_reg_txt.relative_to(ROOT)), _present(p_fusion_reg_txt)),
    ]
    md_lines.append("| Item | Path | Present |")
    md_lines.append("|---|---|---|")
    for name, path, pres in table:
        md_lines.append(f"| {name} | `{path}` | {pres} |")
    md_lines.append("")
    md_lines.append("## 7) Contractor framing (plain English)")
    md_lines.append("- You are looking at a **prototype ISR/cyber-fusion style reporting stack** adapted for a legal demo hook.")
    md_lines.append("- Outputs are **bounded** and do not claim real-world attribution from synthetic telemetry.")
    md_lines.append(f"- {valuation_note}")
    md_lines.append("")
    md_lines.append("## 8) Notes (operator tail, best effort)")
    if notes_tail:
        md_lines.append("")
        md_lines.append("```")
        md_lines.append(notes_tail)
        md_lines.append("```")
    else:
        md_lines.append("")
        md_lines.append("_NOTES.txt not present or unreadable._")

    md = "\n".join(md_lines).strip() + "\n"

    # TXT is same content without markdown table formatting quirks
    txt_lines = []
    txt_lines.append("GLL WEEK-3 DEMO — CUSTOMER HANDOFF (ONE-PAGER)")
    txt_lines.append(f"generated_at_utc: {generated}")
    txt_lines.append(f"context: {context}")
    txt_lines.append("")
    txt_lines.append("WHAT THIS IS:")
    txt_lines.append("Demo-safe, read-only package of Week-3 artifacts for stakeholder demo.")
    txt_lines.append("")
    txt_lines.append("DEMO SAFETY:")
    if demo_lock.get("demo_locked"):
        txt_lines.append("DEMO MODE ACTIVE — READ ONLY")
        txt_lines.append(demo_lock.get("banner") or "")
    else:
        txt_lines.append("DEMO LOCK NOT DETECTED (enable for stakeholder demo).")
    txt_lines.append("")
    txt_lines.append("STATUS (best effort):")
    txt_lines.append(f"- Orchestrator verdict: {orchestrator_verdict}")
    txt_lines.append(f"- Readiness gate verdict: {readiness_verdict}")
    txt_lines.append(f"- Demo pack gate verdict: {demo_pack_verdict}")
    if commander_posture:
        txt_lines.append(f"- Commander posture: {commander_posture}")
    if legal_posture:
        txt_lines.append(f"- Legal snapshot posture: {legal_posture}")
    txt_lines.append("")
    txt_lines.append("DEMO ORDER (2–5 minutes):")
    txt_lines.append("1) Demo narrative")
    txt_lines.append("2) Commander brief (bounded)")
    txt_lines.append("3) Legal snapshot (Shari Hook)")
    txt_lines.append("4) Operator summary")
    txt_lines.append("5) Readiness gate")
    txt_lines.append("")
    txt_lines.append("HOW TO RUN (local):")
    txt_lines.append("python src/week3_demo_orchestrator.py")
    txt_lines.append("cat docs/briefs/week3_shari_demo_packet_latest.txt")
    txt_lines.append("cat docs/briefs/commander_brief_latest.txt | head -n 60")
    txt_lines.append("cat docs/briefs/legal_case_snapshot_latest.txt")
    txt_lines.append("")
    txt_lines.append("KEY FILES:")
    for name, path, pres in table:
        txt_lines.append(f"- {name}: {path} ({pres})")
    txt_lines.append("")
    txt_lines.append("CONTRACTOR FRAMING:")
    txt_lines.append("- Prototype reporting stack. Outputs are bounded; no real-world attribution from synthetic telemetry.")
    txt_lines.append(f"- {valuation_note}")
    txt_lines.append("")
    txt_lines.append("NOTES (tail, best effort):")
    if notes_tail:
        txt_lines.append(notes_tail)
    else:
        txt_lines.append("NOTES.txt not present or unreadable.")
    txt = "\n".join([l for l in txt_lines if l is not None]).strip() + "\n"

    latest_md = PACKAGES_DIR / "week3_customer_handoff_one_pager_latest.md"
    stamped_md = PACKAGES_DIR / f"week3_customer_handoff_one_pager_{stamp}.md"
    latest_txt = PACKAGES_DIR / "week3_customer_handoff_one_pager_latest.txt"
    stamped_txt = PACKAGES_DIR / f"week3_customer_handoff_one_pager_{stamp}.txt"

    # Writes must never crash
    try:
        latest_md.write_text(md, encoding="utf-8")
    except Exception:
        pass
    try:
        stamped_md.write_text(md, encoding="utf-8")
    except Exception:
        pass
    try:
        latest_txt.write_text(txt, encoding="utf-8")
    except Exception:
        pass
    try:
        stamped_txt.write_text(txt, encoding="utf-8")
    except Exception:
        pass

    res: Dict[str, Any] = {
        "generated_at_utc": generated,
        "context": context,
        "demo_lock": demo_lock,
        "orchestrator_verdict": orchestrator_verdict,
        "readiness_verdict": readiness_verdict,
        "demo_pack_verdict": demo_pack_verdict,
        "paths": {
            "latest_md": str(latest_md.relative_to(ROOT)),
            "stamped_md": str(stamped_md.relative_to(ROOT)),
            "latest_txt": str(latest_txt.relative_to(ROOT)),
            "stamped_txt": str(stamped_txt.relative_to(ROOT)),
        },
    }
    return res


def main() -> int:
    out = write_week3_customer_handoff_one_pager()
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

