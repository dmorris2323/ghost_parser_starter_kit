"""
mission_brief_html.py
---------------------

Builds an HTML version of the Daily Mission Brief with:

 - Clean profile badge (no raw Python object repr)
 - Daily mission brief text
 - Fusion Mini-Map (text) section

Outputs:
    docs/daily_mission_brief.html
"""

from __future__ import annotations

from pathlib import Path

from profile_config import get_active_profile
from daily_mission_brief import write_daily_brief
from fusion_minimap import build_minimap

BASE = Path(__file__).parent
DOCS_DIR = BASE / "docs"
TXT_BRIEF_PATH = DOCS_DIR / "daily_mission_brief.txt"
HTML_BRIEF_PATH = DOCS_DIR / "daily_mission_brief.html"
MINIMAP_TXT = BASE / "minimap.txt"


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def _safe_profile_info() -> dict:
    """
    Normalize the active profile into a simple dict so we don't dump a raw
    Python object repr into the HTML.
    """
    try:
        raw = get_active_profile()
    except Exception:
        return {
            "display_name": "Unknown Profile",
            "key": "unknown",
            "mission_context": "Profile loader encountered an error.",
        }

    # Case 1: already a dict
    if isinstance(raw, dict):
        return {
            "display_name": (
                raw.get("display_name")
                or raw.get("name")
                or raw.get("key")
                or "Unknown Profile"
            ),
            "key": raw.get("key", "unknown"),
            "mission_context": raw.get("mission_context", ""),
        }

    # Case 2: custom object (dataclass, namedtuple, etc.)
    display = (
        getattr(raw, "display_name", None)
        or getattr(raw, "name", None)
        or getattr(raw, "key", None)
        or str(raw)
    )

    key = getattr(raw, "key", None)
    if not key:
        key = str(display).lower().replace(" ", "_")

    mission_context = getattr(raw, "mission_context", "")

    return {
        "display_name": str(display),
        "key": str(key),
        "mission_context": str(mission_context),
    }


def _get_daily_brief_text() -> str:
    """
    Ensure the text daily mission brief exists, then load it.
    """
    if not TXT_BRIEF_PATH.exists():
        write_daily_brief()

    try:
        return TXT_BRIEF_PATH.read_text(encoding="utf-8")
    except Exception as e:
        return f"[ERROR reading daily brief] {e}"


def _get_minimap_text() -> str:
    """
    Ensure minimap.txt exists (build if needed), then load it.
    """
    try:
        build_minimap()
    except Exception as e:
        return f"[Mini-map build error] {e}"

    if not MINIMAP_TXT.exists():
        return "[Mini-map missing] minimap.txt not found."

    try:
        return MINIMAP_TXT.read_text(encoding="utf-8")
    except Exception as e:
        return f"[Mini-map load error] {e}"


# ------------------------------------------------------------
# HTML Builder
# ------------------------------------------------------------

def build_html_brief() -> str:
    """
    Construct the full HTML for the daily mission brief.
    """
    profile = _safe_profile_info()
    brief_text = _get_daily_brief_text()
    minimap_text = _get_minimap_text()

    profile_badge = f"{profile['display_name']} ({profile['key']})"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Ghost Lantern Labs — Daily Mission Brief</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background-color: #0b0c10;
      color: #e5e5e5;
      margin: 0;
      padding: 20px;
    }}
    .container {{
      max-width: 960px;
      margin: 0 auto;
      background: #161821;
      border-radius: 16px;
      padding: 24px 32px;
      box-shadow: 0 0 24px rgba(0,0,0,0.6);
    }}
    h1 {{
      margin-top: 0;
      font-size: 28px;
      color: #ffffff;
    }}
    .subtitle {{
      color: #9ca3af;
      margin-bottom: 16px;
    }}
    .profile-pill {{
      display: inline-block;
      padding: 6px 12px;
      border-radius: 999px;
      background: #1f2937;
      color: #e5e7eb;
      font-size: 13px;
      margin-bottom: 8px;
    }}
    .section-title {{
      margin-top: 24px;
      margin-bottom: 8px;
      font-size: 16px;
      color: #f9fafb;
    }}
    pre {{
      background: #111827;
      padding: 12px 16px;
      border-radius: 8px;
      white-space: pre-wrap;
      word-wrap: break-word;
      font-size: 13px;
      line-height: 1.5;
    }}
    .minimap {{
      margin-top: 8px;
      margin-bottom: 16px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Ghost Lantern Labs — Daily Mission Brief</h1>
    <div class="profile-pill">Profile: {profile_badge}</div>
    <div class="subtitle">
      Operator view — fused system, sensor readiness, AOI mini-map, and profile context.
    </div>

    <div class="section">
      <div class="section-title">Fusion Mini-Map (AOI Overview)</div>
      <pre class="minimap">{minimap_text}</pre>
    </div>

    <div class="section">
      <div class="section-title">Daily Mission Brief</div>
      <pre>{brief_text}</pre>
    </div>
  </div>
</body>
</html>
"""
    return html


def write_html_brief() -> None:
    """
    Write the HTML brief to docs/daily_mission_brief.html
    """
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    html = build_html_brief()
    HTML_BRIEF_PATH.write_text(html, encoding="utf-8")
    print(f"[OK] HTML mission brief -> {HTML_BRIEF_PATH}")


def main():
    write_html_brief()


if __name__ == "__main__":
    main()

