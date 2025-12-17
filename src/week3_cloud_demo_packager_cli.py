# src/week3_cloud_demo_packager_cli.py
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[1]


def run_week3_cloud_demo_packager_cli() -> Dict[str, Any]:
    """
    Runs the Week-3 Cloud Demo Packager as a subprocess.
    This avoids import coupling and keeps ghost_cli stable.
    Never raises; returns a bounded result envelope.
    """
    cmd = [sys.executable, "src/week3_cloud_demo_packager.py"]
    try:
        p = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        stdout = (p.stdout or "").strip()
        stderr = (p.stderr or "").strip()

        # packager prints JSON on stdout on success
        parsed = None
        if stdout:
            try:
                parsed = json.loads(stdout)
            except Exception:
                parsed = None

        return {
            "generated_at_utc": __import__("datetime").datetime.utcnow().isoformat() + "Z",
            "context": "week3_cloud_demo_packager_cli",
            "cmd": " ".join(cmd),
            "returncode": p.returncode,
            "ok": (p.returncode == 0 and isinstance(parsed, dict)),
            "result": parsed,
            "stdout_tail": stdout[-1200:] if stdout else "",
            "stderr_tail": stderr[-1200:] if stderr else "",
        }
    except Exception as e:
        return {
            "generated_at_utc": __import__("datetime").datetime.utcnow().isoformat() + "Z",
            "context": "week3_cloud_demo_packager_cli",
            "cmd": " ".join(cmd),
            "returncode": 999,
            "ok": False,
            "result": None,
            "stdout_tail": "",
            "stderr_tail": f"{type(e).__name__}:{e}",
        }


def main() -> int:
    out = run_week3_cloud_demo_packager_cli()
    print(json.dumps(out, indent=2))
    return 0 if out.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())

