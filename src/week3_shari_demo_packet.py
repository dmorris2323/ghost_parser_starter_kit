from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

# Demo lock (must be present in your repo from prior modules)
from demo_lock import is_demo_locked, demo_lock_banner, enforce_demo_lock

BRIEFS_DIR = Path("docs") / "briefs"
VALIDATION_DIR = Path("docs") / "validation"

# Core demo artifacts (best effort)
P_COMMANDER_TXT = BRIEFS_DIR / "commander_brief_latest.txt"
P_COMMANDER_JSON = BRIEFS_DIR / "commander_brief_latest.json"
P_OPERATOR_SUMMARY = BRIEFS_DIR / "week3_operator_summary_latest.txt"
P_LEGAL_TXT = BRIEFS_DIR / "legal_case_snapshot_latest.txt"
P_LEGAL_JSON = BRIEFS_DIR / "legal_case_snapshot_latest.json"
P_NARRATIVE = BRIEFS_DIR / "week3_demo_narrative_latest.txt"
P_MOBILE_MANIFEST = BRIEFS_DIR / "mobile_enjoy_manifest_latest.json"

P_READINESS_TXT = VALIDATION_DIR / "week3_demo_readiness_gate_latest.txt"
P_READINESS_JSON = VALIDATION_DIR / "week3_demo_readiness_gate_latest.json"
P_REGRESSION_TXT = VALIDATION_DIR / "fusion_core_regression_latest.txt"
P_REGRESSION_JSON = VALIDATION_DIR / "fusion_core_regression_latest.json"
P_DEMO_PACK = VALIDATION_DIR / "week3_demo_pack_gate_latest.json"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _read_txt_best_effort(p: Path, max_chars: int = 8000) -> Optional[str]:
    try:
        if not p.exists():
            return None
        txt = p.read_text(encoding="utf-8", errors="replace")
        return txt[:max_chars]
    except Exception:
        return None


def _read_json_best_effort(p: Path) -> Optional[dict]:
    try:
        if not p.exists():
            return None
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _present(p: Path) -> bool:
    try:
        return p.exists()
    except Exception:
        return False


def build_demo_packet(context: str = "week3_shari_demo_packet") -> Dict[str, Any]:
    """
    Produce a Shari-friendly demo packet (text + json manifest).
    Must never crash.
    """
    generated_at_utc = _utc_now_iso()

    # Best-effort reads for previews
    commander_head = _read_txt_best_effort(P_COMMANDER_TXT, max_chars=1400) or ""
    legal_head = _read_txt_best_effort(P_LEGAL_TXT, max_chars=1400) or ""
    op_sum = _read_txt_best_effort(P_OPERATOR_SUMMARY, max_chars=1200) or ""
    narrative = _read_txt_best_effort(P_NARRATIVE, max_chars=1600) or ""
    readiness_txt = _read_txt_best_effort(P_READINESS_TXT, max_chars=1600) or ""
    regression_txt = _read_txt_best_effort(P_REGRESSION_TXT, max_chars=1600) or ""

    # Presence map (truth source)
    presence = {
        "commander_brief_latest.txt": {"path": str(P_COMMANDER_TXT), "present": _present(P_COMMANDER_TXT)},
        "commander_brief_latest.json": {"path": str(P_COMMANDER_JSON), "present": _present(P_COMMANDER_JSON)},
        "week3_operator_summary_latest.txt": {"path": str(P_OPERATOR_SUMMARY), "present": _present(P_OPERATOR_SUMMARY)},
        "legal_case_snapshot_latest.txt": {"path": str(P_LEGAL_TXT), "present": _present(P_LEGAL_TXT)},
        "legal_case_snapshot_latest.json": {"path": str(P_LEGAL_JSON), "present": _present(P_LEGAL_JSON)},
        "week3_demo_narrative_latest.txt": {"path": str(P_NARRATIVE), "present": _present(P_NARRATIVE)},
        "mobile_enjoy_manifest_latest.json": {"path": str(P_MOBILE_MANIFEST), "present": _present(P_MOBILE_MANIFEST)},
        "week3_demo_readiness_gate_latest.txt": {"path": str(P_READINESS_TXT), "present": _present(P_READINESS_TXT)},
        "week3_demo_readiness_gate_latest.json": {"path": str(P_READINESS_JSON), "present": _present(P_READINESS_JSON)},
        "fusion_core_regression_latest.txt": {"path": str(P_REGRESSION_TXT), "present": _present(P_REGRESSION_TXT)},
        "fusion_core_regression_latest.json": {"path": str(P_REGRESSION_JSON), "present": _present(P_REGRESSION_JSON)},
        "week3_demo_pack_gate_latest.json": {"path": str(P_DEMO_PACK), "present": _present(P_DEMO_PACK)},
    }

    missing = [k for k, v in presence.items() if not (isinstance(v, dict) and v.get("present") is True)]

    # Build a clean, Shari-safe “demo flow” (bounded language)
    demo_flow = [
        "1) Open the GUI (Command Center).",
        "2) Read the Commander Brief (bounded, commander-safe).",
        "3) Show the Legal Case Snapshot (Shari hook).",
        "4) Show Operator Summary (PASS in 10 seconds).",
        "5) Show Readiness Gate (proof of demo-lock + presence checks).",
        "6) Optional: Mobile Enjoy Manifest (read-only paths for phone viewing).",
        "",
        "Reminder: Assessment is probabilistic and bounded; operator judgment applies.",
    ]

    talking_points = [
        "GLL is built to survive missing inputs — outputs stay bounded and readable.",
        "Every demo artifact is written to standardized locations (latest + stamped).",
        "Demo Lock prevents mutation/training/baseline updates (read-only safety).",
        "Gates prove integrity (SIS/SPS) and readiness (presence + lock markers).",
    ]

    packet: Dict[str, Any] = {
        "generated_at_utc": generated_at_utc,
        "context": context,
        "verdict": "PASS" if len(missing) == 0 else "WARN",
        "missing": missing,
        "presence": presence,
        "demo_flow": demo_flow,
        "talking_points": talking_points,
        "previews": {
            "commander_brief_head": commander_head.strip(),
            "legal_case_snapshot_head": legal_head.strip(),
            "operator_summary": op_sum.strip(),
            "demo_narrative": narrative.strip(),
            "readiness_gate_head": readiness_txt.strip(),
            "fusion_core_regression_head": regression_txt.strip(),
        },
        "notes": [
            "Commander-safe phrasing only. No attribution. No intent claims.",
            "Outputs are bounded; demo is stable without perfect inputs.",
        ],
    }

    # Enforce demo lock in the packet manifest (never mutate anything)
    if is_demo_locked():
        packet["demo_notice"] = demo_lock_banner()
        packet.update(enforce_demo_lock(context))

    return packet


