"""
mission_brief_html.py — Ghost Lantern Labs
------------------------------------------

Takes the text mission brief from daily_mission_brief.build_mission_brief()
and exports a simple, styled HTML version for demos and future GUI work.

Output:
- docs/daily_mission_brief.html
"""

from __future__ import annotations

from pathlib import Path
from html import escape

from daily_mission_brief import build_mission_brief


BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "docs"
DOCS_DIR.mkdir(exist_ok=True, parents=True)

HTML_PATH = DOCS_DIR / "daily_mission_brief.html"


def text_to_html_paragraphs(text: str) -> str:
    """
    Convert newline-based sections into <p> and <pre>-style blocks.
    Very simple formatting: blank lines separate paragraphs.
    """
    lines = text.splitlines()
    blocks = []
    current_block: list[str] = []

    for line in lines:
        if line.strip() == "":
            if current_block:
                blocks.append("\n".join(current_block))
                current_block = []
        else:
            current_block.append(line)

    if current_block:
        blocks.append("\n".join(current_block))

    html_parts = []
    for blk in blocks:
        # Escape HTML special chars
        safe = escape(blk)
        # If it's clearly a header-style block, render bold
        if blk.startswith("===") or blk.startswith(">> "):
            html_parts.append(f"<pre><strong>{safe}</strong></pre>")
        else:
            html_parts.append(f"<pre>{safe}</pre>")

    return "\n".join(html_parts)


def build_html() -> str:
    """
    Build the complete HTML for the mission brief.
    """
    brief_text = build_mission_brief()
    brief_body = text_to_html_paragraphs(brief_text)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>GLL Daily Mission Brief</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background-color: #050810;
      color: #f5f7ff;
      margin: 0;
      padding: 24px;
    }}
    .container {{
      max-width: 960px;
      margin: 0 auto;
      background: #0b1020;
      border-radius: 12px;
      padding: 24px 28px;
      box-shadow: 0 0 24px rgba(0, 0, 0, 0.5);
      border: 1px solid #1f2940;
    }}
    h1 {{
      margin-top: 0;
      font-size: 1.8rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: #7dd3fc;
    }}
    h2 {{
      font-size: 1.1rem;
      margin-top: 1.5rem;
      color: #a5b4fc;
      text-transform: uppercase;
      letter-spacing: 0.12em;
    }}
    pre {{
      background: #050816;
      padding: 8px 10px;
      border-radius: 6px;
      overflow-x: auto;
      font-size: 0.9rem;
      line-height: 1.4;
      border: 1px solid #1f2937;
      margin-bottom: 8px;
      white-space: pre-wrap;
    }}
    .badge {{
      display: inline-block;
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.16em;
      padding: 3px 8px;
      border-radius: 999px;
      background: #111827;
      color: #e5e7eb;
      border: 1px solid #374151;
      margin-left: 8px;
    }}
    .meta {{
      font-size: 0.75rem;
      color: #9ca3af;
      margin-bottom: 16px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>
      Ghost Lantern Labs
      <span class="badge">Daily Mission Brief</span>
    </h1>
    <div class="meta">
      Rendered from pipeline outputs (run_history, threat_levels, sensor health, analyst notes).
    </div>
    {brief_body}
  </div>
</body>
</html>
"""
    return html


def main() -> None:
    html = build_html()
    HTML_PATH.write_text(html, encoding="utf-8")
    print("✅ HTML mission brief generated.")
    print(f"   Path: {HTML_PATH}")


if __name__ == "__main__":
    main()

