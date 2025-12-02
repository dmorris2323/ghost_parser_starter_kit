"""
apps/gui/app.py — Ghost Lantern Labs GUI

Simple Tkinter-based GUI that shows:
- Daily mission brief (text)
- Spectral fusion minimap sidebar (from gui_minimap.json)

Minimap file is produced by:
    python src/fusion_minimap_overlay.py
or via CLI option 19:
    python src/ghost_cli.py -> 19) Export GUI Minimap Overlay
"""

import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

# --------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = BASE_DIR / "src"
DOCS_DIR = SRC_DIR / "docs"

MINIMAP_FILE = SRC_DIR / "gui_minimap.json"
MISSION_BRIEF_TXT = DOCS_DIR / "daily_mission_brief.txt"
PROFILE_BRIEF_TXT = DOCS_DIR / "profile_mission_brief.txt"


# --------------------------------------------------------------------
# Data loaders
# --------------------------------------------------------------------

def load_gui_minimap():
    """
    Safe loader for the GUI minimap overlay JSON.
    Returns a dict with keys: "map", "timestamp".
    """
    if not MINIMAP_FILE.exists():
        return {"map": {}, "timestamp": None}

    try:
        return json.loads(MINIMAP_FILE.read_text())
    except Exception:
        return {"map": {}, "timestamp": None}


def format_minimap(minimap: dict) -> str:
    """
    Turn the minimap dict into a human-readable text block.
    """
    lines = []
    ts = minimap.get("timestamp")
    if ts:
        lines.append(f"Timestamp: {ts}")
        lines.append("")

    m = minimap.get("map", {})
    if not m:
        lines.append("[No minimap data available]")
        return "\n".join(lines)

    lines.append("=== SENSOR FUSION MINI-MAP ===")
    for sector, stats in m.items():
        c = stats.get("critical", 0)
        w = stats.get("warning", 0)
        s = stats.get("stable", 0)
        lines.append(f"[{sector}]  C:{c}  W:{w}  S:{s}")
    return "\n".join(lines)


def load_mission_brief_text() -> str:
    """
    Try to load a mission brief text file for the main panel.
    Priority:
      1) profile_mission_brief.txt
      2) daily_mission_brief.txt
    """
    if PROFILE_BRIEF_TXT.exists():
        try:
            return PROFILE_BRIEF_TXT.read_text()
        except Exception:
            pass

    if MISSION_BRIEF_TXT.exists():
        try:
            return MISSION_BRIEF_TXT.read_text()
        except Exception:
            pass

    return "[No mission brief text found. Generate one from the CLI or scripts in src/docs.]"


# --------------------------------------------------------------------
# GUI Application
# --------------------------------------------------------------------

class GLLApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ghost Lantern Labs — Spectral Dashboard")
        self.geometry("1100x700")

        self._build_layout()
        self._load_initial_content()

    def _build_layout(self):
        # Main container with two columns
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        # Left: Mission brief
        left_frame = ttk.Frame(self, padding=10)
        left_frame.grid(row=0, column=0, sticky="nsew")

        left_frame.rowconfigure(0, weight=1)
        left_frame.columnconfigure(0, weight=1)

        brief_label = ttk.Label(left_frame, text="Mission Brief", font=("Helvetica", 14, "bold"))
        brief_label.grid(row=0, column=0, sticky="w")

        self.brief_text = tk.Text(left_frame, wrap="word")
        self.brief_text.grid(row=1, column=0, sticky="nsew", pady=(5, 0))

        brief_scroll = ttk.Scrollbar(left_frame, orient="vertical", command=self.brief_text.yview)
        self.brief_text.configure(yscrollcommand=brief_scroll.set)
        brief_scroll.grid(row=1, column=1, sticky="ns")

        # Right: Minimap sidebar
        right_frame = ttk.Frame(self, padding=10)
        right_frame.grid(row=0, column=1, sticky="nsew")

        right_frame.rowconfigure(1, weight=1)
        right_frame.columnconfigure(0, weight=1)

        minimap_label = ttk.Label(right_frame, text="Fusion Mini-Map", font=("Helvetica", 14, "bold"))
        minimap_label.grid(row=0, column=0, sticky="w")

        self.minimap_text = tk.Text(right_frame, width=35, wrap="word")
        self.minimap_text.grid(row=1, column=0, sticky="nsew", pady=(5, 0))

        minimap_scroll = ttk.Scrollbar(right_frame, orient="vertical", command=self.minimap_text.yview)
        self.minimap_text.configure(yscrollcommand=minimap_scroll.set)
        minimap_scroll.grid(row=1, column=1, sticky="ns")

        # Bottom controls
        bottom_frame = ttk.Frame(self, padding=10)
        bottom_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        bottom_frame.columnconfigure(0, weight=0)
        bottom_frame.columnconfigure(1, weight=0)
        bottom_frame.columnconfigure(2, weight=1)

        refresh_brief_btn = ttk.Button(bottom_frame, text="Refresh Mission Brief", command=self.refresh_brief)
        refresh_brief_btn.grid(row=0, column=0, padx=(0, 10))

        refresh_minimap_btn = ttk.Button(bottom_frame, text="Refresh Mini-Map", command=self.refresh_minimap)
        refresh_minimap_btn.grid(row=0, column=1, padx=(0, 10))

        info_label = ttk.Label(
            bottom_frame,
            text="Tip: Run CLI option 19 (Export GUI Minimap Overlay) before refreshing minimap.",
            font=("Helvetica", 9),
        )
        info_label.grid(row=0, column=2, sticky="w")

    def _load_initial_content(self):
        self.refresh_brief()
        self.refresh_minimap()

    def refresh_brief(self):
        text = load_mission_brief_text()
        self.brief_text.delete("1.0", tk.END)
        self.brief_text.insert(tk.END, text)

    def refresh_minimap(self):
        data = load_gui_minimap()
        formatted = format_minimap(data)
        self.minimap_text.delete("1.0", tk.END)
        self.minimap_text.insert(tk.END, formatted)
        if not data.get("map"):
            messagebox.showinfo(
                "Mini-Map",
                "No minimap data found.\n\nRun:\n  python src/fusion_minimap_overlay.py\nor use CLI option 19 to export minimap."
            )


def main():
    app = GLLApp()
    app.mainloop()


if __name__ == "__main__":
    main()