def write_demo_packet(packet: Dict[str, Any]) -> Dict[str, str]:
    _ensure_dir(BRIEFS_DIR)

    stamped = _stamp()
    latest_txt = BRIEFS_DIR / "week3_shari_demo_packet_latest.txt"
    latest_json = BRIEFS_DIR / "week3_shari_demo_packet_latest.json"
    stamped_txt = BRIEFS_DIR / f"week3_shari_demo_packet_{stamped}.txt"
    stamped_json = BRIEFS_DIR / f"week3_shari_demo_packet_{stamped}.json"

    # TXT (Shari-friendly)
    lines = []
    lines.append("WEEK-3 SHARI DEMO PACKET (READ-ONLY / DEMO)")
    lines.append(f"generated_at_utc: {packet.get('generated_at_utc', 'UNKNOWN')}")
    lines.append(f"verdict: {packet.get('verdict', 'UNKNOWN')}")
    lines.append("")
    lines.append("DEMO FLOW (show in this order):")
    for s in packet.get("demo_flow", []):
        lines.append(f"- {s}")
    lines.append("")
    lines.append("TALKING POINTS:")
    for t in packet.get("talking_points", []):
        lines.append(f"- {t}")
    lines.append("")
    lines.append("KEY ARTIFACT PATHS:")
    presence = packet.get("presence", {}) if isinstance(packet.get("presence", {}), dict) else {}
    for k, v in presence.items():
        if isinstance(v, dict):
            lines.append(f"- {k}: {v.get('path')} (present={v.get('present')})")
    if packet.get("missing"):
        lines.append("")
        lines.append("MISSING (non-fatal for demo, but fix before live briefing):")
        for m in packet.get("missing", []):
            lines.append(f"- {m}")

    if is_demo_locked():
        lines.append("")
        lines.append(demo_lock_banner())

    txt = "\n".join(lines).strip() + "\n"
    latest_txt.write_text(txt, encoding="utf-8")
    stamped_txt.write_text(txt, encoding="utf-8")

    # JSON manifest
    latest_json.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    stamped_json.write_text(json.dumps(packet, indent=2), encoding="utf-8")

    return {
        "txt_latest": str(latest_txt),
        "json_latest": str(latest_json),
        "txt_stamped": str(stamped_txt),
        "json_stamped": str(stamped_json),
    }


def main() -> int:
    packet = build_demo_packet()
    paths = write_demo_packet(packet)
    print(json.dumps(paths, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

