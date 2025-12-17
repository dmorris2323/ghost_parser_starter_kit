# src/obasi_command_center.py
"""
OBASI COMMAND CENTER (Module 5E — Demo Auto-Sequence)
- Premium HUD styling (Batman/Iron-Man command center)
- PRESENTATION MODE + BRIEFING VIEW (Module 5D)
- NEW in 5E: Demo Auto-Sequence (Start/Stop)
    * Automatically advances focus: readiness -> operator -> commander -> legal -> validation -> overview
    * Adjustable seconds per step
    * One-cycle or looping
    * Uses safe refresh (no mutation), keeps session state

Run:
  streamlit run src/obasi_command_center.py
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st

# Optional demo lock (expected in your repo)
try:
    from demo_lock import is_demo_locked, demo_lock_banner
except Exception:  # pragma: no cover
    def is_demo_locked() -> bool:
        return False

    def demo_lock_banner() -> str:
        return (
            "DEMO MODE ACTIVE — READ ONLY\n"
            "No baselines updated. No training. No mutation.\n"
            "Assessment is probabilistic and bounded; operator judgment applies."
        )


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
BRIEFS = DOCS / "briefs"
VALIDATION = DOCS / "validation"

DEMO_SEQUENCE = ["readiness", "operator", "commander", "legal", "validation", "overview"]


# ----------------------------
# Helpers
# ----------------------------
def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _read_json(p: Path) -> dict:
    try:
        return json.loads(_read_text(p) or "{}")
    except Exception:
        return {}


def _exists(p: Path) -> bool:
    try:
        return p.exists()
    except Exception:
        return False


def _verdict_color(v: str) -> str:
    v = (v or "").strip().upper()
    if v == "PASS":
        return "ok"
    if v == "FAIL":
        return "bad"
    return "warn"


def _pick_verdict(payload: dict) -> str:
    for k in ("verdict", "status", "result"):
        if isinstance(payload, dict) and k in payload and isinstance(payload[k], str):
            return payload[k].strip().upper()
    return "UNKNOWN"


def _as_int(x, default=0) -> int:
    try:
        return int(x)
    except Exception:
        return default


def _safe_snip(s: str, max_chars: int = 1400) -> str:
    s = s or ""
    if len(s) <= max_chars:
        return s
    return s[:max_chars] + "\n…(truncated)…"


def _now_epoch() -> float:
    # Use Streamlit's monotonic-ish time via datetime; good enough for demo stepping
    return datetime.now(timezone.utc).timestamp()


def _init_state() -> None:
    if "focus" not in st.session_state:
        st.session_state["focus"] = "overview"
    if "compact" not in st.session_state:
        st.session_state["compact"] = True
    if "show_json" not in st.session_state:
        st.session_state["show_json"] = True
    if "show_paths" not in st.session_state:
        st.session_state["show_paths"] = False

    # Module 5D
    if "presentation" not in st.session_state:
        st.session_state["presentation"] = True
    if "briefing_view" not in st.session_state:
        st.session_state["briefing_view"] = True

    # Module 5E: auto-sequence
    if "seq_running" not in st.session_state:
        st.session_state["seq_running"] = False
    if "seq_start_ts" not in st.session_state:
        st.session_state["seq_start_ts"] = 0.0
    if "seq_seconds_per_step" not in st.session_state:
        st.session_state["seq_seconds_per_step"] = 12
    if "seq_loop" not in st.session_state:
        st.session_state["seq_loop"] = True
    if "seq_last_step" not in st.session_state:
        st.session_state["seq_last_step"] = -1


# ----------------------------
# HUD Styling
# ----------------------------
def _inject_hud_css(presentation: bool) -> None:
    size_scale = 1.10 if presentation else 1.00
    code_font = "1.00rem" if presentation else "0.92rem"
    pad_top = "0.55rem" if presentation else "1.05rem"
    max_w = "1440px" if presentation else "1280px"

    st.markdown(
        f"""
