from pathlib import Path
import csv
from datetime import datetime

# Paths
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
DOCS = SRC / "docs"


def read_text_safe(path: Path, max_chars: int = 2000) -> str:
    """
    Safely read a text file. If it's large, truncate.
    If missing, return a simple N/A message instead of crashing.
    """
    if not path.exists():
        return f"N/A (file not found: {path.name})"
    try:
        txt = path.read_text(encoding="utf-8", errors="ignore")
        if len(txt) > max_chars:
            return txt[:max_chars] + "\n...[truncated]..."
        return txt
    except Exception as e:
        return f"Error reading {path.name}: {e}"


def read_last_line(path: Path) -> str:
    """
    Return the last non-empty line from a file (e.g., logs).
    """
    if not path.exists():
        return f"N/A (no file: {path.name})"
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            lines = [ln.strip() for ln in f.readlines() if ln.strip()]
        if not lines:
            return f"N/A (empty file: {path.name})"
        return lines[-1]
    except Exception as e:
        return f"Error reading last line from {path.name}: {e}"


def summarize_csv_rows(path: Path, label: str) -> str:
    """
    Simple row-count summary for CSV files.
    """
    if not path.exists():
        return f"{label}: N/A (file not found: {path.name})"
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            row_count = sum(1 for _ in f)
        # subtract header if present
        if row_count > 0:
            row_count -= 1
        return f"{label}: {row_count} row(s)"
    except Exception as e:
        return f"{label}: error reading csv ({path.name}): {e}"


def summarize_threat_memory(threat_stats_path: Path, threat_csv_path: Path) -> str:
    """
    Build a compact block describing threat memory state.
    """
    lines = []

    if threat_stats_path.exists():
        lines.append("Threat Memory Stats (from threat_memory_stats.txt):")
        lines.append(read_text_safe(threat_stats_path, max_chars=1000))
    else:
        lines.append("Threat Memory Stats: N/A (no stats file yet)")

    lines.append("")
    lines.append(
        summarize_csv_rows(
            threat_csv_path,
            "Total threat memory events logged"
        )
    )

    return "\n".join(lines)


def build_dashboard() -> str:
    """
    Build a full system status HUD using existing files only.
    No fragile imports — file-based only for resilience.
    """
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # Operator / profile context
    profile_txt = read_text_safe(ROOT / "PROFILE.txt", max_chars=500)

    # Offline / AI-independence status (if present)
    offline_status = read_text_safe(SRC / "offline_status.txt", max_chars=300)

    # Golden Dome alignment status
    golden_dome_status = read_text_safe(DOCS / "golden_dome_status.txt", max_chars=500)

    # Pipeline and sensor health summaries
    pipeline_health_txt = read_text_safe(SRC / "pipeline_health.txt", max_chars=1000)
    sensor_health_txt = read_text_safe(SRC / "sensor_health_report.txt", max_chars=1000)

    # Log tails
    fusion_log_last = read_last_line(SRC / "fusion_ops_log.csv")
    run_history_last = read_last_line(SRC / "data" / "run_history.csv")

    # Threat memory block
    threat_block = summarize_threat_memory(
        SRC / "threat_memory_stats.txt",
        SRC / "data" / "threat_memory.csv",
    )

    # Fusion minimap snapshot (if built)
    minimap_txt = read_text_safe(SRC / "minimap.txt", max_chars=1000)

    # Assemble HUD
    lines = []
    lines.append("========================================")
    lines.append(" GHOST LANTERN LABS — SYSTEM STATUS HUD ")
    lines.append("========================================")
    lines.append(f"Generated: {now}")
    lines.append("")
    lines.append("=== ACTIVE PROFILE / OPERATOR CONTEXT ===")
    lines.append(profile_txt)
    lines.append("")
    lines.append("=== OFFLINE / AI-INDEPENDENCE STATUS ===")
    lines.append(offline_status)
    lines.append("")
    lines.append("=== GOLDEN DOME ALIGNMENT ===")
    lines.append(golden_dome_status)
    lines.append("")
    lines.append("=== PIPELINE HEALTH SUMMARY ===")
    lines.append(pipeline_health_txt)
    lines.append("")
    lines.append("=== SENSOR HEALTH SUMMARY ===")
    lines.append(sensor_health_txt)
    lines.append("")
    lines.append("=== LATEST FUSION OPS LOG ENTRY ===")
    lines.append(fusion_log_last)
    lines.append("")
    lines.append("=== LATEST RUN HISTORY ENTRY ===")
    lines.append(run_history_last)
    lines.append("")
    lines.append("=== THREAT MEMORY OVERVIEW ===")
    lines.append(threat_block)
    lines.append("")
    lines.append("=== FUSION MINI-MAP SNAPSHOT ===")
    lines.append(minimap_txt)
    lines.append("")
    lines.append("End of System Status Dashboard.")
    return "\n".join(lines)


def main() -> None:
    """
    Entry point: build and write the dashboard into src/docs/.
    """
    DOCS.mkdir(parents=True, exist_ok=True)
    dashboard = build_dashboard()
    out_path = DOCS / "system_status_dashboard.txt"
    out_path.write_text(dashboard, encoding="utf-8")
    print(f"[OK] System Status Dashboard written → {out_path}")


if __name__ == "__main__":
    main()

