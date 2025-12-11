#!/usr/bin/env python3
"""
joint_readiness_html_brief.py

Ghost Lantern Labs – Joint Readiness HTML Brief
-----------------------------------------------

Purpose:
    Render the Joint Readiness Board + Scorecard + Risk Register into a
    single HTML brief suitable for:
        - Base commander / Wing leadership
        - AFTAC / nuclear SME review
        - AFWERX / SBIR demos
        - Shari demo day

Inputs (all optional, defensive):
    docs/joint_readiness_board.json
    docs/joint_readiness_scorecard.txt
    docs/joint_risk_register.json

Outputs:
    docs/joint_readiness_brief.html

This module is read-only on upstream artifacts. It does not modify any
other files.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional, List

BASE_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(BASE_DIR, "docs")


def _safe_read_json(path: str) -> Optional[Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _safe_read_text(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def _fmt_float(val: Any, default: float = 0.0) -> float:
    try:
        return float(val)
    except Exception:
        return default


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def build_joint_readiness_html_brief() -> str:
    os.makedirs(DOCS_DIR, exist_ok=True)

    board_path = os.path.join(DOCS_DIR, "joint_readiness_board.json")
    scorecard_path = os.path.join(DOCS_DIR, "joint_readiness_scorecard.txt")
    risk_path = os.path.join(DOCS_DIR, "joint_risk_register.json")

    board = _safe_read_json(board_path)
    scorecard_txt = _safe_read_text(scorecard_path)
    risk = _safe_read_json(risk_path)

    # Defaults if upstream files not present
    if not isinstance(board, dict):
        board = {}
    if not isinstance(risk, dict):
        risk = {"risks": []}
    if scorecard_txt is None:
        scorecard_txt = "Joint Readiness Scorecard not available – run joint_readiness_scorecard.py."

    generated_at = board.get("generated_at", datetime.utcnow().isoformat() + "Z")

    jr_score = _fmt_float(board.get("joint_readiness_score"), 0.0)
    jr_level = str(board.get("joint_readiness_level", "UNKNOWN"))

    nuclear = board.get("nuclear", {}) or {}
    base_def = board.get("base_defense", {}) or {}
    outage = board.get("outage", {}) or {}
    dist = board.get("distributed_readiness", {}) or {}

    n_level = str(nuclear.get("level", "UNKNOWN"))
    n_score = _fmt_float(nuclear.get("score"))
    n_vol = _fmt_float(nuclear.get("volatility_index"))
    n_drift_conf = _fmt_float(nuclear.get("drift_confidence"))
    n_align = str(nuclear.get("alignment", "UNKNOWN"))

    b_level = str(base_def.get("level", "UNKNOWN"))
    b_score = _fmt_float(base_def.get("score"))
    b_sectors = int(base_def.get("sectors", 0))

    o_risk = _fmt_float(outage.get("outage_risk_score"))
    o_crit = int(outage.get("critical_sensors_at_risk", 0))

    d_fusion = _fmt_float(dist.get("fusion_trust_score"))
    d_rel = _fmt_float(dist.get("average_reliability"))
    d_units = int(dist.get("units_tracked", 0))

    risks: List[Dict[str, Any]] = []
    if isinstance(risk.get("risks"), list):
        risks = [r for r in risk["risks"] if isinstance(r, dict)]

    # Build HTML document
    title = "Ghost Lantern Labs – Joint Readiness Brief"
    html_lines: List[str] = []

    html_lines.append("<!DOCTYPE html>")
    html_lines.append("<html lang='en'>")
    html_lines.append("<head>")
    html_lines.append(f"  <meta charset='utf-8' />")
    html_lines.append(f"  <title>{_escape_html(title)}</title>")
    html_lines.append("  <style>")
    html_lines.append("    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 0; background-color: #050814; color: #f5f5f5; }")
    html_lines.append("    .page { max-width: 1100px; margin: 0 auto; padding: 32px 24px 64px 24px; }")
    html_lines.append("    h1, h2, h3 { margin: 0 0 8px 0; }")
    html_lines.append("    h1 { font-size: 28px; letter-spacing: 0.06em; text-transform: uppercase; }")
    html_lines.append("    h2 { font-size: 20px; margin-top: 24px; border-bottom: 1px solid #262a3a; padding-bottom: 4px; }")
    html_lines.append("    h3 { font-size: 16px; margin-top: 16px; }")
    html_lines.append("    .meta { font-size: 12px; color: #9ca3af; margin-bottom: 16px; }")
    html_lines.append("    .pill { display: inline-block; padding: 4px 10px; border-radius: 999px; font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; }")
    html_lines.append("    .pill-green { background: #064e3b; color: #bbf7d0; }")
    html_lines.append("    .pill-amber { background: #78350f; color: #fde68a; }")
    html_lines.append("    .pill-red { background: #7f1d1d; color: #fecaca; }")
    html_lines.append("    .pill-muted { background: #111827; color: #9ca3af; }")
    html_lines.append("    .card-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin-top: 16px; }")
    html_lines.append("    .card { background-color: #0b1020; border-radius: 14px; padding: 14px 14px 16px 14px; border: 1px solid #111827; }")
    html_lines.append("    .card h3 { margin-bottom: 4px; }")
    html_lines.append("    .metric-big { font-size: 28px; font-weight: 600; }")
    html_lines.append("    .metric-label { font-size: 11px; text-transform: uppercase; color: #9ca3af; letter-spacing: 0.09em; }")
    html_lines.append("    .risk-list { margin: 0; padding-left: 18px; }")
    html_lines.append("    .risk-list li { margin-bottom: 8px; }")
    html_lines.append("    .severity-high { color: #fecaca; }")
    html_lines.append("    .severity-medium { color: #fef3c7; }")
    html_lines.append("    .severity-low { color: #bbf7d0; }")
    html_lines.append("    pre.scorecard { background-color: #020617; border-radius: 12px; padding: 12px 14px; font-size: 11px; overflow-x: auto; border: 1px solid #111827; }")
    html_lines.append("    footer { margin-top: 40px; font-size: 11px; color: #6b7280; }")
    html_lines.append("  </style>")
    html_lines.append("</head>")
    html_lines.append("<body>")
    html_lines.append("  <div class='page'>")
    html_lines.append(f"    <h1>{_escape_html(title)}</h1>")
    html_lines.append(f"    <div class='meta'>Generated at (UTC): {_escape_html(generated_at)} · Powered by Ghost Lantern Labs – Joint Nuclear + Base Defense Stack</div>")

    # Joint readiness header pill
    if jr_level.upper() == "GREEN":
        pill_class = "pill pill-green"
    elif jr_level.upper() == "AMBER":
        pill_class = "pill pill-amber"
    elif jr_level.upper() == "RED":
        pill_class = "pill pill-red"
    else:
        pill_class = "pill pill-muted"

    html_lines.append("    <div class='card-row'>")
    html_lines.append("      <div class='card'>")
    html_lines.append("        <div class='metric-label'>Joint Readiness</div>")
    html_lines.append(f"        <div class='metric-big'>{jr_score:.1f}/100</div>")
    html_lines.append(f"        <div class='{pill_class}'>{_escape_html(jr_level)}</div>")
    html_lines.append("        <p style='margin-top:10px;font-size:12px;color:#e5e7eb;'>")
    html_lines.append("          Composite readiness across nuclear early warning, base-defense threat, sensor outages, and fusion health.")
    html_lines.append("        </p>")
    html_lines.append("      </div>")

    # Nuclear + Base defense summary cards
    html_lines.append("      <div class='card'>")
    html_lines.append("        <h3>Nuclear Posture</h3>")
    html_lines.append(f"        <div class='metric-big'>{n_score:.1f}/100</div>")
    html_lines.append(f"        <div class='metric-label'>Level: { _escape_html(n_level) }</div>")
    html_lines.append(f"        <div style='margin-top:8px;font-size:11px;'>Volatility: {n_vol:.1f}/100 · Drift Confidence: {n_drift_conf:.1f}/100</div>")
    html_lines.append(f"        <div style='margin-top:2px;font-size:11px;'>Alignment: { _escape_html(n_align) }</div>")
    html_lines.append("      </div>")

    html_lines.append("      <div class='card'>")
    html_lines.append("        <h3>Base Defense Posture</h3>")
    html_lines.append(f"        <div class='metric-big'>{b_score:.1f}/100</div>")
    html_lines.append(f"        <div class='metric-label'>Level: { _escape_html(b_level) }</div>")
    html_lines.append(f"        <div style='margin-top:8px;font-size:11px;'>Sectors Tracked: {b_sectors}</div>")
    html_lines.append("        <div style='margin-top:8px;font-size:11px;'>")
    html_lines.append(f"          Sensor Outage Risk: {o_risk:.1f}/100 · Critical Sensors at Risk: {o_crit}")
    html_lines.append("        </div>")
    html_lines.append("        <div style='margin-top:8px;font-size:11px;'>")
    html_lines.append(f"          Fusion Trust: {d_fusion:.1f}/100 · Avg Reliability: {d_rel:.1f}/100 · Units: {d_units}")
    html_lines.append("        </div>")
    html_lines.append("      </div>")
    html_lines.append("    </div>")  # end card row

    # Top risks section
    html_lines.append("    <h2>Top Joint Risks</h2>")
    if not risks:
        html_lines.append("    <p style='font-size:13px;color:#9ca3af;'>No significant risks identified from the current Joint Readiness Board.</p>")
    else:
        html_lines.append("    <ul class='risk-list'>")
        for idx, r in enumerate(risks, start=1):
            severity = str(r.get("severity", "MEDIUM")).upper()
            domain = str(r.get("domain", "JOINT")).upper()
            title_text = r.get("title", "")
            detail_text = r.get("detail", "")

            if severity == "HIGH":
                sev_class = "severity-high"
            elif severity == "MEDIUM":
                sev_class = "severity-medium"
            else:
                sev_class = "severity-low"

            html_lines.append("      <li>")
            html_lines.append(
                f"        <span class='{sev_class}'>[{_escape_html(severity)}]</span> "
                f"{_escape_html(domain)} – <strong>{_escape_html(title_text)}</strong><br/>"
                f"        <span style='font-size:12px;color:#d1d5db;'>{_escape_html(detail_text)}</span>"
            )
            html_lines.append("      </li>")
        html_lines.append("    </ul>")

    # Raw scorecard section (for reviewers who like text)
    html_lines.append("    <h2>Scorecard (Text View)</h2>")
    html_lines.append("    <pre class='scorecard'>")
    html_lines.append(_escape_html(scorecard_txt))
    html_lines.append("    </pre>")

    # Footer
    html_lines.append("    <footer>")
    html_lines.append("      Ghost Lantern Labs · Joint Nuclear / Base-Defense Readiness Prototype<br/>")
    html_lines.append("      This brief fuses nuclear early warning, base-defense threat, sensor outage risk, and fusion health into a single commander-readable view.")
    html_lines.append("    </footer>")

    html_lines.append("  </div>")
    html_lines.append("</body>")
    html_lines.append("</html>")

    html_path = os.path.join(DOCS_DIR, "joint_readiness_brief.html")
    with open(html_path, "w", encoding="utf-8") as f_html:
        f_html.write("\n".join(html_lines))

    return html_path


if __name__ == "__main__":
    out_path = build_joint_readiness_html_brief()
    print("Joint Readiness HTML Brief generated:")
    print(f"  - {os.path.join('docs', 'joint_readiness_brief.html')}")