<style>
:root{{
  --bg0:#070A0F;
  --bg1:#0B1220;
  --text:#DDE7FF;
  --muted:#8BA3C7;
  --cyan:#14F1FF;
  --cyan2:#00B7FF;
  --amber:#FFB020;
  --red:#FF3B3B;
  --green:#3CFF9A;
  --shadow: 0 12px 40px rgba(0,0,0,.55);
}}

.stApp {{
  background: radial-gradient(1200px 800px at 15% 20%, rgba(20,241,255,.09), rgba(0,0,0,0) 55%),
              radial-gradient(900px 700px at 85% 30%, rgba(0,183,255,.08), rgba(0,0,0,0) 55%),
              linear-gradient(180deg, var(--bg0), var(--bg1) 30%, var(--bg0));
  color: var(--text);
  font-size: {size_scale}em;
}}

.block-container{{
  padding-top: {pad_top};
  padding-bottom: 2rem;
  max-width: {max_w};
}}

header {{visibility: hidden;}}
footer {{visibility: hidden;}}

.hud-title{{
  text-align:center;
  font-weight: 900;
  letter-spacing: .22em;
  text-transform: uppercase;
  font-size: 2.55rem;
  margin: .25rem 0 .18rem 0;
  color: var(--cyan);
  text-shadow: 0 0 18px rgba(20,241,255,.22);
}}
.hud-sub{{
  text-align:center;
  font-size: 1.02rem;
  color: var(--muted);
  letter-spacing: .08em;
  margin-bottom: .6rem;
}}

.banner{{
  border: 1px solid rgba(20,241,255,.35);
  background: linear-gradient(180deg, rgba(20,241,255,.08), rgba(0,0,0,0));
  border-radius: 16px;
  padding: 14px 16px;
  box-shadow: var(--shadow);
  position: relative;
  overflow: hidden;
}}
.banner:before{{
  content:"";
  position:absolute;
  inset:-80px -60px auto auto;
  width: 260px;
  height: 260px;
  background: radial-gradient(circle, rgba(20,241,255,.18), rgba(0,0,0,0) 70%);
  filter: blur(2px);
}}
.banner .label{{
  font-size:.78rem;
  text-transform:uppercase;
  letter-spacing:.18em;
  color: var(--muted);
  margin-bottom: 4px;
}}
.banner .msg{{
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  white-space: pre-wrap;
  color: var(--text);
  line-height: 1.35;
}}

.chips{{
  display:flex;
  gap: 10px;
  flex-wrap: wrap;
  margin: 12px 0 10px 0;
}}
.chip{{
  border: 1px solid rgba(221,231,255,.14);
  background: linear-gradient(180deg, rgba(255,255,255,.05), rgba(0,0,0,0));
  border-radius: 999px;
  padding: 10px 14px;
  box-shadow: 0 10px 30px rgba(0,0,0,.35);
  min-width: 220px;
}}
.chip .k{{
  font-size: .72rem;
  text-transform: uppercase;
  letter-spacing: .18em;
  color: var(--muted);
}}
.chip .v{{
  font-size: 1.38rem;
  font-weight: 900;
  letter-spacing: .04em;
  margin-top: 4px;
}}

.tiles{{
  display:flex;
  gap: 12px;
  flex-wrap: wrap;
  margin: 10px 0 18px 0;
}}
.tile{{
  border: 1px solid rgba(20,241,255,.16);
  background: linear-gradient(180deg, rgba(11,18,32,.92), rgba(7,10,15,.86));
  border-radius: 16px;
  padding: 12px 14px;
  box-shadow: var(--shadow);
  min-width: 210px;
}}
.tile .t{{
  font-size: .72rem;
  text-transform: uppercase;
  letter-spacing: .18em;
  color: var(--muted);
}}
.tile .n{{
  font-size: 1.55rem;
  font-weight: 900;
  margin-top: 4px;
}}

