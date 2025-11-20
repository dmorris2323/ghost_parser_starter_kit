# ============================
# validators.py (FINAL VERSION)
# ============================

import pandas as pd

# ----------------------------
# Required column validator
# ----------------------------
def validate_required_columns(df: pd.DataFrame, required: list, module_name: str) -> bool:
    missing = [c for c in required if c not in df.columns]
    if missing:
        from fusion_logger import log_event
        msg = f"Missing required columns: {missing}"
        print(f"❌ {module_name}: {msg}")
        log_event(module_name, "error", msg)
        return False
    return True


# ----------------------------
# Numeric field validator
# ----------------------------
def validate_numeric_fields(df: pd.DataFrame, fields: list, module_name: str) -> bool:
    from fusion_logger import log_event

    for field in fields:
        if field in df.columns:
            try:
                pd.to_numeric(df[field])
            except Exception:
                msg = f"Non-numeric values in '{field}'"
                print(f"❌ {module_name}: {msg}")
                log_event(module_name, "error", msg)
                return False
    return True


# ----------------------------
# Row integrity validator
# ----------------------------
def validate_row_integrity(df: pd.DataFrame, module_name: str) -> bool:
    from fusion_logger import log_event
    if df.isnull().any().any():
        idx = df[df.isnull().any(axis=1)].index.tolist()
        msg = f"Null rows found at indexes: {idx}"
        print(f"❌ {module_name}: {msg}")
        log_event(module_name, "error", msg)
        return False
    return True


# ----------------------------
# Physics validator
# Ensures plausible ranges:
# seismic: 4.0–9.5
# radiation: 0–500 µSv
# comms: Normal/Burst/Silence
# ----------------------------
def validate_physics(df: pd.DataFrame, module_name: str) -> bool:
    from fusion_logger import log_event

    bad_rows = []

    for i, r in df.iterrows():
        # Seismic magnitude
        if "Seismic_Mag" in r and not (4.0 <= float(r["Seismic_Mag"]) <= 9.5):
            bad_rows.append(i)

        # Radiation
        if "Radiation_uSv" in r and not (0 <= float(r["Radiation_uSv"]) <= 500):
            bad_rows.append(i)

        # Comms
        if "Comms_State" in r:
            if r["Comms_State"] not in ["Normal", "Burst", "Silence"]:
                bad_rows.append(i)

    if bad_rows:
        msg = f"Invalid physics rows at indexes: {bad_rows}"
        print(f"❌ Invalid physics rows at indexes: {bad_rows}")
        log_event(module_name, "invalid_physics", msg)
        return False

    return True

