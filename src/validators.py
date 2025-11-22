# ============================
# validators.py (SCHEMA + PHYSICS AWARE)
# ============================

import pandas as pd

from fusion_logger import log_event
from schema_loader import load_schema


# -----------------------------------------
# ROW INTEGRITY
# -----------------------------------------
def validate_row_integrity(df: pd.DataFrame, module_name: str) -> bool:
    """
    Fail if any completely empty rows exist.
    """
    empty_rows = df.isnull().all(axis=1)
    if empty_rows.any():
        idx = df[empty_rows].index.tolist()
        msg = f"Empty rows detected at indexes: {idx}"
        print(f"❌ {module_name}: {msg}")
        log_event(module_name, "error", msg)
        return False
    return True


# -----------------------------------------
# REQUIRED COLUMNS
# -----------------------------------------
def validate_required_columns(df: pd.DataFrame, required: list, module_name: str) -> bool:
    missing = [c for c in required if c not in df.columns]
    if missing:
        msg = f"Missing required columns: {missing}"
        print(f"❌ {module_name}: {msg}")
        log_event(module_name, "error", msg)
        return False
    return True


# -----------------------------------------
# NUMERIC TYPE CHECKS
# -----------------------------------------
def validate_numeric_fields(df: pd.DataFrame, numeric_cols: list, module_name: str) -> bool:
    bad = []
    for col in numeric_cols:
        if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
            bad.append(col)
    if bad:
        msg = f"Non-numeric values in numeric fields: {bad}"
        print(f"❌ {module_name}: {msg}")
        log_event(module_name, "error", msg)
        return False
    return True


# -----------------------------------------
# PHYSICS CHECKS
# -----------------------------------------
def validate_physics(df: pd.DataFrame, module_name: str) -> bool:
    """
    Simple physics sanity checks:
    - Seismic_Mag >= 0
    - Radiation_uSv >= 0
    """
    bad_indexes = []

    if "Seismic_Mag" in df.columns:
        bad_indexes += df[df["Seismic_Mag"] < 0].index.tolist()

    if "Radiation_uSv" in df.columns:
        bad_indexes += df[df["Radiation_uSv"] < 0].index.tolist()

    bad_indexes = sorted(set(bad_indexes))

    if bad_indexes:
        msg = f"Invalid physics rows at indexes: {bad_indexes}"
        print(f"❌ {module_name}: {msg}")
        log_event(module_name, "invalid_physics", msg)
        return False

    return True


# -----------------------------------------
# SCHEMA VALIDATION (STRICT MODE)
# -----------------------------------------
def validate_schema(df: pd.DataFrame, module_name: str) -> bool:
    """
    Enforce schema from baseline_schema.csv:
    - All required columns present
    - No extra columns
    - Basic type enforcement for int/float/bool
    """

    try:
        schema_df, required_cols = load_schema()
    except Exception as e:
        msg = f"Failed to load schema: {e}"
        print(f"⚠️ {module_name}: {msg}")
        log_event(module_name, "schema_load_error", str(e))
        # If schema file itself is broken, fail safe
        return False

    # 1) Required columns present
    for col in required_cols:
        if col not in df.columns:
            msg = f"Schema error: missing required column '{col}'"
            print(f"❌ {module_name}: {msg}")
            log_event(module_name, "schema_error", msg)
            return False

    # 2) No extra columns beyond what's defined in schema
    allowed = set(schema_df["column_name"].tolist())
    incoming = set(df.columns.tolist())

    extra = sorted(list(incoming - allowed))
    if extra:
        msg = f"Extra columns present: {extra}"
        print(f"❌ {module_name}: {msg}")
        log_event(module_name, "schema_error", msg)
        return False

    # 3) Type enforcement (basic)
    for _, row in schema_df.iterrows():
        col = row["column_name"]
        expected = str(row["type"]).strip().lower()

        if col not in df.columns:
            continue

        series = df[col]

        if expected == "int":
            if not pd.api.types.is_integer_dtype(series):
                msg = f"Type mismatch: {col} must be INT"
                print(f"❌ {module_name}: {msg}")
                log_event(module_name, "schema_error", msg)
                return False

        elif expected == "float":
            if not pd.api.types.is_float_dtype(series) and not pd.api.types.is_integer_dtype(series):
                msg = f"Type mismatch: {col} must be FLOAT-compatible"
                print(f"❌ {module_name}: {msg}")
                log_event(module_name, "schema_error", msg)
                return False

        elif expected == "bool":
            if not pd.api.types.is_bool_dtype(series):
                msg = f"Type mismatch: {col} must be BOOL"
                print(f"❌ {module_name}: {msg}")
                log_event(module_name, "schema_error", msg)
                return False

        # For 'str', we allow object dtype and don't hard-fail

    return True