.dot{{
  display:inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 8px;
}}
.dot.ok{{ background: var(--green); box-shadow: 0 0 18px rgba(60,255,154,.26); }}
.dot.bad{{ background: var(--red);   box-shadow: 0 0 18px rgba(255,59,59,.22); }}
.dot.warn{{ background: var(--amber); box-shadow: 0 0 18px rgba(255,176,32,.22); }}

@keyframes pulseGlow {{
  0%   {{ transform: scale(1.0); filter: brightness(1.0); }}
  50%  {{ transform: scale(1.18); filter: brightness(1.35); }}
  100% {{ transform: scale(1.0); filter: brightness(1.0); }}
}}
.pulse {{ animation: pulseGlow 1.6s ease-in-out infinite; }}

details {{
  border-radius: 14px !important;
  border: 1px solid rgba(221,231,255,.12) !important;
  background: rgba(10,19,36,.45) !important;
}}

.stCodeBlock, pre {{
  background: rgba(5,8,12,.65) !important;
  border: 1px solid rgba(221,231,255,.10) !important;
  font-size: {code_font} !important;
}}

.stButton button{{
  border-radius: 999px;
  border: 1px solid rgba(20,241,255,.35);
  background: linear-gradient(180deg, rgba(20,241,255,.12), rgba(0,0,0,0));
  color: var(--text);
  box-shadow: 0 12px 30px rgba(0,0,0,.35);
}}
.stButton button:hover{{
  border: 1px solid rgba(20,241,255,.55);
  transform: translateY(-1px);
}}

section[data-testid="stSidebar"]{{
  background: linear-gradient(180deg, rgba(5,8,12,.88), rgba(7,10,15,.82));
  border-right: 1px solid rgba(20,241,255,.12);
}}
</style>
        """,
        unsafe_allow_html=True,
    )


def _hud_header() -> None:
    st.markdown('<div class="hud-title">OBASI COMMAND CENTER</div>', unsafe_allow_html=True)
    st.markdown('<div class="hud-sub">Spectral Owl • Week-3 Demo • Read-Only HUD</div>', unsafe_allow_html=True)


def _banner_block(text: str) -> None:
    st.markdown(
        f"""
