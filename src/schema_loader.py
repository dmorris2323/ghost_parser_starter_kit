import pandas as pd
from pathlib import Path


def load_schema(schema_file: str = "baseline_schema.csv"):
    """
    Load baseline schema from CSV.

    Returns:
        schema_df (DataFrame): full schema table
        required_cols (list): list of required column names
    """

    path = Path(schema_file)

    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {path.resolve()}")

    df = pd.read_csv(path)

    # Ensure schema file has correct columns
    expected_cols = {"column_name", "required", "type", "description"}
    if not expected_cols.issubset(df.columns):
        raise ValueError(
            f"Schema file missing required columns.\n"
            f"Expected: {expected_cols}\n"
            f"Found: {set(df.columns)}"
        )

    # Normalize the "required" field
    df["required"] = (
        df["required"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    required_cols = df[df["required"] == "yes"]["column_name"].tolist()

    return df, required_cols


if __name__ == "__main__":
    schema_df, required_cols = load_schema()
    print("✅ Schema loaded successfully.")
    print("Required columns:", required_cols)

