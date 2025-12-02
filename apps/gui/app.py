"""
apps/gui/app.py — Ghost Lantern Labs GUI

Spectral Dashboard GUI showing:
- Mission Brief (text)
- Fusion Mini-Map (from gui_minimap.json)
- Spectral S.O.S. Overlay (from gui_sos_overlay.json)

Minimap file is produced by:
    python src/fusion_minimap_overlay.py
or via CLI option 19:
    python src/ghost_cli.py -> 19) Export GUI Minimap Overlay

S.O.S. overlay file is produced by:
    python src/spectral_sos_overlay.py
or via CLI option 20:
    python src/ghost_cli.py -> 20) Export SOS Overlay (Situation Summary)
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
SOS_FILE = SRC_DIR / "gui_sos_overlay.json"

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


# --- SOS Overlay Loader -------------------------------------------------------

def load_sos_overlay():
    """
    Safe loader for the Spectral S.O.S. overlay JSON.
    Expected structure (from spectral_sos_overlay.py):
      {
        "timestamp": "...Z",
        "active_profile": {...},
        "ai_engine": {...},
        "threat_memory_summary": "...",
        "critical_alerts": [...],
        "top_scores": [...]
      }
    """
    if not SOS_FILE.exists():
        return {"status": "empty", "data": {}}
    try:
        data = json.loads(SOS_FILE.read_text())
        return {"status": "ok", "data": data}
    except Exception:
        return {"status": "corrupted", "data": {}}


def format_sos_overlay(sos: dict) -> str:
    """
    Turn the SOS overlay dict into a human-readable text block.
    """
    status = sos.get("status", "empty")
    data = sos.get("data", {})

    if status == "empty":
        return "[No SOS overlay found. Run CLI option 20 or spectral_sos_overlay.py.]"
    if status == "corrupted":
        return "[SOS overlay file is corrupted or unreadable.]"

    lines = []

    ts = data.get("timestamp")
    if ts:
        lines.append(f"Timestamp: {ts}")
        lines.append("")

    # Profile
    prof = data.get("active_profile", {})
    lines.append("=== ACTIVE PROFILE ===")
    lines.append(f"Key:   {prof.get('key', 'N/A')}")
    lines.append(f"Name:  {prof.get('display_name', 'N/A')}")
    lines.append("")

    # AI Engine
    eng = data.get("ai_engine", {})
    lines.append("=== AI ENGINE (Phase-2) ===")
    lines.append(f"Provider: {eng.get('provider', 'N/A')}")
    lines.append("")

    # Threat summary
    t_summary = data.get("threat_memory_summary", "")
    lines.append("=== THREAT MEMORY SUMMARY ===")
    lines.append(t_summary if t_summary else "[No threat memory summary]")
    lines.append("")

    # Critical alerts
    lines.append("=== CRITICAL ALERTS (Top 5) ===")
    alerts = data.get("critical_alerts", [])
    if not alerts:
        lines.append("[No critical alerts]")
    else:
        for a in alerts:
            # You can adjust fields depending on your CSV schema
            ts = a.get("timestamp", "N/A")
            level = a.get("level", a.get("severity", "N/A"))
            desc = a.get("description", a.get("message", ""))
            lines.append(f"- [{level}] {ts} — {desc}")
    lines.append("")

    # Top scores
    lines.append("=== TOP FUSION SCORES (Top 5) ===")
    scores = data.get("top_scores", [])
    if not scores:
        lines.append("[No scored events]")
    else:
        for s in scores:
            sid = s.get("id", s.get("event_id", "N/A"))
            score = s.get("score", "N/A")
            lines.append(f"- Event {sid}: score={score}")
    lines.append("")

    return "\n".join(lines)


# --------------------------------------------------------------------
# GUI Application
# --------------------------------------------------------------------

class GLLApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ghost Lantern Labs — Spectral Dashboard")
        self.geometry("1200x750")

        self._build_layout()
        self._load_initial_content()

    def _build_layout(self):
        # Main container with two columns
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        # Left: Mission brief
        left_frame = ttk.Frame(self, padding=10)
        left_frame.grid(row=0, column=0, sticky="nsew")

        left_frame.rowconfigure(1, weight=1)
        left_frame.columnconfigure(0, weight=1)

        brief_label = ttk.Label(left_frame, text="Mission Brief", font=("Helvetica", 14, "bold"))
        brief_label.grid(row=0, column=0, sticky="w")

        self.brief_text = tk.Text(left_frame, wrap="word")
        self.brief_text.grid(row=1, column=0, sticky="nsew", pady=(5, 0))

        brief_scroll = ttk.Scrollbar(left_frame, orient="vertical", command=self.brief_text.yview)
        self.brief_text.configure(yscrollcommand=brief_scroll.set)
        brief_scroll.grid(row=1, column=1, sticky="ns")

        # Right: Minimap + SOS overlay stacked vertically
        right_frame = ttk.Frame(self, padding=10)
        right_frame.grid(row=0, column=1, sticky="nsew")

        right_frame.rowconfigure(1, weight=1)  # minimap text
        right_frame.rowconfigure(3, weight=1)  # sos text
        right_frame.columnconfigure(0, weight=1)

        # Minimap section
        minimap_label = ttk.Label(right_frame, text="Fusion Mini-Map", font=("Helvetica", 14, "bold"))
        minimap_label.grid(row=0, column=0, sticky="w")

        self.minimap_text = tk.Text(right_frame, width=40, wrap="word")
        self.minimap_text.grid(row=1, column=0, sticky="nsew", pady=(5, 10))

        minimap_scroll = ttk.Scrollbar(right_frame, orient="vertical", command=self.minimap_text.yview)
        self.minimap_text.configure(yscrollcommand=minimap_scroll.set)
        minimap_scroll.grid(row=1, column=1, sticky="ns", pady=(5, 10))

        # SOS overlay section
        sos_label = ttk.Label(right_frame, text="Spectral S.O.S. Overlay", font=("Helvetica", 14, "bold"))
        sos_label.grid(row=2, column=0, sticky="w")

        self.sos_text = tk.Text(right_frame, width=40, wrap="word")
        self.sos_text.grid(row=3, column=0, sticky="nsew", pady=(5, 0))

        sos_scroll = ttk.Scrollbar(right_frame, orient="vertical", command=self.sos_text.yview)
        self.sos_text.configure(yscrollcommand=sos_scroll.set)
        sos_scroll.grid(row=3, column=1, sticky="ns", pady=(5, 0))

        # Bottom controls
        bottom_frame = ttk.Frame(self, padding=10)
        bottom_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        bottom_frame.columnconfigure(0, weight=0)
        bottom_frame.columnconfigure(1, weight=0)
        bottom_frame.columnconfigure(2, weight=0)
        bottom_frame.columnconfigure(3, weight=1)

        refresh_brief_btn = ttk.Button(bottom_frame, text="Refresh Mission Brief", command=self.refresh_brief)
        refresh_brief_btn.grid(row=0, column=0, padx=(0, 10))

        refresh_minimap_btn = ttk.Button(bottom_frame, text="Refresh Mini-Map", command=self.refresh_minimap)
        refresh_minimap_btn.grid(row=0, column=1, padx=(0, 10))

        refresh_sos_btn = ttk.Button(bottom_frame, text="Refresh S.O.S. Overlay", command=self.refresh_sos)
        refresh_sos_btn.grid(row=0, column=2, padx=(0, 10))

        info_label = ttk.Label(
            bottom_frame,
            text="Tip: Use CLI options 19 (minimap) and 20 (SOS) before refreshing side panels.",
            font=("Helvetica", 9),
        )
        info_label.grid(row=0, column=3, sticky="w")

    def _load_initial_content(self):
        self.refresh_brief()
        self.refresh_minimap()
        self.refresh_sos()

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
                "No minimap data found.\n\nRun:\n  python src/fusion_minimap_overlay.py\n"
                "or use CLI option 19 to export minimap."
            )

    def refresh_sos(self):
        sos = load_sos_overlay()
        formatted = format_sos_overlay(sos)
        self.sos_text.delete("1.0", tk.END)
        self.sos_text.insert(tk.END, formatted)
        if sos.get("status") == "empty":
            messagebox.showinfo(
                "S.O.S. Overlay",
                "No SOS overlay found.\n\nRun:\n  python src/spectral_sos_overlay.py\n"
                "or use CLI option 20 to export the situation summary."
            )
        elif sos.get("status") == "corrupted":
            messagebox.showwarning(
                "S.O.S. Overlay",
                "SOS overlay file appears corrupted.\nTry regenerating via CLI option 20."
            )


def main():
    app = GLLApp()
    app.mainloop()


if __name__ == "__main__":
    main()

