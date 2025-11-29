"""
config_guard.py — Day 53 v2
GLL configuration & path guard.

Purpose:
- Check that critical files and directories exist.
- Verify schema file is present and well-formed.
- Sanity-check log and memory locations.
- Confirm key modules (Spectral Owl, cloud, anti-DoS, CLI) exist.
- Give the operator a single "green/red" view of readiness.

Run standalone:
    poetry run python src/config_guard.py
"""

from pathlib import Path
from typing import List, Tuple

from fusion_logger import log_event

# Assume we run from repo root: ~/ghost/parser_starter_kit
REPO_ROOT = Path(__file__).resolve().parent.parent

SRC_DIR = REPO_ROOT / "src"
DATA_DIR = SRC_DIR / "data"

# Core files
BASELINE_SCHEMA = SRC_DIR / "baseline_schema.csv"

# fused_output candidates
FUSED_CANDIDATES = [
    REPO_ROOT / "fused_output.csv",
    SRC_DIR / "fused_output.csv",
    DATA_DIR / "fused_output.csv",
]

LOG_FILE = REPO_ROOT / "fusion_ops_log.csv"
OWL_MEMORY = REPO_ROOT / "owl_memory.txt"

# Cloud + anti-DoS + Owl + CLI components
CLOUD_DIR = SRC_DIR / "cloud"
CLOUD_FILES = [
    CLOUD_DIR / "__init__.py",
    CLOUD_DIR / "azure_blob_stub.py",
    CLOUD_DIR / "azure_function_flow.md",
    CLOUD_DIR / "README.md",
]

CLOUD_DOCS = [
    REPO_ROOT / "CLOUD_READY.md",
    REPO_ROOT / "azure_architecture.md",
]

ANTI_DOS_FILE = SRC_DIR / "anti_dos.py"
BAD_DATA_QUARANTINE = SRC_DIR / "bad_data_quarantine.csv"     # may or may not exist yet
BAD_DATA_HEATMAP = SRC_DIR / "bad_data_heatmap.csv"           # may or may not exist yet

SPECTRAL_OWL_DIR = SRC_DIR / "spectral_owl"
SPECTRAL_OWL_FILES = [
    SPECTRAL_OWL_DIR / "__init__.py",
    SPECTRAL_OWL_DIR / "owl_brain.py",
    SPECTRAL_OWL_DIR / "owl_memory.py",
    SPECTRAL_OWL_DIR / "llm_adapter.py",
]

GHOST_CLI_FILE = SRC_DIR / "ghost_cli.py"
QA_VALIDATOR_FILE = SRC_DIR / "qa_validator.py"


def _check_exists(path: Path, label: str) -> Tuple[bool, str]:
    if path.exists():
        return True, f"✅ {label}: {path}"
    return False, f"❌ {label} MISSING: {path}"


def _check_dir(path: Path, label: str) -> Tuple[bool, str]:
    if path.exists() and path.is_dir():
        return True, f"✅ {label} directory present: {path}"
    return False, f"❌ {label} directory missing: {path}"


def _check_schema(path: Path) -> Tuple[bool, str]:
    if not path.exists():
        return False, f"❌ baseline_schema.csv missing at: {path}"

    try:
        text = path.read_text().strip().splitlines()
    except Exception as e:
        return False, f"❌ baseline_schema.csv unreadable: {e}"

    if not text:
        return False, "❌ baseline_schema.csv is empty."

    header = text[0].strip().split(",")
    required_cols = {"column_name", "required", "type", "description"}
    if not required_cols.issubset(set(header)):
        return (
            False,
            f"❌ baseline_schema.csv header mismatch. "
            f"Expected columns: {required_cols}, found: {set(header)}",
        )

    return True, f"✅ baseline_schema.csv present and header looks correct: {path}"


def _check_fused_output() -> Tuple[bool, str]:
    for candidate in FUSED_CANDIDATES:
        if candidate.exists():
            return True, f"✅ fused_output.csv found at: {candidate}"
    return False, (
        "❌ fused_output.csv not found in any known location. "
        "Run your fusion pipeline first."
    )


def _ensure_owl_memory() -> Tuple[bool, str]:
    try:
        if not OWL_MEMORY.exists():
            OWL_MEMORY.touch()
        # Simple read/write sanity
        _ = OWL_MEMORY.read_text()
        return True, f"✅ Owl memory file OK: {OWL_MEMORY}"
    except Exception as e:
        return False, f"❌ Owl memory file not writable: {e}"


def run_config_guard() -> str:
    """
    Run all checks and return a human-readable summary string.
    Also logs a single summary event to fusion_logger.
    """
    results: List[str] = []
    ok = True

    # Core directories
    for good, msg in [
        _check_dir(SRC_DIR, "SRC"),
        _check_dir(DATA_DIR, "DATA"),
        _check_dir(SPECTRAL_OWL_DIR, "Spectral Owl"),
        _check_dir(CLOUD_DIR, "Cloud"),
    ]:
        results.append(msg)
        if not good:
            ok = False

    # Core schema + fused output
    for good, msg in [
        _check_schema(BASELINE_SCHEMA),
        _check_fused_output(),
    ]:
        results.append(msg)
        if not good:
            ok = False

    # Key Python modules
    for good, msg in [
        _check_exists(GHOST_CLI_FILE, "ghost_cli.py"),
        _check_exists(QA_VALIDATOR_FILE, "qa_validator.py"),
        _check_exists(ANTI_DOS_FILE, "anti_dos.py"),
    ]:
        results.append(msg)
        if not good:
            ok = False

    # Owl components
    for path in SPECTRAL_OWL_FILES:
        good, msg = _check_exists(path, f"Spectral Owl component ({path.name})")
        results.append(msg)
        if not good:
            ok = False

    # Cloud supporting files (docs + stubs) — these are important but not fatal
    for path in CLOUD_FILES:
        good, msg = _check_exists(path, f"Cloud module file ({path.name})")
        results.append(msg)
        if not good:
            ok = False

    for path in CLOUD_DOCS:
        good, msg = _check_exists(path, f"Cloud doc ({path.name})")
        results.append(msg)
        if not good:
            ok = False

    # Owl memory
    good, msg = _ensure_owl_memory()
    results.append(msg)
    if not good:
        ok = False

    # Log file presence (non-fatal)
    if LOG_FILE.exists():
        results.append(f"✅ Log file present: {LOG_FILE}")
    else:
        results.append(
            f"⚠️ Log file not found yet: {LOG_FILE} (will be created on first use)"
        )

    # Optional: bad-data files (just warn)
    if BAD_DATA_QUARANTINE.exists():
        results.append(f"✅ bad_data_quarantine.csv present: {BAD_DATA_QUARANTINE}")
    else:
        results.append(
            f"⚠️ bad_data_quarantine.csv not found (will appear when sanitizer quarantines rows)."
        )

    if BAD_DATA_HEATMAP.exists():
        results.append(f"✅ bad_data_heatmap.csv present: {BAD_DATA_HEATMAP}")
    else:
        results.append(
            f"⚠️ bad_data_heatmap.csv not found (will appear when heatmap prep runs)."
        )

    summary = "\n".join(results)
    status = "ok" if ok else "degraded"
    log_event("config_guard", status, summary.replace("\n", " | "))

    header = "GLL CONFIG GUARD — STATUS\n" + ("=" * 32) + "\n"
    return header + summary


if __name__ == "__main__":
    print(run_config_guard())

