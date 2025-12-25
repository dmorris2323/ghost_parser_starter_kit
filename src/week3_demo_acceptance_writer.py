from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Tuple


REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
DEMO_DIR = DOCS_DIR / "demo"
VALIDATION_DIR = DOCS_DIR / "validation"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _read_manifest() -> Tuple[Dict[str, Any], str]:
    """
    Prefer loader if available; otherwise read docs/demo/demo_freeze_manifest.json.
    Returns: (manifest, loaded_from)
    """
    # Preferred path: demo_freeze_loader.py if it exists and works
    try:
        from demo_freeze_loader import load_demo_freeze_manifest  # type: ignore

        m = load_demo_freeze_manifest()
        return m, "demo_freeze_loader.load_demo_freeze_manifest()"
    except Exception:
        pass

    # Fallback: read the canonical manifest file directly
    p = DEMO_DIR / "demo_freeze_manifest.json"
    if not p.exists():
        # If the manifest is missing, return a safe default that forces FAIL downstream.
        return {"mode": "UNKNOWN", "demo_safe": False, "required_banner_text": ""}, str(p)

    return json.loads(p.read_text(encoding="utf-8")), str(p)


def _is_demo_safe(m: Dict[str, Any]) -> bool:
    """
    Prefer loader helper if available; otherwise evaluate locally.
    """
    try:
        from demo_freeze_loader import is_demo_safe  # type: ignore

        return bool(is_demo_safe(m))
    except Exception:
        pass

    # Local rule: demo_safe True + mode DEMO_FREEZE + banner present
    return bool(m.get("demo_safe") is True) and str(m.get("mode", "")).strip() == "DEMO_FREEZE" and bool(
        (m.get("required_banner_text") or "").strip()
    )


@dataclass
class AcceptanceResult:
    generated_at_utc: str
    context: str
    verdict: str
    mode: str
    demo_safe: bool
    loaded_from: str
    banner_len: int
    statement_present: bool
    checklist_present: bool

    def to_json(self) -> Dict[str, Any]:
        return {
            "generated_at_utc": self.generated_at_utc,
            "context": self.context,
            "verdict": self.verdict,
            "mode": self.mode,
            "demo_safe": self.demo_safe,
            "loaded_from": self.loaded_from,
            "banner_len": self.banner_len,
            "statement_present": self.statement_present,
            "checklist_present": self.checklist_present,
        }


def run_week3_demo_acceptance_writer() -> Dict[str, Any]:
    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)

    m, loaded_from = _read_manifest()
    mode = str(m.get("mode", "UNKNOWN")).strip()
    demo_safe = _is_demo_safe(m)
    banner_len = len((m.get("required_banner_text") or "").strip())

    statement_present = (DEMO_DIR / "demo_acceptance_statement.txt").exists()
    checklist_present = (DEMO_DIR / "phase_ii_handoff_checklist.txt").exists()

    verdict = "PASS" if (demo_safe and mode == "DEMO_FREEZE" and statement_present and checklist_present) else "FAIL"

    res = AcceptanceResult(
        generated_at_utc=_utc_now_iso(),
        context="week3_demo_acceptance_writer",
        verdict=verdict,
        mode=mode,
        demo_safe=demo_safe,
        loaded_from=loaded_from,
        banner_len=banner_len,
        statement_present=statement_present,
        checklist_present=checklist_present,
    )

    # Write outputs
    latest_txt = VALIDATION_DIR / "week3_demo_acceptance_latest.txt"
    latest_json = VALIDATION_DIR / "week3_demo_acceptance_latest.json"
    stamped_txt = VALIDATION_DIR / f"week3_demo_acceptance_{_stamp()}.txt"
    stamped_json = VALIDATION_DIR / f"week3_demo_acceptance_{_stamp()}.json"

    txt = "\n".join(
        [
            "DEMO STATUS: ACCEPTED" if verdict == "PASS" else "DEMO STATUS: NOT ACCEPTED",
            f"MODE: {mode}",
            f"READY FOR: Briefing / Evaluation" if verdict == "PASS" else "READY FOR: None (fix violations)",
            "NOT READY FOR: Operational deployment",
            "",
            f"generated_at_utc: {res.generated_at_utc}",
            f"demo_safe: {demo_safe}",
            f"loaded_from: {loaded_from}",
            f"banner_len: {banner_len}",
            f"demo_acceptance_statement_present: {statement_present}",
            f"phase_ii_handoff_checklist_present: {checklist_present}",
            "",
            "No further changes permitted without Phase II authorization.",
        ]
    )

    latest_txt.write_text(txt, encoding="utf-8")
    stamped_txt.write_text(txt, encoding="utf-8")
    latest_json.write_text(json.dumps(res.to_json(), indent=2), encoding="utf-8")
    stamped_json.write_text(json.dumps(res.to_json(), indent=2), encoding="utf-8")

    return {
        "result": res.to_json(),
        "paths": {
            "latest_txt": str(latest_txt),
            "latest_json": str(latest_json),
            "stamped_txt": str(stamped_txt),
            "stamped_json": str(stamped_json),
        },
    }


def main() -> int:
    out = run_week3_demo_acceptance_writer()
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

