"""
owl_brain.py — Spectral Owl v3

Analyzes fused scores and writes results into threat memory.
Now auto-detects the score column instead of assuming a fixed name.

Run via:
    python -m spectral_owl.owl_brain
from the src directory, or call analyze_fusion() from other modules.
"""

from pathlib import Path
import pandas as pd

from .threat_memory import append_event


def _detect_score_column(df: pd.DataFrame) -> str | None:
    """
    Try to find which column represents the fusion score.

    Priority:
      1) Column literally named "score"
      2) Any column whose name contains "score" (case-insensitive)
      3) If at least 2 columns exist, assume the second column is the score

    Returns the column name or None if no reasonable guess can be made.
    """
    cols = list(df.columns)

    # 1) Exact match
    if "score" in cols:
        return "score"

    # 2) Case-insensitive contains "score"
    lower_map = {c.lower(): c for c in cols}
    for lc, original in lower_map.items():
        if "score" in lc:
            return original

    # 3) Fallback: second column (common pattern: id, score)
    if len(cols) >= 2:
        return cols[1]

    return None


def analyze_fusion(file_path: str = "scored_output.csv"):
    """
    Reads scored fusion output and decides if critical events exist.
    Writes results to threat memory for long-term learning.

    Returns a dict with:
      - status
      - risk (low/moderate/high if status ok)
      - events (int)
      - message
      - score_column (which column was used)
    """

    src = Path(file_path)
    if not src.exists():
        return {"status": "no_file", "message": f"{file_path} not found"}

    df = pd.read_csv(src)

    score_col = _detect_score_column(df)
    if score_col is None:
        return {
            "status": "bad_schema",
            "message": f"No usable score column detected in {file_path}. Columns: {list(df.columns)}",
        }

    scores = df[score_col]

    critical = df[scores >= 0.80]
    high = df[(scores >= 0.60) & (scores < 0.80)]

    # Log to threat memory
    for _ in critical.to_dict(orient="records"):
        append_event("CRITICAL", "fusion_spike", f"{score_col} ≥ 0.80 detected")

    for _ in high.to_dict(orient="records"):
        append_event("HIGH", "elevated", f"{score_col} between 0.60–0.79")

    if len(critical) > 0:
        return {
            "status": "ok",
            "risk": "high",
            "events": len(critical),
            "message": "Critical threat signatures detected.",
            "score_column": score_col,
        }
    elif len(high) > 0:
        append_event("MEDIUM", "elevated_state", f"{score_col} elevated but sub-critical")
        return {
            "status": "ok",
            "risk": "moderate",
            "events": len(high),
            "message": "Elevated threat activity.",
            "score_column": score_col,
        }
    else:
        append_event("LOW", "normal_state", f"{score_col}: environment stable")
        return {
            "status": "ok",
            "risk": "low",
            "events": 0,
            "message": "Environment stable.",
            "score_column": score_col,
        }


if __name__ == "__main__":
    result = analyze_fusion("scored_output.csv")
    print(result)

