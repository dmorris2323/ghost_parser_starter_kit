from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Optional: demo lock module (best-effort import)
try:
    from demo_lock import is_demo_locked, demo_lock_banner
except Exception:  # pragma: no cover
    def is_demo_locked() -> bool:
        return False

    def demo_lock_banner() -> str:
        return "DEMO MODE ACTIVE — READ ONLY\nAssessment is probabilistic and bounded; operator judgment applies."


BRIEFS_DIR = Path("docs") / "briefs"
VALIDATION_DIR = Path("docs") / "validation"

# Expected artifacts (presence-only, best-effort)
A_COMMANDER_BRIEF_TXT = BRIEFS_DIR / "commander_brief_latest.txt"
A_COMMANDER_BRIEF_JSON = BRIEFS_DIR / "commander_brief_latest.json"
A_OPERATOR_SUMMARY_TXT = BRIEFS_DIR / "week3_operator_summary_latest.txt"
A_LEGAL_TXT = BRIEFS_DIR / "legal_case_snapshot_latest.txt"
A_LEGAL_JSON = BRIEFS_DIR / "legal_case_snapshot_latest.json"
A_MOBILE_MANIFEST = BRIEFS_DIR / "mobile_enjoy_manifest_latest.json"
A_DEMO_NARRATIVE = BRIEFS_DIR / "week3_demo_narrative_latest.txt"

A_FUSION_CORE_TXT = VALIDATION_DIR / "fusion_core_regression_latest.txt"
A_FUSION_CORE_JSON = VALIDATION_DIR / "fusion_core_regression_latest.json"
A_DEMO_PACK_GATE = VALIDATION_DIR / "week3_demo_pack_gate_latest.json"
A_DEMO_READINESS_TXT = VALIDATION_DIR / "week3_demo_readiness_gate_latest.txt"
A_DEMO_READINESS_JSON = VALIDATION_DIR / "week3_demo_readiness_gate_latest.json"

# Scripts we can run (best-effort)
S_COMMAND_BRIEF = Path("src") / "command_brief_exporter.py"
S_OPERATOR_SUMMARY = Path("src") / "week3_operator_summary.py"
S_LEGAL_SNAPSHOT = Path("src") / "legal_case_snapshot.py"
S_DEMO_READINESS_GATE = Path("src") / "week3_demo_readiness_gate.py"

# Optional / may not exist in every branch
S_DEMO_NARRATIVE = Path("src") / "week3_demo_narrative.py"
S_MOBILE_ENJOY_MODE = Path("src") / "mobile_enjoy_mode.py"
S_DEMO_PACK_GATE = Path("src") / "week3_demo_pack_gate.py"
S_FUSION_CORE_REGRESSION_GATE = Path("src") / "gll_fusion_core_regression_gate.py"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _read_text_head(path: Path, max_lines: int = 40) -> str:
    try:
        if not path.exists():
            return "MISSING"
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(lines[:max_lines]).strip() or "EMPTY"
    except Exception as e:
        return f"UNREADABLE:{type(e).__name__}:{e}"


def _read_json_best_effort(path: Path) -> Optional[dict]:
    try:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def _write_text(path: Path, text: str) -> None:
    _ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, obj: Any) -> None:
    _ensure_dir(path.parent)
    # harden against non-serializable objects
    def _default(o: Any) -> str:
        return f"<non_serializable:{type(o).__name__}>"

    path.write_text(json.dumps(obj, indent=2, default=_default), encoding="utf-8")


@dataclass
class RunResult:
    ok: bool
    returncode: int
    stdout: str
    stderr: str
    note: str


