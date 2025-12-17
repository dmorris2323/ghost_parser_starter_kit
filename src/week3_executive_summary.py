# src/week3_executive_summary.py
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parents[1]
BRIEFS_DIR = ROOT / "docs" / "briefs"
VALIDATION_DIR = ROOT / "docs" / "validation"
PACKAGES_DIR = ROOT / "docs" / "packages"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _read_text_best_effort(p: Path, max_chars: int = 4000) -> str:
    try:
        if not p.exists():
            return ""
        t = p.read_text(encoding="utf-8", errors="replace")
        return t[:max_chars]
    except Exception:
        return ""


def _read_json_best_effort(p: Path) -> Dict[str, Any]:
    try:
        if not p.exists():
            return {}
        return json.loads(p.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}


def _safe_rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except Exception:
        return str(p)


def _demo_lock_banner_best_effort() -> str:
    try:
        from demo_lock import is_demo_locked, demo_lock_banner  # type: ignore

        if bool(is_demo_locked()):
            return str(demo_lock_banner())
        return ""
    except Exception:
        return ""


def write_week3_executive_summary(
    context: str = "week3_executive_summary",
) -> Dict[str, Any]:
    """
    Writes a premium, demo-safe Executive Summary HTML (dark HUD style).
    Outputs:
      - docs/packages/week3_executive_summary_latest.html
      - stamped variant
      - optional txt mirror for quick diff
    Must never crash.
    """
    PACKAGES_DIR.mkdir(parents=True, exist_ok=True)

    generated = _utc_now_iso()
    stamp = _stamp()

    banner = _demo_lock_banner_best_effort()

    # Pull latest artifacts (best effort)
    orch_json = _read_json_best_effort(BRIEFS_DIR / "week3_demo_orchestrator_latest.json")
    readiness_json = _read_json_best_effort(VALIDATION_DIR / "week3_demo_readiness_gate_latest.json")
    pack_manifest = _read_json_best_effort(PACKAGES_DIR / "week3_cloud_demo_package_manifest_latest.json")

    commander_head = _read_text_best_effort(BRIEFS_DIR / "commander_brief_latest.txt", max_chars=1400)
    narrative_head = _read_text_best_effort(BRIEFS_DIR / "week3_demo_narrative_latest.txt", max_chars=1400)
    legal_head = _read_text_best_effort(BRIEFS_DIR / "legal_case_snapshot_latest.txt", max_chars=1400)
    ops_summary_head = _read_text_best_effort(BRIEFS_DIR / "week3_operator_summary_latest.txt", max_chars=600)

    orch_verdict = orch_json.get("verdict", "UNKNOWN")
    orch_crashes = orch_json.get("crashes", "UNKNOWN")
    readiness_verdict = readiness_json.get("verdict", "UNKNOWN")
    readiness_crashes = readiness_json.get("crashes", "UNKNOWN")
    readiness_strict = readiness_json.get("strict", True)
    package_verdict = pack_manifest.get("verdict", "UNKNOWN")
    package_missing = pack_manifest.get("required_missing", [])

    # Build HTML (HUD theme)
    subtitle = "Obasi Command Center — Week-3 Cloud-Ready Demo Package"
    safety_line = "Assessment is probabilistic and bounded; operator judgment applies."
    demo_line = "DEMO MODE ACTIVE — READ ONLY" if banner else "DEMO LOCK NOT DETECTED (enable for stakeholder demo)"

    def esc(s: str) -> str:
        return (
            s.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Week-3 Executive Summary — Obasi</title>
  <style>
    :root {{
      --bg0: #070a10;
      --bg1: #0b1220;
      --panel: rgba(12, 18, 32, 0.75);
      --line: rgba(90, 220, 255, 0.18);
      --glow: rgba(90, 220, 255, 0.35);
      --text: rgba(230, 245, 255, 0.92);
      --muted: rgba(190, 220, 240, 0.70);
      --accent: rgba(90, 220, 255, 0.95);
      --good: rgba(120, 255, 190, 0.95);
      --bad: rgba(255, 130, 130, 0.95);
      --warn: rgba(255, 210, 130, 0.95);
      --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      --sans: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: var(--sans);
      background: radial-gradient(1200px 800px at 20% 10%, rgba(90,220,255,0.10), transparent 60%),
                  radial-gradient(900px 700px at 90% 20%, rgba(120,255,190,0.06), transparent 55%),
                  linear-gradient(180deg, var(--bg0), var(--bg1));
      color: var(--text);
      min-height: 100vh;
    }}
    .topbar {{
      position: sticky;
      top: 0;
      z-index: 20;
      backdrop-filter: blur(10px);
      background: rgba(7,10,16,0.55);
      border-bottom: 1px solid var(--line);
    }}
    .topbar-inner {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 14px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
    }}
    .brand {{
      display: flex;
      flex-direction: column;
      line-height: 1.2;
    }}
    .brand .title {{
      font-weight: 800;
      letter-spacing: 0.6px;
      font-size: 14px;
      text-transform: uppercase;
      color: var(--accent);
      text-shadow: 0 0 14px var(--glow);
    }}
    .brand .subtitle {{
      font-size: 12px;
      color: var(--muted);
    }}
    .meta {{
      font-family: var(--mono);
      font-size: 11px;
      color: var(--muted);
      text-align: right;
      line-height: 1.35;
    }}
    .wrap {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 18px 16px 30px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 14px;
    }}
    @media (max-width: 980px) {{
      .grid {{ grid-template-columns: 1fr; }}
      .meta {{ text-align: left; }}
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      box-shadow: 0 0 0 1px rgba(90,220,255,0.06) inset, 0 18px 50px rgba(0,0,0,0.35);
      border-radius: 14px;
      overflow: hidden;
      position: relative;
    }}
    .panel::before {{
      content: "";
      position: absolute;
      inset: 0;
      background: radial-gradient(800px 200px at 20% 0%, rgba(90,220,255,0.06), transparent 60%);
      pointer-events: none;
    }}
    .panel-head {{
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 10px;
    }}
    .panel-title {{
      font-weight: 800;
      letter-spacing: 0.4px;
      font-size: 12px;
      text-transform: uppercase;
      color: rgba(235,250,255,0.92);
    }}
    .badge {{
      font-family: var(--mono);
      font-size: 11px;
      padding: 6px 10px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: rgba(0,0,0,0.25);
      color: var(--muted);
    }}
    .badge.good {{ color: var(--good); border-color: rgba(120,255,190,0.28); }}
    .badge.bad  {{ color: var(--bad);  border-color: rgba(255,130,130,0.28); }}
    .badge.warn {{ color: var(--warn); border-color: rgba(255,210,130,0.28); }}
    .panel-body {{
      padding: 12px 14px;
    }}
    .kv {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }}
    .k {{
      border: 1px solid rgba(90,220,255,0.10);
      border-radius: 12px;
      padding: 10px 12px;
      background: rgba(0,0,0,0.20);
    }}
    .k .label {{
      font-size: 11px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.4px;
      margin-bottom: 6px;
    }}
    .k .value {{
      font-family: var(--mono);
      font-size: 12px;
      color: rgba(230,245,255,0.92);
    }}
    .mono {{
      font-family: var(--mono);
      font-size: 12px;
      color: rgba(230,245,255,0.88);
      white-space: pre-wrap;
      overflow-wrap: anywhere;
    }}
    .callout {{
      padding: 10px 12px;
      border-radius: 12px;
      border: 1px dashed rgba(90,220,255,0.22);
      background: rgba(0,0,0,0.22);
      color: rgba(230,245,255,0.86);
      font-size: 12px;
      line-height: 1.45;
    }}
    .divider {{
      height: 1px;
      background: var(--line);
      margin: 12px 0;
    }}
    .small {{
      font-size: 12px;
      color: var(--muted);
      line-height: 1.45;
    }}
    .footer {{
      margin-top: 14px;
      font-family: var(--mono);
      font-size: 11px;
      color: rgba(190,220,240,0.62);
    }}
    a {{ color: var(--accent); text-decoration: none; }}
  </style>
