from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"


def _safe_read_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text())
    except Exception:
        pass
    return default


def _escape(text: str) -> str:
    """Simple HTML escaping for <pre> blocks."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_war_room_html() -> str:
    """
    Build an HTML representation of the War Room Brief.

    Uses:
      • docs/war_room_brief_latest.json if present
      • Otherwise calls gll_war_room_brief.build_war_room_bundle()
    """
    from gll_war_room_brief import build_war_room_bundle

    json_path = DOCS_DIR / "war_room_brief_latest.json"

    if json_path.exists():
        try:
            bundle = json.loads(json_path.read_text())
        except Exception:
            bundle = build_war_room_bundle()
    else:
        bundle = build_war_room_bundle()

    meta = bundle.get("meta", {})
    system_health = bundle.get("system_health", {})
    base_defense = bundle.get("base_defense", {})
    nuclear_picture = bundle.get("nuclear_picture", {})
    china_threat = bundle.get("china_threat", {})

    # Prettify chunks
    ph = json.dumps(system_health.get("pipeline_health", {}), indent=2)
    rel = json.dumps(system_health.get("reliability", {}), indent=2)
    bd = json.dumps(base_defense, indent=2)
    nuk = json.dumps(nuclear_picture, indent=2)
    chn = json.dumps(china_threat, indent=2)

    title_time = meta.get("generated_at", datetime.utcnow().isoformat() + "Z")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Ghost Lantern Labs — War Room Brief</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #050711;
      color: #f5f5f5;
      padding: 24px;
      line-height: 1.5;
    }}
    h1, h2 {{
      color: #e0f0ff;
    }}
    .section {{
      border: 1px solid #273043;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 16px;
      background: #0c1220;
    }}
    pre {{
      background: #050a16;
      padding: 12px;
      border-radius: 6px;
      overflow-x: auto;
      font-size: 13px;
    }}
    .meta {{
      font-size: 13px;
      color: #a0a8c0;
    }}
  </style>
</head>
<body>

  <h1>Ghost Lantern Labs — War Room Brief</h1>
  <div class="meta">
    Generated: {title_time}<br/>
    Source: Ghost Lantern Labs / gll_war_room_brief.py
  </div>

  <div class="section">
    <h2>System Health</h2>
    <h3>Pipeline Health</h3>
    <pre>{_escape(ph)}</pre>

    <h3>Sensor Reliability</h3>
    <pre>{_escape(rel)}</pre>
  </div>

  <div class="section">
    <h2>Base Defense Picture</h2>
    <pre>{_escape(bd)}</pre>
  </div>

  <div class="section">
    <h2>Nuclear / Golden Dome Picture</h2>
    <pre>{_escape(nuk)}</pre>
  </div>

  <div class="section">
    <h2>China / Space Threat Context</h2>
    <pre>{_escape(chn)}</pre>
  </div>

</body>
</html>
"""
    return html


def write_war_room_html() -> str:
    """
    Write docs/war_room_brief_latest.html and return its path.
    """
    DOCS_DIR.mkdir(exist_ok=True, parents=True)
    html = build_war_room_html()
    out_path = DOCS_DIR / "war_room_brief_latest.html"
    out_path.write_text(html)
    return str(out_path)


if __name__ == "__main__":
    out = write_war_room_html()
    print(f"War Room HTML written to: {out}")