<div class="banner">
  <div class="label">DEMO SAFETY / READ-ONLY</div>
  <div class="msg">{text}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def _chips(system_status: str, mode: str, env: str, generated_at: str) -> None:
    sys_class = _verdict_color(system_status)
    st.markdown(
        f"""
<div class="chips">
  <div class="chip">
    <div class="k">System Status</div>
    <div class="v"><span class="dot {sys_class} pulse"></span>{system_status}</div>
  </div>
  <div class="chip">
    <div class="k">Mode</div>
    <div class="v">{mode}</div>
  </div>
  <div class="chip">
    <div class="k">Environment</div>
    <div class="v">{env}</div>
  </div>
  <div class="chip">
    <div class="k">Generated (UTC)</div>
    <div class="v" style="font-size:1.08rem;font-weight:900;">{generated_at}</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def _tiles(items: list[tuple[str, str]]) -> None:
    blocks = []
    for title, value in items:
        blocks.append(
            f"""
<div class="tile">
  <div class="t">{title}</div>
  <div class="n">{value}</div>
</div>
            """.strip()
        )
    st.markdown(f'<div class="tiles">{"".join(blocks)}</div>', unsafe_allow_html=True)


# ----------------------------
# Load artifacts
# ----------------------------
def load_artifacts() -> dict:
    paths = {
        "commander_txt": BRIEFS / "commander_brief_latest.txt",
        "commander_json": BRIEFS / "commander_brief_latest.json",
        "operator_txt": BRIEFS / "week3_operator_summary_latest.txt",
        "legal_txt": BRIEFS / "legal_case_snapshot_latest.txt",
        "legal_json": BRIEFS / "legal_case_snapshot_latest.json",
        "narrative_txt": BRIEFS / "week3_demo_narrative_latest.txt",
        "mobile_manifest": BRIEFS / "mobile_enjoy_manifest_latest.json",
        "fusion_reg_json": VALIDATION / "fusion_core_regression_latest.json",
        "fusion_reg_txt": VALIDATION / "fusion_core_regression_latest.txt",
        "demo_gate_json": VALIDATION / "week3_demo_readiness_gate_latest.json",
        "demo_gate_txt": VALIDATION / "week3_demo_readiness_gate_latest.txt",
        "demo_pack_gate_json": VALIDATION / "week3_demo_pack_gate_latest.json",
    }

    res = {"paths": {k: str(v) for k, v in paths.items()}, "present": {}, "payloads": {}}

    for k, p in paths.items():
        res["present"][k] = _exists(p)

    # JSON payloads
    for k in (
        "commander_json",
        "legal_json",
        "mobile_manifest",
        "fusion_reg_json",
        "demo_gate_json",
        "demo_pack_gate_json",
    ):
        p = paths[k]
        res["payloads"][k] = _read_json(p) if _exists(p) else {}

    # Text payloads
    for k in (
        "commander_txt",
        "operator_txt",
        "legal_txt",
        "narrative_txt",
        "fusion_reg_txt",
        "demo_gate_txt",
    ):
        p = paths[k]
        res["payloads"][k] = _read_text(p) if _exists(p) else ""

    # Status
    demo_gate = res["payloads"].get("demo_gate_json", {}) or {}
    verdict = _pick_verdict(demo_gate)
    if verdict == "UNKNOWN":
        verdict = _pick_verdict(res["payloads"].get("fusion_reg_json", {}) or {})
    res["system_status"] = verdict if verdict else "UNKNOWN"

    # crashes
    crashes = 0
    if isinstance(demo_gate, dict):
        crashes = max(crashes, _as_int(demo_gate.get("crashes", 0), 0))
    fr = res["payloads"].get("fusion_reg_json", {}) or {}
    if isinstance(fr, dict):
        crashes = max(crashes, _as_int(fr.get("crashes", 0), 0))
    res["crashes"] = crashes

    res["demo_locked"] = bool(is_demo_locked())
    res["generated_at_utc"] = _now_utc_iso()

    # Coverage math
    present = res["present"]
    total = len(present)
    present_count = sum(1 for _k, v in present.items() if v)
    missing_count = total - present_count
    res["coverage"] = {
        "total": total,
        "present": present_count,
        "missing": missing_count,
        "pct": int(round((present_count / total) * 100)) if total else 0,
    }

    # Verdicts
    res["demo_gate_verdict"] = _pick_verdict(demo_gate)
    res["fusion_verdict"] = _pick_verdict(fr)
    res["pack_gate_verdict"] = _pick_verdict(res["payloads"].get("demo_pack_gate_json", {}) or {})

    return res


# ----------------------------
# Module 5E: Auto-Sequence Engine
# ----------------------------
def _sequence_tick() -> None:
    """
    If sequence is running, compute which focus should be active based on elapsed time.
    Stops after one cycle if seq_loop == False.
    """
    if not st.session_state.get("seq_running", False):
        return

    secs = max(5, int(st.session_state.get("seq_seconds_per_step", 12)))
    start_ts = float(st.session_state.get("seq_start_ts", 0.0) or 0.0)
    if start_ts <= 0:
        st.session_state["seq_start_ts"] = _now_epoch()
        st.session_state["seq_last_step"] = -1
        start_ts = st.session_state["seq_start_ts"]

    elapsed = max(0.0, _now_epoch() - start_ts)
    step = int(elapsed // secs)

    total_steps = len(DEMO_SEQUENCE)
    if total_steps <= 0:
        return

    if not st.session_state.get("seq_loop", True) and step >= total_steps:
        # end on last view
        st.session_state["focus"] = DEMO_SEQUENCE[-1]
        st.session_state["seq_running"] = False
        return

    idx = step % total_steps
    if step != st.session_state.get("seq_last_step", -1):
        st.session_state["focus"] = DEMO_SEQUENCE[idx]
        st.session_state["seq_last_step"] = step


def _inject_refresh_js(ms: int) -> None:
    st.markdown(
        f"""
<script>
setTimeout(function() {{
  window.location.reload();
}}, {int(ms)});
</script>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------
# Demo Flow Controls
# ----------------------------
def _demo_flow_controls() -> None:
    st.markdown("#### Demo Flow")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    if c1.button("Overview", use_container_width=True):
        st.session_state["focus"] = "overview"
        st.rerun()
    if c2.button("Readiness", use_container_width=True):
        st.session_state["focus"] = "readiness"
        st.rerun()
    if c3.button("Operator", use_container_width=True):
        st.session_state["focus"] = "operator"
        st.rerun()
    if c4.button("Commander", use_container_width=True):
        st.session_state["focus"] = "commander"
        st.rerun()
    if c5.button("Legal", use_container_width=True):
        st.session_state["focus"] = "legal"
        st.rerun()
    if c6.button("Validation", use_container_width=True):
        st.session_state["focus"] = "validation"
        st.rerun()

    st.caption(f"Current focus: **{st.session_state.get('focus','overview')}**")


def _expander_default(name: str) -> bool:
    focus = st.session_state.get("focus", "overview")
    if focus == "overview":
        return name in ("briefing_view", "readiness_txt", "commander_brief")
    mapping = {
        "readiness": {"readiness_txt", "readiness_json", "pack_gate"},
        "operator": {"operator_summary"},
        "commander": {"briefing_view", "commander_brief", "commander_json", "narrative"},
        "legal": {"legal_snapshot", "legal_json"},
        "validation": {"fusion_regression_txt", "fusion_regression_json", "mobile_manifest"},
    }
    return name in mapping.get(focus, set())


# ----------------------------
# Presentation panels
# ----------------------------
def _briefing_view_panel(data: dict, compact: bool) -> None:
    cov = data.get("coverage", {})
    demo_gate = data.get("demo_gate_verdict", "UNKNOWN")
    fusion = data.get("fusion_verdict", "UNKNOWN")
    pack = data.get("pack_gate_verdict", "UNKNOWN")
    crashes = data.get("crashes", 0)

    commander_txt = data["payloads"].get("commander_txt", "")
    operator_txt = data["payloads"].get("operator_txt", "")
    narrative_txt = data["payloads"].get("narrative_txt", "")

    st.markdown("### 🎯 Briefing View (Stage / Commander)")
    st.caption("Minimal, high-signal. Designed for screen share.")

    r1, r2, r3, r4, r5 = st.columns(5)
    r1.metric("Demo Gate", demo_gate)
    r2.metric("Pack Gate", pack)
    r3.metric("Fusion Regression", fusion)
    r4.metric("Crashes", str(crashes))
    r5.metric("Coverage", f"{cov.get('present',0)}/{cov.get('total',0)} ({cov.get('pct',0)}%)")

    st.markdown("---")

    st.markdown("#### Commander Brief (first lines)")
    if commander_txt:
        st.code(_safe_snip(commander_txt, 1500) if compact else _safe_snip(commander_txt, 2200), language="markdown")
    else:
        st.warning("Missing: docs/briefs/commander_brief_latest.txt")

    st.markdown("#### Operator Summary (first lines)")
    if operator_txt:
        st.code(_safe_snip(operator_txt, 1100) if compact else _safe_snip(operator_txt, 1600), language="markdown")
    else:
        st.info("Missing: docs/briefs/week3_operator_summary_latest.txt")

    st.markdown("#### Demo Narrative (talk track)")
    if narrative_txt:
        st.code(_safe_snip(narrative_txt, 2000) if compact else _safe_snip(narrative_txt, 2800), language="markdown")
    else:
        st.info("Missing: docs/briefs/week3_demo_narrative_latest.txt")


# ----------------------------
# UI
# ----------------------------
def main() -> int:
    _init_state()

    st.set_page_config(
        page_title="Obasi Command Center",
        page_icon="🦉",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # ---- Sidebar: Mode (5D) ----
    st.sidebar.markdown("### Mode")
    st.session_state["presentation"] = st.sidebar.checkbox("Presentation Mode (recommended)", value=st.session_state["presentation"])
    st.session_state["briefing_view"] = st.sidebar.checkbox("Briefing View (stage)", value=st.session_state["briefing_view"])

    # In presentation mode: hide JSON by default
    if st.session_state["presentation"]:
        st.session_state["show_json"] = False

    _inject_hud_css(st.session_state["presentation"])
    st.markdown('<div class="hud-title">OBASI COMMAND CENTER</div>', unsafe_allow_html=True)
    st.markdown('<div class="hud-sub">Spectral Owl • Week-3 Demo • Read-Only HUD</div>', unsafe_allow_html=True)

    # ---- Sidebar: Module 5E Auto-Sequence ----
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Module 5E — Demo Auto-Sequence")

    seq_cols = st.sidebar.columns(2)
    if seq_cols[0].button("▶ Start", use_container_width=True):
        st.session_state["seq_running"] = True
        st.session_state["seq_start_ts"] = _now_epoch()
        st.session_state["seq_last_step"] = -1
        st.rerun()

    if seq_cols[1].button("■ Stop", use_container_width=True):
        st.session_state["seq_running"] = False
        st.rerun()

    st.session_state["seq_seconds_per_step"] = st.sidebar.slider(
        "Seconds per step",
        6, 30,
        int(st.session_state["seq_seconds_per_step"]),
        step=1,
    )
    st.session_state["seq_loop"] = st.sidebar.checkbox("Loop sequence", value=bool(st.session_state["seq_loop"]))

    # Run the tick BEFORE rendering the rest so focus updates are applied cleanly
    _sequence_tick()

    # Status line
    if st.session_state.get("seq_running", False):
        secs = int(st.session_state.get("seq_seconds_per_step", 12))
        st.sidebar.success(f"Auto-Sequence: RUNNING ({secs}s/step)")
        st.sidebar.caption(f"Sequence: {' → '.join(DEMO_SEQUENCE)}")
    else:
        st.sidebar.info("Auto-Sequence: OFF")

    data = load_artifacts()

    banner = demo_lock_banner() if data["demo_locked"] else "READ-ONLY HUD\nAssessment is probabilistic and bounded; operator judgment applies."
    _banner_block(banner.replace("\n", "<br/>"))

    sys_status = data.get("system_status", "UNKNOWN")
    mode = "DEMO LOCKED" if data.get("demo_locked") else "READ ONLY"
    env = "LOCAL HUD"
    gen = data.get("generated_at_utc", _now_utc_iso())
    _chips(sys_status, mode, env, gen)

    cov = data.get("coverage", {})
    _tiles(
        [
            ("Artifact Coverage", f"{cov.get('pct',0)}%"),
            ("Artifacts Present", f"{cov.get('present',0)}/{cov.get('total',0)}"),
            ("Artifacts Missing", str(cov.get("missing", 0))),
            ("Crashes", str(data.get("crashes", 0))),
            ("Demo Gate", data.get("demo_gate_verdict", "UNKNOWN")),
            ("Fusion Regression", data.get("fusion_verdict", "UNKNOWN")),
        ]
    )

    _demo_flow_controls()

    # ---- Sidebar: Controls ----
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Controls")
    auto_refresh = st.sidebar.checkbox("Auto-refresh (manual demo)", value=False)
    refresh_secs = st.sidebar.slider("Refresh interval (seconds)", 5, 60, 15, step=5)

    st.session_state["compact"] = st.sidebar.checkbox("Compact text", value=True if st.session_state["presentation"] else st.session_state["compact"])
    if not st.session_state["presentation"]:
        st.session_state["show_json"] = st.sidebar.checkbox("Show JSON panels", value=st.session_state["show_json"])
    st.session_state["show_paths"] = st.sidebar.checkbox("Show artifact paths (operator only)", value=st.session_state["show_paths"])

    # ---- Sidebar: Demo Focus ----
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Demo Focus")
    focus = st.sidebar.radio(
        "Set focus",
        ["overview", "readiness", "operator", "commander", "legal", "validation"],
        index=["overview", "readiness", "operator", "commander", "legal", "validation"].index(st.session_state.get("focus", "overview")),
    )
    if focus != st.session_state.get("focus"):
        st.session_state["focus"] = focus
        st.rerun()

    if st.sidebar.button("Refresh Now"):
        st.rerun()

    # Auto-refresh behavior:
    # - If sequence is running, we *must* refresh at the step cadence so it advances.
    # - Otherwise, use the optional manual refresh toggle.
    if st.session_state.get("seq_running", False):
        ms = int(max(6, int(st.session_state.get("seq_seconds_per_step", 12))) * 1000)
        _inject_refresh_js(ms)
    elif auto_refresh:
        st.sidebar.caption("Auto-refresh enabled.")
        _inject_refresh_js(int(refresh_secs) * 1000)

    if st.session_state["show_paths"]:
        with st.sidebar.expander("Artifact Paths", expanded=False):
            st.code(json.dumps(data["paths"], indent=2), language="json")

    compact = bool(st.session_state["compact"])
    show_json = bool(st.session_state["show_json"])

    # ---- Presentation layout (5D) ----
    if st.session_state["briefing_view"]:
        with st.expander("Briefing View (Stage / Commander)", expanded=_expander_default("briefing_view")):
            _briefing_view_panel(data, compact)

        st.markdown("---")

    left, right = st.columns(2, gap="large")

    with left:
        st.markdown("### 🧠 Commander / Briefing Outputs")
        st.caption("Bounded, commander-safe outputs. Demo-locked; operator judgment applies.")

        commander_txt = data["payloads"].get("commander_txt", "")
        with st.expander("Commander Brief (TXT)", expanded=_expander_default("commander_brief")):
            if commander_txt:
                st.code(_safe_snip(commander_txt, 3200) if compact else commander_txt, language="markdown")
            else:
                st.warning("Missing: docs/briefs/commander_brief_latest.txt (run orchestrator).")

        narrative_txt = data["payloads"].get("narrative_txt", "")
        with st.expander("Week-3 Demo Narrative (Commander-Safe)", expanded=_expander_default("narrative")):
            if narrative_txt:
                st.code(_safe_snip(narrative_txt, 3600) if compact else narrative_txt, language="markdown")
            else:
                st.info("Missing: docs/briefs/week3_demo_narrative_latest.txt")

        operator_txt = data["payloads"].get("operator_txt", "")
        with st.expander("Operator Summary (Week-3)", expanded=_expander_default("operator_summary")):
            if operator_txt:
                st.code(_safe_snip(operator_txt, 2800) if compact else operator_txt, language="markdown")
            else:
                st.info("Missing: docs/briefs/week3_operator_summary_latest.txt")

        legal_txt = data["payloads"].get("legal_txt", "")
        with st.expander("Legal Case Snapshot (Demo / Training)", expanded=_expander_default("legal_snapshot")):
            if legal_txt:
                st.code(_safe_snip(legal_txt, 3600) if compact else legal_txt, language="markdown")
            else:
                st.info("Missing: docs/briefs/legal_case_snapshot_latest.txt")

        if show_json:
            with st.expander("Legal Snapshot (JSON)", expanded=_expander_default("legal_json")):
                leg_json = data["payloads"].get("legal_json", {}) or {}
                if leg_json:
                    st.json(leg_json)
                else:
                    st.info("Missing: docs/briefs/legal_case_snapshot_latest.json")

    with right:
        st.markdown("### 🛡️ Readiness & System Validation")
        st.caption("Proof of demo safety + regression posture. Gate-driven.")

        demo_gate_json = data["payloads"].get("demo_gate_json", {}) or {}
        dg_verdict = data.get("demo_gate_verdict", "UNKNOWN")
        dg_class = _verdict_color(dg_verdict)

        st.markdown(
            f"""
<div class="tile" style="min-width:100%; margin-bottom: 12px;">
  <div class="t">Demo Readiness Gate</div>
  <div class="n"><span class="dot {dg_class} pulse"></span>{dg_verdict}</div>
</div>
            """,
            unsafe_allow_html=True,
        )

        demo_gate_txt = data["payloads"].get("demo_gate_txt", "")
        with st.expander("Readiness Gate (TXT)", expanded=_expander_default("readiness_txt")):
            if demo_gate_txt:
                st.code(_safe_snip(demo_gate_txt, 4200) if compact else demo_gate_txt, language="markdown")
            else:
                st.info("Missing: docs/validation/week3_demo_readiness_gate_latest.txt")

        if show_json:
            with st.expander("Readiness Gate (JSON)", expanded=_expander_default("readiness_json")):
                if demo_gate_json:
                    st.json(demo_gate_json)
                else:
                    st.info("Missing: docs/validation/week3_demo_readiness_gate_latest.json")

            with st.expander("Demo Pack Gate (JSON)", expanded=_expander_default("pack_gate")):
                pack_gate = data["payloads"].get("demo_pack_gate_json", {}) or {}
                if pack_gate:
                    st.json(pack_gate)
                else:
                    st.info("Missing: docs/validation/week3_demo_pack_gate_latest.json")

        fr_json = data["payloads"].get("fusion_reg_json", {}) or {}
        fr_verdict = data.get("fusion_verdict", "UNKNOWN")
        fr_class = _verdict_color(fr_verdict)

        st.markdown(
            f"""
<div class="tile" style="min-width:100%; margin: 10px 0 12px 0;">
  <div class="t">Fusion Core Regression</div>
  <div class="n"><span class="dot {fr_class} pulse"></span>{fr_verdict}</div>
</div>
            """,
            unsafe_allow_html=True,
        )

        fusion_reg_txt = data["payloads"].get("fusion_reg_txt", "")
        with st.expander("Fusion Regression (TXT)", expanded=_expander_default("fusion_regression_txt")):
            if fusion_reg_txt:
                st.code(_safe_snip(fusion_reg_txt, 4200) if compact else fusion_reg_txt, language="markdown")
            else:
                st.info("Missing: docs/validation/fusion_core_regression_latest.txt")

        if show_json:
            with st.expander("Fusion Regression (JSON)", expanded=_expander_default("fusion_regression_json")):
                if fr_json:
                    st.json(fr_json)
                else:
                    st.info("Missing: docs/validation/fusion_core_regression_latest.json")

            with st.expander("Mobile Enjoy Manifest (JSON)", expanded=_expander_default("mobile_manifest")):
                mobile_manifest = data["payloads"].get("mobile_manifest", {}) or {}
                if mobile_manifest:
                    st.json(mobile_manifest)
                else:
                    st.info("Missing: docs/briefs/mobile_enjoy_manifest_latest.json")

            with st.expander("Commander Brief (JSON envelope)", expanded=_expander_default("commander_json")):
                cmd_json = data["payloads"].get("commander_json", {}) or {}
                if cmd_json:
                    st.json(cmd_json)
                else:
                    st.info("Missing: docs/briefs/commander_brief_latest.json")

    st.markdown("---")
    st.caption("OBASI HUD • Demo-Locked • Read-Only • Operator judgment applies.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

