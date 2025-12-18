# src/week3_demo_freeze_packager_cli.py
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

_THIS = Path(__file__).resolve()
SRC_DIR = _THIS.parent
REPO_ROOT = SRC_DIR.parent


def _utc_now_iso_z() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> int:
    cmd = [sys.executable, "src/week3_demo_freeze_packager.py"]
    p = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, check=False)

    result: Dict[str, Any] = {
        "generated_at_utc": _utc_now_iso_z(),
        "context": "week3_demo_freeze_packager_cli",
        "cmd": " ".join(cmd),
        "returncode": p.returncode,
        "ok": p.returncode == 0,
        "stdout_tail": (p.stdout or "")[-1200:],
        "stderr_tail": (p.stderr or "")[-1200:],
    }

    try:
        payload = json.loads(p.stdout) if p.stdout else None
    except Exception:
        payload = None

    if payload is not None:
        result["result"] = payload

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

