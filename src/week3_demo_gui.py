from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import streamlit as st

# --- Demo Lock (best effort) ---
try:
    from demo_lock import is_demo_locked, demo_lock_banner
except Exception:
    def is_demo_locked() -> bool:  # type: ignore
        return False

    def demo_lock_banner() -> str:  # type: ignore
        return "DEMO MODE (banner unavailable)"

# --- Paths (stable, read-only) ---
BRIEFS_DIR = Path("docs") / "briefs"
VALIDATION_DIR = Path("docs") / "validation"

P_COMMANDER_TXT = BRIEFS_DIR / "commander_brief_latest.txt"
P_OPERATOR_SUMMARY_TXT = BRIEFS_DIR / "week3_operator_summary_latest.txt"
P_LEGAL_TXT = BRIEFS_DIR / "legal_case_snapshot_latest.txt"
P_LEGAL_JSON = BRIEFS_DIR / "legal_case_snapshot_latest.json"
P_NARRATIVE_TXT = BRIEFS_DIR / "week3_demo_narrative_latest.txt"
P_MOBILE_MANIFEST = BRIEFS_DIR / "mobile_enjoy_manifest_latest.json"

P_CORE_REG_TXT = VALIDATION_DIR / "fusion_core_regression_latest.txt"
P_CORE_REG_JSON = VALIDATION_DIR / "fusion_core_regression_latest.json"
P_DEMO_PACK_GATE = VALIDATION_DIR / "week3_demo_pack_gate_latest.json"
P_READINESS_GATE = VALIDATION_DIR / "week3_demo_readiness_gate_latest.json"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_txt(path: Path, max_chars: int = 60_000) -> Tuple[bool, str]:
    try:
        if not path.exists():
            return False, f"[MISSING] {path}"
        s = path.read_text(encoding="utf-8", errors="replace")
        if len(s) > max_chars:
            s = s[:max_chars] + "\n\n[TRUNCATED]"
        return True, s
    except Exception as e:
        return False, f"[ERROR] {path} :: {type(e).__name__}:{e}"


def _read_json(path: Path) -> Tuple[bool, Optional[Dict[str, Any]]]:
    try:
        if not path.exists():
            return False, None
        return True, json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False, None


