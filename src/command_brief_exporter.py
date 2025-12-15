"""
command_brief_exporter.py

Command-Grade Brief Export (NO external dependencies)
- Exports JSON + HTML (printable) instead of PDF
- Designed for Streamlit + CLI use
- Pulls best-available artifacts: training curve, validation report, latest feedback, decision card

Outputs:
- docs/briefs/command_brief_latest.json
- docs/briefs/command_brief_latest.html
- docs/briefs/command_brief_<timestamp>.json/.html
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


BRIEF_DIR = Path("docs") / "briefs"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return None


def _write(path: Path, text: str) -> None:
    _safe_mkdir(path.parent)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, obj: Any) -> None:
    _safe_mkdir(path.parent)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _gather_inputs() -> Dict[str, Any]:
    paths = {
        "training_curve": Path("src") / "docs" / "training" / "training_curve_latest.json",
        "training_feedback": Path("src") / "docs" / "training" / "training_feedback_latest.json",
        "validation_report": Path("docs") / "validation" / "fusion_validation_report.json",
        "decision_card": Path("docs") / "nuclear" / "decision_card_latest.json",
        "degraded_validation": Path("docs") / "validation" / "degraded_fusion_validation_latest.json",
    }
    out: Dict[str, Any] = {"paths": {k: str(v) for k, v in paths.items()}}
    for k, p in paths.items():
        out[k] = _read_json(p) or {"_missing": True}
    return out


def export_command_brief(*, title: str = "GLL Commander Brief", operator: str = "Ghost") -> Dict[str, Any]:
    data = _gather_inputs()

    curve = data.get("training_curve", {})
    fb = data.get("training_feedback", {})
    val = data.get("validation_report", {})
    dc = data.get("decision_card", {})
    deg = data.get("degraded_validation", {})

    brief: Dict[str, Any] = {
        "artifact": "command_brief",
        "version": 1,
        "generated_at": _utc_now_iso(),
        "title": title,
        "operator": operator,
        "summary": {
            "agi": (curve.get("AGI") if isinstance(curve, dict) else None),
            "improvement_slope": (curve.get("improvement_slope") if isinstance(curve, dict) else None),
            "volatility_index": (curve.get("volatility_index") if isinstance(curve, dict) else None),
            "last_validation_status": ((val.get("verdict") or {}).get("status") if isinstance(val, dict) else None),
            "next_training_recommendation": fb if isinstance(fb, dict) else {},
        },
        "attachments": {
            "training_curve": curve,
            "training_feedback": fb,
            "validation_report": val,
            "decision_card": dc,
            "degraded_validation": deg,
        },
        "safe_notice": "This brief aggregates training-safe artifacts unless upstream sources are real.",
    }

    _safe_mkdir(BRIEF_DIR)
    stamp = _ts()

    json_latest = BRIEF_DIR / "command_brief_latest.json"
    html_latest = BRIEF_DIR / "command_brief_latest.html"
    json_stamped = BRIEF_DIR / f"command_brief_{stamp}.json"
    html_stamped = BRIEF_DIR / f"command_brief_{stamp}.html"

    _write_json(json_latest, brief)
    _write_json(json_stamped, brief)

    html = _render_html(brief)
    _write(html_latest, html)
    _write(html_stamped, html)

    return {
        "json_latest": str(json_latest),
        "html_latest": str(html_latest),
        "json_stamped": str(json_stamped),
        "html_stamped": str(html_stamped),
        "brief": brief,
    }


def _render_html(brief: Dict[str, Any]) -> str:
    s = brief.get("summary", {})
    def esc(x: Any) -> str:
        return str(x).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>{esc(brief.get("title"))}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Arial, sans-serif; margin: 28px; }}
    h1 {{ margin: 0 0 6px 0; }}
    .meta {{ color: #555; margin-bottom: 18px; }}
    .card {{ border: 1px solid #ddd; border-radius: 10px; padding: 14px; margin: 12px 0; }}
    pre {{ background: #f7f7f7; padding: 12px; border-radius: 8px; overflow-x: auto; }}
  </style>
</head>
<body>
  <h1>{esc(brief.get("title"))}</h1>
  <div class="meta">
    <div><b>Operator:</b> {esc(brief.get("operator"))}</div>
    <div><b>Generated:</b> {esc(brief.get("generated_at"))}</div>
  </div>

  <div class="card">
    <h2>Operational Summary</h2>
    <ul>
      <li><b>AGI:</b> {esc(s.get("agi"))}</li>
      <li><b>Improvement Slope:</b> {esc(s.get("improvement_slope"))}</li>
      <li><b>Volatility Index:</b> {esc(s.get("volatility_index"))}</li>
      <li><b>Last Validation:</b> {esc(s.get("last_validation_status"))}</li>
    </ul>
  </div>

  <div class="card">
    <h2>Next Training Recommendation</h2>
    <pre>{esc(json.dumps(s.get("next_training_recommendation", {}), indent=2))}</pre>
  </div>

  <div class="card">
    <h2>Attachments (JSON)</h2>
    <pre>{esc(json.dumps(brief.get("attachments", {}), indent=2)[:15000])}</pre>
    <div class="meta">Note: large attachments are truncated in HTML view for readability.</div>
  </div>

  <div class="meta">{esc(brief.get("safe_notice"))}</div>
</body>
</html>
"""


if __name__ == "__main__":
    out = export_command_brief()
    print("WROTE:", out["html_latest"])

