"""
data/loader.py — Load and prepare the tractor and implement databases

This module reads two Excel files:
  1. "DB trattori.xlsx" - contains a list of available tractors with their specs
  2. "DB macchine.xlsx" - contains a list of implements/machines with their specs

It cleans up the data (removes extra spaces, handles missing values) so that
the matching logic can work smoothly. The data is cached so if you load it
multiple times, it doesn't read the file again.
"""

from __future__ import annotations
from pathlib import Path
import pandas as pd


# ── Locate DB files ──────────────────────────────────────────────────────────
_ROOT = Path(__file__).parent.parent
_DB_TRATTORI = _ROOT / "data" / "DB trattori.xlsx"
_DB_MACCHINE  = _ROOT / "data" / "DB macchine.xlsx"

# Fall back to repo root for convenience during dev
_DB_TRATTORI_ALT = _ROOT / "DB trattori.xlsx"
_DB_MACCHINE_ALT  = _ROOT / "DB macchine.xlsx"


def _resolve(primary: Path, fallback: Path) -> Path:
    """
    Find a database file in one of two possible locations.
    
    First tries to find the file in the preferred location (primary).
    If not found there, looks in a backup location (fallback).
    If found nowhere, shows a helpful error message telling the user
    where the file should be placed.
    
    Args:
        primary: The preferred folder location for the file
        fallback: The backup folder location if primary doesn't exist
    
    Returns:
        The path to the file that was found
    
    Raises:
        FileNotFoundError: If the file doesn't exist in either location
    """
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
    """
    Clean up the database by removing extra spaces and handling empty values.
    
    This makes the data consistent so searches work properly. For example:
    - Removes leading/trailing spaces from column headers
    - Removes extra spaces from text in cells
    - Converts "nan" text entries into proper empty values
    
    Args:
        df: The raw database table (DataFrame) to clean
    
    Returns:
        The same table with spaces trimmed and data normalized
    """
    df.columns = df.columns.str.strip()
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip().replace("nan", pd.NA)
    return df


_cache: tuple[pd.DataFrame, pd.DataFrame] | None = None


def load_databases() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load and prepare both the tractor and implement databases.
    
    This is the main function you call to get the data. It:
    - Finds the two Excel files (tractors and implements)
    - Reads them into data tables
    - Cleans them up (removes spaces, fixes formatting)
    - Remembers them so future calls are fast
    
    Returns:
        A pair of tables: (tractors_table, implements_table)
        Each table is a spreadsheet-like structure with rows and columns
    
    Raises:
        FileNotFoundError: If the Excel files can't be found
    """
    global _cache
    if _cache is not None:
        return _cache

    path_trattori = _resolve(_DB_TRATTORI, _DB_TRATTORI_ALT)
    path_macchine  = _resolve(_DB_MACCHINE,  _DB_MACCHINE_ALT)

    df_trattori = _normalise(pd.read_excel(path_trattori))
    df_macchine  = _normalise(pd.read_excel(path_macchine))

    _cache = (df_trattori, df_macchine)
    return _cache
