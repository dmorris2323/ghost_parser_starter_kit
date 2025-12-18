import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import streamlit as st
import streamlit.components.v1 as components

# =========================
# Spectral Owl explain hooks
# =========================
try:
    from spectral_owl_explain import (
        explain_installation_threat_map,
        explain_commander_brief,
        explain_legal_snapshot,
    )
except Exception:
    # Hard fail not allowed in demo GUI
    def explain_installation_threat_map() -> Dict[str, str]:
        return {"ERROR": "spectral_owl_explain.py not available."}

    def explain_commander_brief() -> Dict[str, str]:
        return {"ERROR": "spectral_owl_explain.py not available."}

    def explain_legal_snapshot() -> Dict[str, str]:
        return {"ERROR": "spectral_owl_explain.py not available."}


BASE = Path(".")
DOCS = BASE / "docs"
BRIEFS = DOCS / "briefs"
VALIDATION = DOCS / "validation"
BASEDEF = DOCS / "base_defense"


# -------------------------
# Safe file reads
# -------------------------
def _read_text_best_effort(p: Path, max_chars: int = 120_000) -> str:
    try:
        if not p.exists():
            return ""
        txt = p.read_text(encoding="utf-8", errors="ignore")
        if len(txt) > max_chars:
            return txt[:max_chars] + "\n\n[TRUNCATED]"
        return txt
    except Exception:
        return ""


