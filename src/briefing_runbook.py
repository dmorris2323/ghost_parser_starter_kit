from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

# Local imports (src is already inserted by ghost_cli in most setups)
from gll_run_gates import run_gates
from command_brief_exporter import build_commander_sections, write_commander_brief
from commander_brief_consistency_gate import run_gate as run_commander_brief_gate


def _print_json(obj: Any) -> None:
    print(json.dumps(obj, indent=2))


def run_commander_brief_one_shot(
    context: str = "day72_commander_brief_one_shot",
    update_baselines: bool = False,
) -> Dict[str, Any]:
    """
    Runs:
      PRE gate -> commander brief exporter -> commander brief consistency gate -> POST gate

    Returns a dict with paths + verdicts. Must not crash.
    """
    results: Dict[str, Any] = {
        "context": context,
        "update_baselines": bool(update_baselines),
        "pre_gate": None,
        "brief_paths": None,
        "brief_gate": None,
        "post_gate": None,
        "ok": False,
    }

    # 1) PRE gate
    pre = run_gates(gate_type="PRE", context=context, update_baselines=update_baselines)
    results["pre_gate"] = pre

    # 2) Build + write commander brief
    sections, inputs = build_commander_sections()
    paths = write_commander_brief(sections, inputs)
    results["brief_paths"] = paths

    # 3) Consistency gate
    gate = run_commander_brief_gate()
    results["brief_gate"] = gate

    # 4) POST gate (always run, even if brief gate fails)
    post = run_gates(gate_type="POST", context=context, update_baselines=update_baselines)
    results["post_gate"] = post

    results["ok"] = bool(pre.get("ok")) and (gate.get("verdict") == "PASS") and bool(post.get("ok"))
    return results


def main() -> None:
    # CLI-friendly defaults (no args to keep it simple)
    res = run_commander_brief_one_shot()
    _print_json(res)

    # Exit code: 0 on success, 2 on gate failure
    if not res.get("ok"):
        sys.exit(2)


if __name__ == "__main__":
    main()

