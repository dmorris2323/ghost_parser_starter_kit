from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

OUT_DIR = Path("docs") / "briefs"
LATEST_TXT = OUT_DIR / "commander_brief_latest.txt"
LATEST_JSON = OUT_DIR / "commander_brief_latest.json"


REQUIRED_TOKENS = [
    "probabilistic",
    "bounded",
    "operator judgment",
]

REQUIRED_SECTION_HEADERS = [
    "1. What changed:",
    "2. Why it matters:",
    "3. What we know:",
    "4. What we do NOT know:",
    "5. Recommended posture:",
]

ALLOWED_POSTURES = {
    "ROUTINE_MONITORING",
    "DUTY_OFFICER_NOTIFY",
    "SECURITY_FORCES_DISPATCH",
    "INSTALLATION_COMMANDER_NOTIFY",
    "NATIONAL_COMMAND_ALERT",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _find_posture(txt: str) -> str:
    # Posture is on section 5 line(s). We accept the first non-empty line after the header.
    if "5. Recommended posture:" not in txt:
        return ""
    after = txt.split("5. Recommended posture:", 1)[1]
    for line in after.splitlines():
        s = line.strip()
        if s:
            # posture may include extra safety sentence after newline; keep first token-ish line
            return s.split()[0].strip()
    return ""


def run_gate() -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamped = _stamp()

    txt = _read_text(LATEST_TXT)
    meta = _read_json(LATEST_JSON)

    violations: List[str] = []

    # File presence
    if not txt.strip():
        violations.append("MISSING_OR_EMPTY:commander_brief_latest.txt")
    if not meta:
        violations.append("MISSING_OR_EMPTY:commander_brief_latest.json")

    # Section headers
    for h in REQUIRED_SECTION_HEADERS:
        if h not in txt:
            violations.append(f"MISSING_SECTION:{h}")

    # Required safety tokens
    txt_lower = txt.lower()
    for tok in REQUIRED_TOKENS:
        if tok not in txt_lower:
            violations.append(f"MISSING_REQUIRED_TOKEN:{tok}")

    # Posture bounded
    posture = _find_posture(txt)
    if posture and posture not in ALLOWED_POSTURES:
        violations.append(f"UNKNOWN_POSTURE:{posture}")

    verdict = "PASS" if len(violations) == 0 else "FAIL"

    payload: Dict[str, Any] = {
        "generated_at_utc": _utc_now_iso(),
        "verdict": verdict,
        "violations": violations,
        "posture_detected": posture,
        "required_tokens": REQUIRED_TOKENS,
        "required_sections": REQUIRED_SECTION_HEADERS,
    }

    latest_json = OUT_DIR / "commander_brief_consistency_latest.json"
    stamped_json = OUT_DIR / f"commander_brief_consistency_{stamped}.json"

    latest_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    stamped_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    return {
        "verdict": verdict,
        "latest": str(latest_json),
        "stamped": str(stamped_json),
        "violations": violations,
    }


def main() -> None:
    res = run_gate()
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()

