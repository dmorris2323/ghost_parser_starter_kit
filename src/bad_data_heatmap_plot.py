"""
bad_data_heatmap_plot.py — Ghost Lantern Labs
---------------------------------------------
Reads bad-data / anomaly CSV and generates a heatmap PNG
for use in demos, briefs, and future dashboards.

Priority:
  1) bad_data_heatmap.csv
  2) heatmap_data.csv

Supports:
  - Case A: 1 categorical + 1 numeric column
      e.g., reason, count
      -> 1D heatmap (reasons on Y-axis, single "count" column)

  - Case B: 2 categoricals + 1 numeric column
      e.g., sensor, reason, count
      -> 2D heatmap (sensor x reason)

Output:
  - bad_data_heatmap.png  (in current directory)
  - Optional copy in demos/dayXX/ if those folders exist.
"""

from pathlib import Path
from typing import Tuple, Optional

import pandas as pd
import matplotlib.pyplot as plt


def find_source_file() -> Path:
    """
    Decide which file to visualize.
    """
    candidates = [
        Path("bad_data_heatmap.csv"),
        Path("heatmap_data.csv"),
    ]

    for c in candidates:
        if c.exists():
            return c

    raise FileNotFoundError(
        "No bad_data_heatmap.csv or heatmap_data.csv found. "
        "Run bad_data_heatmap_prep.py or your fusion heatmap prep first."
    )


def detect_columns(df: pd.DataFrame) -> Tuple[str, Optional[str], str]:
    """
    Auto-detect:
      - row category column (e.g., sensor, reason)
      - column category (e.g., reason, anomaly_type) or None if only 1 category
      - numeric column (e.g., count, frequency, score)

    Strategy:
      - numeric_cols: first numeric column
      - non_numeric: all non-numeric columns

    Cases:
      - If 1+ numeric, 2+ non-numeric:
          row = non_numeric[0], col = non_numeric[1], value = numeric[0]
      - If 1+ numeric, 1 non-numeric:
          row = non_numeric[0], col = None, value = numeric[0]
      - Otherwise: error
    """
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    non_numeric_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]

    if len(numeric_cols) == 0 or len(non_numeric_cols) == 0:
        raise ValueError(
            f"Unable to detect suitable columns. "
            f"Numeric: {numeric_cols}, Non-numeric: {non_numeric_cols}. "
            f"Expected at least 1 numeric and 1 non-numeric column."
        )

    value_col = numeric_cols[0]

    if len(non_numeric_cols) >= 2:
        row_col = non_numeric_cols[0]
        col_col = non_numeric_cols[1]
        return row_col, col_col, value_col

    # Only one category column (your case: reason, count)
    row_col = non_numeric_cols[0]
    col_col = None
    return row_col, col_col, value_col


def build_heatmap_matrix(
    df: pd.DataFrame,
    row_col: str,
    col_col: Optional[str],
    value_col: str,
) -> pd.DataFrame:
    """
    Pivot into a 2D matrix suitable for heatmap display.
    Missing values are filled with 0.

    - If col_col is None:
        Produce a 1D matrix with a single column "value".
    - Else:
        Standard pivot (row x column).
    """
    if col_col is None:
        # 1D case: index=row_col, single numeric column
        sub = df[[row_col, value_col]].copy()
        matrix = sub.set_index(row_col)
        matrix.columns = ["value"]
        return matrix

    # 2D case: full pivot
    pivot = df.pivot_table(
        index=row_col,
        columns=col_col,
        values=value_col,
        aggfunc="sum",
        fill_value=0,
    )
    return pivot


def plot_heatmap(
    matrix: pd.DataFrame,
    title: str = "GLL Bad-Data Heatmap",
    output_path: Path = Path("bad_data_heatmap.png"),
):
    """
    Plot and save the heatmap using matplotlib.
    Handles both 1D (single column) and 2D (multi-column) cases.
    """
    plt.figure(figsize=(10, 6))

    # imshow expects numeric matrix
    data = matrix.values

    plt.imshow(data, aspect="auto")
    plt.colorbar(label="Count / Score")

    # X-axis labels
    if matrix.shape[1] == 1:
        # Single column heatmap
        plt.xticks([0], [matrix.columns[0]])
    else:
        plt.xticks(range(len(matrix.columns)), matrix.columns, rotation=45, ha="right")

    # Y-axis labels
    plt.yticks(range(len(matrix.index)), matrix.index)

    # Labels
    x_name = matrix.columns.name or ("value" if matrix.shape[1] == 1 else "Category")
    y_name = matrix.index.name or "Category"

    plt.title(title)
    plt.xlabel(x_name)
    plt.ylabel(y_name)

    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def maybe_copy_to_demos(src_path: Path):
    """
    If demos/dayXX folders exist, drop a copy there for brief use.
    """
    for day_folder in ["demos/day54", "demos/day55", "demos/day53"]:
        d = Path(day_folder)
        if d.exists() and d.is_dir():
            target = d / src_path.name
            try:
                target.write_bytes(src_path.read_bytes())
                print(f"[OK] Copied {src_path.name} → {target}")
            except Exception as e:
                print(f"[WARN] Could not copy to {target}: {e}")


def main():
    source = find_source_file()
    print(f"[INFO] Using source file: {source}")

    df = pd.read_csv(source)
    print(f"[INFO] Loaded {len(df)} rows with columns: {list(df.columns)}")

    row_col, col_col, value_col = detect_columns(df)
    print(f"[INFO] Using row={row_col}, col={col_col}, value={value_col}")

    matrix = build_heatmap_matrix(df, row_col, col_col, value_col)
    print(f"[INFO] Heatmap matrix shape: {matrix.shape}")

    output = Path("bad_data_heatmap.png")
    plot_heatmap(matrix, title="GLL Bad-Data Heatmap", output_path=output)
    print(f"[OK] Heatmap written → {output}")

    maybe_copy_to_demos(output)


if __name__ == "__main__":
    main()

