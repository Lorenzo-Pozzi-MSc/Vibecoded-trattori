"""
data/loader.py — Load and lightly normalise the two Excel databases.
Cached so the files are only read once per Streamlit session.
"""

from __future__ import annotations
from pathlib import Path
import pandas as pd
import streamlit as st


# ── Locate DB files ──────────────────────────────────────────────────────────
_ROOT = Path(__file__).parent.parent
_DB_TRATTORI = _ROOT / "data" / "DB trattori.xlsx"
_DB_MACCHINE  = _ROOT / "data" / "DB macchine.xlsx"

# Fall back to repo root for convenience during dev
_DB_TRATTORI_ALT = _ROOT / "DB trattori.xlsx"
_DB_MACCHINE_ALT  = _ROOT / "DB macchine.xlsx"


def _resolve(primary: Path, fallback: Path) -> Path:
    if primary.exists():
        return primary
    if fallback.exists():
        return fallback
    raise FileNotFoundError(
        f"Database non trovato.\n"
        f"Atteso: {primary}\n"
        f"Oppure: {fallback}\n\n"
        "Copia i file Excel nella cartella 'data/' o nella root del progetto."
    )


def _normalise(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace from column names and string cells."""
    df.columns = df.columns.str.strip()
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip().replace("nan", pd.NA)
    return df


@st.cache_data(show_spinner="Caricamento database…")
def load_databases() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns (db_trattori, db_macchine) as cleaned DataFrames.
    Raises FileNotFoundError with a helpful message if files are missing.
    """
    path_trattori = _resolve(_DB_TRATTORI, _DB_TRATTORI_ALT)
    path_macchine  = _resolve(_DB_MACCHINE,  _DB_MACCHINE_ALT)

    df_trattori = _normalise(pd.read_excel(path_trattori))
    df_macchine  = _normalise(pd.read_excel(path_macchine))

    return df_trattori, df_macchine
