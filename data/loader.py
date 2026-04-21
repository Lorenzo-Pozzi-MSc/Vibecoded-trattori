"""
data/loader.py — Load and prepare the tractor and implement databases

This module reads two Excel files:
  1. "DB trattori.xlsx" - contains a list of available tractors with their specs
  2. "DB macchine.xlsx" - contains a list of implements/machines with their specs

It cleans up the data (removes extra spaces, handles missing values) and creates
structured data models from the raw Excel data. The databases are cached so if you 
load them multiple times, it doesn't read the file again.
"""

from __future__ import annotations
from pathlib import Path
import pandas as pd

from data.models import Tractor, Machine, TractorDatabase, MachineDatabase


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


_cache: tuple[TractorDatabase, MachineDatabase] | None = None


def _float_or_none(val) -> float | None:
    """
    Safely convert a value to float, returning None if it can't be converted.
    Handles commas as decimal separators (European format).
    """
    if pd.isna(val) or str(val).strip().lower() in ("nan", "na", ""):
        return None
    try:
        return float(str(val).replace(",", ".").strip())
    except (ValueError, TypeError):
        return None


def _bool_or_false(val) -> bool:
    """
    Safely convert a value to boolean.
    Accepts "sì", "si", "yes", "true", "1" as True.
    """
    if pd.isna(val):
        return False
    val_str = str(val).strip().lower()
    return val_str in ("sì", "si", "yes", "true", "1")


def _string_or_empty(val) -> str:
    """Safely convert a value to string, returning empty string for None/NaN."""
    if pd.isna(val):
        return ""
    return str(val).strip()


def _create_tractors(df: pd.DataFrame) -> list[Tractor]:
    """
    Create Tractor model instances from a DataFrame.
    
    Parses each row and creates a Tractor object with properly typed fields.
    """
    tractors = []
    for _, row in df.iterrows():
        tractor = Tractor(
            name=_string_or_empty(row.get("Nome serie/modello", "")),
            brand=_string_or_empty(row.get("Marchio", "")),
            traction_type=_string_or_empty(row.get("Trazione", "")),
            power_min_cv=_float_or_none(row.get("Pot. min (CV)")),
            power_max_cv=_float_or_none(row.get("Pot. max (CV)")),
            turning_radius_m=_float_or_none(row.get("Raggio di Sterzata min (m)")),
            attachment_categories=_string_or_empty(row.get("Categorie attacco a 3 punti disponibili", "")),
            pto_speeds=_string_or_empty(row.get("Regimi PDP disponibili", "")),
            link=_string_or_empty(row.get("link", "")),
            raw_data=row.to_dict(),
        )
        if tractor.name:  # Only add if name is not empty
            tractors.append(tractor)
    return tractors


def _create_machines(df: pd.DataFrame) -> list[Machine]:
    """
    Create Machine model instances from a DataFrame.
    
    Parses each row and creates a Machine object with properly typed fields.
    """
    machines = []
    for _, row in df.iterrows():
        machine = Machine(
            name=_string_or_empty(row.get("Nome", "")),
            manufacturer=_string_or_empty(row.get("Produttore", "")),
            operation_type=_string_or_empty(row.get("Tipo di operazione", "")),
            machine_type=_string_or_empty(row.get("Tipo di macchina", "")),
            min_power_required_hp=_float_or_none(row.get("Potenza minima richiesta HP")),
            max_power_recommended_hp=_float_or_none(row.get("Potenza massima consigliata HP")),
            min_work_width_m=_float_or_none(row.get("Larghezza di lavoro min")),
            max_work_width_m=_float_or_none(row.get("Larghezza di lavoro max")),
            min_turning_radius_m=_float_or_none(row.get("Raggio di svolta min")),
            attachment_type=_string_or_empty(row.get("Attacco al trattore", "")),
            is_foldable=_bool_or_false(row.get("Ripiegabile", False)),
            technical_sheet_url=_string_or_empty(row.get("URL scheda tecnica produttore/fonte", "")),
            raw_data=row.to_dict(),
        )
        if machine.name:  # Only add if name is not empty
            machines.append(machine)
    return machines


def load_databases() -> tuple[TractorDatabase, MachineDatabase]:
    """
    Load and prepare both the tractor and implement databases.
    
    This is the main function you call to get the data. It:
    - Finds the two Excel files (tractors and implements)
    - Reads them into data tables
    - Cleans them up (removes spaces, fixes formatting)
    - Creates structured Tractor and Machine model instances
    - Returns database containers with both models and raw DataFrames
    - Caches the result so future calls are fast
    
    Returns:
        A pair of databases: (tractor_database, machine_database)
        Each provides both type-safe model access and DataFrame access
    
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

    # Create model instances
    tractors = _create_tractors(df_trattori)
    machines = _create_machines(df_macchine)
    
    # Create database containers
    tractor_db = TractorDatabase(tractors, df_trattori)
    machine_db = MachineDatabase(machines, df_macchine)

    _cache = (tractor_db, machine_db)
    return _cache
