from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_read_json(path: Path) -> Optional[dict]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _safe_read_text(path: Path, max_chars: int = 3000) -> Optional[str]:
    try:
        txt = path.read_text(encoding="utf-8", errors="replace")
        return txt[:max_chars]
    except Exception:
        return None


@dataclass
class OneShotResult:
    generated_at_utc: str
    ok: bool
    context: str
    gates: Dict[str, Any]
    commander_brief: Dict[str, Any]
    nuclear_product_consistency: Dict[str, Any]
    errors: Dict[str, str]


def run_commander_brief_one_shot(
    context: str = "commander_brief_one_shot",
    update_baselines: bool = False,
) -> Dict[str, Any]:
    """
    Owner/operator one-shot:
      PRE gate -> generate commander brief -> nuclear product consistency -> POST gate
    No UI. No drift. Best-effort reads.
    """

    errors: Dict[str, str] = {}
    gates_out: Dict[str, Any] = {}

    # ---------- PRE GATE ----------
    try:
        from gll_run_gates import run_gates  # local module in src/

        gates_out["pre"] = run_gates(
            gate_type="PRE",
            context=context,
            update_baselines=bool(update_baselines),
        )
    except Exception as e:
        errors["pre_gate"] = f"{type(e).__name__}:{e}"
        gates_out["pre"] = {"ok": False, "error": errors["pre_gate"]}

    # ---------- COMMANDER BRIEF ----------
    brief_paths: Dict[str, Any] = {}
    try:
        # Prefer calling the exporter as a library if it exposes functions
        import command_brief_exporter as cbe

        # If exporter has a main() that writes latest outputs, call it.
        # We keep this tolerant: if it fails, we'll still return a structured result.
        if hasattr(cbe, "main"):
            cbe.main()

        # The exporter (in your repo) writes docs/briefs/commander_brief_latest.txt typically.
        # We include best-effort reading for traceability.
        latest_txt = Path("docs") / "briefs" / "commander_brief_latest.txt"
        latest_json = Path("docs") / "briefs" / "commander_brief_latest.json"

        brief_paths = {
            "latest_txt": str(latest_txt),
            "latest_json": str(latest_json),
            "preview_txt": _safe_read_text(latest_txt),
            "json_obj": _safe_read_json(latest_json),
        }
    except Exception as e:
        errors["commander_brief"] = f"{type(e).__name__}:{e}"
        brief_paths = {"ok": False, "error": errors["commander_brief"]}

    # ---------- NUCLEAR PRODUCT CONSISTENCY ----------
    npc_out: Dict[str, Any] = {}
    try:
        import nuclear_product_consistency_gate as npc

        # If gate has a main() that writes latest outputs, call it
        if hasattr(npc, "main"):
            npc.main()

        latest_txt = Path("docs") / "nuclear" / "nuclear_product_consistency_latest.txt"
        latest_json = Path("docs") / "nuclear" / "nuclear_product_consistency_latest.json"

        npc_out = {
            "latest_txt": str(latest_txt),
            "latest_json": str(latest_json),
            "preview_txt": _safe_read_text(latest_txt),
            "json_obj": _safe_read_json(latest_json),
        }

        # Try to surface verdict if present
        j = npc_out.get("json_obj") or {}
        npc_out["verdict"] = j.get("verdict")
        npc_out["ok"] = (npc_out["verdict"] == "PASS") if npc_out["verdict"] else True
    except Exception as e:
        errors["nuclear_product_consistency"] = f"{type(e).__name__}:{e}"
        npc_out = {"ok": False, "error": errors["nuclear_product_consistency"]}

    # ---------- POST GATE ----------
    try:
        from gll_run_gates import run_gates  # local module in src/

        gates_out["post"] = run_gates(
            gate_type="POST",
            context=context,
            update_baselines=bool(update_baselines),
        )
    except Exception as e:
        errors["post_gate"] = f"{type(e).__name__}:{e}"
        gates_out["post"] = {"ok": False, "error": errors["post_gate"]}

    ok = True
    # If any hard failure occurred, mark not ok (we still return structured output)
    for k, v in errors.items():
        if v:
            ok = False
            break

    res = OneShotResult(
        generated_at_utc=_utc_now_iso(),
        ok=ok,
        context=context,
        gates=gates_out,
        commander_brief=brief_paths,
        nuclear_product_consistency=npc_out,
        errors=errors,
    )
    return res.__dict__


if __name__ == "__main__":
    out = run_commander_brief_one_shot(
        context="manual_run_commander_brief_one_shot",
        update_baselines=False,
    )
    print(json.dumps(out, indent=2))

