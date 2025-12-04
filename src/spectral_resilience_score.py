"""
spectral_resilience_score.py

Ghost Lantern Labs – Spectral Resilience Scorecard

Purpose:
    Compute a single "resilience score" (0–100) for the GLL platform by
    reading existing health artifacts and summarizing:

    - Fusion QA health
    - Sensor health
    - Sensor reliability
    - Cross-sensor validation
    - AI-Independence / Offline readiness

Outputs:
    - Prints a human-readable summary to stdout
    - Writes docs/spectral_resilience_score.txt

Safe behavior:
    - If any source file is missing or malformed, the module degrades
      gracefully and uses default mid-range scores instead of crashing.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, Optional


BASE = Path(__file__).parent
DOCS_DIR = BASE / "docs"

QA_FILE = BASE / "qa_summary.txt"
SENSOR_HEALTH_FILE = BASE / "sensor_health_report.txt"
RELIABILITY_FILE = DOCS_DIR / "reliability_report.txt"
CROSS_SENSOR_FILE = DOCS_DIR / "cross_sensor_report.txt"
OFFLINE_STATUS_FILE = BASE / "offline_status.txt"

OUTPUT_FILE = DOCS_DIR / "spectral_resilience_score.txt"


def _safe_read(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    try:
        return path.read_text()
    except Exception:
        return None


# -----------------------------
# 1. QA / Fusion Health
# -----------------------------
def score_qa_health() -> Dict[str, Any]:
    """
    Parse qa_summary.txt and compute a QA health score.
    If the file is missing or malformed, fall back to defaults.
    """
    text = _safe_read(QA_FILE)
    if not text:
        return {
            "component": "qa_health",
            "score": 70,
            "details": "qa_summary.txt missing; using default mid-range score."
        }

    total = None
    passed = None

    for line in text.splitlines():
        line = line.strip()
        if line.lower().startswith("total tests"):
            # e.g., "Total tests: 7"
            parts = line.split(":")
            if len(parts) == 2:
                try:
                    total = int(parts[1].strip())
                except ValueError:
                    pass
        elif line.lower().startswith("passed"):
            parts = line.split(":")
            if len(parts) == 2:
                try:
                    passed = int(parts[1].strip())
                except ValueError:
                    pass

    if not total or total <= 0 or passed is None:
        return {
            "component": "qa_health",
            "score": 75,
            "details": "qa_summary.txt present but could not parse pass rate; using safe default."
        }

    ratio = passed / float(total)
    score = int(50 + ratio * 50)  # 50–100 range
    score = max(0, min(100, score))

    return {
        "component": "qa_health",
        "score": score,
        "details": f"{passed}/{total} tests passed → QA health ratio {ratio:.2f}"
    }


# -----------------------------
# 2. Sensor Health
# -----------------------------
def score_sensor_health() -> Dict[str, Any]:
    """
    Score sensor health based on sensor_health_report.txt.
    We look for keywords and derive a rough score.
    """
    text = _safe_read(SENSOR_HEALTH_FILE)
    if not text:
        return {
            "component": "sensor_health",
            "score": 72,
            "details": "sensor_health_report.txt missing; assuming basic operational state."
        }

    lower = text.lower()
    # Very rough heuristic
    if "all sensors healthy" in lower or "no issues detected" in lower:
        score = 95
        details = "Report indicates all sensors healthy."
    elif "degraded" in lower or "warning" in lower:
        score = 80
        details = "Report shows some warnings / degraded sensors."
    elif "failed" in lower or "critical" in lower:
        score = 60
        details = "Report indicates some sensor failures or critical issues."
    else:
        score = 78
        details = "Sensor health report present; no clear critical issues detected."

    return {
        "component": "sensor_health",
        "score": score,
        "details": details
    }


# -----------------------------
# 3. Reliability Score
# -----------------------------
def score_reliability() -> Dict[str, Any]:
    """
    Read docs/reliability_report.txt and extract a high-level reliability score.
    Expect a line like: 'Overall Reliability Score: 92%'
    If missing, use a default.
    """
    text = _safe_read(RELIABILITY_FILE)
    if not text:
        return {
            "component": "reliability",
            "score": 75,
            "details": "reliability_report.txt missing; using default reliability score."
        }

    score = None
    for line in text.splitlines():
        line = line.strip()
        lower = line.lower()
        if "overall reliability" in lower or "overall reliability score" in lower:
            # Try to extract an integer percentage
            digits = "".join(ch for ch in line if ch.isdigit())
            if digits:
                try:
                    score = int(digits)
                except ValueError:
                    score = None
            break

    if score is None:
        score = 80
        details = "Reliability report present; could not parse explicit score, using safe default."
    else:
        score = max(0, min(100, score))
        details = f"Overall reliability reported as ~{score}%."

    return {
        "component": "reliability",
        "score": score,
        "details": details
    }


# -----------------------------
# 4. Cross-Sensor Validation
# -----------------------------
def score_cross_sensor() -> Dict[str, Any]:
    """
    Read docs/cross_sensor_report.txt and derive a cross-sensor agreement score.
    If missing, we assume the feature is not yet fully enabled.
    """
    text = _safe_read(CROSS_SENSOR_FILE)
    if not text:
        return {
            "component": "cross_sensor_validation",
            "score": 68,
            "details": "Cross-sensor report missing; assuming early-stage deployment."
        }

    lower = text.lower()
    if "no major contradictions" in lower or "high agreement" in lower:
        score = 92
        details = "Cross-sensor report indicates high agreement between sensors."
    elif "some contradictions" in lower or "partial disagreement" in lower:
        score = 78
        details = "Report indicates some disagreements; still mostly coherent."
    elif "severe contradictions" in lower or "major mismatch" in lower:
        score = 60
        details = "Report indicates major cross-sensor contradictions."
    else:
        score = 80
        details = "Cross-sensor report present; status appears generally stable."

    return {
        "component": "cross_sensor_validation",
        "score": score,
        "details": details
    }


# -----------------------------
# 5. AI-Independence / Offline
# -----------------------------
def score_ai_independence() -> Dict[str, Any]:
    """
    Look at offline_status.txt and derive a score for AI-Independence / offline readiness.
    """
    text = _safe_read(OFFLINE_STATUS_FILE)
    if not text:
        return {
            "component": "ai_independence",
            "score": 70,
            "details": "offline_status.txt missing; assuming Phase 1–2 complete but not actively monitored."
        }

    lower = text.lower()
    if "phase 2 complete" in lower or "phase-2 complete" in lower:
        base = 85
    elif "phase 1 complete" in lower or "phase-1 complete" in lower:
        base = 78
    else:
        base = 72

    if "offline_ok" in lower or "offline-ready" in lower:
        base += 5
    if "degraded" in lower or "fallback-only" in lower:
        base -= 5

    score = max(0, min(100, base))

    return {
        "component": "ai_independence",
        "score": score,
        "details": f"Offline / AI-Independence status parsed from offline_status.txt (base={base})."
    }


# -----------------------------
# Aggregation
# -----------------------------
def compute_resilience_score() -> Dict[str, Any]:
    """
    Compute component scores and aggregate into a single resilience score.
    """
    components = [
        score_qa_health(),
        score_sensor_health(),
        score_reliability(),
        score_cross_sensor(),
        score_ai_independence(),
    ]

    valid_scores = [c["score"] for c in components if isinstance(c.get("score"), (int, float))]
    if not valid_scores:
        overall = 70
    else:
        overall = int(sum(valid_scores) / len(valid_scores))

    return {
        "overall_score": overall,
        "components": components,
    }


def build_ascii_bar(score: int, width: int = 20) -> str:
    """
    Build a simple ASCII progress bar: [██████░░░░] 82%
    """
    score = max(0, min(100, score))
    filled = int((score / 100.0) * width)
    empty = width - filled
    return f"[{'█' * filled}{'░' * empty}] {score}%"


def build_resilience_report() -> str:
    """
    Build the human-readable text report that will be written to disk.
    """
    result = compute_resilience_score()
    overall = result["overall_score"]
    components = result["components"]

    lines = []
    lines.append("=== GLL SPECTRAL RESILIENCE SCORE ===")
    lines.append("")
    lines.append(f"Overall Resilience: {overall}/100")
    lines.append(build_ascii_bar(overall))
    lines.append("")

    for comp in components:
        name = comp.get("component", "unknown")
        score = comp.get("score", 0)
        details = comp.get("details", "")
        lines.append(f"[{name}]")
        lines.append(f"  Score: {score}/100  {build_ascii_bar(int(score))}")
        if details:
            lines.append(f"  Notes: {details}")
        lines.append("")

    lines.append("Interpretation:")
    if overall >= 90:
        lines.append("  → System is mission-ready for demanding ISR / AFTAC-style demos.")
    elif overall >= 80:
        lines.append("  → System is solid and resilient; ready for internal demos and SBIR-style pitches.")
    elif overall >= 70:
        lines.append("  → System is functional with some risk areas; prioritize hardening before high-stakes demos.")
    else:
        lines.append("  → System requires additional hardening before serious demo or deployment.")

    return "\n".join(lines)


def write_resilience_report() -> Path:
    """
    Generate and write the resilience report to docs/spectral_resilience_score.txt.
    Returns the output path.
    """
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    text = build_resilience_report()
    OUTPUT_FILE.write_text(text)
    return OUTPUT_FILE


def get_resilience_snapshot() -> Dict[str, Any]:
    """
    Lightweight helper for other modules (CLI, GUI, HTML) to grab
    the current resilience score + components without touching files.
    """
    data = compute_resilience_score()
    return data


def export_resilience_badge() -> Dict[str, Any]:
    """
    Export a very small JSON + text badge to docs/ for GUI / HTML use.

    - docs/spectral_resilience_badge.txt   (ASCII one-liner)
    - docs/spectral_resilience_badge.json  (machine-friendly)
    """
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    snap = compute_resilience_score()
    overall = snap["overall_score"]
    badge_text = f"SPECTRAL RESILIENCE: {overall}/100 {build_ascii_bar(overall, width=10)}"

    badge_txt_path = DOCS_DIR / "spectral_resilience_badge.txt"
    badge_json_path = DOCS_DIR / "spectral_resilience_badge.json"

    badge_txt_path.write_text(badge_text)

    badge_payload = {
        "overall": overall,
        "components": snap["components"],
        "badge": badge_text,
    }
    badge_json_path.write_text(json.dumps(badge_payload, indent=2))

    return {
        "status": "ok",
        "txt": str(badge_txt_path),
        "json": str(badge_json_path),
        "overall": overall,
    }


def main() -> Dict[str, Any]:
    """
    Entry point for CLI usage.
    """
    out_path = write_resilience_report()
    badge_info = export_resilience_badge()
    summary = compute_resilience_score()
    summary["output_file"] = str(out_path)
    summary["badge"] = badge_info
    print(f"[OK] Spectral Resilience Score written → {out_path}")
    print(f"[OK] Spectral Resilience Badge written → {badge_info['txt']}")
    print(f"Overall resilience: {summary['overall_score']}/100")
    return summary


if __name__ == "__main__":
    main()

