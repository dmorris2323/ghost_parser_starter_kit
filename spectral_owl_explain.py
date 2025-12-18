# spectral_owl_explain.py  (repo root shim)
from __future__ import annotations

# This shim exists so imports work from repo root AND Streamlit.
# It forwards to src.spectral_owl_explain which contains the real code.

from src.spectral_owl_explain import (  # noqa: F401
    explain_installation_threat_map,
    explain_commander_brief,
    explain_legal_snapshot,
)

__all__ = [
    "explain_installation_threat_map",
    "explain_commander_brief",
    "explain_legal_snapshot",
]

