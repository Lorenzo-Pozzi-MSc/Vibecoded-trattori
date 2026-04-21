"""
logic/matcher.py — The brain of the matching system

This module contains the logic that decides which tractors and machines are
compatible with each other based on your filters.

How it works:
  1. HARD FILTERS ("must-haves") - These eliminate incompatible equipment.
     For example: if you specify a tractor must have 4-wheel drive,
     any 2-wheel drive tractor is immediately ruled out.
  
  2. SOFT FILTERS ("nice-to-haves") - These don't eliminate items, but
     add points to a "match score". The better an item matches these
     optional preferences, the higher its score (0-100%).

For example:
  - Hard filter: "Power must be at least 50 CV" → rules out weak tractors
  - Soft filter: "Smaller turning radius is better" → a 12m radius scores higher
                 than a 15m radius, but both survive because of hard filter

The results are sorted so the best matches appear first.
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Any


# ════════════════════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════════════════════

def _to_float(val: Any) -> float | None:
    """
    Try to convert any value into a decimal number.
    
    Handles common issues like:
    - Text that contains commas instead of decimal points (e.g., "3,5" → 3.5)
    - Extra spaces around numbers
    - Invalid values that can't be converted (returns None)
    
    Args:
        val: Any value (text, number, etc.) to convert
    
    Returns:
        The number as a decimal, or None if conversion fails
    """
    try:
        return float(str(val).replace(",", ".").strip())
    except (ValueError, TypeError):
        return None


def _cell_contains_any(series: pd.Series, values: list[str]) -> pd.Series:
    """
    Check which cells in a table column contain at least one of given keywords.
    
    This is useful for flexible matching. For example, if a cell contains
    "2-wheel drive, 4-wheel drive" and you search for "4-wheel", it matches
    because "4-wheel" appears in that cell.
    
    The search is case-insensitive ("4WD" matches "4wd").
    
    Args:
        series: A column of data to search through
        values: A list of keywords to look for
    
    Returns:
        A list of True/False values for each cell:
        True = cell contains at least one keyword
        False = cell doesn't contain any keyword
    """
    if not values:
        return pd.Series(True, index=series.index)
    pattern = "|".join(map(lambda v: v.strip(), values))
    return series.fillna("").str.contains(pattern, case=False, regex=True, na=False)


def _numeric_col(df: pd.DataFrame, col: str) -> pd.Series:
    """
    Convert a table column to numbers, handling common formatting issues.
    
    For example:
    - "100,5" (European format with comma) → 100.5
    - " 150 " (with extra spaces) → 150
    - "N/A" or broken text → treated as empty/unknown
    
    Args:
        df: The data table
        col: The name of the column to convert
    
    Returns:
        The column as numbers, with empty values marked as NaN
    """
    return pd.to_numeric(df[col].astype(str).str.replace(",", "."), errors="coerce")


# ════════════════════════════════════════════════════════════════════════════
# Tractor matching
# ════════════════════════════════════════════════════════════════════════════

def _match_trattori(df: pd.DataFrame, f: dict) -> pd.DataFrame:
    """
    Find tractors that match your criteria and rank them by compatibility.
    
    This function:
    1. Takes out any tractors that can't possibly meet your requirements (hard filters)
    2. Scores the remaining tractors based on how well they match nice-to-have features (soft filters)
    3. Sorts them from best match to worst match
    
    Args:
        df: The list of all tractors from the database
        f: A dictionary of your search filters (power range, traction type, etc.)
    
    Returns:
        A sorted list of tractors that match your criteria,
        each with a "_score" column showing the match percentage (0-100%)
    """
    mask = pd.Series(True, index=df.index)
    score_cols: list[pd.Series] = []

    # ── Hard: traction ───────────────────────────────────────────────────
    if f.get("trazione"):
        mask &= df.get("Trazione", pd.Series("", index=df.index)).fillna("").str.contains(
            f["trazione"], case=False, na=False
        )


    # ── Hard: power range ────────────────────────────────────────────────
    p_min_req, p_max_req = f.get("potenza_range", (0, 600))
    pot_min = _numeric_col(df, "Pot. min (CV)") if "Pot. min (CV)" in df.columns else pd.Series(np.nan, index=df.index)
    pot_max = _numeric_col(df, "Pot. max (CV)") if "Pot. max (CV)" in df.columns else pd.Series(np.nan, index=df.index)

    # Tractor overlaps the requested range if:  tractor_min <= req_max  AND  tractor_max >= req_min
    power_ok = (pot_min.fillna(0) <= p_max_req) & (pot_max.fillna(9999) >= p_min_req)
    mask &= power_ok


    # ── Soft: turning radius ─────────────────────────────────────────────
    if "Raggio di Sterzata min (m)" in df.columns:
        raggio = _numeric_col(df, "Raggio di Sterzata min (m)")
        req_raggio = f.get("raggio_svolta", 15.0)
        score_cols.append((raggio <= req_raggio).fillna(True))

    # ── Build score ───────────────────────────────────────────────────────
    filtered = df[mask].copy()
    if not filtered.empty and score_cols:
        score_df = pd.concat([s[mask] for s in score_cols], axis=1)
        filtered["_score"] = (score_df.mean(axis=1) * 100).round(0).astype(int)
    elif not filtered.empty:
        filtered["_score"] = 100

    return filtered.sort_values("_score", ascending=False) if not filtered.empty else filtered


# ════════════════════════════════════════════════════════════════════════════
# Implement matching
# ════════════════════════════════════════════════════════════════════════════

def _match_macchine(df: pd.DataFrame, f: dict) -> pd.DataFrame:
    """
    Find implements/machines that match your criteria and rank them by compatibility.
    
    This function:
    1. Takes out any machines that can't work with your requirements (hard filters)
    2. Scores the remaining machines based on how well they match nice-to-have features (soft filters)
    3. Sorts them from best match to worst match
    
    Args:
        df: The list of all implements/machines from the database
        f: A dictionary of your search filters (power needed, width, operation type, etc.)
    
    Returns:
        A sorted list of machines that match your criteria,
        each with a "_score" column showing the match percentage (0-100%)
    """
    mask = pd.Series(True, index=df.index)
    score_cols: list[pd.Series] = []

    # ── Hard: operation type ──────────────────────────────────────────────
    if f.get("tipo_operazione"):
        col = "Tipo di operazione"
        if col in df.columns:
            mask &= _cell_contains_any(df[col], f["tipo_operazione"])

    # ── Hard: power compatibility ─────────────────────────────────────────
    p_min_req, p_max_req = f.get("potenza_range", (0, 600))
    # Convert tractor CV to HP (≈ 1:1 for practical purposes here)
    if "Potenza minima richiesta HP" in df.columns:
        pot_min_req = _numeric_col(df, "Potenza minima richiesta HP")
        mask &= pot_min_req.fillna(0) <= p_max_req  # tractor can cover minimum


    # ── Hard: transport width ─────────────────────────────────────────────
    ingombro_req = f.get("ingombro_larghezza", 3.0)
    if "Ingombro larghezza min" in df.columns:
        ingombro_min = _numeric_col(df, "Ingombro larghezza min")
        mask &= ingombro_min.fillna(0) <= ingombro_req


    # ── Soft: turning radius ──────────────────────────────────────────────
    req_raggio = f.get("raggio_svolta", 15.0)
    if "Raggio di svolta min" in df.columns:
        raggio = _numeric_col(df, "Raggio di svolta min")
        score_cols.append((raggio <= req_raggio).fillna(True))

    # ── Build score ───────────────────────────────────────────────────────
    filtered = df[mask].copy()
    if not filtered.empty and score_cols:
        score_df = pd.concat([s[mask] for s in score_cols], axis=1)
        filtered["_score"] = (score_df.mean(axis=1) * 100).round(0).astype(int)
    elif not filtered.empty:
        filtered["_score"] = 100

    return filtered.sort_values("_score", ascending=False) if not filtered.empty else filtered


# ════════════════════════════════════════════════════════════════════════════
# Public entry point
# ════════════════════════════════════════════════════════════════════════════

def run_matching(
    db_trattori: pd.DataFrame,
    db_macchine: pd.DataFrame,
    filters: dict[str, Any],
) -> dict[str, pd.DataFrame]:
    """
    Run the complete matching process for both tractors and machines.
    
    This is the main entry point. Given all your filters, it:
    1. Searches the tractor database for compatible tractors
    2. Searches the machine database for compatible implements/machines
    3. Scores and sorts both results
    4. Returns everything organized and ready to display
    
    Args:
        db_trattori: The complete tractor database
        db_macchine: The complete implements/machines database
        filters: Your search criteria (power range, traction, size, etc.)
    
    Returns:
        A dictionary with two results:
        - 'trattori': List of matching tractors, ranked by score
        - 'macchine': List of matching machines, ranked by score
    """
    trattori = _match_trattori(db_trattori, filters)
    macchine = _match_macchine(db_macchine, filters)
    return {"trattori": trattori, "macchine": macchine}
