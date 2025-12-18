# src/spectral_owl_explain.py
"""
Spectral Owl Explain (LOCKED)
-----------------------------
Reads latest demo artifacts (best effort) and returns stable explanation dicts.

IMPORTANT:
- This is deterministic formatting + bounded interpretation.
- Not an LLM.
- Never crashes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from spectral_owl_reasoning_templates import render_template


# -----------------------------
# Repo paths (best effort)
# -----------------------------
_THIS_FILE = Path(__file__).resolve()
SRC_DIR = _THIS_FILE.parent
REPO_ROOT = SRC_DIR.parent

BRIEFS_DIR = REPO_ROOT / "docs" / "briefs"
BASEDEF_DIR = REPO_ROOT / "docs" / "base_defense"


def _read_json_best_effort(path: Path) -> Optional[dict]:
    try:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _read_txt_best_effort(path: Path) -> Optional[str]:
    try:
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def explain_installation_threat_map() -> Dict[str, str]:
    """
    Uses docs/base_defense/installation_threat_map_latest.json if present.
    Falls back to txt parse if needed.
    """
    latest_json = BASEDEF_DIR / "installation_threat_map_latest.json"
    latest_txt = BASEDEF_DIR / "installation_threat_map_latest.txt"

    data: Dict[str, Any] = {}
    j = _read_json_best_effort(latest_json)
    if isinstance(j, dict):
        # Try to normalize expected fields
        data["posture"] = j.get("posture") or j.get("recommended_posture") or "DUTY_OFFICER_NOTIFY"
        data["overall_risk_band"] = j.get("overall_risk_band") or j.get("risk_band") or "UNKNOWN"
        data["max_risk_score"] = j.get("max_risk_score") or j.get("risk_score") or ""
        # Zones can be dict or list; normalize
        zones = j.get("zones")
        if isinstance(zones, list):
            norm = []
            for item in zones:
                if isinstance(item, dict):
                    # expected: {"zone": "NORTH", "risk_score": 12.0, "band": "LOW", "notes": "..."}
                    norm.append(
                        {
                            "zone": item.get("zone") or item.get("name") or "ZONE",
                            "risk_score": item.get("risk_score", ""),
                            "band": item.get("band", ""),
                            "notes": item.get("notes", ""),
                        }
                    )
            data["zones"] = norm
        elif isinstance(zones, dict):
            # map->list
            norm = []
            for k, v in zones.items():
                if isinstance(v, dict):
                    norm.append(
                        {
                            "zone": k,
                            "risk_score": v.get("risk_score", ""),
                            "band": v.get("band", ""),
                            "notes": v.get("notes", ""),
                        }
                    )
            data["zones"] = norm
    else:
        # fallback: text only (no strict parsing; keep bounded)
        t = _read_txt_best_effort(latest_txt) or ""
        data["posture"] = "DUTY_OFFICER_NOTIFY"
        data["overall_risk_band"] = "UNKNOWN"
        data["max_risk_score"] = ""
        data["zones"] = [f"TXT_PRESENT:{bool(t.strip())}"]

    return render_template("installation_threat_map", data)


def explain_commander_brief() -> Dict[str, str]:
    """
    Uses docs/briefs/commander_brief_latest.txt/json (best effort).
    We keep it bounded: extract statuses where possible.
    """
    latest_json = BRIEFS_DIR / "commander_brief_latest.json"
    latest_txt = BRIEFS_DIR / "commander_brief_latest.txt"

    data: Dict[str, Any] = {}
    j = _read_json_best_effort(latest_json)
    if isinstance(j, dict):
        # Some versions store envelope/report differently; best effort
        envelope = j
        report = j.get("report") if isinstance(j.get("report"), dict) else {}
        # statuses we can safely show
        data["fusion_validation_status"] = (
            report.get("fusion_validation_status")
            or report.get("fusion_validation_verdict")
            or envelope.get("fusion_validation_status")
            or "UNKNOWN"
        )
        data["degraded_validation_status"] = (
            report.get("degraded_validation_status")
            or report.get("degraded_validation_verdict")
            or envelope.get("degraded_validation_status")
            or "UNKNOWN"
        )
        data["recommended_posture"] = (
            report.get("recommended_posture")
            or envelope.get("recommended_posture")
            or envelope.get("posture")
            or "MAINTAIN_CURRENT_POSTURE"
        )
    else:
        # fallback: scan the text for a posture/status hint (still bounded)
        t = _read_txt_best_effort(latest_txt) or ""
        posture = "MAINTAIN_CURRENT_POSTURE"
        if "DUTY_OFFICER_NOTIFY" in t:
            posture = "DUTY_OFFICER_NOTIFY"
        data["fusion_validation_status"] = "UNKNOWN"
        data["degraded_validation_status"] = "UNKNOWN"
        data["recommended_posture"] = posture

    return render_template("commander_brief", data)


def explain_legal_snapshot() -> Dict[str, str]:
    """
    Uses docs/briefs/legal_case_snapshot_latest.json/txt.
    """
    latest_json = BRIEFS_DIR / "legal_case_snapshot_latest.json"
    latest_txt = BRIEFS_DIR / "legal_case_snapshot_latest.txt"

    data: Dict[str, Any] = {}
    j = _read_json_best_effort(latest_json)
    if isinstance(j, dict):
        data["risk_band"] = j.get("risk_band") or j.get("risk_band_name") or "UNKNOWN"
        data["risk_score"] = j.get("risk_score") or ""
        data["recommended_posture"] = j.get("recommended_posture") or "HOLD_ACTION_PENDING_REVIEW"
        flags = j.get("ambiguity_flags")
        if isinstance(flags, list):
            data["ambiguity_flags"] = flags
        else:
            data["ambiguity_flags"] = []
    else:
        t = _read_txt_best_effort(latest_txt) or ""
        # keep bounded: don’t parse too hard
        data["risk_band"] = "UNKNOWN"
        data["risk_score"] = ""
        data["recommended_posture"] = "HOLD_ACTION_PENDING_REVIEW"
        data["ambiguity_flags"] = ["TXT_PRESENT" if bool(t.strip()) else "TXT_MISSING"]

    return render_template("legal_snapshot", data)


def main() -> int:
    """
    Quick local smoke test:
      python src/spectral_owl_explain.py
    """
    ex1 = explain_installation_threat_map()
    ex2 = explain_commander_brief()
    ex3 = explain_legal_snapshot()

    print("installation_threat_map keys:", list(ex1.keys()))
    print("commander_brief keys:", list(ex2.keys()))
    print("legal_snapshot keys:", list(ex3.keys()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