</head>
<body>
  <div class="topbar">
    <div class="topbar-inner">
      <div class="brand">
        <div class="title">OBASI // COMMAND CENTER</div>
        <div class="subtitle">{esc(subtitle)}</div>
      </div>
      <div class="meta">
        generated_at_utc: {esc(generated)}<br/>
        context: {esc(context)}<br/>
        safety: {esc(safety_line)}
      </div>
    </div>
  </div>

  <div class="wrap">
    <div class="grid">
      <div class="panel">
        <div class="panel-head">
          <div class="panel-title">SYSTEM STATUS</div>
          <div class="badge {'good' if str(orch_verdict).upper()=='PASS' else 'bad' if str(orch_verdict).upper()=='FAIL' else 'warn'}">
            Orchestrator: {esc(str(orch_verdict))}
          </div>
        </div>
        <div class="panel-body">
          <div class="callout">
            <b>{esc(demo_line)}</b><br/>
            {esc(safety_line)}
          </div>

          <div class="divider"></div>

          <div class="kv">
            <div class="k">
              <div class="label">Readiness Gate</div>
              <div class="value">verdict={esc(str(readiness_verdict))} | strict={esc(str(readiness_strict))} | crashes={esc(str(readiness_crashes))}</div>
            </div>
            <div class="k">
              <div class="label">Orchestrator</div>
              <div class="value">verdict={esc(str(orch_verdict))} | crashes={esc(str(orch_crashes))}</div>
            </div>
            <div class="k">
              <div class="label">Cloud Package</div>
              <div class="value">verdict={esc(str(package_verdict))} | required_missing={esc(str(len(package_missing) if isinstance(package_missing, list) else 'UNK'))}</div>
            </div>
            <div class="k">
              <div class="label">Primary Outputs</div>
              <div class="value">
                commander_brief_latest.txt<br/>
                week3_demo_narrative_latest.txt<br/>
                legal_case_snapshot_latest.txt<br/>
                week3_operator_summary_latest.txt
              </div>
            </div>
          </div>

          <div class="divider"></div>

          <div class="panel-title" style="margin-bottom:8px;">10-SECOND SIGNAL (Operator Summary)</div>
          <div class="mono">{esc(ops_summary_head or "Unavailable.")}</div>

          <div class="divider"></div>

          <div class="panel-title" style="margin-bottom:8px;">DEMO NARRATIVE (Read First)</div>
          <div class="mono">{esc(narrative_head or "Unavailable.")}</div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-head">
          <div class="panel-title">COMMANDER SAFE PREVIEWS</div>
          <div class="badge">Bounded / Demo-Safe</div>
        </div>
        <div class="panel-body">
          <div class="panel-title" style="margin-bottom:8px;">Commander Brief (head)</div>
          <div class="mono">{esc(commander_head or "Unavailable.")}</div>

          <div class="divider"></div>

          <div class="panel-title" style="margin-bottom:8px;">Legal Snapshot (head)</div>
          <div class="mono">{esc(legal_head or "Unavailable.")}</div>

          <div class="divider"></div>

          <div class="small">
            <b>Non-negotiables:</b><br/>
            • No attribution from synthetic telemetry.<br/>
            • No baselines updated during demo lock.<br/>
            • Operator judgment applies before escalation.<br/>
          </div>

          <div class="footer">
            Files live under <code>docs/briefs</code>, <code>docs/validation</code>, <code>docs/packages</code>.
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
"""

    txt = []
    txt.append("WEEK-3 EXECUTIVE SUMMARY — OBASI (DEMO SAFE)")
    txt.append(f"generated_at_utc: {generated}")
    txt.append(f"context: {context}")
    txt.append("")
    txt.append("STATUS:")
    txt.append(f"- orchestrator_verdict: {orch_verdict}")
    txt.append(f"- readiness_verdict: {readiness_verdict} (strict={readiness_strict})")
    txt.append(f"- package_verdict: {package_verdict}")
    txt.append("")
    if banner:
        txt.append("DEMO LOCK:")
        txt.append(banner)
        txt.append("")
    txt.append("OPERATOR SUMMARY (head):")
    txt.append(ops_summary_head or "Unavailable.")
    txt.append("")
    txt.append("NARRATIVE (head):")
    txt.append(narrative_head or "Unavailable.")
    txt.append("")
    txt_text = "\n".join(txt).strip() + "\n"

    latest_html = PACKAGES_DIR / "week3_executive_summary_latest.html"
    stamped_html = PACKAGES_DIR / f"week3_executive_summary_{stamp}.html"
    latest_txt = PACKAGES_DIR / "week3_executive_summary_latest.txt"
    stamped_txt = PACKAGES_DIR / f"week3_executive_summary_{stamp}.txt"

    try:
        latest_html.write_text(html, encoding="utf-8")
    except Exception:
        pass
    try:
        stamped_html.write_text(html, encoding="utf-8")
    except Exception:
        pass
    try:
        latest_txt.write_text(txt_text, encoding="utf-8")
    except Exception:
        pass
    try:
        stamped_txt.write_text(txt_text, encoding="utf-8")
    except Exception:
        pass

    res: Dict[str, Any] = {
        "generated_at_utc": generated,
        "context": context,
        "html_latest": _safe_rel(latest_html),
        "html_stamped": _safe_rel(stamped_html),
        "txt_latest": _safe_rel(latest_txt),
        "txt_stamped": _safe_rel(stamped_txt),
    }
    return res


def main() -> int:
    out = write_week3_executive_summary()
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

