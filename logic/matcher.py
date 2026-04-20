"""
logic/matcher.py — Core matching logic.

Architecture
────────────
Each filter is applied as an independent boolean mask.
Rows surviving ALL hard filters are then scored by counting how many
soft/optional criteria they satisfy → "_score" column (0–100 %).

Hard filters  : eliminate rows that are clearly incompatible.
Soft filters  : add to the match score but don't disqualify.

This file is intentionally structured so each filter section is easy
to extend, adjust, or replace with more sophisticated logic later.
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Any


# ════════════════════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════════════════════

def _to_float(val: Any) -> float | None:
    """Safely coerce a value to float, returning None on failure."""
    try:
        return float(str(val).replace(",", ".").strip())
    except (ValueError, TypeError):
        return None


def _cell_contains_any(series: pd.Series, values: list[str]) -> pd.Series:
    """
    Return a boolean mask: True if the cell (possibly comma-separated list)
    contains at least one of the given values (case-insensitive substring match).
    """
    if not values:
        return pd.Series(True, index=series.index)
    pattern = "|".join(map(lambda v: v.strip(), values))
    return series.fillna("").str.contains(pattern, case=False, regex=True, na=False)


def _numeric_col(df: pd.DataFrame, col: str) -> pd.Series:
    """Return column coerced to numeric, NaN for unparseable values."""
    return pd.to_numeric(df[col].astype(str).str.replace(",", "."), errors="coerce")


# ════════════════════════════════════════════════════════════════════════════
# Tractor matching
# ════════════════════════════════════════════════════════════════════════════

def _match_trattori(df: pd.DataFrame, f: dict) -> pd.DataFrame:
    """Apply filters to tractor DB and return scored results."""
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
    """Apply filters to implement/machine DB and return scored results."""
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
    Run the full matching pipeline.
    Returns dict with keys 'trattori' and 'macchine', each a scored DataFrame.
    """
    trattori = _match_trattori(db_trattori, filters)
    macchine = _match_macchine(db_macchine, filters)
    return {"trattori": trattori, "macchine": macchine}