def _read_json_best_effort(p: Path) -> Optional[dict]:
    try:
        if not p.exists():
            return None
        return json.loads(p.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return None


def _open_file_in_os(path: Path) -> str:
    """
    Best effort 'open' for macOS demo convenience.
    Never crash.
    """
    try:
        if not path.exists():
            return "MISSING"
        # macOS
        os.system(f'open "{str(path)}"')
        return "OK"
    except Exception:
        return "ERROR"


# -------------------------
# HUD radar animation
# -------------------------
def _radar_widget(height_px: int = 260) -> None:
    """
    Pure eye-candy radar sweep. No live tracking claims.
    """
    html = f"""
    <div style="border:1px solid rgba(80,255,180,0.25); border-radius:14px; padding:10px; background: rgba(0,0,0,0.45);">
      <div style="font-family: ui-monospace, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
                  color: rgba(140,255,210,0.95); font-size: 12px; letter-spacing: 0.06em; margin-bottom:6px;">
        OBASI RADAR (VISUAL ONLY)
      </div>
      <canvas id="radar" width="560" height="{height_px}" style="width:100%; height:{height_px}px;"></canvas>
      <div style="margin-top:6px; color: rgba(160,255,220,0.75); font-size:11px; font-family: ui-monospace, monospace;">
        Demo visualization. Not live tracking. No intent/attribution implied.
      </div>
    </div>
    <script>
      const canvas = document.getElementById('radar');
      const ctx = canvas.getContext('2d');
      const W = canvas.width, H = canvas.height;
      const cx = W*0.35, cy = H*0.55;
      const R = Math.min(W,H)*0.42;

      function rand(min,max){{ return Math.random()*(max-min)+min; }}

      const blips = Array.from({{length: 14}}).map(()=>({{
        r: rand(R*0.15, R*0.98),
        a: rand(0, Math.PI*2),
        s: rand(0.3, 1.0),
        p: rand(0.2, 1.0)
      }}));

      let t = 0;

      function draw() {{
        t += 0.018;
        ctx.clearRect(0,0,W,H);

        // background
        ctx.fillStyle = 'rgba(0,0,0,0.0)';
        ctx.fillRect(0,0,W,H);

        // grid circles
        for (let i=1;i<=4;i++) {{
          ctx.beginPath();
          ctx.arc(cx,cy,(R*i/4),0,Math.PI*2);
          ctx.strokeStyle = 'rgba(80,255,180,0.10)';
          ctx.lineWidth = 1;
          ctx.stroke();
        }}

        // cross lines
        ctx.beginPath();
        ctx.moveTo(cx-R, cy); ctx.lineTo(cx+R, cy);
        ctx.moveTo(cx, cy-R); ctx.lineTo(cx, cy+R);
        ctx.strokeStyle = 'rgba(80,255,180,0.10)';
        ctx.stroke();

        // sweep
        const sweepA = (t % (Math.PI*2));
        const grad = ctx.createRadialGradient(cx,cy,0,cx,cy,R);
        grad.addColorStop(0, 'rgba(80,255,180,0.00)');
        grad.addColorStop(0.65, 'rgba(80,255,180,0.08)');
        grad.addColorStop(1, 'rgba(80,255,180,0.00)');

        ctx.save();
        ctx.translate(cx,cy);
        ctx.rotate(sweepA);
        ctx.beginPath();
        ctx.moveTo(0,0);
        ctx.arc(0,0,R, -0.12, 0.12);
        ctx.closePath();
        ctx.fillStyle = grad;
        ctx.fill();
        ctx.restore();

        // blips
        blips.forEach((b, idx)=>{{
          const x = cx + Math.cos(b.a + t*0.2*b.s)*b.r;
          const y = cy + Math.sin(b.a + t*0.2*b.s)*b.r;
          const pulse = (Math.sin(t*3 + idx) * 0.5 + 0.5);
          const alpha = 0.15 + pulse*0.55*b.p;

          ctx.beginPath();
          ctx.arc(x,y, 2.0 + pulse*2.2, 0, Math.PI*2);
          ctx.fillStyle = `rgba(140,255,210,${{alpha}})`;
          ctx.fill();

          ctx.beginPath();
          ctx.arc(x,y, 7.0 + pulse*6.0, 0, Math.PI*2);
          ctx.strokeStyle = `rgba(140,255,210,${{alpha*0.35}})`;
          ctx.lineWidth = 1;
          ctx.stroke();
        }});

        requestAnimationFrame(draw);
      }}
      draw();
    </script>
    """
    components.html(html, height=height_px + 80)


# -------------------------
# UI helpers
# -------------------------
def _hud_title(text: str) -> None:
    st.markdown(
        f"""
        <div style="
            padding: 14px 16px;
            border-radius: 16px;
            background: linear-gradient(135deg, rgba(0,0,0,0.72), rgba(0,40,30,0.32));
            border: 1px solid rgba(80,255,180,0.25);
            box-shadow: 0 0 24px rgba(80,255,180,0.08);
            ">
          <div style="font-size: 22px; font-weight: 800; letter-spacing: 0.06em; color: rgba(200,255,235,0.95);">
            {text}
          </div>
          <div style="margin-top:6px; font-size: 12px; letter-spacing: 0.08em; color: rgba(160,255,220,0.65);">
            Demo-safe • Bounded statements • Operator judgment applies
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _sidebar_explain(title: str, payload: Dict[str, str]) -> None:
    st.sidebar.markdown("## 🦉 Spectral Owl Explanation")
    st.sidebar.caption(title)
    for k, v in payload.items():
        st.sidebar.markdown(f"**{k}**")
        st.sidebar.write(v)


def main() -> int:
    st.set_page_config(
        page_title="Obasi Command Center",
        page_icon="🦉",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Global HUD styling
    st.markdown(
        """
        <style>
          .stApp { background: radial-gradient(circle at 20% 10%, rgba(0,35,25,0.55), rgba(0,0,0,0.92)); }
          h1,h2,h3 { letter-spacing: 0.05em; }
          [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(0,0,0,0.92), rgba(0,25,18,0.55));
            border-right: 1px solid rgba(80,255,180,0.18);
          }
          .hudCard {
            border: 1px solid rgba(80,255,180,0.22);
            border-radius: 16px;
            padding: 14px;
            background: rgba(0,0,0,0.52);
            box-shadow: 0 0 22px rgba(80,255,180,0.06);
          }
          .hudLabel {
            font-family: ui-monospace, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
            color: rgba(160,255,220,0.85);
            font-size: 12px;
            letter-spacing: 0.10em;
            margin-bottom: 8px;
          }
          .hudText {
            color: rgba(220,255,245,0.92);
            font-size: 14px;
            line-height: 1.35;
            white-space: pre-wrap;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )

    _hud_title("OBASI COMMAND CENTER — WEEK-3 DEMO HUD")

    # Sidebar controls
    st.sidebar.markdown("### Controls")
    if st.sidebar.button("Refresh / Reload"):
        st.rerun()

    show_raw = st.sidebar.toggle("Show raw JSON where available", value=False)

    # Load artifacts (best effort)
    commander_txt = BRIEFS / "commander_brief_latest.txt"
    commander_json = BRIEFS / "commander_brief_latest.json"
    legal_txt = BRIEFS / "legal_case_snapshot_latest.txt"
    legal_json = BRIEFS / "legal_case_snapshot_latest.json"
    operator_summary_txt = BRIEFS / "week3_operator_summary_latest.txt"
    narrative_txt = BRIEFS / "week3_demo_narrative_latest.txt"
    mobile_manifest_json = BRIEFS / "mobile_enjoy_manifest_latest.json"

    threat_map_txt = BASEDEF / "installation_threat_map_latest.txt"
    threat_map_json = BASEDEF / "installation_threat_map_latest.json"

    # Read
    commander_text = _read_text_best_effort(commander_txt)
    legal_text = _read_text_best_effort(legal_txt)
    operator_text = _read_text_best_effort(operator_summary_txt)
    narrative_text = _read_text_best_effort(narrative_txt)
    threat_text = _read_text_best_effort(threat_map_txt)

    commander_obj = _read_json_best_effort(commander_json)
    legal_obj = _read_json_best_effort(legal_json)
    threat_obj = _read_json_best_effort(threat_map_json)
    mobile_obj = _read_json_best_effort(mobile_manifest_json)

    # Layout
    left, right = st.columns([0.42, 0.58], gap="large")

    with left:
        st.markdown('<div class="hudCard">', unsafe_allow_html=True)
        st.markdown('<div class="hudLabel">RADAR VISUAL</div>', unsafe_allow_html=True)
        _radar_widget(height_px=250)
        if st.button("🦉 Explain Radar / Threat Map"):
            _sidebar_explain("Installation Threat Map (bounded)", explain_installation_threat_map())
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="hudCard" style="margin-top:14px;">', unsafe_allow_html=True)
        st.markdown('<div class="hudLabel">INSTALLATION THREAT MAP (ARTIFACT)</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns([0.34, 0.33, 0.33])
        with c1:
            if st.button("Open TXT"):
                _open_file_in_os(threat_map_txt)
        with c2:
            if st.button("Open JSON"):
                _open_file_in_os(threat_map_json)
        with c3:
            st.write("")

        st.markdown(f'<div class="hudText">{threat_text or "MISSING: docs/base_defense/installation_threat_map_latest.txt"}</div>', unsafe_allow_html=True)

        if show_raw and threat_obj is not None:
            st.json(threat_obj)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="hudCard" style="margin-top:14px;">', unsafe_allow_html=True)
        st.markdown('<div class="hudLabel">WEEK-3 OPERATOR SUMMARY</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="hudText">{operator_text or "MISSING: docs/briefs/week3_operator_summary_latest.txt"}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="hudCard">', unsafe_allow_html=True)
        st.markdown('<div class="hudLabel">COMMANDER BRIEF</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns([0.34, 0.33, 0.33])
        with c1:
            if st.button("Open Brief TXT"):
                _open_file_in_os(commander_txt)
        with c2:
            if st.button("Open Brief JSON"):
                _open_file_in_os(commander_json)
        with c3:
            if st.button("🦉 Explain Commander Brief"):
                _sidebar_explain("Commander Brief (bounded)", explain_commander_brief())

        st.markdown(f'<div class="hudText">{commander_text or "MISSING: docs/briefs/commander_brief_latest.txt"}</div>', unsafe_allow_html=True)

        if show_raw and commander_obj is not None:
            st.json(commander_obj)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="hudCard" style="margin-top:14px;">', unsafe_allow_html=True)
        st.markdown('<div class="hudLabel">LEGAL CASE SNAPSHOT (SHARI HOOK)</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns([0.34, 0.33, 0.33])
        with c1:
            if st.button("Open Legal TXT"):
                _open_file_in_os(legal_txt)
        with c2:
            if st.button("Open Legal JSON"):
                _open_file_in_os(legal_json)
        with c3:
            if st.button("🦉 Explain Legal Snapshot"):
                _sidebar_explain("Legal Snapshot (bounded)", explain_legal_snapshot())

        st.markdown(f'<div class="hudText">{legal_text or "MISSING: docs/briefs/legal_case_snapshot_latest.txt"}</div>', unsafe_allow_html=True)

        if show_raw and legal_obj is not None:
            st.json(legal_obj)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="hudCard" style="margin-top:14px;">', unsafe_allow_html=True)
        st.markdown('<div class="hudLabel">DEMO NARRATIVE (RUNBOOK)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="hudText">{narrative_text or "MISSING: docs/briefs/week3_demo_narrative_latest.txt"}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="hudCard" style="margin-top:14px;">', unsafe_allow_html=True)
        st.markdown('<div class="hudLabel">MOBILE ENJOY MANIFEST (DEMO PACK PATHS)</div>', unsafe_allow_html=True)
        if mobile_obj is None:
            st.markdown('<div class="hudText">MISSING: docs/briefs/mobile_enjoy_manifest_latest.json</div>', unsafe_allow_html=True)
        else:
            st.json(mobile_obj)
        st.markdown("</div>", unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Paths (debug)")
    st.sidebar.code(
        "\n".join(
            [
                f"commander_txt: {commander_txt}",
                f"threat_map_txt: {threat_map_txt}",
                f"legal_txt: {legal_txt}",
                f"operator_summary_txt: {operator_summary_txt}",
                f"narrative_txt: {narrative_txt}",
                f"mobile_manifest_json: {mobile_manifest_json}",
            ]
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