def _pill(label: str, ok: bool) -> None:
    st.markdown(
        f"""
        <div style="
            display:inline-block;
            padding:6px 10px;
            border-radius:999px;
            font-size:13px;
            margin-right:8px;
            border:1px solid rgba(255,255,255,0.15);
            background:{'rgba(34,197,94,0.20)' if ok else 'rgba(239,68,68,0.20)'};
        ">
            <b>{label}</b>: {'OK' if ok else 'MISSING'}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _big_banner(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div style="
            padding:18px 18px;
            border-radius:18px;
            background: linear-gradient(135deg, rgba(59,130,246,0.25), rgba(168,85,247,0.18));
            border:1px solid rgba(255,255,255,0.18);
            box-shadow: 0 8px 30px rgba(0,0,0,0.25);
        ">
            <div style="font-size:28px; font-weight:800; letter-spacing:0.5px;">{title}</div>
            <div style="opacity:0.85; font-size:14px; margin-top:6px;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _obasi_boot_card(demo_locked: bool) -> None:
    """
    Pure UI. No side effects. Just the vibe.
    """
    lock_line = "DEMO LOCK: ON (READ-ONLY)" if demo_locked else "DEMO LOCK: OFF (TURN ON FOR PRESENTATION)"
    st.markdown(
        f"""
        <div style="
            padding:16px 16px;
            border-radius:18px;
            background: radial-gradient(circle at 20% 20%, rgba(34,197,94,0.12), rgba(0,0,0,0.25) 60%),
                        linear-gradient(135deg, rgba(15,23,42,0.75), rgba(2,6,23,0.85));
            border:1px solid rgba(255,255,255,0.12);
            box-shadow: 0 10px 30px rgba(0,0,0,0.30);
        ">
            <div style="display:flex; align-items:center; justify-content:space-between; gap:14px;">
                <div>
                    <div style="font-size:18px; font-weight:800;">🦉 OBASI — Spectral Owl</div>
                    <div style="opacity:0.85; font-size:12.5px; margin-top:3px;">
                        Boot Sequence • Commander-safe • Bounded output • Operator judgment applies
                    </div>
                </div>
                <div style="
                    padding:6px 10px;
                    border-radius:999px;
                    font-size:12px;
                    border:1px solid rgba(255,255,255,0.14);
                    background: rgba(59,130,246,0.18);
                ">
                    {lock_line}
                </div>
            </div>
            <div style="
                margin-top:10px;
                font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
                font-size:12px;
                opacity:0.90;
                line-height:1.35;
                white-space:pre-wrap;
            ">
[INIT] spectral_bus ................. OK
[INIT] artifact_map ................ OK
[INIT] bounded_reasoning ........... OK
[INIT] briefing_renderer ........... OK
[INIT] demo_safe_guards ............ OK
[READY] week3_demo_pack ............ ARMED
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # subtle loading bar (purely visual)
    st.progress(100, text="OBASI READY")


def _demo_timer_panel() -> None:
    """
    Simple pacing panel. Optional session timer using Streamlit rerun.
    """
    st.markdown("### ⏱ Demo Timer (talk-track pacing)")
    st.caption("Use this to keep the demo crisp. You can run it or ignore it. No system changes.")

    if "demo_timer_running" not in st.session_state:
        st.session_state.demo_timer_running = False
    if "demo_timer_t0" not in st.session_state:
        st.session_state.demo_timer_t0 = 0.0

    colA, colB, colC = st.columns([1, 1, 2], gap="small")
    with colA:
        if st.button("Start", use_container_width=True, disabled=st.session_state.demo_timer_running):
            st.session_state.demo_timer_running = True
            st.session_state.demo_timer_t0 = time.time()
            st.rerun()
    with colB:
        if st.button("Reset", use_container_width=True):
            st.session_state.demo_timer_running = False
            st.session_state.demo_timer_t0 = 0.0
            st.rerun()
    with colC:
        if st.session_state.demo_timer_running and st.session_state.demo_timer_t0:
            elapsed = int(time.time() - st.session_state.demo_timer_t0)
            st.info(f"Running… elapsed: {elapsed}s", icon="⏳")
        else:
            st.info("Stopped.", icon="⏹️")

    st.markdown(
        """
**Recommended flow**
- **0:30** — Operator Summary (confidence + bounded statement)
- **1:30** — Commander Brief (What changed / Why it matters / Posture)
- **0:45** — Legal Snapshot (Shari Hook) + Mobile Enjoy Manifest
        """
    )


def _copy_block(label: str, text: str) -> None:
    """
    Streamlit-native copy helper: shows a compact copy area.
    (Streamlit doesn't provide a guaranteed universal clipboard API for all browsers,
    so this is the most reliable approach.)
    """
    with st.expander(f"📋 Copy: {label}", expanded=False):
        st.text_area("Copy text below", text, height=180)


def main() -> int:
    st.set_page_config(
        page_title="GLL Week-3 Demo",
        page_icon="🦉",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    demo_locked = is_demo_locked()

    # --- Sidebar ---
    st.sidebar.markdown("### 🦉 Ghost Lantern Labs")
    st.sidebar.caption("Week-3 Shari Demo GUI • Read-Only • Demo-Safe")

    st.sidebar.markdown("#### Demo Lock")
    st.sidebar.write("✅ ON" if demo_locked else "⚠️ OFF")
    if demo_locked:
        st.sidebar.code(demo_lock_banner())

    st.sidebar.markdown("#### Quick Actions")
    st.sidebar.code("python src/week3_shari_demo_packet.py")
    st.sidebar.code("python src/week3_demo_readiness_gate.py")
    st.sidebar.code("python src/ghost_cli.py  # option 76")

    st.sidebar.markdown("#### Demo Notes (operator)")
    st.sidebar.caption("- Keep it bounded.\n- Don’t over-explain.\n- End with posture + next step.")

    # --- Header ---
    _big_banner(
        "WEEK-3 SHARI DEMO PACK",
        f"generated_at_utc: {_utc_now_iso()} • DEMO LOCK: {'ON' if demo_locked else 'OFF'} • Read-Only",
    )
    st.write("")

    # --- Top row: Obasi boot + timer + readiness verdict ---
    left, mid, right = st.columns([1.25, 1.0, 1.0], gap="large")
    with left:
        _obasi_boot_card(demo_locked)

    with mid:
        _demo_timer_panel()

    with right:
        st.markdown("### 🎯 Readiness Verdict")
        ok_gate, readiness = _read_json(P_READINESS_GATE)
        verdict = (readiness or {}).get("verdict", "UNKNOWN") if ok_gate else "MISSING"
        if str(verdict).upper() == "PASS":
            st.success("PASS — Demo is presentable", icon="✅")
        elif verdict == "MISSING":
            st.error("MISSING — run week3_demo_readiness_gate.py", icon="❌")
        else:
            st.error("FAIL — fix violations before demo", icon="❌")

        if ok_gate and isinstance(readiness, dict):
            v = readiness.get("violations") or []
            if v:
                st.write("Violations:")
                st.code("\n".join([str(x) for x in v]))
            else:
                st.caption("No violations detected.")

        st.markdown("### 📱 Mobile Enjoy")
        st.caption("Open artifacts on phone without touching baselines.")
        ok_manifest = P_MOBILE_MANIFEST.exists()
        st.write("✅ Manifest present" if ok_manifest else "❌ Manifest missing")

    st.write("")
    st.divider()

    # --- Presence strip ---
    st.markdown("### ✅ Demo Artifact Presence")
    ok_cmd = P_COMMANDER_TXT.exists()
    ok_sum = P_OPERATOR_SUMMARY_TXT.exists()
    ok_legal = P_LEGAL_TXT.exists() and P_LEGAL_JSON.exists()
    ok_narr = P_NARRATIVE_TXT.exists()
    ok_readiness = P_READINESS_GATE.exists()
    ok_manifest = P_MOBILE_MANIFEST.exists()
    ok_reg = P_CORE_REG_TXT.exists() and P_CORE_REG_JSON.exists()

    _pill("Commander Brief", ok_cmd)
    _pill("Operator Summary", ok_sum)
    _pill("Legal Snapshot", ok_legal)
    _pill("Demo Narrative", ok_narr)
    _pill("Readiness Gate", ok_readiness)
    _pill("Mobile Manifest", ok_manifest)
    _pill("Core Regression", ok_reg)

    if demo_locked:
        st.warning(demo_lock_banner(), icon="🔒")
    else:
        st.info("Demo lock appears OFF. If you’re presenting, turn it ON before demo.", icon="⚠️")

    st.write("")
    st.divider()

    # --- Read key text once for copy blocks ---
    ok_n, narrative_txt = _read_txt(P_NARRATIVE_TXT)
    ok_l, legal_txt = _read_txt(P_LEGAL_TXT)
    ok_s, summary_txt = _read_txt(P_OPERATOR_SUMMARY_TXT)
    ok_c, commander_txt = _read_txt(P_COMMANDER_TXT)

    # --- Main tabs ---
    tabs = st.tabs(
        [
            "🧭 Demo Narrative",
            "🧾 Legal Snapshot",
            "📌 Operator Summary",
            "🧠 Commander Brief",
            "🧪 Regression + Gates",
            "📱 Mobile Enjoy Manifest",
            "📋 Copy Center",
        ]
    )

    # Tab 1: Narrative
    with tabs[0]:
        st.markdown("## 🧭 Demo Narrative (talk track)")
        if ok_n:
            st.text_area("Narrative", narrative_txt, height=420)
        else:
            st.error(narrative_txt)

    # Tab 2: Legal snapshot
    with tabs[1]:
        st.markdown("## 🧾 Legal Case Snapshot (Shari Hook)")
        ok_js, js = _read_json(P_LEGAL_JSON)
        left2, right2 = st.columns([1, 1], gap="large")
        with left2:
            if ok_l:
                st.text_area("Text Snapshot", legal_txt, height=520)
            else:
                st.error(legal_txt)
        with right2:
            if ok_js and js is not None:
                st.json(js, expanded=False)
            else:
                st.error(f"[MISSING/ERROR] {P_LEGAL_JSON}")

    # Tab 3: Operator summary
    with tabs[2]:
        st.markdown("## 📌 Operator Summary (10-second status)")
        if ok_s:
            st.text_area("Summary", summary_txt, height=260)
        else:
            st.error(summary_txt)
        st.caption("This is what you read out loud first. Short. Confident. Bounded.")

    # Tab 4: Commander brief
    with tabs[3]:
        st.markdown("## 🧠 Commander Brief (bounded)")
        if ok_c:
            st.text_area("Commander Brief", commander_txt, height=560)
        else:
            st.error(commander_txt)

    # Tab 5: Regression + gates
    with tabs[4]:
        st.markdown("## 🧪 Fusion Core Regression + Gates")
        ok_txt, reg_txt = _read_txt(P_CORE_REG_TXT)
        ok_js, reg_js = _read_json(P_CORE_REG_JSON)
        ok_pack, pack = _read_json(P_DEMO_PACK_GATE)
        ok_read, read_js = _read_json(P_READINESS_GATE)

        a, b = st.columns([1, 1], gap="large")
        with a:
            st.markdown("### Core Regression (TXT)")
            if ok_txt:
                st.text_area("fusion_core_regression_latest.txt", reg_txt, height=420)
            else:
                st.error(reg_txt)

            st.markdown("### Demo Pack Gate (JSON)")
            if ok_pack and pack is not None:
                st.json(pack, expanded=False)
            else:
                st.error(f"[MISSING/ERROR] {P_DEMO_PACK_GATE}")

        with b:
            st.markdown("### Core Regression (JSON)")
            if ok_js and reg_js is not None:
                st.json(reg_js, expanded=False)
            else:
                st.error(f"[MISSING/ERROR] {P_CORE_REG_JSON}")

            st.markdown("### Demo Readiness Gate (JSON)")
            if ok_read and read_js is not None:
                st.json(read_js, expanded=False)
            else:
                st.error(f"[MISSING/ERROR] {P_READINESS_GATE}")

    # Tab 6: Mobile manifest
    with tabs[5]:
        st.markdown("## 📱 Mobile Enjoy Manifest (read-only paths)")
        ok, js = _read_json(P_MOBILE_MANIFEST)
        if ok and js is not None:
            st.json(js, expanded=False)
            st.caption("Use this on your phone to open artifacts without modifying anything.")
        else:
            st.error(f"[MISSING/ERROR] {P_MOBILE_MANIFEST}")

    # Tab 7: Copy center
    with tabs[6]:
        st.markdown("## 📋 Copy Center (for live demo)")
        st.caption("Open an expander and copy text. This is the safest cross-browser method.")

        if ok_s:
            _copy_block("Operator Summary", summary_txt)
        else:
            st.error("Operator Summary missing — generate it first.")

        if ok_c:
            _copy_block("Commander Brief", commander_txt)
        else:
            st.error("Commander Brief missing — generate it first.")

        if ok_n:
            _copy_block("Demo Narrative", narrative_txt)
        else:
            st.error("Demo Narrative missing — generate it first.")

        if ok_l:
            _copy_block("Legal Snapshot", legal_txt)
        else:
            st.error("Legal Snapshot missing — generate it first.")

    st.divider()
    st.caption("DEMO SAFE RULE: No baselines updated. No training. No mutation. Operator judgment applies.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

