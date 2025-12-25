from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any


REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
DEMO_DIR = DOCS_DIR / "demo"
VALIDATION_DIR = DOCS_DIR / "validation"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def run_gate() -> Dict[str, Any]:
    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)

    violations = []
    required_missing = []

    req_files = [
        DEMO_DIR / "demo_acceptance_statement.txt",
        DEMO_DIR / "phase_ii_handoff_checklist.txt",
        VALIDATION_DIR / "week3_demo_acceptance_latest.txt",
        VALIDATION_DIR / "week3_demo_acceptance_latest.json",
    ]

    for p in req_files:
        if not p.exists():
            required_missing.append(str(p))

    acceptance_json = VALIDATION_DIR / "week3_demo_acceptance_latest.json"
    aj = _read_json(acceptance_json)
    verdict = str(aj.get("verdict", "FAIL")).strip()

    if verdict != "PASS":
        violations.append("DEMO_ACCEPTANCE_NOT_PASS")

    out = {
        "generated_at_utc": _utc_now_iso(),
        "context": "week3_demo_acceptance_gate",
        "verdict": "PASS" if (not required_missing and not violations) else "FAIL",
        "required_missing": required_missing,
        "violations": violations,
        "acceptance_verdict": verdict,
    }

    latest_txt = VALIDATION_DIR / "week3_demo_acceptance_gate_latest.txt"
    latest_json = VALIDATION_DIR / "week3_demo_acceptance_gate_latest.json"

    txt_lines = [
        "WEEK-3 DEMO ACCEPTANCE GATE",
        f"generated_at_utc: {out['generated_at_utc']}",
        f"verdict: {out['verdict']}",
        f"acceptance_verdict: {verdict}",
        "",
    ]
    if required_missing:
        txt_lines.append("Missing required files:")
        txt_lines += [f"- {x}" for x in required_missing]
        txt_lines.append("")
    if violations:
        txt_lines.append("Violations:")
        txt_lines += [f"- {v}" for v in violations]
        txt_lines.append("")

    latest_txt.write_text("\n".join(txt_lines).strip() + "\n", encoding="utf-8")
    latest_json.write_text(json.dumps(out, indent=2), encoding="utf-8")

    return {
        "latest_txt": str(latest_txt),
        "latest_json": str(latest_json),
        "result": out,
    }


def main() -> int:
    out = run_gate()
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