def _run_script_best_effort(script_path: Path, note: str) -> RunResult:
    """
    Runs: python <script>
    Never raises; always returns a structured result.
    """
    if not script_path.exists():
        return RunResult(
            ok=False,
            returncode=127,
            stdout="",
            stderr="",
            note=f"{note}:SKIP (missing {script_path})",
        )

    try:
        cp = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        ok = (cp.returncode == 0)
        return RunResult(
            ok=ok,
            returncode=cp.returncode,
            stdout=(cp.stdout or "").strip(),
            stderr=(cp.stderr or "").strip(),
            note=f"{note}:{'OK' if ok else 'FAIL'}",
        )
    except Exception as e:
        return RunResult(
            ok=False,
            returncode=1,
            stdout="",
            stderr=f"{type(e).__name__}:{e}",
            note=f"{note}:CRASH",
        )


def _presence(path: Path) -> Dict[str, Any]:
    return {
        "path": str(path),
        "present": bool(path.exists()),
    }


def run_week3_shari_demo_packet(strict: bool = True) -> Dict[str, Any]:
    """
    One-button packet builder for Shari demo.
    - Regenerates key artifacts (best-effort)
    - Runs readiness gate
    - Writes checklist + packet json
    Never crashes.
    """
    generated_at = _utc_now_iso()
    stamp = _stamp()

    # 1) Best-effort regen (do NOT assume every script exists)
    runs: List[Dict[str, Any]] = []
    for script, label in [
        (S_FUSION_CORE_REGRESSION_GATE, "fusion_core_regression_gate"),
        (S_COMMAND_BRIEF, "commander_brief_exporter"),
        (S_OPERATOR_SUMMARY, "week3_operator_summary"),
        (S_LEGAL_SNAPSHOT, "legal_case_snapshot"),
        (S_DEMO_NARRATIVE, "week3_demo_narrative"),
        (S_DEMO_PACK_GATE, "week3_demo_pack_gate"),
        (S_MOBILE_ENJOY_MODE, "mobile_enjoy_mode"),
    ]:
        rr = _run_script_best_effort(script, label)
        runs.append(
            {
                "label": label,
                "script": str(script),
                "ok": rr.ok,
                "returncode": rr.returncode,
                "note": rr.note,
                "stdout_tail": rr.stdout[-700:] if rr.stdout else "",
                "stderr_tail": rr.stderr[-700:] if rr.stderr else "",
            }
        )

    # 2) Run readiness gate last (this is the “truth”)
    gate_rr = _run_script_best_effort(S_DEMO_READINESS_GATE, "week3_demo_readiness_gate")
    runs.append(
        {
            "label": "week3_demo_readiness_gate",
            "script": str(S_DEMO_READINESS_GATE),
            "ok": gate_rr.ok,
            "returncode": gate_rr.returncode,
            "note": gate_rr.note,
            "stdout_tail": gate_rr.stdout[-900:] if gate_rr.stdout else "",
            "stderr_tail": gate_rr.stderr[-900:] if gate_rr.stderr else "",
        }
    )

    # 3) Determine verdict from gate JSON if present; else fallback
    gate_json = _read_json_best_effort(A_DEMO_READINESS_JSON) or {}
    verdict = str(gate_json.get("verdict") or ("PASS" if gate_rr.ok else "FAIL"))

    # 4) Build packet payload (presence + previews)
    packet: Dict[str, Any] = {
        "generated_at_utc": generated_at,
        "context": "week3_shari_demo_packet",
        "strict": bool(strict),
        "verdict": verdict,
        "demo_lock": bool(is_demo_locked()),
        "demo_notice": demo_lock_banner() if is_demo_locked() else "",
        "artifacts": {
            "commander_brief_txt": _presence(A_COMMANDER_BRIEF_TXT),
            "commander_brief_json": _presence(A_COMMANDER_BRIEF_JSON),
            "week3_operator_summary_txt": _presence(A_OPERATOR_SUMMARY_TXT),
            "legal_case_snapshot_txt": _presence(A_LEGAL_TXT),
            "legal_case_snapshot_json": _presence(A_LEGAL_JSON),
            "mobile_enjoy_manifest": _presence(A_MOBILE_MANIFEST),
            "week3_demo_narrative_txt": _presence(A_DEMO_NARRATIVE),
            "fusion_core_regression_txt": _presence(A_FUSION_CORE_TXT),
            "fusion_core_regression_json": _presence(A_FUSION_CORE_JSON),
            "week3_demo_pack_gate": _presence(A_DEMO_PACK_GATE),
            "week3_demo_readiness_txt": _presence(A_DEMO_READINESS_TXT),
            "week3_demo_readiness_json": _presence(A_DEMO_READINESS_JSON),
        },
        "previews": {
            "operator_summary_head": _read_text_head(A_OPERATOR_SUMMARY_TXT, 25),
            "legal_snapshot_head": _read_text_head(A_LEGAL_TXT, 35),
            "commander_brief_head": _read_text_head(A_COMMANDER_BRIEF_TXT, 45),
            "demo_narrative_head": _read_text_head(A_DEMO_NARRATIVE, 60),
            "readiness_gate_head": _read_text_head(A_DEMO_READINESS_TXT, 60),
        },
        "runs": runs,
        "notes": [
            "Assessment is probabilistic and bounded; operator judgment applies.",
            "This packet is demo-safe and should survive missing inputs.",
        ],
    }

    # 5) Write checklist + packet outputs
    _ensure_dir(BRIEFS_DIR)

    checklist_latest = BRIEFS_DIR / "week3_shari_demo_checklist_latest.txt"
    checklist_stamped = BRIEFS_DIR / f"week3_shari_demo_checklist_{stamp}.txt"
    packet_latest = BRIEFS_DIR / "week3_shari_demo_packet_latest.json"
    packet_stamped = BRIEFS_DIR / f"week3_shari_demo_packet_{stamp}.json"

    checklist_lines: List[str] = []
    checklist_lines.append("WEEK-3 SHARI DEMO CHECKLIST (ONE-BUTTON PACKET)")
    checklist_lines.append(f"generated_at_utc: {generated_at}")
    checklist_lines.append(f"verdict: {verdict}")
    checklist_lines.append("")
    if is_demo_locked():
        checklist_lines.append(demo_lock_banner())
        checklist_lines.append("")

    checklist_lines.append("WHAT TO SHOW (3-minute flow):")
    checklist_lines.append("1) Operator Summary (10 seconds): docs/briefs/week3_operator_summary_latest.txt")
    checklist_lines.append("2) Commander Brief (bounded): docs/briefs/commander_brief_latest.txt")
    checklist_lines.append("3) Legal Snapshot (Shari hook): docs/briefs/legal_case_snapshot_latest.txt")
    checklist_lines.append("4) Demo Narrative (optional): docs/briefs/week3_demo_narrative_latest.txt")
    checklist_lines.append("5) Proof: Demo Readiness Gate: docs/validation/week3_demo_readiness_gate_latest.txt")
    checklist_lines.append("")
    checklist_lines.append("PRESENCE CHECKS:")
    for k, meta in packet["artifacts"].items():
        checklist_lines.append(f"- {k}: {'OK' if meta.get('present') else 'MISSING'} ({meta.get('path')})")

    checklist_text = "\n".join(checklist_lines).strip() + "\n"

    _write_text(checklist_latest, checklist_text)
    _write_text(checklist_stamped, checklist_text)
    _write_json(packet_latest, packet)
    _write_json(packet_stamped, packet)

    # also include written paths in the returned dict
    packet["outputs"] = {
        "checklist_latest": str(checklist_latest),
        "checklist_stamped": str(checklist_stamped),
        "packet_latest": str(packet_latest),
        "packet_stamped": str(packet_stamped),
    }

    return packet


def main() -> int:
    res = run_week3_shari_demo_packet(strict=True)
    print(json.dumps(res.get("outputs", {}), indent=2))
    print(f"Verdict: {res.get('verdict')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

