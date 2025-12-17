from __future__ import annotations

import json
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


def main() -> int:
    st.set_page_config(
        page_title="GLL Week-3 Demo",
        page_icon="🦉",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # --- Sidebar ---
    st.sidebar.markdown("### 🦉 Ghost Lantern Labs")
    st.sidebar.caption("Week-3 Shari Demo GUI • Read-Only • Demo-Safe")

    demo_locked = is_demo_locked()
    st.sidebar.markdown("#### Demo Lock")
    st.sidebar.write("✅ ON" if demo_locked else "⚠️ OFF")
    if demo_locked:
        st.sidebar.code(demo_lock_banner())

    st.sidebar.markdown("#### Quick Actions")
    st.sidebar.code("python src/week3_shari_demo_packet.py")
    st.sidebar.code("python src/week3_demo_readiness_gate.py")
    st.sidebar.code("python src/ghost_cli.py  # option 76")

    # --- Header ---
    _big_banner(
        "WEEK-3 SHARI DEMO PACK",
        f"generated_at_utc: {_utc_now_iso()} • DEMO LOCK: {'ON' if demo_locked else 'OFF'} • Read-Only",
    )
    st.write("")

    if demo_locked:
        st.warning(demo_lock_banner(), icon="🔒")
    else:
        st.info("Demo lock appears OFF. If you’re presenting, turn it ON before demo.", icon="⚠️")

    # --- Presence strip ---
    c1, c2 = st.columns([3, 2], gap="large")
    with c1:
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

    with c2:
        st.markdown("### 🎯 Readiness Verdict")
        ok_gate, readiness = _read_json(P_READINESS_GATE)
        verdict = (readiness or {}).get("verdict", "UNKNOWN") if ok_gate else "MISSING"
        if str(verdict).upper() == "PASS":
            st.success(f"PASS — Demo is presentable", icon="✅")
        elif verdict == "MISSING":
            st.error("MISSING — run week3_demo_readiness_gate.py", icon="❌")
        else:
            st.error(f"FAIL — fix violations before demo", icon="❌")

        if ok_gate and isinstance(readiness, dict):
            v = readiness.get("violations") or []
            if v:
                st.write("Violations:")
                st.code("\n".join([str(x) for x in v]))
            else:
                st.caption("No violations detected.")

    st.write("")
    st.divider()

    # --- Main tabs ---
    tabs = st.tabs(
        [
            "🧭 Demo Narrative",
            "🧾 Legal Snapshot",
            "📌 Operator Summary",
            "🧠 Commander Brief",
            "🧪 Regression + Gates",
            "📱 Mobile Enjoy Manifest",
        ]
    )

    # Tab 1: Narrative
    with tabs[0]:
        st.markdown("## 🧭 Demo Narrative (talk track)")
        ok, txt = _read_txt(P_NARRATIVE_TXT)
        if ok:
            st.text_area("Narrative", txt, height=420)
        else:
            st.error(txt)

    # Tab 2: Legal snapshot
    with tabs[1]:
        st.markdown("## 🧾 Legal Case Snapshot (Shari Hook)")
        ok_txt, txt = _read_txt(P_LEGAL_TXT)
        ok_js, js = _read_json(P_LEGAL_JSON)
        left, right = st.columns([1, 1], gap="large")
        with left:
            if ok_txt:
                st.text_area("Text Snapshot", txt, height=520)
            else:
                st.error(txt)
        with right:
            if ok_js and js is not None:
                st.json(js, expanded=False)
            else:
                st.error(f"[MISSING/ERROR] {P_LEGAL_JSON}")

    # Tab 3: Operator summary
    with tabs[2]:
        st.markdown("## 📌 Operator Summary (10-second status)")
        ok, txt = _read_txt(P_OPERATOR_SUMMARY_TXT)
        if ok:
            st.text_area("Summary", txt, height=260)
        else:
            st.error(txt)

        st.caption("This is what you read out loud first. Short. Confident. Bounded.")

    # Tab 4: Commander brief
    with tabs[3]:
        st.markdown("## 🧠 Commander Brief (bounded)")
        ok, txt = _read_txt(P_COMMANDER_TXT)
        if ok:
            st.text_area("Commander Brief", txt, height=560)
        else:
            st.error(txt)

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

    st.divider()
    st.caption("DEMO SAFE RULE: No baselines updated. No training. No mutation. Operator judgment applies.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

