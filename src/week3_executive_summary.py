# src/week3_executive_summary.py
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
BRIEFS_DIR = ROOT / "docs" / "briefs"
VALIDATION_DIR = ROOT / "docs" / "validation"
PACKAGES_DIR = ROOT / "docs" / "packages"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _safe_rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except Exception:
        return str(p)


def _read_text_best_effort(p: Path, max_chars: int = 1600) -> str:
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
    Premium, demo-safe Executive Summary HTML (HUD theme) + interactive artifact viewer.
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

    # Best-effort reads (never crash)
    orch_json = _read_json_best_effort(BRIEFS_DIR / "week3_demo_orchestrator_latest.json")
    readiness_json = _read_json_best_effort(VALIDATION_DIR / "week3_demo_readiness_gate_latest.json")
    pack_manifest = _read_json_best_effort(PACKAGES_DIR / "week3_cloud_demo_package_manifest_latest.json")

    commander_head = _read_text_best_effort(BRIEFS_DIR / "commander_brief_latest.txt", max_chars=1100)
    narrative_head = _read_text_best_effort(BRIEFS_DIR / "week3_demo_narrative_latest.txt", max_chars=1100)
    legal_head = _read_text_best_effort(BRIEFS_DIR / "legal_case_snapshot_latest.txt", max_chars=1100)
    ops_summary_head = _read_text_best_effort(BRIEFS_DIR / "week3_operator_summary_latest.txt", max_chars=500)

    orch_verdict = str(orch_json.get("verdict", "UNKNOWN")).upper()
    orch_crashes = orch_json.get("crashes", "UNKNOWN")
    readiness_verdict = str(readiness_json.get("verdict", "UNKNOWN")).upper()
    readiness_crashes = readiness_json.get("crashes", "UNKNOWN")
    readiness_strict = readiness_json.get("strict", True)
    package_verdict = str(pack_manifest.get("verdict", "UNKNOWN")).upper()
    package_missing = pack_manifest.get("required_missing", [])

    subtitle = "Obasi Command Center — Week-3 Cloud-Ready Demo Package"
    safety_line = "Assessment is probabilistic and bounded; operator judgment applies."
    demo_line = "DEMO MODE ACTIVE — READ ONLY" if banner else "DEMO LOCK NOT DETECTED (enable for stakeholder demo)"

    # Viewer targets (relative to docs/packages HTML location)
    # NOTE: HTML lives in docs/packages -> use ../briefs and ../validation paths.
    viewer_items = [
        ("Commander Brief", "../briefs/commander_brief_latest.txt", "Brief"),
        ("Demo Narrative", "../briefs/week3_demo_narrative_latest.txt", "Narrative"),
        ("Legal Snapshot", "../briefs/legal_case_snapshot_latest.txt", "Legal"),
        ("Operator Summary", "../briefs/week3_operator_summary_latest.txt", "Ops"),
        ("Readiness Gate", "../validation/week3_demo_readiness_gate_latest.txt", "Gate"),
        ("Orchestrator", "../briefs/week3_demo_orchestrator_latest.txt", "Orch"),
        ("Package Manifest", "week3_cloud_demo_package_manifest_latest.json", "Pkg"),
    ]

    def esc(s: str) -> str:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # HUD HTML with interactive viewer (iframe)
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Obasi Command Center — Week-3 Executive Summary</title>
  <style>
    :root {{
      --bg0: #05070c;
      --bg1: #0a1221;
      --panel: rgba(10, 16, 30, 0.78);
      --panel2: rgba(8, 12, 22, 0.55);
      --line: rgba(90, 220, 255, 0.18);
      --glow: rgba(90, 220, 255, 0.30);
      --text: rgba(230, 245, 255, 0.92);
      --muted: rgba(190, 220, 240, 0.72);
      --accent: rgba(90, 220, 255, 0.95);
      --good: rgba(120, 255, 190, 0.95);
      --bad: rgba(255, 130, 130, 0.95);
      --warn: rgba(255, 210, 130, 0.95);
      --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      --sans: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: var(--sans);
      background:
        radial-gradient(1100px 700px at 20% 10%, rgba(90,220,255,0.10), transparent 60%),
        radial-gradient(900px 700px at 95% 20%, rgba(120,255,190,0.06), transparent 55%),
        radial-gradient(900px 700px at 20% 90%, rgba(255,210,130,0.04), transparent 55%),
        linear-gradient(180deg, var(--bg0), var(--bg1));
      color: var(--text);
      min-height: 100vh;
    }}
    .scanlines::before {{
      content:"";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background: repeating-linear-gradient(
        to bottom,
        rgba(255,255,255,0.02),
        rgba(255,255,255,0.02) 1px,
        rgba(0,0,0,0.0) 3px,
        rgba(0,0,0,0.0) 6px
      );
      opacity: 0.30;
      mix-blend-mode: overlay;
    }}
    .topbar {{
      position: sticky;
      top: 0;
      z-index: 30;
      backdrop-filter: blur(10px);
      background: rgba(5,7,12,0.58);
      border-bottom: 1px solid var(--line);
    }}
    .topbar-inner {{
      max-width: 1240px;
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
      line-height: 1.15;
    }}
    .brand .title {{
      font-weight: 900;
      letter-spacing: 1.2px;
      font-size: 13px;
      text-transform: uppercase;
      color: var(--accent);
      text-shadow: 0 0 16px var(--glow);
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
      max-width: 1240px;
      margin: 0 auto;
      padding: 18px 16px 30px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: 0.95fr 1.05fr;
      gap: 14px;
    }}
    @media (max-width: 1080px) {{
      .grid {{ grid-template-columns: 1fr; }}
      .meta {{ text-align: left; }}
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      box-shadow: 0 0 0 1px rgba(90,220,255,0.06) inset, 0 18px 60px rgba(0,0,0,0.45);
      border-radius: 14px;
      overflow: hidden;
      position: relative;
    }}
    .panel::before {{
      content: "";
      position: absolute;
      inset: 0;
      background: radial-gradient(900px 220px at 20% 0%, rgba(90,220,255,0.06), transparent 62%);
      pointer-events: none;
    }}
    .panel-head {{
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
    }}
    .panel-title {{
      font-weight: 900;
      letter-spacing: 0.8px;
      font-size: 12px;
      text-transform: uppercase;
      color: rgba(235,250,255,0.94);
    }}
    .badge {{
      font-family: var(--mono);
      font-size: 11px;
      padding: 6px 10px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: rgba(0,0,0,0.25);
      color: var(--muted);
      white-space: nowrap;
    }}
    .badge.good {{ color: var(--good); border-color: rgba(120,255,190,0.28); }}
    .badge.bad  {{ color: var(--bad);  border-color: rgba(255,130,130,0.28); }}
    .badge.warn {{ color: var(--warn); border-color: rgba(255,210,130,0.28); }}
    .panel-body {{
      padding: 12px 14px;
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
      letter-spacing: 0.5px;
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
    .tiles {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
    }}
    @media (max-width: 1080px) {{
      .tiles {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    .tile {{
      border-radius: 14px;
      border: 1px solid rgba(90,220,255,0.16);
      background: linear-gradient(180deg, rgba(0,0,0,0.30), rgba(0,0,0,0.20));
      padding: 12px 12px;
      cursor: pointer;
      position: relative;
      overflow: hidden;
      transition: transform 0.08s ease, box-shadow 0.12s ease, border-color 0.12s ease;
      box-shadow: 0 0 0 1px rgba(90,220,255,0.05) inset;
    }}
    .tile::before {{
      content:"";
      position:absolute;
      inset:-40px -60px auto -60px;
      height: 120px;
      background: radial-gradient(200px 70px at 30% 50%, rgba(90,220,255,0.14), transparent 65%);
      transform: rotate(-8deg);
      pointer-events: none;
    }}
    .tile:hover {{
      transform: translateY(-1px);
      border-color: rgba(90,220,255,0.32);
      box-shadow: 0 0 22px rgba(90,220,255,0.14), 0 0 0 1px rgba(90,220,255,0.08) inset;
    }}
    .tile-top {{
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 8px;
      margin-bottom: 6px;
    }}
    .tile-name {{
      font-weight: 900;
      font-size: 12px;
      letter-spacing: 0.6px;
      text-transform: uppercase;
      color: rgba(235,250,255,0.92);
    }}
    .tile-tag {{
      font-family: var(--mono);
      font-size: 11px;
      color: rgba(190,220,240,0.75);
      border: 1px solid rgba(90,220,255,0.16);
      padding: 3px 8px;
      border-radius: 999px;
      background: rgba(0,0,0,0.22);
      white-space: nowrap;
    }}
    .tile-path {{
      font-family: var(--mono);
      font-size: 11px;
      color: rgba(190,220,240,0.70);
      opacity: 0.95;
    }}
    .viewer {{
      border-radius: 14px;
      border: 1px solid rgba(90,220,255,0.18);
      background: rgba(0,0,0,0.24);
      overflow: hidden;
    }}
    .viewer-head {{
      display:flex;
      align-items:center;
      justify-content: space-between;
      gap: 10px;
      padding: 10px 12px;
      border-bottom: 1px solid rgba(90,220,255,0.16);
      background: rgba(0,0,0,0.18);
    }}
    .viewer-title {{
      font-weight: 900;
      font-size: 12px;
      letter-spacing: 0.6px;
      text-transform: uppercase;
      color: rgba(235,250,255,0.92);
    }}
    .viewer-actions a {{
      font-family: var(--mono);
      font-size: 11px;
      color: var(--accent);
      text-decoration: none;
      border: 1px solid rgba(90,220,255,0.18);
      padding: 6px 10px;
      border-radius: 10px;
      background: rgba(0,0,0,0.18);
      margin-left: 8px;
    }}
    iframe {{
      width: 100%;
      height: 560px;
      border: 0;
      background: rgba(0,0,0,0.18);
    }}
    .small {{
      font-size: 12px;
      color: var(--muted);
      line-height: 1.45;
    }}
  </style>
</head>
<body class="scanlines">
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
          <div class="badge {"good" if orch_verdict=="PASS" else "bad" if orch_verdict=="FAIL" else "warn"}">
            Orchestrator: {esc(orch_verdict)}
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
              <div class="value">verdict={esc(readiness_verdict)} | strict={esc(str(readiness_strict))} | crashes={esc(str(readiness_crashes))}</div>
            </div>
            <div class="k">
              <div class="label">Cloud Package</div>
              <div class="value">verdict={esc(package_verdict)} | required_missing={esc(str(len(package_missing) if isinstance(package_missing, list) else "UNK"))}</div>
            </div>
            <div class="k">
              <div class="label">Operator Summary (head)</div>
              <div class="value">{esc((ops_summary_head.splitlines() or ["Unavailable."])[0])}</div>
            </div>
            <div class="k">
              <div class="label">Non-negotiables</div>
              <div class="value">No baselines updated during demo lock.<br/>No attribution from synthetic telemetry.<br/>Operator judgment applies.</div>
            </div>
          </div>

          <div class="divider"></div>

          <div class="panel-title" style="margin-bottom:10px;">TACTICAL TILES (click to load viewer)</div>
          <div class="tiles">
"""

    # tiles
    for name, path, tag in viewer_items:
        html += f"""
            <div class="tile" onclick="loadArtifact('{esc(path)}','{esc(name)}')">
              <div class="tile-top">
                <div class="tile-name">{esc(name)}</div>
                <div class="tile-tag">{esc(tag)}</div>
              </div>
              <div class="tile-path">{esc(path)}</div>
            </div>
"""

    html += f"""
          </div>

          <div class="divider"></div>

          <div class="panel-title" style="margin-bottom:8px;">DEMO NARRATIVE (head)</div>
          <div class="mono">{esc(narrative_head or "Unavailable.")}</div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-head">
          <div class="panel-title">LIVE VIEWER</div>
          <div class="badge">Artifact Preview</div>
        </div>
        <div class="panel-body">
          <div class="viewer">
            <div class="viewer-head">
              <div class="viewer-title" id="viewerTitle">Commander Brief</div>
              <div class="viewer-actions">
                <a id="openNewTab" href="../briefs/commander_brief_latest.txt" target="_blank" rel="noopener">Open</a>
              </div>
            </div>
            <iframe id="viewerFrame" src="../briefs/commander_brief_latest.txt"></iframe>
          </div>

          <div class="divider"></div>

          <div class="panel-title" style="margin-bottom:8px;">Commander Brief (head)</div>
          <div class="mono">{esc(commander_head or "Unavailable.")}</div>

          <div class="divider"></div>

          <div class="panel-title" style="margin-bottom:8px;">Legal Snapshot (head)</div>
          <div class="mono">{esc(legal_head or "Unavailable.")}</div>

          <div class="divider"></div>

          <div class="small">
            Tip: This HTML is designed to be opened locally from <code>docs/packages/</code>.
            Tiles load artifacts via relative paths (<code>../briefs</code>, <code>../validation</code>).
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    function loadArtifact(path, title) {{
      try {{
        var frame = document.getElementById('viewerFrame');
        var t = document.getElementById('viewerTitle');
        var open = document.getElementById('openNewTab');
        t.textContent = title || 'Artifact';
        frame.src = path;
        open.href = path;
      }} catch (e) {{}}
    }}
  </script>
</body>
</html>
"""

    # TXT mirror (simple)
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

    return {
        "generated_at_utc": generated,
        "context": context,
        "html_latest": _safe_rel(latest_html),
        "html_stamped": _safe_rel(stamped_html),
        "txt_latest": _safe_rel(latest_txt),
        "txt_stamped": _safe_rel(stamped_txt),
    }


def main() -> int:
    out = write_week3_executive_summary()
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

